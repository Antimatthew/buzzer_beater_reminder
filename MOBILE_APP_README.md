# NBA压哨绝杀提醒 - 移动应用版

这是NBA压哨绝杀提醒系统的移动应用版本，支持Android和iOS平台。

## 功能特点

- 📱 原生移动应用体验
- 🔔 手机推送通知提醒
- 📊 实时显示比赛列表
- ⚡ 关键时刻自动提醒
- 🎨 现代化Material Design界面

## 安装方式

### 方式一：使用Buildozer打包Android APK（推荐）

#### 前置要求

1. **安装Buildozer**
   ```bash
   pip install buildozer
   ```

2. **安装Android SDK和NDK**
   - 下载并安装Android Studio
   - 配置环境变量：
     ```bash
     export ANDROID_HOME=/path/to/android/sdk
     export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
     ```

3. **安装依赖工具**（Linux/Mac）
   ```bash
   # Ubuntu/Debian
   sudo apt-get install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   
   # macOS
   brew install autoconf automake libtool pkg-config
   brew install libffi openssl
   ```

#### 打包步骤

1. **初始化Buildozer配置**（如果还没有buildozer.spec文件）
   ```bash
   buildozer init
   ```

2. **构建APK**
   ```bash
   buildozer android debug
   ```
   或者构建发布版本：
   ```bash
   buildozer android release
   ```

3. **安装到手机**
   - 生成的APK文件在 `bin/` 目录下
   - 将APK传输到Android手机
   - 在手机上启用"未知来源"安装
   - 点击APK文件安装

### 方式二：使用Kivy Launcher（快速测试）

1. 在Android手机上安装 [Kivy Launcher](https://play.google.com/store/apps/details?id=org.kivy.pygame)
2. 将 `nba_reminder_app.py` 和 `requirements.txt` 复制到手机
3. 在Kivy Launcher中运行应用

### 方式三：使用BeeWare（跨平台）

BeeWare可以将Python应用打包成原生移动应用：

```bash
pip install briefcase

# 初始化项目
briefcase create

# 构建Android应用
briefcase build android

# 运行应用
briefcase run android
```

## 使用方法

1. **启动应用**
   - 打开应用后，会看到主界面

2. **开启监控**
   - 点击"开启监控"开关
   - 应用会每60秒自动检查比赛

3. **查看比赛**
   - 比赛列表会显示所有正在进行的比赛
   - 关键时刻的比赛会用红色高亮显示

4. **接收通知**
   - 当比赛满足提醒条件时，手机会弹出通知
   - 点击通知可以打开应用查看详情

## 配置说明

### 修改提醒条件

编辑 `nba_reminder_app.py` 中的 `NBAGameReminderCore` 类：

```python
self.TIME_THRESHOLD = 120  # 剩余时间阈值（秒），默认2分钟
self.SCORE_DIFF_THRESHOLD = 5  # 分差阈值，默认5分
```

### 修改检查间隔

在主屏幕的 `_monitor_loop` 方法中修改：

```python
time.sleep(60)  # 改为你想要的秒数
```

## 权限说明

应用需要以下权限：
- **INTERNET**: 访问网络获取比赛数据
- **POST_NOTIFICATIONS**: 发送推送通知（Android 13+）

## 故障排除

### 问题：通知不显示

**解决方案：**
1. 检查手机通知权限是否已授予
2. Android 8.0+需要创建通知渠道（代码已包含）
3. 确保应用在后台运行时没有被系统杀死

### 问题：无法获取比赛数据

**解决方案：**
1. 检查网络连接
2. 确认虎扑网站可以正常访问
3. 查看日志文件 `nba_reminder.log`

### 问题：应用崩溃

**解决方案：**
1. 查看日志文件了解错误信息
2. 确保所有依赖都已正确安装
3. 检查Python版本（需要3.7+）

## 开发说明

### 本地测试（桌面）

在开发时，可以在桌面环境测试应用：

```bash
pip install kivy kivymd requests beautifulsoup4 lxml
python nba_reminder_app.py
```

### 项目结构

```
.
├── nba_reminder_app.py      # 移动应用主文件
├── nba_game_reminder.py     # 原始桌面版
├── buildozer.spec          # Buildozer配置文件
├── requirements.txt         # Python依赖
└── MOBILE_APP_README.md     # 本文档
```

## 注意事项

1. **电池优化**：建议将应用添加到电池优化白名单，确保后台运行
2. **网络流量**：应用每60秒检查一次，注意流量消耗
3. **数据更新**：如果虎扑网站结构变化，可能需要更新解析代码

## 技术支持

如有问题，请查看：
- 日志文件：`nba_reminder.log`
- 状态文件：`nba_reminder_state.json`

## License

本项目采用 MIT License。

