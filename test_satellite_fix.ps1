# Quick Test: Verify Fixed Satellite API

$body = @{
    latitude = 21.396030
    longitude = 80.770597
} | ConvertTo-Json

Write-Host "🧪 Testing satellite analysis API..." -ForegroundColor Cyan
Write-Host "Location: Dongargarh-Dhaara Reserve Forest" -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analyze-satellite" -Method POST -Body $body -ContentType "application/json"
    
    Write-Host "✅ SUCCESS! API Response:" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Coordinates:" -ForegroundColor Cyan
    Write-Host "   Lat: $($response.coordinates.lat)" -ForegroundColor White
    Write-Host "   Lon: $($response.coordinates.lon)" -ForegroundColor White
    Write-Host ""
    Write-Host "🌲 Vegetation Metrics:" -ForegroundColor Cyan
    Write-Host "   NDVI: $($response.ndvi)" -ForegroundColor $(if($response.ndvi -gt 0.7){'Green'}elseif($response.ndvi -gt 0.5){'Yellow'}else{'Red'})
    Write-Host "   Tree Cover: $($response.tree_cover_percentage)%" -ForegroundColor White
    Write-Host "   Land Type: $($response.land_cover_type)" -ForegroundColor White
    Write-Host ""
    Write-Host "🌍 Classification:" -ForegroundColor Cyan
    Write-Host "   Forest Type: $($response.land_classification.forest_type)" -ForegroundColor White
    Write-Host "   Confidence: $($response.land_classification.confidence)" -ForegroundColor White
    Write-Host ""
    Write-Host "🚨 Risk Assessment:" -ForegroundColor Cyan
    Write-Host "   Deforestation Risk: $($response.change_detection.deforestation_risk)" -ForegroundColor $(if($response.change_detection.deforestation_risk -eq 'Low'){'Green'}elseif($response.change_detection.deforestation_risk -eq 'Medium'){'Yellow'}else{'Red'})
    Write-Host "   Trend: $($response.change_detection.trend)" -ForegroundColor White
    Write-Host "   Encroachment: $($response.change_detection.encroachment_detected)" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Recommendations:" -ForegroundColor Cyan
    foreach($rec in $response.recommendations) {
        Write-Host "   - $rec" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "📊 Data Source: $($response.metadata.data_source)" -ForegroundColor DarkGray
    Write-Host ""
    
    if($response.ndvi -gt 0) {
        Write-Host "🎉 PERFECT! The zeros are FIXED! NDVI is showing real data!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARNING: NDVI is still zero!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure AI service is running:" -ForegroundColor Yellow
    Write-Host "   cd ai-service" -ForegroundColor White
    Write-Host "   python main.py" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
