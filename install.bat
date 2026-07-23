@echo off
chcp 65001 >nul
title 十二动物号码归纳器 - 安装程序
echo.
echo ================================
echo   十二动物号码归纳器 v1.1.0
echo   安装程序
echo ================================
echo.

set "INSTALL_DIR=%ProgramFiles%\十二动物号码归纳器"

echo 正在安装到: %INSTALL_DIR%
echo.

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

echo 正在复制文件...
copy /Y "十二动物号码归纳器-v1.1.0.exe" "%INSTALL_DIR%\" >nul

if errorlevel 1 (
    echo.
    echo [错误] 安装失败！请以管理员身份运行此安装程序。
    pause
    exit /b 1
)

echo 文件复制完成！
echo.

set /p CREATE_SHORTCUT="是否创建桌面快捷方式？(Y/N): "

if /i "%CREATE_SHORTCUT%"=="Y" (
    echo 正在创建桌面快捷方式...
    powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\十二动物号码归纳器.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\十二动物号码归纳器-v1.1.0.exe'; $Shortcut.Save()"
    echo 快捷方式已创建！
)

echo.
echo 正在创建开始菜单快捷方式...
set "START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\十二动物号码归纳器"
if not exist "%START_MENU%" mkdir "%START_MENU%"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\十二动物号码归纳器.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\十二动物号码归纳器-v1.1.0.exe'; $Shortcut.Save()"

echo.
echo ================================
echo   安装完成！
echo ================================
echo.
echo 安装位置: %INSTALL_DIR%
echo.

set /p RUN_NOW="是否立即运行程序？(Y/N): "

if /i "%RUN_NOW%"=="Y" (
    start "" "%INSTALL_DIR%\十二动物号码归纳器-v1.1.0.exe"
)

echo.
echo 按任意键退出安装程序...
pause >nul
