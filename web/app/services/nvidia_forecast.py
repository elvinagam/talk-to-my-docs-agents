"""NVIDIA Forecast Service to handle real EFM data format."""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
from pathlib import Path


class NvidiaForecastService:
    """Service that processes real NVIDIA EFM forecast data."""
    
    def __init__(self, data_file_path: Optional[str] = None):
        """Initialize with NVIDIA forecast data."""
        self.data_file_path = data_file_path or self._get_default_data_path()
        self.df: Optional[pd.DataFrame] = None
        self._load_data()
        
    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Access to the underlying DataFrame."""
        return self.df
        
    def _get_default_data_path(self) -> str:
        """Get default path for NVIDIA data file."""
        return str(Path(__file__).parent.parent.parent.parent / "data" / "nvidia_forecast_data.csv")
        
    def _load_data(self):
        """Load and preprocess NVIDIA forecast data."""
        try:
            if os.path.exists(self.data_file_path):
                # Try UTF-8 first, then latin1 for encoding issues
                try:
                    self.df = pd.read_csv(self.data_file_path)
                except UnicodeDecodeError:
                    print("⚠️  UTF-8 encoding failed, trying latin1...")
                    self.df = pd.read_csv(self.data_file_path, encoding='latin1')
                    
                print(f"✅ Loaded NVIDIA data: {len(self.df)} rows, {len(self.df.columns)} columns")
                self._preprocess_data()
            else:
                print(f"⚠️  Data file not found at {self.data_file_path}. Creating sample data structure.")
                self.df = self._create_sample_nvidia_data()
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            print("Creating sample data structure as fallback.")
            self.df = self._create_sample_nvidia_data()
            
    def _preprocess_data(self):
        """Clean and prepare the data for analysis."""
        if self.df is None:
            return
            
        try:
            # Convert numeric columns for real NVIDIA data
            numeric_columns = ['Final BUF Rev. (Outbound)', 'Final RSF Rev. (Outbound)', 'Probability %']
            for col in numeric_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
            
            # Calculate variance and handle NaN
            if 'Final BUF Rev. (Outbound)' in self.df.columns and 'Final RSF Rev. (Outbound)' in self.df.columns:
                self.df['BUF_RSF_Variance'] = (self.df['Final BUF Rev. (Outbound)'] - self.df['Final RSF Rev. (Outbound)']).fillna(0)
                    
            print(f"✅ Preprocessed data: {len(self.df)} rows ready for analysis")
            
        except Exception as e:
            print(f"⚠️  Error during preprocessing: {e}")
    
    def _create_sample_nvidia_data(self) -> pd.DataFrame:
        """Create sample NVIDIA data structure matching the real format."""
        import random
        
        # Sample accounts and products based on NVIDIA's structure
        accounts = ['Tesla', 'Mercedes-Benz', 'BMW Group', 'Toyota', 'Ford', 'GM', 'Audi', 'Volvo', 'NIO', 'BYD']
        products = ['DRIVE Orin', 'DRIVE Thor', 'DRIVE Hyperion', 'GeForce RTX', 'Jetson AGX', 'Clara AGX']
        regions = ['North America', 'Europe', 'Asia Pacific', 'China', 'Japan']
        
        # Generate 100 sample records
        sample_data = []
        for i in range(100):
            buf_rev = random.uniform(1000000, 50000000)  # $1M - $50M
            rsf_rev = buf_rev * random.uniform(0.7, 1.3)  # RSF varies by ±30%
            variance = buf_rev - rsf_rev
            variance_pct = (variance / rsf_rev * 100) if rsf_rev != 0 else 0
            
            record = {
                'Customer Desc.': random.choice(accounts),
                'Product Description': random.choice(products),
                'Region': random.choice(regions),
                'BUF Rev': buf_rev,
                'RSF Rev': rsf_rev,
                'BUF vs RSF Revenue Variance': variance,
                'BUF vs RSF Revenue Variance %': variance_pct,
                'BUF Date': datetime.now() - timedelta(days=random.randint(0, 90)),
                'RSF Date': datetime.now() - timedelta(days=random.randint(0, 90)),
                'Deal Close Date': datetime.now() + timedelta(days=random.randint(0, 180)),
                'Probability %': random.uniform(50, 95),
                'Stage': random.choice(['Qualified', 'Proposal', 'Negotiation', 'Closing']),
                'Sales Rep': f'Rep_{i%10}',
                'Account Manager': f'AM_{i%5}',
                'Business Unit': random.choice(['Automotive', 'Data Center', 'Gaming', 'Professional Visualization']),
            }
            sample_data.append(record)
            
        df = pd.DataFrame(sample_data)
        print(f"✅ Created sample NVIDIA data: {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def _safe_df_operation(self, operation_name: str, default_result: Any = None) -> Any:
        """Safely perform DataFrame operations with fallback."""
        if self.df is None or self.df.empty:
            print(f"⚠️  No data available for {operation_name}")
            return default_result
        return None
    
    def _clean_numeric_value(self, value: Any) -> float:
        """Clean numeric values, replacing NaN/inf with 0."""
        try:
            if pd.isna(value) or not isinstance(value, (int, float)):
                return 0.0
            if np.isinf(value):
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def get_buf_vs_rsf_analysis(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get BUF vs RSF variance analysis."""
        if self.df is None or self.df.empty:
            print("⚠️  No data available for BUF vs RSF analysis")
            return []
            
        try:
            # Get records with significant variance
            analysis_data = self.df.copy()
            if 'BUF_RSF_Variance' in analysis_data.columns:
                analysis_data = analysis_data.dropna(subset=['BUF_RSF_Variance'])
                analysis_data['abs_variance'] = analysis_data['BUF_RSF_Variance'].abs()
                analysis_data = analysis_data.nlargest(limit, 'abs_variance')
            else:
                analysis_data = analysis_data.head(limit)
            
            results = []
            for _, row in analysis_data.iterrows():
                buf_rev = self._clean_numeric_value(row.get('Final BUF Rev. (Outbound)', 0))
                rsf_rev = self._clean_numeric_value(row.get('Final RSF Rev. (Outbound)', 0))
                variance = self._clean_numeric_value(row.get('BUF_RSF_Variance', buf_rev - rsf_rev))
                variance_pct = (variance / rsf_rev * 100) if rsf_rev != 0 else 0
                
                results.append({
                    'account': str(row.get('Customer Desc.', 'Unknown')),
                    'product': str(row.get('Item Family', row.get('Product_Family', 'Unknown'))),
                    'region': str(row.get('EC Customer Region', 'Unknown')),
                    'buf_revenue': buf_rev,
                    'rsf_revenue': rsf_rev,
                    'variance_amount': variance,
                    'variance_percentage': round(variance_pct, 2),
                    'probability': self._clean_numeric_value(row.get('Probability %', 0)),
                    'stage': 'Active',  # Not in this dataset
                    'close_date': None,  # Not in this dataset
                })
            
            print(f"✅ Generated BUF vs RSF analysis: {len(results)} records")
            return results
            
        except Exception as e:
            print(f"❌ Error in BUF vs RSF analysis: {e}")
            return []
    
    def get_account_variance_details(self, account_name: Optional[str] = None, period: str = "current", limit: int = 10) -> List[Dict[str, Any]]:
        """Get detailed variance analysis for accounts."""
        if self.df is None or self.df.empty:
            print("⚠️  No data available for account variance analysis")
            return []
            
        try:
            current_data = self.df.copy()
            
            # Filter by account if specified
            if account_name and 'Customer Desc.' in current_data.columns:
                current_data = current_data[current_data['Customer Desc.'].str.contains(account_name, case=False, na=False)]
                
            if current_data.empty:
                available_accounts = []
                if 'Customer Desc.' in self.df.columns:
                    available_accounts = self.df['Customer Desc.'].unique()[:10].tolist()
                    
                return [{
                    "error": f"No data found for account: {account_name}" if account_name else "No account data available",
                    "available_accounts": available_accounts
                }]
            
            # Group by account and calculate metrics
            if 'Customer Desc.' in current_data.columns:
                account_summary = current_data.groupby('Customer Desc.').agg({
                    'Final BUF Rev. (Outbound)': 'sum' if 'Final BUF Rev. (Outbound)' in current_data.columns else lambda x: 0,
                    'Final RSF Rev. (Outbound)': 'sum' if 'Final RSF Rev. (Outbound)' in current_data.columns else lambda x: 0,
                    'BUF_RSF_Variance': 'sum' if 'BUF_RSF_Variance' in current_data.columns else lambda x: 0,
                    'Item Family': 'count' if 'Item Family' in current_data.columns else lambda x: 1
                }).reset_index()
                
                account_summary = account_summary.head(limit)
            else:
                account_summary = current_data.head(limit)
            
            results = []
            for _, row in account_summary.iterrows():
                buf_total = self._clean_numeric_value(row.get('Final BUF Rev. (Outbound)', 0))
                rsf_total = self._clean_numeric_value(row.get('Final RSF Rev. (Outbound)', 0))
                variance_total = self._clean_numeric_value(row.get('BUF_RSF_Variance', buf_total - rsf_total))
                deal_count = max(1, int(self._clean_numeric_value(row.get('Item Family', 1))))
                
                results.append({
                    'account': str(row.get('Customer Desc.', 'Unknown')),
                    'total_buf_revenue': buf_total,
                    'total_rsf_revenue': rsf_total,
                    'total_variance': variance_total,
                    'variance_percentage': round((variance_total / rsf_total * 100) if rsf_total != 0 else 0, 2),
                    'deal_count': deal_count,
                    'avg_deal_size': rsf_total / deal_count if deal_count > 0 else 0,
                })
            
            print(f"✅ Generated account variance analysis: {len(results)} accounts")
            return results
            
        except Exception as e:
            print(f"❌ Error in account variance analysis: {e}")
            return []
    
    def get_product_impact_analysis(self, product_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get product-level impact analysis."""
        if self._safe_df_operation("product impact analysis", []) is not None:
            return []
            
        try:
            current_data = self.df.copy()
            
            # Filter by product if specified
            if product_name and 'Item Family' in current_data.columns:
                current_data = current_data[current_data['Item Family'].str.contains(product_name, case=False, na=False)]
                
            if current_data.empty:
                available_products = []
                if self.df is not None and 'Item Family' in self.df.columns:
                    available_products = self.df['Item Family'].unique()[:10].tolist()
                    
                return [{
                    "error": f"No data found for product: {product_name}" if product_name else "No product data available",
                    "available_products": available_products
                }]
            
            # Group by product and calculate metrics
            if 'Item Family' in current_data.columns:
                product_summary = current_data.groupby('Item Family').agg({
                    'Final BUF Rev. (Outbound)': 'sum' if 'Final BUF Rev. (Outbound)' in current_data.columns else lambda x: 0,
                    'Final RSF Rev. (Outbound)': 'sum' if 'Final RSF Rev. (Outbound)' in current_data.columns else lambda x: 0,
                    'BUF_RSF_Variance': 'sum' if 'BUF_RSF_Variance' in current_data.columns else lambda x: 0,
                    'Customer Desc.': 'nunique' if 'Customer Desc.' in current_data.columns else lambda x: 1,
                    'Probability %': 'mean' if 'Probability %' in current_data.columns else lambda x: 75
                }).reset_index()
                
                product_summary = product_summary.head(limit)
            else:
                product_summary = current_data.head(limit)
            
            results = []
            for _, row in product_summary.iterrows():
                buf_total = self._clean_numeric_value(row.get('Final BUF Rev. (Outbound)', 0))
                rsf_total = self._clean_numeric_value(row.get('Final RSF Rev. (Outbound)', 0))
                variance_total = self._clean_numeric_value(row.get('BUF_RSF_Variance', buf_total - rsf_total))
                account_count = max(1, int(self._clean_numeric_value(row.get('Customer Desc.', 1))))
                avg_probability = self._clean_numeric_value(row.get('Probability %', 75))
                
                results.append({
                    'product': str(row.get('Item Family', 'Unknown')),
                    'total_buf_revenue': buf_total,
                    'total_rsf_revenue': rsf_total,
                    'total_variance': variance_total,
                    'variance_percentage': round((variance_total / rsf_total * 100) if rsf_total != 0 else 0, 2),
                    'account_count': account_count,
                    'avg_probability': round(avg_probability, 1),
                    'revenue_per_account': rsf_total / account_count if account_count > 0 else 0,
                })
            
            print(f"✅ Generated product impact analysis: {len(results)} products")
            return results
            
        except Exception as e:
            print(f"❌ Error in product impact analysis: {e}")
            return []
    
    def get_forecast_summary(self, user_id: str = "analyst", user_role: str = "forecast_analyst") -> Dict[str, Any]:
        """Get comprehensive forecast summary with user context."""
        if self._safe_df_operation("forecast summary", {}) is not None:
            return {"error": "No data available for forecast summary"}
            
        try:
            current_data = self.df.copy()
            
            # Calculate summary metrics
            total_buf = self._clean_numeric_value(current_data['Final BUF Rev. (Outbound)'].sum()) if 'Final BUF Rev. (Outbound)' in current_data.columns else 0
            total_rsf = self._clean_numeric_value(current_data['Final RSF Rev. (Outbound)'].sum()) if 'Final RSF Rev. (Outbound)' in current_data.columns else 0
            total_variance = total_buf - total_rsf
            variance_pct = (total_variance / total_rsf * 100) if total_rsf != 0 else 0
            
            # Get top accounts by variance
            top_accounts = self.get_account_variance_details(limit=5)
            
            # Get product breakdown
            product_analysis = self.get_product_impact_analysis(limit=5)
            
            active_opportunities = 0
            if 'Probability %' in current_data.columns:
                active_opportunities = current_data[current_data['Probability %'] > 0].shape[0]
            
            summary = {
                "forecast_metrics": {
                    "total_buf_revenue": float(total_buf),
                    "total_rsf_revenue": float(total_rsf),
                    "total_variance": float(total_variance),
                    "variance_percentage": round(variance_pct, 2),
                    "deal_count": len(current_data),
                    "active_opportunities": active_opportunities
                },
                "top_variance_accounts": top_accounts,
                "product_breakdown": product_analysis,
                "user_context": {
                    "user_id": user_id,
                    "role": user_role,
                    "data_freshness": datetime.now().isoformat(),
                    "record_count": len(current_data),
                    "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            print(f"✅ Generated forecast summary with {len(current_data)} records")
            return summary
            
        except Exception as e:
            print(f"❌ Error generating forecast summary: {e}")
            return {"error": f"Error generating summary: {str(e)}"}


# Global instance for use in the application
nvidia_forecast_service = NvidiaForecastService()
