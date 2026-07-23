#!/bin/bash
# macOS 打包脚本

set -e

echo "开始打包 macOS 版本..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3，请先安装"
    exit 1
fi

# 安装依赖
echo "安装依赖..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt

# 运行测试
echo "运行测试..."
python3 -m pytest tests/ -v -p no:cacheprovider

# 打包
echo "打包应用..."
python3 -m PyInstaller --name="十二动物号码归纳器-v1.1.0" \
    --windowed \
    --onefile \
    --add-data "VERSION:." \
    --hidden-import=customtkinter \
    --hidden-import=tkinter \
    --hidden-import=sqlite3 \
    --collect-all customtkinter \
    app.py

echo ""
echo "========================================"
echo "打包完成！"
echo "应用位于: dist/十二动物号码归纳器-v1.1.0.app"
echo "========================================"
echo ""

# 计算 SHA-256
echo "计算文件校验值..."
shasum -a 256 "dist/十二动物号码归纳器-v1.1.0.app/Contents/MacOS/十二动物号码归纳器-v1.1.0" > "dist/SHA256.txt"
cat "dist/SHA256.txt"

echo "完成"
