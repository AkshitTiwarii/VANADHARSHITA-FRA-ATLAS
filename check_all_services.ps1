# FRA Atlas - Service Health Check
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "FRA ATLAS - ALL SERVICES HEALTH CHECK" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check AI Service
Write-Host "Checking AI Service (Port 8000)..." -ForegroundColor Yellow
try {
    $ai = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "  [OK] AI Service ONLINE" -ForegroundColor Green
    $aiStatus = "ONLINE"
} catch {
    Write-Host "  [X] AI Service OFFLINE" -ForegroundColor Red
    $aiStatus = "OFFLINE"
}

# Check Blockchain Service
Write-Host "Checking Blockchain Service (Port 8001)..." -ForegroundColor Yellow
try {
    $blockchain = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "  [OK] Blockchain Service ONLINE" -ForegroundColor Green
    $blockchainStatus = "ONLINE"
} catch {
    Write-Host "  [X] Blockchain Service OFFLINE" -ForegroundColor Red
    $blockchainStatus = "OFFLINE"
}

# Check Frontend
Write-Host "Checking Frontend (Port 3002)..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3002" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "  [OK] Frontend ONLINE" -ForegroundColor Green
    $frontendStatus = "ONLINE"
} catch {
    Write-Host "  [X] Frontend OFFLINE" -ForegroundColor Red
    $frontendStatus = "OFFLINE"
}

# Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "SERVICE STATUS SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "AI Service (8000):        $aiStatus" -ForegroundColor $(if($aiStatus -eq "ONLINE"){"Green"}else{"Red"})
Write-Host "Blockchain Service (8001): $blockchainStatus" -ForegroundColor $(if($blockchainStatus -eq "ONLINE"){"Green"}else{"Red"})
Write-Host "Frontend (3002):          $frontendStatus" -ForegroundColor $(if($frontendStatus -eq "ONLINE"){"Green"}else{"Red"})
Write-Host ""

if ($aiStatus -eq "ONLINE" -and $blockchainStatus -eq "ONLINE" -and $frontendStatus -eq "ONLINE") {
    Write-Host "ALL SERVICES RUNNING! System ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Open http://localhost:3002 in browser" -ForegroundColor White
    Write-Host "2. Run: python test_blockchain_duplicate.py" -ForegroundColor White
    Write-Host "3. See: BLOCKCHAIN_ANTI_FRAUD_SYSTEM.md" -ForegroundColor White
} else {
    Write-Host "Some services are offline!" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
