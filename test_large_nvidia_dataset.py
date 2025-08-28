#!/usr/bin/env python3
"""
Test the NVIDIA service with the large dataset using chunked loading
"""
import sys
import os
sys.path.append('/Users/elvin.aghammadzada/github_dr/talk-to-my-docs-agents/web')
sys.path.append('/Users/elvin.aghammadzada/github_dr/talk-to-my-docs-agents/web/app')
import pandas as pd
import time
from pathlib import Path

def test_large_dataset_chunked():
    """Test loading the large dataset in chunks to analyze structure and performance."""
    
    large_file = "/Users/elvin.aghammadzada/github_dr/talk-to-my-docs-agents/data/nvidia_data.csv"
    
    print(f"🗂️ Testing Large NVIDIA Dataset: {Path(large_file).name}")
    file_size_mb = os.path.getsize(large_file) / (1024 * 1024)
    print(f"📊 File Size: {file_size_mb:.1f} MB")
    
    # Test 1: Read first chunk to understand structure
    print("\n=== TEST 1: DATA STRUCTURE ANALYSIS ===")
    try:
        start_time = time.time()
        sample_chunk = pd.read_csv(large_file, nrows=1000)
        load_time = time.time() - start_time
        
        print(f"✅ Loaded sample: {len(sample_chunk)} rows in {load_time:.2f}s")
        print(f"✅ Columns: {len(sample_chunk.columns)}")
        print(f"✅ Sample columns: {list(sample_chunk.columns)[:10]}...")
        
        # Check key columns we need
        key_columns = ['Customer Desc.', 'Item Family', 'Final BUF Rev. (Outbound)', 'Final RSF Rev. (Outbound)']
        for col in key_columns:
            if col in sample_chunk.columns:
                print(f"✅ Found key column: {col}")
            else:
                print(f"❌ Missing key column: {col}")
        
        # Show data sample
        print(f"\n📈 Sample data preview:")
        if 'Customer Desc.' in sample_chunk.columns:
            print(f"   - Accounts: {sample_chunk['Customer Desc.'].nunique()} unique")
        if 'Item Family' in sample_chunk.columns:
            print(f"   - Products: {sample_chunk['Item Family'].nunique()} unique")
            print(f"   - Product types: {sample_chunk['Item Family'].unique()[:5].tolist()}")
        
    except Exception as e:
        print(f"❌ Error loading sample: {e}")
        return
    
    # Test 2: Estimate full dataset size
    print("\n=== TEST 2: DATASET SIZE ESTIMATION ===")
    try:
        # Read just first row to get total row count estimate
        chunk_size = 10000
        row_count = 0
        start_time = time.time()
        
        print(f"🔄 Counting rows in chunks of {chunk_size}...")
        
        for i, chunk in enumerate(pd.read_csv(large_file, chunksize=chunk_size)):
            row_count += len(chunk)
            if i == 0:  # First chunk timing
                chunk_time = time.time() - start_time
                estimated_total_time = chunk_time * (file_size_mb / 10)  # Rough estimate
                print(f"   - First chunk: {len(chunk)} rows in {chunk_time:.2f}s")
                print(f"   - Estimated total time: {estimated_total_time:.1f}s for full load")
            
            if i >= 2:  # Just check first few chunks for now
                print(f"   - Processed {row_count} rows so far...")
                break
        
        print(f"✅ Estimated dataset size: {row_count}+ rows")
        
    except Exception as e:
        print(f"❌ Error estimating size: {e}")
    
    # Test 3: Test with NvidiaForecastService
    print("\n=== TEST 3: SERVICE INTEGRATION TEST ===")
    try:
        from app.services.nvidia_forecast import NvidiaForecastService
        
        print("🔄 Creating service instance with large dataset...")
        start_time = time.time()
        
        # This will attempt to load the full dataset
        large_service = NvidiaForecastService(large_file)
        load_time = time.time() - start_time
        
        if large_service.df is not None:
            print(f"✅ Large dataset loaded: {len(large_service.df)} rows in {load_time:.2f}s")
            
            # Test basic operations
            print("🧪 Testing operations on large dataset...")
            
            # Get summary
            summary_start = time.time()
            summary = large_service.get_forecast_summary()
            summary_time = time.time() - summary_start
            
            print(f"✅ Summary generated in {summary_time:.2f}s")
            print(f"   - Total BUF: ${summary['forecast_metrics']['total_buf_revenue']:,.2f}")
            print(f"   - Total RSF: ${summary['forecast_metrics']['total_rsf_revenue']:,.2f}")
            print(f"   - Deal Count: {summary['forecast_metrics']['deal_count']:,}")
            
            # Test account analysis
            account_start = time.time()
            accounts = large_service.get_account_variance_details(limit=5)
            account_time = time.time() - account_start
            
            print(f"✅ Account analysis in {account_time:.2f}s")
            if accounts and 'error' not in accounts[0]:
                for i, acc in enumerate(accounts[:3]):
                    print(f"   {i+1}. {acc['account'][:30]}: ${acc['total_rsf_revenue']:,.0f}")
        else:
            print("❌ Failed to load large dataset")
            
    except Exception as e:
        print(f"❌ Error testing service: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Large dataset testing completed!")

if __name__ == "__main__":
    test_large_dataset_chunked()
