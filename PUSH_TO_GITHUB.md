# 推送到GitHub的步骤

## 1. 在GitHub上创建仓库

访问 https://github.com/new 创建新仓库：
- 仓库名：`buzzer_beater_reminder`（或你喜欢的名字）
- 选择 Public 或 Private
- **不要**勾选任何初始化选项（README、.gitignore等）

## 2. 推送代码

创建仓库后，GitHub会显示推送命令。或者运行：

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/buzzer_beater_reminder.git

# 重命名分支为main（如果GitHub要求）
git branch -M main

# 推送代码
git push -u origin main
```

## 3. 触发构建

1. 在GitHub仓库页面，点击 **"Actions"** 标签
2. 如果看到 "Build Android APK" 工作流，点击它
3. 点击 **"Run workflow"** 按钮
4. 选择分支（main），点击 **"Run workflow"**
5. 等待构建完成（30-60分钟）

## 4. 下载APK

构建完成后：
1. 在Actions页面找到构建记录（会有绿色✓）
2. 点击构建记录
3. 在 "Artifacts" 部分下载 **"nba-reminder-apk"**
4. 解压后找到 `.apk` 文件

## 5. 安装到一加11

1. 将APK传输到手机（USB或云盘）
2. 在手机上点击APK安装
3. 允许"未知来源安装"
4. 授予通知权限

---

## 如果推送时要求认证

如果GitHub要求用户名和密码：
- **用户名**：你的GitHub用户名
- **密码**：使用 Personal Access Token（不是GitHub密码）

### 创建Personal Access Token：

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成并复制token
5. 推送时密码处粘贴token

---

## 快速命令（复制粘贴）

```bash
# 替换 YOUR_USERNAME 为你的GitHub用户名
git remote add origin https://github.com/YOUR_USERNAME/buzzer_beater_reminder.git
git branch -M main
git push -u origin main
```

