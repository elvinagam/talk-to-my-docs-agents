#!/usr/bin/env python3
"""
Test script to check NVIDIA forecast service with large dataset
"""
import os
import sys
import traceback
from pathlib import Path

# Add web app to path
sys.path.insert(0, 'web/app')

try:
    from services.nvidia_forecast import NvidiaForecastService
    print("✅ Successfully imported NvidiaForecastService")
    
    # Initialize service with sample data first
    sample_data_path = "data/nvidia_forecast_data.csv"
    print(f"📊 Testing with sample data: {sample_data_path}")
    
    if os.path.exists(sample_data_path):
        service = NvidiaForecastService(sample_data_path)
        print(f"✅ Service initialized with {len(service.data)} rows")
        
        # Test BUF vs RSF analysis
        print("\n📈 Testing BUF vs RSF analysis...")
        buf_rsf_data = service.get_buf_vs_rsf_analysis()
        print(f"   - Found {len(buf_rsf_data)} BUF vs RSF records")
        
        # Test variance analysis
        print("\n📊 Testing variance analysis...")
        variance_data = service.get_account_variance_details(limit=5)
        print(f"   - Found {len(variance_data)} variance records")
        
        # Test product analysis
        print("\n🔍 Testing product impact analysis...")
        product_data = service.get_product_impact_analysis(limit=5)
        print(f"   - Found {len(product_data)} product records")
        
    else:
        print(f"❌ Sample data file not found: {sample_data_path}")
    
    # Test with large dataset if it exists
    large_data_path = "data/nvidia_data.csv"
    if os.path.exists(large_data_path):
        print(f"\n🗂️ Testing with large dataset: {large_data_path}")
        file_size = os.path.getsize(large_data_path) / (1024 * 1024)  # MB
        print(f"   - File size: {file_size:.1f} MB")
        
        if file_size > 100:
            print("   ⚠️  Large file detected - testing with chunking approach")
            # Test loading just a few rows to check format
            import pandas as pd
            chunk_data = pd.read_csv(large_data_path, nrows=1000)
            print(f"   - Sample chunk: {len(chunk_data)} rows, {len(chunk_data.columns)} columns")
            print(f"   - Columns: {list(chunk_data.columns)[:10]}...")  # First 10 columns
        else:
            service_large = NvidiaForecastService(large_data_path)
            print(f"   ✅ Large dataset loaded: {len(service_large.data)} rows")
    else:
        print(f"\n📋 Large dataset not found: {large_data_path}")
    
    print("\n✅ All tests completed successfully!")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
