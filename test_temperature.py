#!/usr/bin/env python3
"""
Test script to verify temperature data accuracy
"""

from app import get_current_and_today_weather
from datetime import datetime

def test_all_locations():
    locations = ['beluwakhan', 'nainital', 'delhi', 'mumbai']
    
    print("🔭 Telescope Weather App - Temperature Test")
    print("=" * 50)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for location in locations:
        print(f"📍 Testing {location.title()}...")
        try:
            data = get_current_and_today_weather(location)
            print(f"   🌡️  Current: {data['temperature']}°C (Feels like {data['feels_like']}°C)")
            print(f"   📊 Range: {data['today_min_temp']}°C to {data['today_max_temp']}°C")
            print(f"   💧 Humidity: {data['humidity']}%")
            print(f"   💨 Wind: {data['wind_speed']} m/s {data['wind_direction']}")
            print(f"   🌊 Pressure: {data['pressure']} hPa")
            print(f"   📡 Source: {data['api_source']}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
    
    print("✅ Temperature data test completed!")
    print("🚀 Ready to start the app: python app.py")

if __name__ == "__main__":
    test_all_locations()