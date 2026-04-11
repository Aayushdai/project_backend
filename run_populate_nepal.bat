@echo off
REM Quick script to populate 100 Nepali users

echo 🇳🇵 Travel Companion - Nepali Users Population

REM Navigate to project directory
cd /d C:\Users\Aayush\Desktop\chatbot\Travel_Companion_Backend

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the populate script
echo.
echo Starting population script...
echo.

python manage.py populate_nepal_users

echo.
echo ✅ Done! Check your database for 100 new Nepali users.
echo.
pause
