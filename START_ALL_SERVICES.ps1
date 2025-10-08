# 🚀 START ALL SERVICES - Master Script

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "        🌲 FRA ATLAS - Starting All Services" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "C:\Users\akshi\OneDrive\Desktop\PROJECTS\FRA"

# Function to start service in new window
function Start-ServiceWindow {
    param(
        [string]$Name,
        [string]$Path,
        [string]$Command,
        [string]$Color = "Green"
    )
    
    Write-Host "🚀 Starting $Name..." -ForegroundColor $Color
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Path'; Write-Host '═════════════════════════════════' -ForegroundColor Cyan; Write-Host '  $Name' -ForegroundColor Green; Write-Host '═════════════════════════════════' -ForegroundColor Cyan; Write-Host ''; $Command"
    Start-Sleep -Seconds 2
}

# 1. Start AI Service (Python FastAPI)
Start-ServiceWindow -Name "AI Service (Port 8000)" `
    -Path "$projectRoot\ai-service" `
    -Command "python main_v2.py" `
    -Color "Magenta"

Write-Host "   ⏳ Waiting for AI service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# 2. Start Frontend (React)
Start-ServiceWindow -Name "Frontend (Port 3000)" `
    -Path "$projectRoot\frontend-main" `
    -Command "`$env:CI='true'; npm start" `
    -Color "Cyan"

Write-Host "   ⏳ Waiting for frontend to compile..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "         ✅ ALL SERVICES STARTING!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Service URLs:" -ForegroundColor Yellow
Write-Host "   🤖 AI Service:  http://localhost:8000" -ForegroundColor Magenta
Write-Host "   🌐 Frontend:    http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏳ Services are starting in separate windows..." -ForegroundColor Yellow
Write-Host "   Please wait 30-60 seconds for full initialization" -ForegroundColor Yellow
Write-Host ""

# Wait a bit more
Start-Sleep -Seconds 10

# Health Check
Write-Host "🔍 Running Health Checks..." -ForegroundColor Cyan
Write-Host ""

try {
    $aiHealth = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ AI Service: ONLINE" -ForegroundColor Green
} catch {
    Write-Host "⏳ AI Service: Starting... (check window)" -ForegroundColor Yellow
}

try {
    $frontendHealth = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Frontend: ONLINE" -ForegroundColor Green
} catch {
    Write-Host "⏳ Frontend: Compiling... (check window)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "         🎯 NEXT STEPS" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Wait for all services to fully start" -ForegroundColor White
Write-Host "2. Open browser: http://localhost:3000" -ForegroundColor White
Write-Host "3. Generate test data:" -ForegroundColor White
Write-Host "   cd ai-service" -ForegroundColor Gray
Write-Host "   python generate_test_documents.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Run tests:" -ForegroundColor White
Write-Host "   python test_all_services_comprehensive.py" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
