#!/bin/bash
# 在WSL中构建APK的脚本

echo "=== NBA提醒APP - APK构建脚本 ==="
echo ""

# 检查是否在WSL中
if [ -z "$WSL_DISTRO_NAME" ]; then
    echo "警告: 这似乎不在WSL环境中"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查buildozer是否安装
if ! command -v buildozer &> /dev/null; then
    echo "Buildozer未安装，正在安装..."
    pip3 install buildozer cython
fi

# 检查Android SDK
if [ -z "$ANDROID_HOME" ]; then
    echo "警告: ANDROID_HOME未设置"
    echo "请先安装Android Studio并设置环境变量"
    echo "在 ~/.bashrc 中添加:"
    echo "export ANDROID_HOME=\$HOME/Android/Sdk"
    echo "export PATH=\$PATH:\$ANDROID_HOME/tools:\$ANDROID_HOME/platform-tools"
    exit 1
fi

echo "开始构建APK..."
echo "这可能需要30分钟到1小时（首次构建）"
echo ""

# 构建APK
buildozer android debug

# 检查构建结果
if [ -f "bin/*.apk" ]; then
    echo ""
    echo "✅ APK构建成功！"
    echo "APK文件位置: bin/"
    ls -lh bin/*.apk
else
    echo ""
    echo "❌ APK构建失败，请查看上面的错误信息"
    exit 1
fi

