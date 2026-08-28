@echo off
cd /d "C:\Users\victo\Documents\Default Project\camarasview2"
python capturar_local.py >> "%TEMP%\camaras_log.txt" 2>&1
