@echo off
chcp 65001 >nul
echo ================================
echo   🚀 启动小说推荐网站
echo ================================
echo.

echo [1/3] 启动番茄小说 Web 服务...
start /b cmd /c "cd /d D:\personProject && .\TomatoNovelDownloader-Win64-v2.4.13.exe --server > nul 2>&1"
timeout /t 2 /nobreak >nul

echo [2/3] 启动 Flask 网站...
start /b cmd /c "cd /d D:\personProject && .venv\Scripts\activate && python app.py > nul 2>&1"
timeout /t 2 /nobreak >nul

echo [3/3] 打开浏览器...
start http://127.0.0.1:5000

echo.
echo 所有服务已启动！
echo.
echo 停止服务请运行 stop.bat
timeout /t 3 /nobreak >nul
exit