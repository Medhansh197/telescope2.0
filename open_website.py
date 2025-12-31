import webbrowser
import subprocess
import time
import sys

print("🔭 Starting Telescope Weather App...")
print("Opening website in your browser...")

# Start Flask app
flask_process = subprocess.Popen([sys.executable, "app.py"])

# Wait for server to start
time.sleep(3)

# Open browser
webbrowser.open("http://127.0.0.1:5000")

print("\n✅ Website opened!")
print("Press Ctrl+C to stop the server")

try:
    flask_process.wait()
except KeyboardInterrupt:
    print("\n\n🛑 Stopping server...")
    flask_process.terminate()
