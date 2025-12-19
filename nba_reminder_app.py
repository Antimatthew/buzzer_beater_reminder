#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NBA压哨绝杀球提醒系统 - 移动应用版
基于KivyMD开发的Android/iOS应用
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import re
from datetime import datetime
import json
import os
from threading import Thread

# KivyMD imports
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.utils import platform
from kivy.core.text import LabelBase
import sys

# KivyMD imports
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.theming import ThemeManager

# 移动平台通知
try:
    if platform == 'android':
        from jnius import autoclass
        from android.runnable import run_on_ui_thread
        from android import api_version
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Notification = autoclass('android.app.Notification')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        Context = autoclass('android.content.Context')
        PendingIntent = autoclass('android.app.PendingIntent')
        Intent = autoclass('android.content.Intent')
        ANDROID_AVAILABLE = True
    else:
        ANDROID_AVAILABLE = False
except:
    ANDROID_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nba_reminder.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class NBAGameReminderCore:
    """NBA比赛提醒核心逻辑类（复用原有代码）"""
    
    def __init__(self):
        self.url = "https://nba.hupu.com/games"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.notified_games = set()
        self.state_file = 'nba_reminder_state.json'
        self.load_state()
        self.TIME_THRESHOLD = 120  # 2分钟
        self.SCORE_DIFF_THRESHOLD = 5  # 5分
        
    def load_state(self):
        """加载之前提醒过的比赛状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.notified_games = set(data.get('notified_games', []))
                    logger.info(f"已加载 {len(self.notified_games)} 场已提醒的比赛记录")
            except Exception as e:
                logger.error(f"加载状态文件失败: {e}")
    
    def save_state(self):
        """保存提醒状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'notified_games': list(self.notified_games),
                    'last_update': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态文件失败: {e}")
    
    def fetch_games(self):
        """从虎扑获取NBA比赛数据"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"获取比赛数据失败: {e}")
            return None
    
    def parse_period(self, period_str):
        """解析比赛节次"""
        if not period_str:
            return None
        period_str = period_str.strip().upper()
        if 'Q4' in period_str or '第四节' in period_str:
            return 'Q4'
        elif 'OT' in period_str or '加时' in period_str:
            return 'OT'
        return None
    
    def parse_game_info(self, html):
        """解析HTML，提取比赛信息"""
        games = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            game_boxes = soup.find_all('div', class_='list_box')
            logger.info(f"找到 {len(game_boxes)} 个比赛盒子")
            
            for box in game_boxes:
                try:
                    game_info = self.extract_game_data_from_box(box)
                    if game_info and game_info.get('score1') is not None:
                        games.append(game_info)
                except Exception as e:
                    logger.debug(f"解析单个比赛盒子失败: {e}")
                    continue
        except Exception as e:
            logger.error(f"解析HTML失败: {e}")
        return games
    
    def extract_game_data_from_box(self, box):
        """从比赛盒子中提取比赛数据"""
        game_info = {
            'team1': None,
            'team2': None,
            'score1': None,
            'score2': None,
            'period': None,
            'time_remaining': None,
            'status': None
        }
        
        try:
            team_vs_a = box.find('div', class_='team_vs_a')
            if not team_vs_a:
                return None
            
            # 提取第一支球队
            team_a_1 = team_vs_a.find('div', class_='team_vs_a_1')
            if team_a_1:
                txt_div = team_a_1.find('div', class_='txt')
                if txt_div:
                    team1_link = txt_div.find('a')
                    if team1_link:
                        game_info['team1'] = team1_link.get_text(strip=True)
                    score_elem = txt_div.find('span', class_='num')
                    if score_elem:
                        try:
                            game_info['score1'] = int(score_elem.get_text(strip=True))
                        except ValueError:
                            pass
            
            # 提取第二支球队
            team_a_2 = team_vs_a.find('div', class_='team_vs_a_2')
            if team_a_2:
                txt_div = team_a_2.find('div', class_='txt')
                if txt_div:
                    team2_link = txt_div.find('a')
                    if team2_link:
                        game_info['team2'] = team2_link.get_text(strip=True)
                    score_elem = txt_div.find('span', class_='num')
                    if score_elem:
                        try:
                            game_info['score2'] = int(score_elem.get_text(strip=True))
                        except ValueError:
                            pass
            
            # 提取比赛状态和时间信息
            team_vs_c = box.find('div', class_='team_vs_c')
            if team_vs_c:
                status_elem = team_vs_c.find('span', class_='b')
                if status_elem:
                    status_text = status_elem.get_text(strip=True)
                    game_info['status'] = status_text
                    
                    period_time_p = status_elem.find('p')
                    if period_time_p:
                        period_time_text = period_time_p.get_text(strip=True)
                        
                        period_pattern = r'(第[一二三四]节|加时(?:赛)?)'
                        period_match = re.search(period_pattern, period_time_text)
                        if period_match:
                            period_str = period_match.group(0)
                            if '第四节' in period_str:
                                game_info['period'] = 'Q4'
                            elif '加时' in period_str:
                                game_info['period'] = 'OT'
                        
                        time_pattern = r'剩\s*(\d{1,2}):(\d{2})'
                        time_match = re.search(time_pattern, period_time_text)
                        if time_match:
                            minutes = int(time_match.group(1))
                            seconds = int(time_match.group(2))
                            if 0 <= minutes <= 12 and 0 <= seconds < 60:
                                game_info['time_remaining'] = minutes * 60 + seconds
                        elif '结束' in period_time_text:
                            game_info['time_remaining'] = 0
            
            if game_info.get('score1') is not None and game_info.get('score2') is not None:
                return game_info
        except Exception as e:
            logger.debug(f"提取比赛数据出错: {e}")
        return None
    
    def check_game_condition(self, game):
        """检查比赛是否满足提醒条件"""
        period = self.parse_period(game.get('period', ''))
        if period not in ['Q4', 'OT']:
            return False
        
        time_remaining = game.get('time_remaining')
        if time_remaining is None or time_remaining > self.TIME_THRESHOLD:
            return False
        
        score1 = game.get('score1')
        score2 = game.get('score2')
        if score1 is None or score2 is None:
            return False
        
        score_diff = abs(score1 - score2)
        if score_diff >= self.SCORE_DIFF_THRESHOLD:
            return False
        
        return True
    
    def get_game_id(self, game):
        """生成比赛唯一标识"""
        team1 = game.get('team1', 'Team1')
        team2 = game.get('team2', 'Team2')
        score1 = game.get('score1', 0)
        score2 = game.get('score2', 0)
        period = game.get('period', '')
        time_remaining = game.get('time_remaining', 0)
        return f"{team1}_{team2}_{score1}_{score2}_{period}_{time_remaining}"


class NotificationHelper:
    """移动平台通知助手"""
    
    @staticmethod
    def send_notification(title, message, game_info=None):
        """发送移动平台通知"""
        if platform == 'android' and ANDROID_AVAILABLE:
            NotificationHelper._send_android_notification(title, message, game_info)
        else:
            # iOS或其他平台可以在这里添加
            logger.info(f"通知: {title} - {message}")
    
    @staticmethod
    def _send_android_notification(title, message, game_info=None):
        """发送Android通知"""
        try:
            context = PythonActivity.mActivity.getApplicationContext()
            notification_service = context.getSystemService(Context.NOTIFICATION_SERVICE)
            
            # 创建通知渠道（Android 8.0+需要）
            if api_version >= 26:
                channel_id = "nba_reminder_channel"
                channel_name = "NBA提醒"
                channel = NotificationChannel(
                    channel_id,
                    channel_name,
                    NotificationManager.IMPORTANCE_HIGH
                )
                channel.setDescription("NBA压哨绝杀提醒通知")
                notification_service.createNotificationChannel(channel)
            else:
                channel_id = None
            
            # 创建通知
            builder = Notification.Builder(context)
            if channel_id:
                builder.setChannelId(channel_id)
            
            builder.setContentTitle(title)
            builder.setContentText(message)
            builder.setSmallIcon(context.getApplicationInfo().icon)
            builder.setAutoCancel(True)
            builder.setPriority(Notification.PRIORITY_HIGH)
            
            # 创建点击通知的Intent
            intent = Intent(context, PythonActivity)
            pending_intent = PendingIntent.getActivity(
                context, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT
            )
            builder.setContentIntent(pending_intent)
            
            notification = builder.build()
            notification_service.notify(1, notification)
            logger.info("Android通知已发送")
        except Exception as e:
            logger.error(f"发送Android通知失败: {e}")


class GameListCard(MDCard):
    """比赛信息卡片"""
    pass


class MainScreen(MDScreen):
    """主屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 主布局
        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # 顶部工具栏
        toolbar = MDTopAppBar(
            title="NBA压哨绝杀提醒",
            elevation=2
        )
        main_layout.add_widget(toolbar)
        
        # 控制面板
        control_panel = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120)
        )
        
        # 监控开关
        switch_layout = MDBoxLayout(orientation='horizontal', spacing=dp(10))
        switch_label = MDLabel(
            text="开启监控",
            size_hint_x=0.7
        )
        # 使用Kivy原生的Switch（KivyMD 1.2.0没有MDSwitch）
        from kivy.uix.switch import Switch
        self.monitor_switch = Switch()
        self.monitor_switch.bind(active=self.on_switch_active)
        switch_layout.add_widget(switch_label)
        switch_layout.add_widget(self.monitor_switch)
        control_panel.add_widget(switch_layout)
        
        # 状态标签
        self.status_label = MDLabel(
            text="状态: 未启动",
            theme_text_color="Secondary"
        )
        control_panel.add_widget(self.status_label)
        
        # 刷新按钮
        refresh_btn = MDRaisedButton(
            text="立即刷新",
            on_press=self.refresh_games
        )
        control_panel.add_widget(refresh_btn)
        
        main_layout.add_widget(control_panel)
        
        # 比赛列表
        scroll = MDScrollView()
        self.games_list = MDList(spacing=dp(10))
        scroll.add_widget(self.games_list)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def set_app(self, app):
        """设置应用引用"""
        self.app = app
    
    def on_switch_active(self, instance, value):
        """监控开关切换"""
        if value:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.status_label.text = "状态: 监控中..."
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.status_label.text = "状态: 已停止"
        logger.info("监控已停止")
    
    def _monitor_loop(self):
        """监控循环（在后台线程运行）"""
        while self.is_monitoring:
            try:
                Clock.schedule_once(lambda dt: self.refresh_games(None))
                time.sleep(60)  # 每60秒检查一次
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                time.sleep(60)
    
    def refresh_games(self, instance):
        """刷新比赛列表"""
        def update_ui(games):
            """更新UI（必须在主线程）"""
            self.games_list.clear_widgets()
            
            if not games:
                item = OneLineListItem(text="暂无比赛数据")
                self.games_list.add_widget(item)
                return
            
            for game in games:
                team1 = game.get('team1', '球队1') or '未知'
                team2 = game.get('team2', '球队2') or '未知'
                score1 = game.get('score1', 0)
                score2 = game.get('score2', 0)
                period = game.get('period', '未知')
                time_remaining = game.get('time_remaining')
                
                if time_remaining is not None:
                    minutes = time_remaining // 60
                    seconds = time_remaining % 60
                    time_str = f"{minutes}:{seconds:02d}"
                else:
                    time_str = "未知"
                
                score_diff = abs(score1 - score2)
                
                # 检查是否满足提醒条件
                is_critical = False
                if self.app:
                    is_critical = self.app.reminder_core.check_game_condition(game)
                
                # 创建卡片
                card = MDCard(
                    orientation='vertical',
                    padding=dp(15),
                    spacing=dp(5),
                    size_hint_y=None,
                    height=dp(100),
                    md_bg_color=(1, 0.8, 0.8, 1) if is_critical else (1, 1, 1, 1)
                )
                
                # 比赛信息
                game_text = f"{team1} {score1} - {score2} {team2}"
                game_label = MDLabel(
                    text=game_text,
                    theme_text_color="Primary",
                    bold=True
                )
                card.add_widget(game_label)
                
                info_text = f"{period} | 剩余: {time_str} | 分差: {score_diff}分"
                if is_critical:
                    info_text += " ⚠️ 关键时刻！"
                info_label = MDLabel(
                    text=info_text,
                    theme_text_color="Secondary",
                    font_style="Caption"
                )
                card.add_widget(info_label)
                
                self.games_list.add_widget(card)
                
                # 发送通知
                if is_critical and self.app:
                    game_id = self.app.reminder_core.get_game_id(game)
                    if game_id not in self.app.reminder_core.notified_games:
                        title = "⚡ NBA压哨绝杀提醒 ⚡"
                        message = f"{team1} {score1} - {score2} {team2}\n{period} | 剩余: {time_str} | 分差: {score_diff}分"
                        NotificationHelper.send_notification(title, message, game)
                        self.app.reminder_core.notified_games.add(game_id)
                        self.app.reminder_core.save_state()
        
        # 在后台线程获取数据
        def fetch_and_update():
            if not self.app:
                return
            
            html = self.app.reminder_core.fetch_games()
            if html:
                games = self.app.reminder_core.parse_game_info(html)
                Clock.schedule_once(lambda dt: update_ui(games))
                self.status_label.text = f"状态: 已更新 ({len(games)}场比赛)"
            else:
                Clock.schedule_once(lambda dt: self.status_label.setter('text')('状态: 获取失败'))
        
        Thread(target=fetch_and_update, daemon=True).start()


