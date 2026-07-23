@echo off
REM Windows 打包脚本

echo 开始打包 Windows 版本...

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.11 或更高版本
    pause
    exit /b 1
)

REM 安装依赖
echo 安装依赖...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt

REM 运行测试
echo 运行测试...
python -m pytest tests/ -v -p no:cacheprovider
if errorlevel 1 (
    echo 错误: 测试失败，已停止打包
    exit /b 1
)

REM 打包
echo 打包应用...
python -m PyInstaller --name="十二动物号码归纳器-v1.1.0" ^
    --windowed ^
    --onefile ^
    --icon=NONE ^
    --add-data "VERSION;." ^
    --hidden-import=customtkinter ^
    --hidden-import=tkinter ^
    --hidden-import=sqlite3 ^
    --collect-all customtkinter ^
    app.py

if errorlevel 1 (
    echo 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo 可执行文件位于: dist\十二动物号码归纳器-v1.1.0.exe
echo ========================================
echo.

REM 计算 SHA-256
echo 计算文件校验值...
powershell -NoProfile -Command "$hash=(Get-FileHash -LiteralPath 'dist\十二动物号码归纳器-v1.1.0.exe' -Algorithm SHA256).Hash.ToLower(); @('十二动物号码归纳器-v1.1.0.exe  SHA-256', $hash) | Set-Content -LiteralPath 'dist\SHA256.txt' -Encoding UTF8; Get-Content -LiteralPath 'dist\SHA256.txt'"

pause
