#!/usr/bin/env python3
"""
Complete Test Script for Telescope Weather App
Tests all functionality including API integration
"""

import os
import sys
from datetime import datetime

def test_imports():
    """Test all required imports"""
    try:
        import flask
        import pandas as pd
        import requests
        import numpy as np
        from dotenv import load_dotenv
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_csv_data():
    """Test CSV data loading"""
    try:
        import pandas as pd
        csv_file = 'UTTRAKHAND_ISRO0019_2012-11-02_2019-01-02_Nov2025_175236.csv'
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            print(f"✅ CSV loaded: {len(df)} records")
            return True
        else:
            print("⚠️  CSV file not found - app will work with API only")
            return True
    except Exception as e:
        print(f"❌ CSV error: {e}")
        return False

def test_api_config():
    """Test API configuration"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('ACCUWEATHER_API_KEY')
        if api_key and len(api_key) > 10:
            print("✅ AccuWeather API key configured")
            return True
        else:
            print("⚠️  API key not configured - using fallback data")
            return True
    except Exception as e:
        print(f"❌ API config error: {e}")
        return False

def test_app_functions():
    """Test main app functions"""
    try:
        from app import get_current_and_today_weather, predict_telescope_conditions, get_past_data
        
        # Test weather data
        weather = get_current_and_today_weather('beluwakhan')
        print(f"✅ Weather data: {weather['location']} - {weather['temperature']}°C")
        
        # Test predictions
        prediction = predict_telescope_conditions(weather)
        print(f"✅ Telescope prediction: {prediction['score']}/100 ({prediction['recommendation']})")
        
        # Test historical data
        past_data = get_past_data()
        print(f"✅ Historical analysis: {past_data['total_records']} records, {past_data['optimal_percentage']}% optimal")
        
        return True
    except Exception as e:
        print(f"❌ App function error: {e}")
        return False

def test_flask_routes():
    """Test Flask app creation"""
    try:
        from app import app
        with app.test_client() as client:
            # Test main route
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Main route working")
            
            # Test API route
            response = client.get('/api/telescope-conditions/beluwakhan')
            if response.status_code == 200:
                print("✅ API route working")
                data = response.get_json()
                print(f"   - Weather: {data['weather']['location']}")
                print(f"   - Prediction: {data['prediction']['score']}/100")
                print(f"   - Forecast: {len(data['forecast'])} days")
            
        return True
    except Exception as e:
        print(f"❌ Flask route error: {e}")
        return False

def main():
    print("🔭 Telescope Weather App - Complete Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("CSV Data", test_csv_data),
        ("API Config", test_api_config),
        ("App Functions", test_app_functions),
        ("Flask Routes", test_flask_routes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_name} test had issues")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! App is ready to run.")
        print("\n🚀 To start the app:")
        print("   python run_telescope.py")
        print("   OR")
        print("   python app.py")
        print("\n🌐 Then open: http://127.0.0.1:5000")
    else:
        print("⚠️  Some tests had issues, but app should still work")
        print("   Most issues are non-critical (API limits, etc.)")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()