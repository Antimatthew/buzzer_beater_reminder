[app]

# (str) 应用标题
title = NBA压哨绝杀提醒

# (str) 包名
package.name = nbareminder

# (str) 包域名
package.domain = org.nba

# (str) 应用源代码目录
source.dir = .

# (list) 应用源代码文件
source.include_exts = py,png,jpg,kv,atlas,json

# (str) 应用入口点
source.main = nba_reminder_app.py

# (list) 应用依赖
requirements = python3,kivy>=2.1.0,kivymd>=1.1.1,requests,beautifulsoup4,lxml,pyjnius

# (str) Python版本
requirements.source.python3 = 3.9

# (list) 应用权限
android.permissions = INTERNET,POST_NOTIFICATIONS

# (int) 目标Android API，应该尽可能高
android.api = 33

# (str) Android NDK版本
android.ndk = 23b

# (str) Android SDK Build-Tools版本
android.sdk_build_tools = 34.0.0

# (int) 最小Android API
android.minapi = 21

# (str) Android架构
android.archs = arm64-v8a,armeabi-v7a

# (bool) 启用AndroidX支持
android.enable_androidx = True

# (str) 应用版本号
version = 0.1

# (str) 应用版本代码（整数，用于应用商店）
version.code = 1

# (str) 应用版本名称
version.name = 0.1

# (str) 应用图标（可选，需要提供图标文件）
# icon.filename = %(source.dir)s/data/icon.png

# (str) 应用启动画面（可选）
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) 应用方向（portrait或landscape）
orientation = portrait

# (bool) 全屏模式
fullscreen = 0
