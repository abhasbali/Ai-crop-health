@echo off
echo ================================================================================
echo 🧪 CropHealth Multi-Spectral Analysis - Integration Test
echo ================================================================================
echo.

REM Check if services are running
echo 🔍 Testing service availability...
echo.

REM Test backend health
echo Testing backend health check...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -TimeoutSec 5; Write-Output '✅ Backend: ' + $response.StatusCode } catch { Write-Output '❌ Backend: Not responding' }"

echo.
REM Test frontend
echo Testing frontend availability...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 5; Write-Output '✅ Frontend: ' + $response.StatusCode } catch { Write-Output '❌ Frontend: Not responding' }"

echo.
echo 🧪 Testing multi-spectral analysis API...
echo.

REM Test multi-spectral analysis endpoint
powershell -Command "
$body = @{
    spectral_bands = @{
        red = @(0.05, 0.06, 0.04, 0.07, 0.05)
        green = @(0.07, 0.08, 0.06, 0.09, 0.07)
        nir = @(0.6, 0.7, 0.5, 0.8, 0.65)
        swir = @(0.1, 0.12, 0.08, 0.15, 0.11)
    }
    location = @{
        latitude = 40.7128
        longitude = -74.0060
    }
} | ConvertTo-Json -Depth 3

try {
    $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/predictions/multi-spectral-analysis' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 15
    $result = $response.Content | ConvertFrom-Json
    
    Write-Output '✅ Multi-Spectral Analysis API: Working'
    Write-Output '📊 Response Summary:'
    Write-Output '   • Indices calculated: ' + ($result.indices_stats.PSObject.Properties.Name -join ', ')
    Write-Output '   • Land cover types: ' + $result.land_cover_analysis.land_cover_stats.PSObject.Properties.Count
    Write-Output '   • Visualizations: ' + ($result.visualizations.PSObject.Properties.Name -join ', ')
    
} catch {
    Write-Output '❌ Multi-Spectral Analysis API: Failed - ' + $_.Exception.Message
}
"

echo.
echo 🗄️ Testing database connectivity...

REM Test database through backend
powershell -Command "
try {
    # This will test if backend can connect to database
    $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -TimeoutSec 5
    $result = $response.Content | ConvertFrom-Json
    if ($result.status -eq 'healthy') {
        Write-Output '✅ Database connectivity: Working'
    } else {
        Write-Output '⚠️ Database connectivity: Limited'
    }
} catch {
    Write-Output '❌ Database connectivity: Failed'
}
"

echo.
echo 📱 Testing container status...
docker-compose ps

echo.
echo ================================================================================
echo 🎯 Integration Test Complete
echo ================================================================================
echo.
echo 🚀 Quick Start Commands:
echo   • Open app:        http://localhost:3000
echo   • Login:           demo@crophealth.com / demo123
echo   • Test analysis:   Navigate to 'Spectral Analysis' → Run Analysis
echo.
echo 💾 Management:
echo   • View logs:       docker-compose logs -f
echo   • Restart:         docker-compose restart
echo   • Stop:            docker-compose down
echo.
pause
