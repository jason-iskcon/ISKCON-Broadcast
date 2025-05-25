Write-Host "Activating ISKCON-Broadcast virtual environment..." -ForegroundColor Green
& .\Scripts\Activate.ps1
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Yellow
Write-Host "  cd src" -ForegroundColor Cyan
Write-Host "  python video_stream.py --debug-time 04:30" -ForegroundColor Cyan
Write-Host ""
Write-Host "To deactivate: deactivate" -ForegroundColor Yellow 