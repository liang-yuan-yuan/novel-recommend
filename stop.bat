@echo off
chcp 65001 >nul
echo ================================
echo   🛑 停止所有服务
echo ================================
echo.

echo [1/2] 停止 Python 服务...
taskkill /f /im python.exe 2>nul

echo [2/2] 停止番茄下载器...
taskkill /f /im TomatoNovelDownloader-Win64-v2.4.13.exe 2>nul

echo.
echo ✅ 所有服务已停止
timeout /t 2 /nobreak >nul
exit