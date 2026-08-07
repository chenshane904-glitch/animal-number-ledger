#!/bin/bash
# macOS 本地打包测试脚本

set -e  # 遇到错误立即退出

echo "==================================="
echo "macOS 打包本地测试"
echo "==================================="

# 检查Python版本
echo ""
echo "[1] 检查 Python 版本"
python3 --version

# 检查项目结构
echo ""
echo "[2] 检查项目结构"

if [ ! -f "app.py" ]; then
    echo "✗ app.py 不存在"
    exit 1
fi
echo "✓ app.py 存在"

if [ ! -d "assets" ]; then
    echo "✗ assets 目录不存在"
    exit 1
fi
echo "✓ assets 目录存在"

if [ ! -f "packaging/macos.spec" ]; then
    echo "✗ packaging/macos.spec 不存在"
    exit 1
fi
echo "✓ packaging/macos.spec 存在"

# 检查assets内容
echo ""
echo "[3] 检查 assets 内容"
ls -la assets/

# 安装依赖
echo ""
echo "[4] 安装依赖"
if [ ! -f "requirements-macos.txt" ]; then
    echo "✗ requirements-macos.txt 不存在"
    exit 1
fi

pip3 install -r requirements-macos.txt

# 清理旧的构建
echo ""
echo "[5] 清理旧的构建"
rm -rf build dist *.spec

# 运行PyInstaller
echo ""
echo "[6] 运行 PyInstaller"
pyinstaller packaging/macos.spec --clean --noconfirm

# 验证构建结果
echo ""
echo "[7] 验证构建结果"

if [ ! -d "dist/AnimalNumberLedger.app" ]; then
    echo "✗ .app 不存在"
    exit 1
fi
echo "✓ .app 已创建"

if [ ! -f "dist/AnimalNumberLedger.app/Contents/Info.plist" ]; then
    echo "✗ Info.plist 不存在"
    exit 1
fi
echo "✓ Info.plist 存在"

if [ ! -f "dist/AnimalNumberLedger.app/Contents/MacOS/AnimalNumberLedger" ]; then
    echo "✗ 可执行文件不存在"
    exit 1
fi
echo "✓ 可执行文件存在"

if [ ! -d "dist/AnimalNumberLedger.app/Contents/MacOS/assets" ]; then
    echo "✗ assets 未打包"
    exit 1
fi
echo "✓ assets 已打包"

# 显示assets内容
echo ""
echo "打包的 assets 内容:"
ls -la dist/AnimalNumberLedger.app/Contents/MacOS/assets/

# 检查架构
echo ""
echo "[8] 检查可执行文件架构"
file dist/AnimalNumberLedger.app/Contents/MacOS/AnimalNumberLedger
lipo -info dist/AnimalNumberLedger.app/Contents/MacOS/AnimalNumberLedger || true

# 签名
echo ""
echo "[9] 签名应用"
codesign --force --deep --sign - dist/AnimalNumberLedger.app
codesign --verify --verbose dist/AnimalNumberLedger.app

# 创建DMG
echo ""
echo "[10] 创建 DMG"
mkdir -p dmg
cp -r dist/AnimalNumberLedger.app dmg/
ln -s /Applications dmg/Applications

hdiutil create -volname "AnimalNumberLedger" \
    -srcfolder dmg \
    -ov -format UDZO \
    AnimalNumberLedger-arm64.dmg

ls -lh AnimalNumberLedger-arm64.dmg

echo ""
echo "==================================="
echo "✓ 本地打包测试完成"
echo "==================================="
echo ""
echo "下一步:"
echo "1. 双击 AnimalNumberLedger-arm64.dmg"
echo "2. 将应用拖动到 Applications"
echo "3. 从 Launchpad 或 Applications 启动应用"
echo "4. 验证功能正常"
