# PowerShell script to prepare the repository for GitHub

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$DefaultColor = "White"

Write-Host "Preparing Farmora repository for GitHub..." -ForegroundColor $Yellow

# Make sure we don't include .env files
Write-Host "Checking for .env files..." -ForegroundColor $Green
Get-ChildItem -Path . -Filter ".env" -Recurse -File | ForEach-Object {
  Write-Host "Warning: .env file found: $($_.FullName) - ensure this is in .gitignore" -ForegroundColor $Yellow
}

# Clean up Python cache files
Write-Host "Cleaning up Python cache files..." -ForegroundColor $Green
Get-ChildItem -Path . -Include "__pycache__" -Directory -Recurse | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Include "*.pyc", "*.pyo", "*.pyd" -File -Recurse | Remove-Item -Force

Write-Host "Repository is ready for upload!" -ForegroundColor $Green
Write-Host "Suggested commit message: 'Implement Appwrite authentication for Farmora backend'" -ForegroundColor $Green
Write-Host "Use the following commands to push to GitHub:" -ForegroundColor $Green
Write-Host "git add ." -ForegroundColor $DefaultColor
Write-Host "git commit -m ""Implement Appwrite authentication for Farmora backend""" -ForegroundColor $DefaultColor
Write-Host "git push origin main" -ForegroundColor $DefaultColor