class NBAReminderApp(MDApp):
    """NBA提醒应用主类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reminder_core = NBAGameReminderCore()
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        # 注册中文字体（在Windows上）
        if platform == 'win':
            try:
                # 获取Windows字体目录
                fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
                yahei_font = os.path.join(fonts_dir, 'msyh.ttc')  # 微软雅黑
                simhei_font = os.path.join(fonts_dir, 'simhei.ttf')  # 黑体
                simsun_font = os.path.join(fonts_dir, 'simsun.ttc')  # 宋体
                
                # 按优先级尝试注册字体
                font_registered = False
                for font_path, font_name in [(yahei_font, 'Chinese'), 
                                             (simhei_font, 'Chinese'),
                                             (simsun_font, 'Chinese')]:
                    if os.path.exists(font_path):
                        try:
                            LabelBase.register(name=font_name, fn_regular=font_path)
                            logger.info(f"已注册中文字体: {font_path}")
                            font_registered = True
                            break
                        except Exception as e:
                            logger.warning(f"注册字体失败 {font_path}: {e}")
                            continue
                
                # 如果注册成功，更新字体样式
                if font_registered:
                    self.theme_cls.font_styles.update({
                        'H1': ['Chinese', 96, False, -1.5],
                        'H2': ['Chinese', 60, False, -0.5],
                        'H3': ['Chinese', 48, False, 0],
                        'H4': ['Chinese', 34, False, 0.25],
                        'H5': ['Chinese', 24, False, 0],
                        'H6': ['Chinese', 20, False, 0.15],
                        'Subtitle1': ['Chinese', 16, False, 0.15],
                        'Subtitle2': ['Chinese', 14, False, 0.1],
                        'Body1': ['Chinese', 16, False, 0.5],
                        'Body2': ['Chinese', 14, False, 0.25],
                        'Button': ['Chinese', 14, True, 1.25],
                        'Caption': ['Chinese', 12, False, 0.4],
                        'Overline': ['Chinese', 10, True, 1.5],
                    })
            except Exception as e:
                logger.warning(f"设置中文字体失败: {e}，将使用默认字体")
    
    def build(self):
        """构建应用界面"""
        screen_manager = MDScreenManager()
        main_screen = MainScreen(name='main')
        main_screen.set_app(self)
        screen_manager.add_widget(main_screen)
        return screen_manager
    
    def on_start(self):
        """应用启动时"""
        logger.info("NBA提醒应用已启动")
    
    def on_stop(self):
        """应用停止时"""
        self.reminder_core.save_state()
        logger.info("NBA提醒应用已停止")


if __name__ == "__main__":
    # 运行应用
    NBAReminderApp().run()

