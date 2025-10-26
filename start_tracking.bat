@echo off
echo ============================================================
echo STARTING ROBOT TRACKING SYSTEM - CONTINUOUS MOTION MODE
echo ============================================================
echo.
echo CRITICAL: Make sure LEGO hub is:
echo   1. POWERED ON (press center button until light shows)
echo   2. Within 3 feet of computer (Bluetooth range)
echo   3. Not connected to another device
echo.
pause
echo.
echo Starting bridge - this will connect to hub...
echo.
start "Robot Bridge" cmd /k "python robot_stream.py"
echo.
echo Waiting 15 seconds for hub to connect...
timeout /t 15 /nobreak
echo.
echo Starting vision system...
echo.
python main.py --use_robot --target_object bottle
