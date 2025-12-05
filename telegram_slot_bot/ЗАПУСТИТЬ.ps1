# PowerShell скрипт для запуска UserBot
Write-Host "===============================================================" -ForegroundColor Green
Write-Host "        ЗАПУСК USERBOT ДЛЯ ОТПРАВКИ ЗВЁЗД" -ForegroundColor Green
Write-Host "===============================================================" -ForegroundColor Green
Write-Host ""

# Переход в папку проекта
Set-Location -Path "C:\Users\wtk_x\OneDrive\Рабочий стол\TIMLY\telegram_slot_bot"
Write-Host "Текущая папка: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Проверка наличия Python
Write-Host "Проверка Python..." -ForegroundColor Cyan
python --version

Write-Host ""
Write-Host "Запуск авторизации..." -ForegroundColor Cyan
Write-Host ""

# Запуск авторизации
python auth.py

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Если авторизация прошла успешно, нажмите Enter" -ForegroundColor Yellow
Write-Host "для запуска основного UserBot..." -ForegroundColor Yellow
Read-Host

Write-Host ""
Write-Host "Запуск UserBot..." -ForegroundColor Cyan
python userbot_practical.py

Write-Host ""
Write-Host "Нажмите Enter для выхода..." -ForegroundColor Yellow
Read-Host