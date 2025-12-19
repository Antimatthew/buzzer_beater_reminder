# 推送到GitHub的命令

## 你的GitHub信息
- 用户名：**Antimatthew**
- 仓库URL：https://github.com/Antimatthew/buzzer_beater_reminder

## 下一步操作

### 1. 在GitHub上创建仓库

访问：https://github.com/new

填写信息：
- Repository name: `buzzer_beater_reminder`
- Description: `NBA压哨绝杀提醒 - 移动应用版`
- 选择 Public 或 Private
- **不要勾选**任何初始化选项（README、.gitignore等）

点击 "Create repository"

### 2. 推送代码

创建仓库后，运行以下命令：

```bash
git push -u origin main
```

如果GitHub要求认证：
- **用户名**：Antimatthew
- **密码**：使用 Personal Access Token（不是GitHub密码）

### 3. 创建Personal Access Token（如果需要）

如果推送时要求密码，需要创建Token：

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 点击 "Generate token"
5. **复制token**（只显示一次）
6. 推送时在密码处粘贴token

### 4. 触发GitHub Actions构建

推送成功后：

1. 访问：https://github.com/Antimatthew/buzzer_beater_reminder
2. 点击 **"Actions"** 标签
3. 选择 **"Build Android APK"** 工作流
4. 点击 **"Run workflow"** 按钮
5. 选择分支 `main`，点击 **"Run workflow"**
6. 等待构建完成（30-60分钟）

### 5. 下载APK

构建完成后：
1. 在Actions页面找到构建记录（绿色✓）
2. 点击构建记录
3. 在 "Artifacts" 部分下载 **"nba-reminder-apk"**
4. 解压后找到 `.apk` 文件

### 6. 安装到一加11

1. 将APK传输到手机（USB或云盘）
2. 在手机上点击APK安装
3. 允许"未知来源安装"
4. 授予通知权限

---

## 快速命令

```bash
# 推送代码（创建仓库后运行）
git push -u origin main
```

---

## 遇到问题？

- **认证失败**：使用Personal Access Token而不是密码
- **仓库不存在**：确保先在GitHub上创建了仓库
- **权限错误**：确保Token有 `repo` 权限

祝你成功！🎉

