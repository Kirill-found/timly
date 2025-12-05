@echo off
echo ========================================
echo Остановка всех процессов Python...
echo ========================================
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo.
echo ========================================
echo Запуск Group Slot Bot с User-bot...
echo ========================================
echo.

cd /d "c:\Users\wtk_x\OneDrive\Рабочий стол\TIMLY\telegram_slot_bot"
python group_slot_bot.py

pause
