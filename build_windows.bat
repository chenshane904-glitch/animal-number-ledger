@echo off
REM Windows 打包脚本
echo ================================================================
echo               Windows 安装包打包脚本
echo ================================================================
echo.

REM 检查 PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 PyInstaller...
    pip install pyinstaller
)

echo.
echo ================================================================
echo 请选择要打包的版本:
echo ================================================================
echo 1. 澳门版
echo 2. V2版
echo 3. 香港版 (推荐)
echo 4. 全部打包
echo ================================================================
set /p choice="请输入选项 (1-4): "

echo.
echo [打包中...]
echo.

if "%choice%"=="3" (
    pyinstaller --name="香港" --windowed --onefile --noconsole --add-data="ui;ui" --add-data="tests;tests" app_hk.py
) else if "%choice%"=="4" (
    pyinstaller --name="动物号码归纳器-澳门版" --windowed --onefile --noconsole --add-data="ui;ui" --add-data="tests;tests" app.py
    pyinstaller --name="动物号码归纳器-V2版" --windowed --onefile --noconsole --add-data="ui;ui" --add-data="tests;tests" app_v2.py
    pyinstaller --name="香港" --windowed --onefile --noconsole --add-data="ui;ui" --add-data="tests;tests" app_hk.py
) else (
    echo 选项 %choice% 暂未实现
)

echo.
echo ================================================================
echo 打包完成！文件位置: dist\
echo ================================================================
pause
