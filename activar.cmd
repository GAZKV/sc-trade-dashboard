@echo off
rem Cambia al directorio donde está este BAT
pushd "%~dp0"

rem Lanza PowerShell, salta la política de ejecución, 
rem y deja la sesión abierta con el entorno activado
powershell -NoExit -ExecutionPolicy Bypass ^
    -Command "& '.venv\Scripts\Activate.ps1'"
popd
rem uvicorn app.web.main:app --reload --port 8000