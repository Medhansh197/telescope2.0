#!/usr/bin/env python3
"""
Telescope Weather App Startup Script
"""

import os
import sys
import subprocess
import webbrowser
import time
from threading import Timer

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask', 'pandas', 'requests', 'numpy', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstalling missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"Installed {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}")
                return False
    
    return True

def setup_environment():
    """Setup environment file if it doesn't exist"""
    env_file = '.env'
    if not os.path.exists(env_file):
        print("Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("# AccuWeather API Key (optional)\n")
            f.write("# Get your free API key from: https://developer.accuweather.com/\n")
            f.write("# ACCUWEATHER_API_KEY=your_api_key_here\n")
        print("Created .env file")

def open_browser():
    """Open browser after a delay"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')

def main():
    """Main startup function"""
    print("Telescope Weather App Startup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("Error: app.py not found in current directory")
        print("Please run this script from the telescope project directory")
        return
    
    # Check CSV data file
    csv_file = 'UTTRAKHAND_ISRO0019_2012-11-02_2019-01-02_Nov2025_175236.csv'
    if not os.path.exists(csv_file):
        print(f"Warning: CSV data file not found: {csv_file}")
        print("The app will work with limited functionality")
    else:
        print("CSV data file found")
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("Failed to install required packages")
        return
    print("All dependencies satisfied")
    
    # Setup environment
    setup_environment()
    
    # Start the Flask app
    print("\nStarting Telescope Weather App...")
    print("Location: http://127.0.0.1:5000")
    print("The app will auto-refresh data every 5 minutes")
    print("CSV data export available at: http://127.0.0.1:5000/export/weather-data")
    print("\nTips:")
    print("  - Add your AccuWeather API key to .env file for live weather data")
    print("  - Use Ctrl+C to stop the server")
    print("  - The app works offline using historical CSV data")
    
    # Open browser after delay
    Timer(2.0, open_browser).start()
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\nTelescope Weather App stopped")
    except Exception as e:
        print(f"\nError starting app: {e}")

if __name__ == "__main__":
    main()