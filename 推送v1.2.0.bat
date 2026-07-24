@echo off
chcp 65001 >nul
cls
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    十二动物号码归纳器 v1.2.0
echo    Git推送助手
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 切换到项目目录
cd /d C:\Users\2SS2\animal-number-ledger

REM 检查Git是否已安装
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Git已安装
    git --version
    echo.
    goto :configure
) else (
    echo ✗ Git未安装
    echo.
    echo 正在打开Git下载页面...
    echo.
    echo 请按照以下步骤操作：
    echo 1. 下载Git for Windows
    echo 2. 使用默认设置安装
    echo 3. 安装完成后重新运行此脚本
    echo.
    pause
    start https://git-scm.com/download/win
    exit /b 1
)

:configure
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 配置Git用户信息
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 检查是否已配置
for /f "tokens=*" %%i in ('git config --global user.name 2^>nul') do set GIT_NAME=%%i
for /f "tokens=*" %%i in ('git config --global user.email 2^>nul') do set GIT_EMAIL=%%i

if not "%GIT_NAME%"=="" (
    echo ✓ 用户名: %GIT_NAME%
) else (
    set /p GIT_NAME="请输入你的名字: "
    git config --global user.name "%GIT_NAME%"
    echo ✓ 已设置用户名
)

if not "%GIT_EMAIL%"=="" (
    echo ✓ 邮箱: %GIT_EMAIL%
) else (
    set /p GIT_EMAIL="请输入你的邮箱: "
    git config --global user.email "%GIT_EMAIL%"
    echo ✓ 已设置邮箱
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 初始化Git仓库
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 检查是否已初始化
if exist .git (
    echo ✓ Git仓库已存在
) else (
    git init
    echo ✓ Git仓库初始化完成
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 添加文件到暂存区
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

git add .
echo ✓ 文件已添加

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 提交到本地仓库
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

git commit -m "v1.2.0: Support all punctuation marks as separators" -m "- Add dot/period as valid separator (. and ．)" -m "- Add 25+ new punctuation marks as separators" -m "- Support ! ? : quotes brackets # @ $ and more" -m "- Update version to 1.2.0" -m "- Update GitHub Actions DMG filename to v1.2.0" -m "- Add comprehensive CHANGELOG.md" -m "- Add UPGRADE_v1.2.0.md report"

if %errorlevel% equ 0 (
    echo ✓ 提交成功
) else (
    echo ℹ️  没有新的更改需要提交（或已经提交）
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 连接到GitHub仓库
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 检查是否已添加remote
git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i
    echo ✓ 远程仓库: !REMOTE_URL!
    echo.
    set /p CHANGE="要更改远程仓库地址吗？(y/N): "
    if /i "!CHANGE!"=="y" (
        set /p REPO_URL="请输入新的仓库地址: "
        git remote set-url origin !REPO_URL!
        echo ✓ 已更新远程仓库地址
    )
) else (
    echo 请先在GitHub创建仓库：
    echo   1. 访问: https://github.com/new
    echo   2. 仓库名: animal-number-ledger
    echo   3. 不要勾选任何选项
    echo   4. 创建后复制仓库地址
    echo.
    echo 示例: https://github.com/你的用户名/animal-number-ledger.git
    echo.
    set /p REPO_URL="请输入GitHub仓库地址: "
    git remote add origin !REPO_URL!
    echo ✓ 已添加远程仓库
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 设置主分支
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

git branch -M main
echo ✓ 主分支已设置为main

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 推送到GitHub
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 正在推送...
echo.

git push -u origin main
if %errorlevel% equ 0 (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo ✅ v1.2.0 推送成功！
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo 🎉 升级内容：
    echo   ✓ 小数点现在作为分隔符
    echo   ✓ 新增25+种标点符号支持
    echo   ✓ 总共支持40+种分隔符
    echo.
    echo 📦 下一步：
    echo   1. 访问GitHub仓库的Actions页面
    echo   2. 等待5-10分钟自动构建
    echo   3. 下载构建产物：
    echo      - macos-app.zip
    echo      - macos-dmg.zip （推荐）
    echo   4. 解压得到：
    echo      十二动物号码归纳器-v1.2.0.dmg
    echo.
    echo 浏览器将打开Actions页面...
    timeout /t 3 >nul

    REM 尝试打开Actions页面
    for /f "tokens=*" %%i in ('git remote get-url origin') do set REPO_URL=%%i
    set REPO_URL=%REPO_URL:.git=%
    set ACTIONS_URL=%REPO_URL%/actions
    start %ACTIONS_URL%
) else (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo ⚠️ 推送失败
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo 可能的原因：
    echo   1. 需要GitHub登录认证
    echo   2. 仓库地址错误
    echo   3. 网络问题
    echo.
    echo 💡 解决方法：
    echo.
    echo 方法1: 使用Personal Access Token
    echo   1. 访问: https://github.com/settings/tokens
    echo   2. 生成新token（勾选repo权限）
    echo   3. 推送时用token作为密码
    echo.
    echo 方法2: 使用SSH
    echo   1. 生成SSH密钥: ssh-keygen
    echo   2. 添加到GitHub: https://github.com/settings/keys
    echo   3. 更改仓库地址为SSH格式
    echo.
)

echo.
pause
