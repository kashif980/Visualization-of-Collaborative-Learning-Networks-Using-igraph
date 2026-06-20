@echo off
REM Run Streamlit app for book2 chapter 20
echo Starting Streamlit app...
echo.
echo Make sure the FastAPI backend is running on port 9620
echo If not, run: python backend/api.py
echo.
streamlit run streamlit_app.py --server.port 8620
pause
