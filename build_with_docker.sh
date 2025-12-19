#!/bin/bash
# 使用Docker构建APK的脚本（备选方案）

echo "=== 使用Docker构建APK ==="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "Docker未安装，请先安装Docker Desktop"
    exit 1
fi

echo "使用Docker构建APK..."
echo "这需要一些时间..."

# 使用buildozer的官方Docker镜像
docker run --interactive --tty --rm \
    --volume "$(pwd)":/home/user/hostcwd \
    --volume "$(pwd)/.buildozer":/home/user/.buildozer \
    kivy/buildozer \
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

