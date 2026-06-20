# Run Streamlit app for book2 chapter 20
Write-Host "Starting Streamlit app..." -ForegroundColor Green
Write-Host ""
Write-Host "Make sure the FastAPI backend is running on port 9620" -ForegroundColor Yellow
Write-Host "If not, run: python backend/api.py" -ForegroundColor Yellow
Write-Host ""

streamlit run streamlit_app.py --server.port 8620
