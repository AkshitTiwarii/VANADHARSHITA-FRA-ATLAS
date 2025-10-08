# Test Satellite Analysis Endpoint
# Run this after starting the AI service (python main_v2.py)

Write-Host "🛰️ Testing FRA Atlas Satellite Analysis..." -ForegroundColor Cyan
Write-Host ""

# Check if service is running
Write-Host "1. Checking if service is running..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -ErrorAction Stop
    Write-Host "   ✅ Service is running!" -ForegroundColor Green
    Write-Host "   Service: $($health.service)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "   ❌ Service is not running!" -ForegroundColor Red
    Write-Host "   Please start the service first:" -ForegroundColor Yellow
    Write-Host "   cd c:\Users\akshi\OneDrive\Desktop\PROJECTS\FRA\ai-service" -ForegroundColor Gray
    Write-Host "   python main_v2.py" -ForegroundColor Gray
    exit 1
}

# Test satellite analysis
Write-Host "2. Testing satellite analysis for Maharashtra, India..." -ForegroundColor Yellow
Write-Host "   Location: 18.9217285°N, 77.0038332°E" -ForegroundColor Gray
Write-Host "   Radius: 500 meters" -ForegroundColor Gray
Write-Host ""

$body = @{
    latitude = 18.9217285
    longitude = 77.0038332
    radius = 500
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analyze-satellite" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "   ✅ Analysis successful!" -ForegroundColor Green
    Write-Host ""
    
    # Display key results
    Write-Host "📊 RESULTS:" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "🌿 Vegetation Analysis:" -ForegroundColor Yellow
    Write-Host "   NDVI (Vegetation Index): $($response.analysis.vegetation_index)" -ForegroundColor White
    Write-Host "   Health Status: $($response.analysis.vegetation_health)" -ForegroundColor White
    Write-Host "   Forest Cover: $($response.analysis.forest_cover_percentage)%" -ForegroundColor White
    
    Write-Host ""
    Write-Host "🗺️ Land Cover:" -ForegroundColor Yellow
    Write-Host "   Primary Type: $($response.analysis.land_cover.primary_type)" -ForegroundColor White
    Write-Host "   Forest Type: $($response.analysis.land_cover.forest_type)" -ForegroundColor White
    Write-Host "   Data Source: $($response.analysis.land_cover.data_source)" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "📈 Change Detection:" -ForegroundColor Yellow
    Write-Host "   Deforestation Risk: $($response.analysis.change_detection.deforestation_risk)" -ForegroundColor White
    Write-Host "   Trend: $($response.analysis.change_detection.trend)" -ForegroundColor White
    Write-Host "   6-Month Change: $($response.analysis.change_detection.last_6_months_change)%" -ForegroundColor White
    
    Write-Host ""
    Write-Host "🌲 Classification Breakdown:" -ForegroundColor Yellow
    Write-Host "   Tree Cover: $($response.analysis.classification.tree_cover)%" -ForegroundColor White
    Write-Host "   Shrubland: $($response.analysis.classification.shrubland)%" -ForegroundColor White
    Write-Host "   Grassland: $($response.analysis.classification.grassland)%" -ForegroundColor White
    Write-Host "   Cropland: $($response.analysis.classification.cropland)%" -ForegroundColor White
    Write-Host "   Built-up: $($response.analysis.classification.built_up)%" -ForegroundColor White
    Write-Host "   Water: $($response.analysis.classification.water_bodies)%" -ForegroundColor White
    
    Write-Host ""
    Write-Host "💡 Recommendations:" -ForegroundColor Yellow
    foreach ($rec in $response.analysis.recommendations) {
        Write-Host "   • $rec" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "ℹ️ Metadata:" -ForegroundColor Yellow
    Write-Host "   Region: $($response.metadata.region)" -ForegroundColor Gray
    Write-Host "   Season: $($response.metadata.season)" -ForegroundColor Gray
    Write-Host "   Data Quality: $($response.metadata.data_quality)" -ForegroundColor Gray
    Write-Host "   Analysis Date: $($response.metadata.analysis_date)" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    # Save full response to file
    $response | ConvertTo-Json -Depth 10 | Out-File "satellite_analysis_result.json"
    Write-Host ""
    Write-Host "✅ Full response saved to: satellite_analysis_result.json" -ForegroundColor Green
    
    # Check data mode
    Write-Host ""
    if ($response.metadata.data_quality -eq "enhanced_fallback") {
        Write-Host "⚠️ Currently using ENHANCED FALLBACK mode" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   To enable real satellite data:" -ForegroundColor Cyan
        Write-Host "   1. Register GEE project at:" -ForegroundColor White
        Write-Host "      https://code.earthengine.google.com/register?project=ee-akshittiwari29" -ForegroundColor Gray
        Write-Host "   2. Restart the service" -ForegroundColor White
        Write-Host "   3. Look for: '✅ Google Earth Engine satellite analysis enabled'" -ForegroundColor Gray
    } elseif ($response.metadata.data_quality -eq "satellite") {
        Write-Host "✅ Using REAL SATELLITE DATA from Google Earth Engine!" -ForegroundColor Green
        Write-Host "   Resolution: 10m (Sentinel-2)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "   ❌ Analysis failed!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Response:" -ForegroundColor Yellow
    Write-Host "   $($_.ErrorDetails.Message)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🎉 Test complete!" -ForegroundColor Cyan
