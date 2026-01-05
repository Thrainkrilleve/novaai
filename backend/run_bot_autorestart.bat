@echo off
title Nova Discord Bot - Auto Restart
echo ===================================
echo Nova Discord Bot - Auto Restart
echo ===================================
echo.

:start
echo [%time%] Starting bot...
python discord_bot.py

echo.
echo [%time%] Bot stopped. Restarting in 5 seconds...
echo Press Ctrl+C to stop auto-restart
timeout /t 5 /nobreak > nul
goto start
