# 快速构建APK指南

## ✅ 当前状态

- ✅ 移动应用代码已准备好 (`nba_reminder_app.py`)
- ✅ 打包配置已准备好 (`buildozer.spec`)
- ✅ GitHub Actions工作流已创建 (`.github/workflows/build_apk.yml`)

## 🚀 三种构建方式

### 方式一：GitHub Actions（最简单，推荐⭐⭐⭐）

**优点：** 无需本地配置，自动构建，直接下载APK

**步骤：**
1. 将项目推送到GitHub
2. 在GitHub Actions中触发构建
3. 下载构建好的APK

**详细步骤：**
```bash
# 1. 初始化Git仓库（如果还没有）
git init
git add .
git commit -m "Add mobile app"

# 2. 推送到GitHub
git remote add origin <你的GitHub仓库URL>
git push -u origin main

# 3. 在GitHub网站：
#    - 进入仓库
#    - 点击 "Actions" 标签
#    - 选择 "Build Android APK"
#    - 点击 "Run workflow"
#    - 等待构建完成（30-60分钟）
#    - 下载APK
```

---

### 方式二：WSL本地构建（需要配置环境）

**优点：** 完全控制，可以调试

**前置要求：**
- WSL2 + Ubuntu（如果没有，运行 `wsl --install -d Ubuntu`）
- Android Studio
- 30-60分钟首次构建时间

**步骤：**
```bash
# 1. 进入WSL
wsl

# 2. 进入项目目录
cd /mnt/d/projects/buzzer_beater_reminder

# 3. 安装依赖
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev build-essential

pip3 install buildozer cython

# 4. 安装Android Studio并配置SDK
# （需要手动操作，见 BUILD_APK_GUIDE.md）

# 5. 设置环境变量（在 ~/.bashrc 中）
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# 6. 构建APK
buildozer android debug
```

---

### 方式三：使用在线构建服务

**推荐服务：**
- GitHub Actions（已配置好）
- GitLab CI/CD
- CircleCI

---

## 📱 安装到一加11

### 1. 传输APK
- USB：连接手机，复制APK
- 云盘：上传到网盘，手机下载
- 直接下载：从GitHub Actions下载

### 2. 安装
- 在手机上找到APK文件
- 点击安装
- 允许"未知来源安装"

### 3. 授予权限
- 网络权限（自动）
- 通知权限（设置 → 应用 → 通知）

---

## 🎯 推荐流程

**最快的方式：**
1. 使用GitHub Actions自动构建（无需本地配置）
2. 等待30-60分钟
3. 下载APK
4. 安装到手机

**详细步骤见 `BUILD_APK_GUIDE.md`**

