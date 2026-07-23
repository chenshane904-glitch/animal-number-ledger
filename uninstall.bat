@echo off
chcp 65001 >nul
title 十二动物号码归纳器 - 卸载程序
echo.
echo ================================
echo   十二动物号码归纳器 v1.1.0
echo   卸载程序
echo ================================
echo.

set "INSTALL_DIR=%ProgramFiles%\十二动物号码归纳器"

if not exist "%INSTALL_DIR%" (
    echo 未找到已安装的程序。
    echo.
    pause
    exit /b 0
)

echo 安装位置: %INSTALL_DIR%
echo.
set /p CONFIRM="确定要卸载吗？(Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo 已取消卸载。
    pause
    exit /b 0
)

echo.
echo 正在卸载...
echo.

:: 删除桌面快捷方式
if exist "%USERPROFILE%\Desktop\十二动物号码归纳器.lnk" (
    del /f /q "%USERPROFILE%\Desktop\十二动物号码归纳器.lnk"
    echo 已删除桌面快捷方式
)

:: 删除开始菜单快捷方式
set "START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\十二动物号码归纳器"
if exist "%START_MENU%" (
    rd /s /q "%START_MENU%"
    echo 已删除开始菜单快捷方式
)

:: 删除程序文件
if exist "%INSTALL_DIR%" (
    rd /s /q "%INSTALL_DIR%"
    echo 已删除程序文件
)

echo.
echo ================================
echo   卸载完成！
echo ================================
echo.
pause
