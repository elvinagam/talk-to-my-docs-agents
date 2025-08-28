#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/elvin.aghammadzada/github_dr/talk-to-my-docs-agents/web')
sys.path.append('/Users/elvin.aghammadzada/github_dr/talk-to-my-docs-agents/web/app')
import asyncio

def test_nvidia_service():
    from app.services.nvidia_forecast import nvidia_forecast_service
    
    print("🧪 Testing NVIDIA Forecast Service with current data...\n")
    
    # Test 1: Forecast Summary
    print("=== TEST 1: FORECAST SUMMARY ===")
    try:
        summary = nvidia_forecast_service.get_forecast_summary('test_user', 'analyst')
        print(f"✅ BUF Total: ${summary['forecast_metrics']['total_buf_revenue']:,.2f}")
        print(f"✅ RSF Total: ${summary['forecast_metrics']['total_rsf_revenue']:,.2f}")
        print(f"✅ Total Variance: ${summary['forecast_metrics']['total_variance']:,.2f}")
        print(f"✅ Deal Count: {summary['forecast_metrics']['deal_count']}")
        print(f"✅ Record Count: {summary['user_context']['record_count']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Test 2: Account Variance
    print("=== TEST 2: ACCOUNT VARIANCE ===")
    try:
        # Test with Microsoft (actual account in data)
        account_data = nvidia_forecast_service.get_account_variance_details('MICROSOFT')
        if account_data and len(account_data) > 0 and 'error' not in account_data[0]:
            first_account = account_data[0]
            print(f"✅ Account: {first_account['account']}")
            print(f"✅ Total BUF: ${first_account['total_buf_revenue']:,.2f}")
            print(f"✅ Total RSF: ${first_account['total_rsf_revenue']:,.2f}")
            print(f"✅ Variance: ${first_account['total_variance']:,.2f}")
        else:
            print(f"⚠️ Account not found or data structure issue")
            if account_data and len(account_data) > 0:
                print(f"Available accounts: {account_data[0].get('available_accounts', [])[:5]}")
        
        # Also test getting all accounts
        print("\n--- All Account Summary ---")
        all_accounts = nvidia_forecast_service.get_account_variance_details()
        print(f"Found {len(all_accounts)} accounts total")
        if all_accounts and 'error' not in all_accounts[0]:
            for i, acc in enumerate(all_accounts[:3]):  # Show first 3
                print(f"  {i+1}. {acc['account']}: ${acc['total_rsf_revenue']:,.2f}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Test 3: Product Impact
    print("=== TEST 3: PRODUCT IMPACT ===")  
    try:
        product_data = nvidia_forecast_service.get_product_impact_analysis('COMPUTE')
        if product_data and len(product_data) > 0 and 'error' not in product_data[0]:
            first_product = product_data[0]
            print(f"✅ Product: {first_product['product']}")
            print(f"✅ Total BUF: ${first_product['total_buf_revenue']:,.2f}")
            print(f"✅ Account Count: {first_product['account_count']}")
        else:
            print(f"⚠️ Product not found or data structure issue")
            if product_data and len(product_data) > 0:
                print(f"Available products: {product_data[0].get('available_products', [])[:5]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 4: Data Structure
    print("=== TEST 4: DATA STRUCTURE ANALYSIS ===")
    try:
        if nvidia_forecast_service.df is not None:
            print(f"✅ Dataset loaded: {len(nvidia_forecast_service.df)} records")
            print(f"✅ Columns: {len(nvidia_forecast_service.df.columns)}")
            print(f"✅ Unique accounts: {nvidia_forecast_service.df['Customer Desc.'].nunique()}")
            if 'Item Family' in nvidia_forecast_service.df.columns:
                print(f"✅ Unique products: {nvidia_forecast_service.df['Item Family'].nunique()}")
                print(f"✅ Product categories: {nvidia_forecast_service.df['Item Family'].unique().tolist()}")
            if 'Time_Period' in nvidia_forecast_service.df.columns:
                print(f"✅ Time periods: {nvidia_forecast_service.df['Time_Period'].unique().tolist()}")
        else:
            print("❌ No dataset loaded")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_nvidia_service()
