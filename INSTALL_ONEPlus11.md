# 在一加11手机上安装NBA提醒APP

## ✅ 当前状态

你的项目已经准备好了移动应用版本：
- ✅ `nba_reminder_app.py` - 移动应用主文件
- ✅ `buildozer.spec` - Android打包配置文件
- ✅ 支持Android推送通知
- ✅ 现代化Material Design界面

## 📱 一加11手机兼容性

**完全支持！** 一加11是Android手机，可以运行这个APP。

## 🚀 安装方法（三种选择）

### 方法一：使用WSL在Windows上打包（推荐）

#### 步骤1：安装WSL2和Ubuntu

1. 以管理员身份打开PowerShell，运行：
```powershell
wsl --install
```

2. 重启电脑
3. 启动Ubuntu，设置用户名和密码

#### 步骤2：在WSL中安装依赖

```bash
# 更新系统
sudo apt-get update

# 安装Python和pip
sudo apt-get install -y python3 python3-pip

# 安装Buildozer
pip3 install buildozer

# 安装系统依赖
sudo apt-get install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev build-essential
```

#### 步骤3：配置Android SDK

1. 下载并安装 [Android Studio](https://developer.android.com/studio)
2. 在Android Studio中安装：
   - Android SDK Platform 33
   - Android SDK Build-Tools
   - Android NDK (推荐版本23b)
3. 设置环境变量（在WSL的 `~/.bashrc` 中添加）：
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

#### 步骤4：复制项目到WSL

```bash
# 在WSL中，项目应该在 /mnt/d/projects/buzzer_beater_reminder
cd /mnt/d/projects/buzzer_beater_reminder
```

#### 步骤5：构建APK

```bash
# 首次构建（需要较长时间，30分钟-1小时）
buildozer android debug

# 生成的APK在 bin/ 目录
```

#### 步骤6：传输到手机并安装

1. 将 `bin/nbareminder-0.1-arm64-v8a-debug.apk` 复制到Windows
2. 通过USB或云盘传输到一加11手机
3. 在手机上：设置 → 安全 → 允许安装未知来源应用
4. 点击APK文件安装

---

### 方法二：使用在线构建服务（最简单）

#### 使用GitHub Actions自动构建

1. 将项目推送到GitHub
2. 创建 `.github/workflows/build.yml`：
```yaml
name: Build Android APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install Buildozer
        run: |
          pip install buildozer
          sudo apt-get update
          sudo apt-get install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev build-essential
      - name: Build APK
        run: buildozer android debug
      - name: Upload APK
        uses: actions/upload-artifact@v2
        with:
          name: app-debug
          path: bin/*.apk
```

3. 在GitHub Actions中下载构建好的APK

---

### 方法三：使用虚拟机（备选）

1. 安装VirtualBox或VMware
2. 安装Ubuntu虚拟机
3. 在虚拟机中按照方法一的步骤操作

---

## 📲 安装到一加11的详细步骤

### 1. 启用未知来源安装

在一加11手机上：
- 打开 **设置**
- 找到 **安全** 或 **应用管理**
- 开启 **允许安装未知来源应用** 或 **安装外部应用**

### 2. 传输APK文件

**方法A：USB传输**
1. 用USB线连接手机和电脑
2. 在手机上选择"文件传输"模式
3. 将APK文件复制到手机

**方法B：云盘传输**
1. 将APK上传到百度网盘/OneDrive/Google Drive
2. 在手机上下载

**方法C：直接下载**
1. 如果使用GitHub Actions，直接在手机上访问GitHub下载

### 3. 安装APK

1. 在手机文件管理器中找到APK文件
2. 点击APK文件
3. 点击"安装"
4. 等待安装完成

### 4. 首次运行

1. 打开"NBA压哨绝杀提醒"应用
2. 授予网络权限（如果需要）
3. 授予通知权限（Android 13+需要）
4. 开启监控开关

---

## ⚙️ 应用权限说明

应用需要以下权限：
- **网络访问**：获取比赛数据
- **通知权限**：发送推送提醒（Android 13+需要手动授予）

---

## 🔧 常见问题

### Q: 构建失败怎么办？
A: 
- 检查是否安装了所有依赖
- 确保Android SDK和NDK已正确安装
- 查看错误日志，根据提示修复

### Q: APK安装失败？
A:
- 确保已启用"未知来源安装"
- 检查APK文件是否完整下载
- 尝试重新下载APK

### Q: 应用无法联网？
A:
- 检查手机网络连接
- 在设置中检查应用是否有网络权限

### Q: 通知不显示？
A:
- Android 13+需要手动授予通知权限
- 设置 → 应用 → NBA压哨绝杀提醒 → 通知 → 允许通知
- 确保应用没有被电池优化杀死

---

## 📝 快速检查清单

- [ ] WSL/虚拟机已安装
- [ ] Buildozer已安装
- [ ] Android SDK已配置
- [ ] APK已成功构建
- [ ] APK已传输到手机
- [ ] 手机已启用未知来源安装
- [ ] 应用已安装
- [ ] 权限已授予
- [ ] 应用可以正常运行

---

## 💡 提示

1. **首次构建很慢**：需要下载Android SDK、NDK等，可能需要30分钟-1小时
2. **后续构建很快**：只需要几分钟
3. **测试建议**：先在电脑上用Kivy测试应用，确认功能正常后再打包
4. **更新应用**：修改代码后重新构建APK，卸载旧版本后安装新版本

---

## 🆘 需要帮助？

如果遇到问题：
1. 查看 `MOBILE_APP_README.md` 了解详细文档
2. 查看 `QUICK_START.md` 了解快速开始指南
3. 检查构建日志中的错误信息

祝你成功安装！🎉

