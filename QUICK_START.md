# 快速开始指南

## 在桌面环境测试应用

在打包成手机应用之前，你可以先在电脑上测试应用：

### 1. 激活虚拟环境（如果使用venv）

**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. 安装依赖

**如果使用venv，使用venv中的pip:**
```bash
# Windows
.\venv\python.exe -m pip install kivy kivymd requests beautifulsoup4 lxml

# Linux/Mac
venv/bin/pip install kivy kivymd requests beautifulsoup4 lxml
```

**或者直接使用pip（如果已激活venv）:**
```bash
pip install kivy kivymd requests beautifulsoup4 lxml
```

### 3. 运行应用

**如果使用venv:**
```bash
# Windows
.\venv\python.exe nba_reminder_app.py

# Linux/Mac
venv/bin/python nba_reminder_app.py
```

**或者直接使用python（如果已激活venv）:**
```bash
python nba_reminder_app.py
```

应用会在桌面窗口打开，你可以测试所有功能。

## 打包成Android APK

### Windows用户

**注意：** Buildozer主要在Linux/Mac上工作。Windows用户有以下选择：

1. **使用WSL（推荐）**
   - 安装WSL2和Ubuntu
   - 在WSL中按照Linux步骤操作

2. **使用云服务**
   - 使用GitHub Actions自动打包
   - 或使用在线构建服务

3. **使用虚拟机**
   - 安装Linux虚拟机
   - 在虚拟机中打包

### Linux/Mac用户

#### 步骤1：安装Buildozer

```bash
pip install buildozer
```

#### 步骤2：安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

**macOS:**
```bash
brew install autoconf automake libtool pkg-config
brew install libffi openssl
```

#### 步骤3：配置Android SDK

1. 下载并安装 [Android Studio](https://developer.android.com/studio)
2. 在Android Studio中安装：
   - Android SDK Platform 33
   - Android SDK Build-Tools
   - Android NDK (推荐版本23b)
3. 设置环境变量：

```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

#### 步骤4：构建APK

```bash
# 首次构建（会下载很多依赖，需要较长时间）
buildozer android debug

# 生成的APK在 bin/ 目录
```

#### 步骤5：安装到手机

1. 将APK文件传输到Android手机
2. 在手机上启用"允许安装未知来源应用"
3. 点击APK文件安装

## 常见问题

### Q: 构建失败，提示找不到某些工具？

A: 确保已安装所有系统依赖。在Ubuntu上运行：
```bash
sudo apt-get install -y build-essential
```

### Q: 构建时间很长？

A: 首次构建需要下载Android SDK、NDK等，可能需要30分钟到1小时。后续构建会快很多。

### Q: 应用在手机上无法联网？

A: 检查：
1. 手机是否已授予应用网络权限
2. buildozer.spec中是否包含INTERNET权限（已包含）

### Q: 通知不显示？

A: 
1. Android 13+需要手动授予通知权限
2. 在手机设置中检查应用的通知权限
3. 确保应用没有被电池优化杀死

### Q: 如何修改检查间隔？

编辑 `nba_reminder_app.py`，找到 `_monitor_loop` 方法中的：
```python
time.sleep(60)  # 改为你想要的秒数，如30表示30秒
```

## 下一步

- 查看 `MOBILE_APP_README.md` 了解详细文档
- 查看 `nba_reminder_app.py` 了解代码结构
- 根据需要自定义界面和功能

