@echo off
REM Startup script for Advanced Document Generator (Windows)

echo 🚀 Starting Advanced Document Generator...

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "temp\" mkdir temp
if not exist "doc_templates\" mkdir doc_templates

REM Check for .env file
if not exist ".env" (
    echo ⚠️  No .env file found!
    echo Creating default .env file...
    echo FLASK_ENV=development > .env
    echo FLASK_DEBUG=True >> .env
    echo PORT=5000 >> .env
    echo ✅ Created .env file
    echo ⚠️  Please set a SECRET_KEY in .env file!
)

REM Run the application
echo ✨ Starting Flask application...
python app.py

pause

