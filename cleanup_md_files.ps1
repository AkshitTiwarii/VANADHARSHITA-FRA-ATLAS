# Cleanup redundant .md files
# Keeps only README.md and DOCUMENTATION.md

Write-Host "🧹 Cleaning up redundant .md files..." -ForegroundColor Cyan

# List of files to DELETE (all the redundant documentation)
$filesToDelete = @(
    "ALL_MAPS_FIXED_REAL_PROJECT.md",
    "ALL_SERVICES_ONLINE_STATUS.md",
    "BLOCKCHAIN_ANTI_FRAUD_SYSTEM.md",
    "BLOCKCHAIN_COMPLETE.md",
    "BLOCKCHAIN_HYPERLEDGER_INTEGRATION.md",
    "BLOCKCHAIN_TEST_SUCCESS.md",
    "BLOCKCHAIN_TESTING_ISSUE.md",
    "COMMITS_VERIFICATION.md",
    "COMPLETE_ANSWER_SERVICES_TESTING_WORK.md",
    "COMPLETE_FIX_SUMMARY.md",
    "COMPLETE_SYSTEM_SUMMARY.md",
    "COMPLETE_WORKFLOW_EXPLANATION.md",
    "DSS_COMPLETE_DOCUMENTATION.md",
    "DSS_FINAL_STATUS.md",
    "DSS_QUICK_REFERENCE.md",
    "ERROR_FIXED_FINAL.md",
    "FOREST_MONITORING_COMPLETE.md",
    "FRA_REAL_WORLD_IMPLEMENTATION.md",
    "FRONTEND_INTEGRATION_COMPLETE.md",
    "GOOGLE_MAPS_COMPLETE.md",
    "GOOGLE_MAPS_INTEGRATION.md",
    "GOOGLE_MAPS_TROUBLESHOOTING.md",
    "HOW_WE_SOLVE_THE_PROBLEM.md",
    "INTEGRATED_ENDPOINT_TESTING.md",
    "MAP_AND_NAVIGATION_COMPLETE.md",
    "MONITORING_IMPLEMENTATION_SUMMARY.md",
    "MULTILINGUAL_FEATURES.md",
    "NAVIGATION_BACK_BUTTON_FIXED.md",
    "NAVIGATION_QUICK_GUIDE.md",
    "NEXT_STEPS_TESTING.md",
    "PROJECT_COMPLETE_SUMMARY.md",
    "QUICK_ANSWER.md",
    "QUICK_FIX_MAP_ISSUE.md",
    "QUICK_REFERENCE_CARD.md",
    "SATELLITE_ANALYSIS_STATUS.md",
    "SATELLITE_QUICK_START.md",
    "SERVICE_TEST_RESULTS.md",
    "SERVICES_STARTUP_AND_TESTING.md",
    "SERVICES_STATUS.md",
    "SUPER_POWERED_MAP_FEATURES.md",
    "TEST_SUPER_MAP_API.md",
    "THREE_FEATURES_COMPLETE.md",
    "THREE_FEATURES_CORRECTED.md",
    "THREE_FEATURES_STATUS.md",
    "UI_IMPROVEMENTS_COMPLETE.md",
    "UI_IMPROVEMENTS_QUICK_REFERENCE.md",
    "UI_IMPROVEMENTS_SUMMARY.md",
    "UI_UX_IMPROVEMENTS_GUIDE.md",
    "WEBGIS_COMPLETE_SUMMARY.md",
    "WEBGIS_DEVELOPER_REFERENCE.md",
    "WEBGIS_FINAL_STATUS.md",
    "WEBGIS_INTEGRATION_COMPLETE.md",
    "WEBGIS_QUICK_START.md",
    "WORK_REMAINING_ASSESSMENT.md",
    "YOU_ARE_READY.md",
    "ZEROS_FIXED_REAL_DATA.md"
)

$deleted = 0
$notFound = 0

foreach ($file in $filesToDelete) {
    $filePath = Join-Path $PSScriptRoot $file
    if (Test-Path $filePath) {
        Remove-Item $filePath -Force
        Write-Host "  ✅ Deleted: $file" -ForegroundColor Green
        $deleted++
    } else {
        Write-Host "  ⚠️  Not found: $file" -ForegroundColor Yellow
        $notFound++
    }
}

Write-Host "`n📊 Cleanup Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Deleted: $deleted files" -ForegroundColor Green
Write-Host "  ⚠️  Not found: $notFound files" -ForegroundColor Yellow
Write-Host "`n📚 Remaining documentation files:" -ForegroundColor Cyan
Write-Host "  - README.md (Quick start guide)" -ForegroundColor White
Write-Host "  - DOCUMENTATION.md (Complete comprehensive docs)" -ForegroundColor White
Write-Host "`n✨ Cleanup complete! Your workspace is now organized." -ForegroundColor Green
