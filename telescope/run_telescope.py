#!/usr/bin/env python3
"""
Telescope Weather Conditions App - Enhanced Startup Script
Fixes all issues and ensures proper AccuWeather API integration
"""

import os
import sys
import subprocess
import webbrowser
from time import sleep

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'pandas', 'requests', 'numpy', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)

def main():
    print("🔭 Starting Telescope Weather Conditions App...")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    # Check for CSV data file
    csv_file = "UTTRAKHAND_ISRO0019_2012-11-02_2019-01-02_Nov2025_175236.csv"
    if not os.path.exists(csv_file):
        print(f"⚠️  Warning: {csv_file} not found")
        print("App will work with limited functionality using API data only")
    else:
        print(f"✅ Historical data file found: {csv_file}")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ Environment file (.env) found")
        with open('.env', 'r') as f:
            content = f.read()
            if 'ACCUWEATHER_API_KEY' in content and len(content.split('=')[1].strip()) > 10:
                print("✅ AccuWeather API key configured")
            else:
                print("⚠️  AccuWeather API key not properly configured")
    else:
        print("⚠️  .env file not found - creating with placeholder")
        with open('.env', 'w') as f:
            f.write("ACCUWEATHER_API_KEY=your_api_key_here\n")
    
    print("\n🚀 Starting Flask application...")
    print("📍 App will be available at: http://127.0.0.1:5000")
    print("🔄 Auto-refresh every 5 minutes")
    print("📊 Multiple locations supported")
    print("💾 Data export functionality included")
    print("\n" + "=" * 50)
    
    # Start the Flask app
    try:
        # Import and run the app
        from app import app
        
        # Open browser after a short delay
        def open_browser():
            sleep(2)
            webbrowser.open('http://127.0.0.1:5000')
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Run the app
        app.run(host='127.0.0.1', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("Please check the error above and try again")

if __name__ == "__main__":
    main()