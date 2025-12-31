#!/usr/bin/env python3
"""
Test script to verify the telescope app functionality
"""

import requests
import json
import sys
import os

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    print("Testing Telescope Weather App API...")
    print("=" * 50)
    
    # Test main page
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✓ Main page loads successfully")
        else:
            print(f"✗ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Main page error: {e}")
    
    # Test locations
    locations = ['beluwakhan', 'nainital', 'delhi', 'mumbai']
    
    for location in locations:
        try:
            response = requests.get(f"{base_url}/api/telescope-conditions/{location}")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {location.title()} API working - Score: {data['prediction']['score']}/100")
                
                # Verify data structure
                required_keys = ['weather', 'prediction', 'forecast', 'past_data']
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    print(f"  ⚠ Missing keys: {missing_keys}")
                else:
                    print(f"  ✓ All required data present")
                    
            else:
                print(f"✗ {location.title()} API failed: {response.status_code}")
        except Exception as e:
            print(f"✗ {location.title()} API error: {e}")
    
    # Test export endpoint
    try:
        response = requests.get(f"{base_url}/export/weather-data")
        if response.status_code == 200:
            print("✓ CSV export working")
        else:
            print(f"✗ CSV export failed: {response.status_code}")
    except Exception as e:
        print(f"✗ CSV export error: {e}")
    
    # Test requirements endpoint
    try:
        response = requests.get(f"{base_url}/requirements")
        if response.status_code == 200:
            print("✓ Requirements endpoint working")
        else:
            print(f"✗ Requirements endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Requirements endpoint error: {e}")

def check_csv_data():
    """Check if CSV data is properly loaded"""
    print("\nChecking CSV Data...")
    print("=" * 30)
    
    csv_file = "UTTRAKHAND_ISRO0019_2012-11-02_2019-01-02_Nov2025_175236.csv"
    if os.path.exists(csv_file):
        print(f"✓ CSV file exists: {csv_file}")
        
        import pandas as pd
        try:
            df = pd.read_csv(csv_file)
            print(f"✓ CSV loaded successfully - {len(df)} records")
            print(f"  Date range: {df['DATE(IST)'].min()} to {df['DATE(IST)'].max()}")
            print(f"  Columns: {list(df.columns)}")
        except Exception as e:
            print(f"✗ CSV loading error: {e}")
    else:
        print(f"✗ CSV file not found: {csv_file}")

if __name__ == "__main__":
    print("Telescope Weather App Test Suite")
    print("================================")
    
    check_csv_data()
    
    print("\nStarting API tests...")
    print("Make sure the Flask app is running on http://127.0.0.1:5000")
    input("Press Enter to continue...")
    
    test_api_endpoints()
    
    print("\nTest completed!")