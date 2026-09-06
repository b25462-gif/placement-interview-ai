@echo off
echo ========================================
echo   Starting Placement Interview AI UI
echo ========================================
cd /d "%~dp0"
streamlit run frontend/app.py --server.port 8501
pause
