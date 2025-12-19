# 打包APK详细指南

## 🚀 快速开始

### 方法一：使用GitHub Actions（最简单，推荐）

1. **将项目推送到GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <你的GitHub仓库URL>
   git push -u origin main
   ```

2. **触发构建**
   - 在GitHub仓库页面，点击 "Actions" 标签
   - 选择 "Build Android APK" 工作流
   - 点击 "Run workflow" 按钮
   - 等待构建完成（约30-60分钟）

3. **下载APK**
   - 构建完成后，在Actions页面下载APK文件
   - 传输到手机安装

---

### 方法二：在WSL中本地构建

#### 步骤1：进入WSL

```bash
wsl
cd /mnt/d/projects/buzzer_beater_reminder
```

#### 步骤2：安装依赖

```bash
# 更新系统
sudo apt-get update

# 安装系统依赖
sudo apt-get install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev build-essential

# 安装Buildozer
pip3 install buildozer cython
```

#### 步骤3：配置Android SDK

1. **下载Android Studio**
   - 访问 https://developer.android.com/studio
   - 下载并安装Android Studio

2. **安装SDK组件**
   - 打开Android Studio
   - Tools → SDK Manager
   - 安装：
     - Android SDK Platform 33
     - Android SDK Build-Tools
     - Android NDK (Side by side) - 选择版本23b

3. **设置环境变量**
   
   编辑 `~/.bashrc`:
   ```bash
   nano ~/.bashrc
   ```
   
   添加以下内容：
   ```bash
   export ANDROID_HOME=$HOME/Android/Sdk
   export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
   export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
   ```
   
   使配置生效：
   ```bash
   source ~/.bashrc
   ```

#### 步骤4：构建APK

```bash
# 使用提供的脚本
chmod +x build_apk_wsl.sh
./build_apk_wsl.sh

# 或直接使用buildozer
buildozer android debug
```

#### 步骤5：找到APK文件

构建完成后，APK文件在 `bin/` 目录：
```bash
ls -lh bin/*.apk
```

---

## 📱 安装到一加11

### 1. 传输APK到手机

**方法A：USB传输**
```bash
# 在WSL中，APK在 /mnt/d/projects/buzzer_beater_reminder/bin/
# 可以直接在Windows文件管理器中访问
```

**方法B：云盘传输**
- 上传APK到百度网盘/OneDrive
- 在手机上下载

### 2. 在手机上安装

1. 打开文件管理器
2. 找到APK文件
3. 点击安装
4. 如果提示"未知来源"，去设置中允许安装

### 3. 授予权限

- **网络权限**：自动授予
- **通知权限**：设置 → 应用 → NBA压哨绝杀提醒 → 通知 → 允许

---

## 🔧 常见问题

### Q: 构建失败，提示找不到Android SDK

**解决方案：**
```bash
# 检查ANDROID_HOME是否设置
echo $ANDROID_HOME

# 如果没有，设置它
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

### Q: 构建失败，提示NDK版本问题

**解决方案：**
在 `buildozer.spec` 中指定NDK版本：
```ini
android.ndk = 23b
```

### Q: 构建时间太长

**正常现象：**
- 首次构建需要下载SDK、NDK等，需要30-60分钟
- 后续构建只需要几分钟

### Q: APK文件太大

**优化方法：**
- 使用 `buildozer android release` 构建发布版本（会压缩）
- 在 `buildozer.spec` 中只包含必要的文件

### Q: 应用安装后无法运行

**检查清单：**
- [ ] 网络权限已授予
- [ ] 通知权限已授予（Android 13+）
- [ ] 应用没有被电池优化杀死
- [ ] 查看日志：`adb logcat | grep python`

---

## 📊 构建输出说明

构建成功后会生成：
- `bin/nbareminder-0.1-arm64-v8a-debug.apk` - 64位ARM设备（推荐，一加11使用）
- `bin/nbareminder-0.1-armeabi-v7a-debug.apk` - 32位ARM设备

**一加11应该使用 arm64-v8a 版本**

---

## 🎯 下一步

1. ✅ 测试应用功能
2. ✅ 构建APK
3. ✅ 安装到手机
4. ✅ 测试通知功能
5. ✅ 享受使用！

---

## 💡 提示

- **首次构建很慢**：这是正常的，需要下载很多依赖
- **后续构建很快**：只需要重新编译代码
- **测试建议**：先在电脑上测试应用，确认功能正常后再打包
- **更新应用**：修改代码后重新构建，卸载旧版本安装新版本

祝你打包成功！🎉

