#!/bin/bash
# macOS 自动打包脚本

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║           🍎 macOS 应用打包脚本                                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# 检查是否在 macOS 上
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  警告: 此脚本需要在 macOS 上运行"
    echo "当前系统: $OSTYPE"
    echo ""
    echo "请将项目复制到 macOS 后运行此脚本"
    exit 1
fi

# 检查 Python
echo "1️⃣  检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3"
    echo "请安装 Python: https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python 版本: $(python3 --version)"
echo ""

# 检查依赖
echo "2️⃣  检查依赖..."
python3 -c "import customtkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装 customtkinter..."
    pip3 install customtkinter
fi
echo "✅ 依赖检查完成"
echo ""

# 安装 PyInstaller
echo "3️⃣  检查 PyInstaller..."
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 安装 PyInstaller..."
    pip3 install pyinstaller
fi
echo "✅ PyInstaller 已安装"
echo ""

# 清理旧的打包文件
echo "4️⃣  清理旧文件..."
rm -rf build dist *.spec
echo "✅ 清理完成"
echo ""

# 选择要打包的版本
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "请选择要打包的版本:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1) 澳门版 (传统布局)"
echo "2) V2版 (卡片布局)"
echo "3) 香港"
echo "4) 全部打包"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "请输入选项 (1-4): " choice
echo ""

# 打包函数
pack_version() {
    local script=$1
    local name=$2

    echo "5️⃣  开始打包: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    pyinstaller \
        --name="$name" \
        --windowed \
        --noconfirm \
        --clean \
        --add-data="ui:ui" \
        --add-data="tests:tests" \
        $script

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 打包成功: $name"
        echo "📁 位置: dist/$name.app"
        echo ""
    else
        echo ""
        echo "❌ 打包失败: $name"
        echo ""
        return 1
    fi
}

# 根据选择打包
case $choice in
    1)
        pack_version "app.py" "动物号码归纳器-澳门版"
        ;;
    2)
        pack_version "app_v2.py" "动物号码归纳器-V2版"
        ;;
    3)
        pack_version "app_hk.py" "香港"
        ;;
    4)
        pack_version "app.py" "动物号码归纳器-澳门版"
        pack_version "app_v2.py" "动物号码归纳器-V2版"
        pack_version "app_hk.py" "香港"
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║           ✅ 打包完成！                                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 打包文件位置: dist/"
echo ""
echo "🚀 使用方法:"
echo "   1. 打开 Finder"
echo "   2. 进入 dist 文件夹"
echo "   3. 双击 .app 文件运行"
echo ""
