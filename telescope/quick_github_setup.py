#!/usr/bin/env python3
"""
Quick GitHub Repository Setup Script
Automates the entire process of uploading telescope weather app to GitHub
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔭 GitHub Repository Upload Script")
    print("=" * 50)
    
    # Check if git is installed
    success, _, _ = run_command("git --version")
    if not success:
        print("❌ Git is not installed. Please install Git first.")
        print("Download from: https://git-scm.com/download/win")
        input("Press Enter to exit...")
        return
    
    # Get repository URL
    repo_url = input("Enter your GitHub repository URL: ").strip()
    if not repo_url:
        print("❌ Repository URL is required!")
        input("Press Enter to exit...")
        return
    
    print("\n🔧 Setting up repository...")
    
    # Create temporary directory
    temp_dir = Path.home() / "temp_telescope_upload"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        # Clone repository
        print("📥 Cloning repository...")
        success, _, error = run_command(f'git clone "{repo_url}" "{temp_dir}"')
        if not success:
            print(f"❌ Failed to clone repository: {error}")
            input("Press Enter to exit...")
            return
        
        # Copy project files
        print("📁 Copying project files...")
        source_dir = Path("c:/Users/PC/Desktop/telescope")
        
        for item in source_dir.iterdir():
            if item.name == '.git':
                continue
            
            dest = temp_dir / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        
        # Secure API key
        print("🔐 Securing API key...")
        env_file = temp_dir / ".env"
        with open(env_file, 'w') as f:
            f.write("ACCUWEATHER_API_KEY=your_api_key_here\n")
        
        # Git operations
        os.chdir(temp_dir)
        
        # Configure git if needed
        success, _, _ = run_command("git config user.name")
        if not success:
            name = input("Enter your name for Git: ").strip()
            email = input("Enter your email for Git: ").strip()
            run_command(f'git config user.name "{name}"')
            run_command(f'git config user.email "{email}"')
        
        # Add files
        print("➕ Adding files to repository...")
        run_command("git add .")
        
        # Commit
        print("💾 Committing changes...")
        commit_msg = """🔭 Complete telescope weather monitoring app

✨ Features:
- Real-time AccuWeather API integration with live clock
- Multi-location support (Beluwakhan, Nainital, Delhi, Mumbai)  
- 5-day forecast with telescope viewing predictions
- Historical data analysis (45,660+ records from 2012-2019)
- AI-powered viewing condition scoring (0-100 scale)
- 3D animated starfield background with space theme
- CSV export and data management functionality
- Responsive design with auto-refresh every 5 minutes

🚀 Ready to use: python app.py
🌐 Access at: http://127.0.0.1:5000
📊 Includes 7+ years of historical weather data
🎯 Perfect for amateur astronomers and stargazing enthusiasts

🔧 Technologies: Flask, Python, AccuWeather API, Pandas, JavaScript
📱 Features: Live clock, real-time data, telescope predictions, CSV export"""
        
        run_command(f'git commit -m "{commit_msg}"')
        
        # Push to GitHub
        print("🚀 Pushing to GitHub...")
        success, _, error = run_command("git push origin main")
        if not success:
            success, _, error = run_command("git push origin master")
        
        if success:
            print("\n✅ SUCCESS! Repository uploaded successfully!")
            print(f"\n🌐 Your repository is now available at:")
            print(repo_url.replace('.git', ''))
            print(f"\n📋 Next steps:")
            print("1. Visit your repository on GitHub")
            print("2. Add topics: telescope, weather, astronomy, flask, python")
            print("3. Enable GitHub Pages if desired")
            print("4. Share with the community!")
            print("\n🔭 Happy stargazing!")
        else:
            print(f"❌ Failed to push to repository: {error}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Cleanup
        os.chdir(Path("c:/Users/PC/Desktop/telescope"))
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()