# Copyright 2025 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from pathlib import Path
from typing import Any, List, Optional, Type, Dict
import json
import os
import requests
from pydantic import BaseModel, Field

from core.document_loader import document_loader
from crewai.tools import BaseTool

sample_documents_path = Path(__file__).parent / "sample_documents"


class FileListTool(BaseTool):  # type: ignore[misc]
    name: str = "File List Tool"
    description: str = (
        "This tool will provide a list of all file names and their associated paths. "
        "You should always check to see if the file you are looking for can be found here. "
        "For future queries you should use the full file path instead of just the name to avoid ambiguity."
        "This tool takes no arguments."
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def _run(self) -> List[str]:
        files = [str(f) for f in sample_documents_path.glob("**/*") if f.is_file()]
        if not files:
            raise ValueError(
                "No files found in the folder. Please verify that you have access to datasets "
                "and that your credentials are correct."
            )
        return files


class DocumentReadToolSchema(BaseModel):
    file_path: str = Field(..., description="Mandatory file_path of the file")


class DocumentReadTool(BaseTool):  # type: ignore[misc]
    name: str = "Read the contents of an file"
    description: str = (
        "A tool that reads the contents of a file. To use this tool, provide a 'file_path' "
        "parameter with the filename and or path of the file that should be read."
        "You will receive a dictionary of pages and their associated text."
    )
    args_schema: Type[BaseModel] = DocumentReadToolSchema
    file_path: Optional[str] = None

    def __init__(self, file_path: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.file_path = file_path

    def _run(
        self,
        **kwargs: Any,
    ) -> dict[int, str]:
        file_path = kwargs.get("file_path", self.file_path)
        if not file_path:
            raise ValueError("file_path is required but was not provided")

        try:
            pages: dict[int, str] = document_loader.convert_document_to_text(
                sample_documents_path / file_path
            )
            return pages
        except Exception as e:
            raise ValueError(
                f"Could not read dataset with file_path '{file_path}'. Please verify that the file_path exists "
                f"and you have access to it. Error: {e}"
            )


class KnowledgeBaseContentToolSchema(BaseModel):
    file_uuids: list[str] = Field(
        ..., description="Mandatory list of file UUIDs to retrieve contents for"
    )


class KnowledgeBaseContentTool(BaseTool):  # type: ignore[misc]
    name: str = "Get contents of a list of files from the Knowledge Base"
    description: str = (
        "This tool retrieves the full content of knowledge base files by their UUIDs. "
        "To use this tool, provide a list of file UUIDs (strings in the format like "
        "'44c6434a-7396-4b05-8ff1-bf1ab7f6000a'). You should get these UUIDs from the "
        "Knowledge Base File Searcher's output. "
        "You will receive a dictionary where the keys are the file UUIDs and values are "
        "dictionaries of pages and their associated text. "
        "Example input: ['44c6434a-7396-4b05-8ff1-bf1ab7f6000a', '22b19e27-15b8-4238-98f4-d66571aa0c58']"
    )
    args_schema: Type[BaseModel] = KnowledgeBaseContentToolSchema
    knowledge_base: dict[str, dict[str, str]] = dict()

    def __init__(
        self, knowledge_base: dict[str, dict[str, str]] | None = None, **kwargs: Any
    ) -> None:
        """
        Initializes the KnowledgeBaseContentTool with a knowledge base.
        """
        super().__init__(**kwargs)
        self.knowledge_base = knowledge_base or dict()

    def _run(self, file_uuids: list[str]) -> dict[str, dict[str, str]]:
        """Retrieve the full content of knowledge base files by their UUIDs."""
        if not file_uuids:
            return {
                "error": {
                    "1": "No file UUIDs provided. Please provide a list of file UUIDs to retrieve content. "
                    "You should get these from the Knowledge Base File Searcher's output."
                }
            }

        print(f"DEBUG: Received UUIDs: {file_uuids}", flush=True)
        print(
            f"DEBUG: Available knowledge base keys: {list(self.knowledge_base.keys())}",
            flush=True,
        )

        content_subset: dict[str, dict[str, str]] = {}
        for file_uuid in file_uuids:
            if file_uuid in self.knowledge_base:
                content_subset[file_uuid] = self.knowledge_base[file_uuid]
                print(f"DEBUG: Found content for UUID: {file_uuid}", flush=True)
            else:
                content_subset[file_uuid] = {
                    "1": f"Content not found for file UUID: {file_uuid}"
                }
                print(f"DEBUG: Content not found for UUID: {file_uuid}", flush=True)
        return content_subset


class ForecastSummaryToolSchema(BaseModel):
    query: str = Field(..., description="The forecast query or question being asked")


class ForecastSummaryTool(BaseTool):  # type: ignore[misc]
    name: str = "Get Forecast Summary"
    description: str = (
        "This tool retrieves a comprehensive forecast summary including top account variances, "
        "product impacts, and overall metrics. Use this when users ask about forecast overviews, "
        "top performers, biggest variances, or general forecast health."
    )
    args_schema: Type[BaseModel] = ForecastSummaryToolSchema

    def _run(self, **kwargs: Any) -> str:
        query = kwargs.get("query", "forecast summary")  # Extract the query parameter
        
        try:
            response = requests.get(
                "http://localhost:8080/api/v1/forecast/summary",
                headers={
                    "Authorization": f"Bearer {os.environ.get('DATAROBOT_API_TOKEN')}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Format the response for our new NVIDIA data structure
            forecast_metrics = data.get('forecast_metrics', {})
            top_accounts = data.get('top_variance_accounts', [])
            product_breakdown = data.get('product_breakdown', [])
            
            summary = f"""
NVIDIA FORECAST SUMMARY:
Total BUF Revenue: ${forecast_metrics.get('total_buf_revenue', 0):,.2f}
Total RSF Revenue: ${forecast_metrics.get('total_rsf_revenue', 0):,.2f}
Overall Variance: ${forecast_metrics.get('total_variance', 0):,.2f} ({forecast_metrics.get('variance_percentage', 0):+.2f}%)
Total Deals: {forecast_metrics.get('deal_count', 0):,}

TOP ACCOUNTS WITH HIGHEST BUF vs RSF VARIANCES:
"""
            for i, account in enumerate(top_accounts[:5], 1):
                variance_pct = account.get('variance_percentage', 0)
                summary += f"{i}. {account.get('account', 'Unknown')}: ${account.get('total_rsf_revenue', 0):,.2f} (Variance: ${account.get('total_variance', 0):,.2f}, {variance_pct:+.1f}%)\n"

            summary += "\nTOP PRODUCT FAMILIES BY REVENUE:\n"
            for i, product in enumerate(product_breakdown[:5], 1):
                variance_pct = product.get('variance_percentage', 0) 
                summary += f"{i}. {product.get('product', 'Unknown')}: ${product.get('total_rsf_revenue', 0):,.2f} ({product.get('account_count', 0)} accounts, {variance_pct:+.1f}% variance)\n"
            
            return summary
            
        except Exception as e:
            return f"Error retrieving forecast summary: {str(e)}"


class AccountVarianceToolSchema(BaseModel):
    account_name: str = Field(..., description="Name of the account to analyze")
    period: str = Field(default="current", description="Time period for analysis (current, previous)")


class AccountVarianceTool(BaseTool):  # type: ignore[misc]
    name: str = "Get Account Variance Details"
    description: str = (
        "This tool retrieves detailed variance analysis for a specific account, including "
        "product-level breakdowns, historical trends, and reasons for variances. "
        "Use this when users ask about specific accounts or companies."
    )
    args_schema: Type[BaseModel] = AccountVarianceToolSchema

    def _run(self, **kwargs: Any) -> str:
        account_name = kwargs.get("account_name", "")
        period = kwargs.get("period", "current")
        
        try:
            response = requests.get(
                f"http://localhost:8080/api/v1/forecast/account/{account_name}/variance",
                params={"period": period},
                headers={
                    "Authorization": f"Bearer {os.environ.get('DATAROBOT_API_TOKEN')}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle our new API format - data is a list of accounts
            if isinstance(data, list):
                if not data:
                    return f"No data found for account: {account_name}"
                
                # Check if first item is an error
                first_item = data[0]
                if "error" in first_item:
                    available_accounts = first_item.get("available_accounts", [])[:5]
                    return f"""
ERROR: {first_item['error']}

AVAILABLE ACCOUNTS (sample):
{chr(10).join(f"- {acc}" for acc in available_accounts)}
"""
                
                # Process account data
                analysis = f"""
NVIDIA ACCOUNT VARIANCE ANALYSIS:

TOP ACCOUNTS BY BUF vs RSF VARIANCE:
"""
                for i, account in enumerate(data[:10], 1):
                    variance_pct = account.get('variance_percentage', 0)
                    analysis += f"{i}. {account.get('account', 'Unknown')}\n"
                    analysis += f"   - BUF Revenue: ${account.get('total_buf_revenue', 0):,.2f}\n"
                    analysis += f"   - RSF Revenue: ${account.get('total_rsf_revenue', 0):,.2f}\n"
                    analysis += f"   - Variance: ${account.get('total_variance', 0):,.2f} ({variance_pct:+.1f}%)\n"
                    analysis += f"   - Deal Count: {account.get('deal_count', 0)}\n"
                    analysis += f"   - Avg Deal Size: ${account.get('avg_deal_size', 0):,.2f}\n\n"
                
                return analysis
            else:
                # Legacy format (shouldn't happen with our new API)
                return f"Unexpected data format received for account: {account_name}"
            
        except Exception as e:
            return f"Error retrieving account variance for {account_name}: {str(e)}"


class ProductImpactToolSchema(BaseModel):
    product_name: str = Field(..., description="Name of the product to analyze")


class ProductImpactTool(BaseTool):  # type: ignore[misc]
    name: str = "Get Product Impact Analysis"
    description: str = (
        "This tool analyzes the impact of a specific product across all accounts, including "
        "total forecast contribution, account-level impacts, market factors, and risk factors. "
        "Use this when users ask about specific products or product lines."
    )
    args_schema: Type[BaseModel] = ProductImpactToolSchema

    def _run(self, **kwargs: Any) -> str:
        product_name = kwargs.get("product_name", "")
        
        try:
            response = requests.get(
                f"http://localhost:8080/api/v1/forecast/product/{product_name}/impact",
                headers={
                    "Authorization": f"Bearer {os.environ.get('DATAROBOT_API_TOKEN')}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle the new NVIDIA API response format (list of products)
            if isinstance(data, list) and len(data) > 0:
                # Check if we have an error response
                if 'error' in data[0]:
                    available_products = data[0].get('available_products', [])
                    return f"Error: {data[0]['error']}\nAvailable products: {', '.join(available_products[:5])}"
                
                # Process the product data
                total_products = len(data)
                total_buf_revenue = sum(product.get('total_buf_revenue', 0) for product in data)
                total_rsf_revenue = sum(product.get('total_rsf_revenue', 0) for product in data)
                total_variance = sum(product.get('total_variance', 0) for product in data)
                total_accounts = sum(product.get('account_count', 0) for product in data)
                
                analysis = f"""
NVIDIA PRODUCT IMPACT ANALYSIS FOR "{product_name}":
Found {total_products} matching product(s)
Total BUF Revenue: ${total_buf_revenue:,.2f}
Total RSF Revenue: ${total_rsf_revenue:,.2f}
Total Variance: ${total_variance:,.2f} ({(total_variance/total_rsf_revenue*100) if total_rsf_revenue != 0 else 0:+.1f}%)
Total Accounts Affected: {total_accounts}

TOP PRODUCT BREAKDOWN:
"""
                for i, product in enumerate(data[:5], 1):  # Show top 5 products
                    variance_pct = product.get('variance_percentage', 0)
                    analysis += f"{i}. {product.get('product', 'Unknown')}: ${product.get('total_rsf_revenue', 0):,.2f} "
                    analysis += f"({product.get('account_count', 0)} accounts, {variance_pct:+.1f}% variance)\n"
                
                return analysis
                
            else:
                return f"No product data found for '{product_name}'. Please check the product name."
            
        except Exception as e:
            return f"Error retrieving product impact for {product_name}: {str(e)}"
