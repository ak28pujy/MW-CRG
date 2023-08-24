@echo off

reg query HKU\S-1-5-19 1>nul 2>nul || goto Admin

SET CurrentDir=%~dp0
cd %CurrentDir%..

:Menu
cls
echo.
echo Installation menu
echo =================
echo.
echo [1] Install requirements
echo [2] Start app
echo [3] Exit
echo.
set /p choose="Please select:"
if %choose%==1 goto Setup
if %choose%==2 goto Start
if %choose%==3 goto Exit
goto Menu

:Setup
cls
echo.
echo Set ExecutionPolicy to RemoteSigned.
powershell -Command "Set-ExecutionPolicy RemoteSigned -Force"
echo.
echo Install requirements.
echo.
powershell -Command "python -m venv venv; .\venv\Scripts\Activate; python.exe -m pip install --upgrade pip; pip install -r requirements.txt; deactivate"
echo.
echo Finished.
goto Success

:Success
echo.
set /p choose="Do you want to start the app now? [y/n]:"
if %choose%==y goto Start
if %choose%==n goto Menu
goto Success

:Start
cd start
start run.vbs
goto Exit

:Admin
cls
echo.
echo This script requires administrator privileges.
echo To do so, right-click on this script and select 'Run as administrator'.
echo.
echo Press any key to exit.
pause >nul
goto Exit

:Exit