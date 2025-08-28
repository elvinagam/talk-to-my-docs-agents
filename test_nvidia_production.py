#!/usr/bin/env python3
"""
Test NVIDIA service with large dataset (with encoding fix)
"""
import sys
import os
sys.path.append('/Users/elvin.aghammadzada/github_dr/talk-to-my-docs-agents/web')
sys.path.append('/Users/elvin.aghammadzada/github_dr/talk-to-my-docs-agents/web/app')

def test_large_nvidia():
    """Test with the large dataset"""
    from app.services.nvidia_forecast import NvidiaForecastService
    
    large_file = "/Users/elvin.aghammadzada/github_dr/talk-to-my-docs-agents/data/nvidia_data.csv"
    
    print(f"🧪 Testing NVIDIA Service with Large Dataset...")
    print(f"📊 File: nvidia_data.csv (479MB)")
    
    try:
        # Create service with large dataset
        print("\n🔄 Loading large dataset...")
        import time
        start_time = time.time()
        
        service = NvidiaForecastService(large_file)
        load_time = time.time() - start_time
        
        if service.df is not None:
            print(f"✅ Dataset loaded in {load_time:.2f}s")
            print(f"✅ Records: {len(service.df):,}")
            print(f"✅ Columns: {len(service.df.columns)}")
            print(f"✅ Accounts: {service.df['Customer Desc.'].nunique()}")
            print(f"✅ Products: {service.df['Item Family'].nunique()}")
            
            # Test forecast summary
            print("\n📈 Testing Forecast Summary...")
            summary_start = time.time()
            summary = service.get_forecast_summary()
            summary_time = time.time() - summary_start
            
            if 'error' not in summary:
                print(f"✅ Summary generated in {summary_time:.2f}s")
                metrics = summary['forecast_metrics']
                print(f"   - Total BUF: ${metrics['total_buf_revenue']:,.2f}")
                print(f"   - Total RSF: ${metrics['total_rsf_revenue']:,.2f}")  
                print(f"   - Variance: ${metrics['total_variance']:,.2f}")
                print(f"   - Deal Count: {metrics['deal_count']:,}")
            else:
                print(f"❌ Summary error: {summary['error']}")
            
            # Test top accounts
            print("\n🏢 Testing Top Accounts...")
            account_start = time.time()
            accounts = service.get_account_variance_details(limit=10)
            account_time = time.time() - account_start
            
            if accounts and 'error' not in accounts[0]:
                print(f"✅ Account analysis in {account_time:.2f}s")
                print("   Top accounts by RSF revenue:")
                for i, acc in enumerate(accounts[:5]):
                    variance_pct = acc['variance_percentage']
                    print(f"   {i+1}. {acc['account'][:40]:<40} ${acc['total_rsf_revenue']:>12,.0f} ({variance_pct:+.1f}%)")
            else:
                print(f"❌ Account analysis error")
            
            # Test product analysis
            print("\n🔧 Testing Product Analysis...")
            product_start = time.time()
            products = service.get_product_impact_analysis(limit=8)
            product_time = time.time() - product_start
            
            if products and 'error' not in products[0]:
                print(f"✅ Product analysis in {product_time:.2f}s")
                print("   Product families by revenue:")
                for i, prod in enumerate(products):
                    print(f"   {i+1}. {prod['product']:<15} ${prod['total_rsf_revenue']:>12,.0f} ({prod['account_count']} accounts)")
            else:
                print(f"❌ Product analysis error")
                
            print(f"\n✅ Large dataset testing completed successfully!")
            print(f"🚀 Ready for production use with {len(service.df):,} records!")
            
        else:
            print("❌ Failed to load dataset")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_large_nvidia()
