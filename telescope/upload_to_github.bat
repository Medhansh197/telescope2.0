@echo off
title GitHub Repository Upload - Telescope Weather App
echo.
echo ========================================
echo   🔭 GitHub Repository Upload Script
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed. Please install Git first.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Get repository URL from user
set /p REPO_URL="Enter your GitHub repository URL (e.g., https://github.com/username/telescope-weather-app.git): "

if "%REPO_URL%"=="" (
    echo ❌ Repository URL is required!
    pause
    exit /b 1
)

echo.
echo 🔧 Setting up repository...

REM Create temporary directory
set TEMP_DIR=%TEMP%\telescope-upload
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

REM Clone repository
echo 📥 Cloning repository...
git clone "%REPO_URL%" "%TEMP_DIR%"
if errorlevel 1 (
    echo ❌ Failed to clone repository. Check URL and permissions.
    pause
    exit /b 1
)

REM Copy all files except .git
echo 📁 Copying project files...
xcopy /E /I /Y "c:\Users\PC\Desktop\telescope\*" "%TEMP_DIR%\" /EXCLUDE:git_exclude.txt

REM Secure API key
echo 🔐 Securing API key...
echo ACCUWEATHER_API_KEY=your_api_key_here > "%TEMP_DIR%\.env"

REM Change to repository directory
cd /d "%TEMP_DIR%"

REM Configure git (if not already configured)
git config user.name >nul 2>&1
if errorlevel 1 (
    set /p GIT_NAME="Enter your name for Git: "
    set /p GIT_EMAIL="Enter your email for Git: "
    git config user.name "!GIT_NAME!"
    git config user.email "!GIT_EMAIL!"
)

REM Add all files
echo ➕ Adding files to repository...
git add .

REM Commit changes
echo 💾 Committing changes...
git commit -m "🔭 Complete telescope weather monitoring app

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
📱 Features: Live clock, real-time data, telescope predictions, CSV export"

REM Push to GitHub
echo 🚀 Pushing to GitHub...
git push origin main
if errorlevel 1 (
    git push origin master
)

if errorlevel 1 (
    echo ❌ Failed to push to repository. Check permissions.
    pause
    exit /b 1
)

echo.
echo ✅ SUCCESS! Repository uploaded successfully!
echo.
echo 🌐 Your repository is now available at:
echo %REPO_URL:~0,-4%
echo.
echo 📋 Next steps:
echo 1. Visit your repository on GitHub
echo 2. Add topics: telescope, weather, astronomy, flask, python
echo 3. Enable GitHub Pages if desired
echo 4. Share with the community!
echo.
echo 🔭 Happy stargazing!
echo.

REM Cleanup
cd /d "c:\Users\PC\Desktop\telescope"
rmdir /s /q "%TEMP_DIR%"

pause