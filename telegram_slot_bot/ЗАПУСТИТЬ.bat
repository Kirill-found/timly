@echo off
echo ===============================================================
echo         ЗАПУСК USERBOT ДЛЯ ОТПРАВКИ ЗВЁЗД
echo ===============================================================
echo.
cd /d "C:\Users\wtk_x\OneDrive\Рабочий стол\TIMLY\telegram_slot_bot"
echo Текущая папка: %CD%
echo.
echo Запускаем авторизацию...
echo.
python auth.py
echo.
echo ===============================================================
echo.
echo Если авторизация прошла успешно, нажмите любую клавишу
echo для запуска основного UserBot...
echo.
pause
echo.
echo Запускаем UserBot...
python userbot_practical.py
pause