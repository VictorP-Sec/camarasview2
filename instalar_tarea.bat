@echo off
echo ========================================
echo  CONFIGURAR CAPTURA CADA 5 MINUTOS
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set PYTHON_PATH=python
set SCRIPT=%SCRIPT_DIR%capturar_local.py

echo Creando tarea Programada...
echo.

schtasks /create /tn "CamarasAlicante" /tr "\"%PYTHON_PATH%\" \"%SCRIPT%\"" /sc minute /mo 5 /ru "%USERNAME%" /rl HIGHEST /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo OK: Tarea "CamarasAlicante" creada.
    echo Se ejecutara cada 5 minutos.
    echo.
    echo Para verla: schtasks /query /tn "CamarasAlicante"
    echo Para borrarla: schtasks /delete /tn "CamarasAlicante" /f
    echo Para ejecutarla ahora: schtasks /run /tn "CamarasAlicante"
) else (
    echo.
    echo ERROR: No se pudo crear la tarea.
    echo Ejecuta este .bat como Administrador.
)

pause
