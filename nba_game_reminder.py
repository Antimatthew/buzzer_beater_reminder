#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NBA压哨绝杀球提醒系统
监控NBA比赛，在比赛最后一分钟且分差小于5分时发送桌面通知
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import re
from datetime import datetime
import json
import os

# 配置日志（需要在导入plyer之前配置，以便记录警告）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nba_reminder.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 尝试导入plyer，如果失败则使用备用方案
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logger.warning("plyer库未安装，桌面通知功能将不可用。请运行: pip install plyer")


class NBAGameReminder:
    """NBA比赛提醒类"""
    
    def __init__(self):
        self.url = "https://nba.hupu.com/games"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.notified_games = set()  # 记录已提醒的比赛
        self.state_file = 'nba_reminder_state.json'  # 保存状态的JSON文件
        
        # 加载之前的状态
        self.load_state()
        
        # 配置参数
        self.TIME_THRESHOLD = 120  # 剩余时间阈值（秒），2分钟
        self.SCORE_DIFF_THRESHOLD = 5  # 分差阈值
        
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
    
    def parse_time(self, time_str):
        """解析比赛剩余时间（格式如 '1:23', '0:45', 'Q4' 等）"""
        if not time_str:
            return None
        
        time_str = time_str.strip()
        
        # 匹配分钟:秒格式（如 "1:23", "0:45"）
        time_pattern = r'(\d+):(\d+)'
        match = re.match(time_pattern, time_str)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return minutes * 60 + seconds
        
        # 如果只是节次信息（如 "Q4", "OT1"），返回None表示无法确定具体时间
        return None
    
    def parse_period(self, period_str):
        """解析比赛节次（如 'Q4', 'OT1', 'OT2' 等）"""
        if not period_str:
            return None
        
        period_str = period_str.strip().upper()
        
        # 第四节
        if 'Q4' in period_str or '第四节' in period_str:
            return 'Q4'
        # 加时赛
        elif 'OT' in period_str or '加时' in period_str:
            return 'OT'
        # 其他节次
        elif 'Q1' in period_str or 'Q2' in period_str or 'Q3' in period_str:
            return None
        
        return None
    
    def parse_game_info(self, html):
        """解析HTML，提取比赛信息"""
        games = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 虎扑NBA比赛结构：每个比赛在 <div class="list_box"> 中
            game_boxes = soup.find_all('div', class_='list_box')
            
            logger.info(f"找到 {len(game_boxes)} 个比赛盒子")
            
            # 解析每个比赛盒子
            for box in game_boxes:
                try:
                    game_info = self.extract_game_data_from_box(box)
                    if game_info and game_info.get('score1') is not None:
                        games.append(game_info)
                except Exception as e:
                    logger.debug(f"解析单个比赛盒子失败: {e}")
                    continue
            
            # 如果仍然没有找到比赛，尝试备用方法
            if not games:
                logger.warning("未能从页面中找到比赛数据，可能需要检查网页结构")
            
        except Exception as e:
            logger.error(f"解析HTML失败: {e}")
        
        return games
    
    def extract_game_data_from_box(self, box):
        """从比赛盒子中提取比赛数据（针对虎扑网站结构）"""
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
            # 提取球队信息和比分
            team_vs_a = box.find('div', class_='team_vs_a')
            if not team_vs_a:
                return None
            
            # 提取第一支球队
            team_a_1 = team_vs_a.find('div', class_='team_vs_a_1')
            if team_a_1:
                # 球队名称 - 在 div.txt > span > a 中
                txt_div = team_a_1.find('div', class_='txt')
                if txt_div:
                    team1_link = txt_div.find('a')
                    if team1_link:
                        game_info['team1'] = team1_link.get_text(strip=True)
                    
                    # 比分 - 在 span.num 中
                    score_elem = txt_div.find('span', class_='num')
                    if score_elem:
                        try:
                            game_info['score1'] = int(score_elem.get_text(strip=True))
                        except ValueError:
                            pass
            
            # 提取第二支球队
            team_a_2 = team_vs_a.find('div', class_='team_vs_a_2')
            if team_a_2:
                # 球队名称 - 在 div.txt > span > a 中
                txt_div = team_a_2.find('div', class_='txt')
                if txt_div:
                    team2_link = txt_div.find('a')
                    if team2_link:
                        game_info['team2'] = team2_link.get_text(strip=True)
                    
                    # 比分 - 在 span.num 中
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
                    # 提取状态文本（如 "进行中"）
                    status_text = status_elem.get_text(strip=True)
                    game_info['status'] = status_text
                    
                    # 提取节次和剩余时间
                    # 格式可能是："第二节结束" 或 "第一节剩4:45"
                    period_time_p = status_elem.find('p')
                    if period_time_p:
                        period_time_text = period_time_p.get_text(strip=True)
                        
                        # 提取节次
                        period_pattern = r'(第[一二三四]节|加时(?:赛)?)'
                        period_match = re.search(period_pattern, period_time_text)
                        if period_match:
                            period_str = period_match.group(0)
                            if '第四节' in period_str:
                                game_info['period'] = 'Q4'
                            elif '第三节' in period_str:
                                game_info['period'] = 'Q3'
                            elif '第二节' in period_str:
                                game_info['period'] = 'Q2'
                            elif '第一节' in period_str:
                                game_info['period'] = 'Q1'
                            elif '加时' in period_str:
                                game_info['period'] = 'OT'
                        
                        # 提取剩余时间（格式："剩4:45"）
                        time_pattern = r'剩\s*(\d{1,2}):(\d{2})'
                        time_match = re.search(time_pattern, period_time_text)
                        if time_match:
                            minutes = int(time_match.group(1))
                            seconds = int(time_match.group(2))
                            if 0 <= minutes <= 12 and 0 <= seconds < 60:
                                game_info['time_remaining'] = minutes * 60 + seconds
                        elif '结束' in period_time_text:
                            # 如果是"结束"，剩余时间为0
                            game_info['time_remaining'] = 0
            
            # 如果至少有了比分，返回游戏信息
            if game_info.get('score1') is not None and game_info.get('score2') is not None:
                return game_info
        
        except Exception as e:
            logger.debug(f"提取比赛数据出错: {e}")
        
        return None
    
    def extract_game_data(self, element):
        """从单个元素中提取比赛数据（备用方法）"""
        # 这个方法保留作为备用，但现在主要使用 extract_game_data_from_box
        return self.extract_game_data_from_box(element)
    
    def parse_games_alternative(self, soup):
        """备用解析方法：尝试通过API或其他方式获取数据"""
        games = []
        
        # 尝试查找JSON数据
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # 查找包含比赛数据的JSON
                json_match = re.search(r'var\s+gameData\s*=\s*(\{.*?\})', script.string, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group(1))
                        # 根据实际JSON结构调整
                        logger.info("找到JSON格式的比赛数据")
                    except:
                        pass
        
        return games
    
    def check_game_condition(self, game):
        """检查比赛是否满足提醒条件"""
        # 必须是第四节或加时赛
        period = self.parse_period(game.get('period', ''))
        if period not in ['Q4', 'OT']:
            return False
        
        # 剩余时间必须在阈值内
        time_remaining = game.get('time_remaining')
        if time_remaining is None or time_remaining > self.TIME_THRESHOLD:
            return False
        
        # 分差必须小于阈值
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
        # 使用球队名称和比分生成唯一ID
        team1 = game.get('team1', 'Team1')
        team2 = game.get('team2', 'Team2')
        score1 = game.get('score1', 0)
        score2 = game.get('score2', 0)
        period = game.get('period', '')
        time_remaining = game.get('time_remaining', 0)
        
        return f"{team1}_{team2}_{score1}_{score2}_{period}_{time_remaining}"
    
    def send_notification(self, game):
        """发送桌面通知"""
        team1 = game.get('team1', '球队1')
        team2 = game.get('team2', '球队2')
        score1 = game.get('score1', 0)
        score2 = game.get('score2', 0)
        period = game.get('period', '')
        time_remaining = game.get('time_remaining', 0)
        
        # 格式化时间显示
        minutes = time_remaining // 60
        seconds = time_remaining % 60
        time_str = f"{minutes}:{seconds:02d}" if time_remaining > 0 else "最后时刻"
        
        title = "⚡ NBA压哨绝杀提醒 ⚡"
        message = f"{team1} {score1} - {score2} {team2}\n"
        message += f"{period} | 剩余时间: {time_str}\n"
        message += f"分差: {abs(score1 - score2)}分"
        
        if not PLYER_AVAILABLE:
            # 如果plyer不可用，只打印到控制台
            logger.warning(f"通知功能不可用，但检测到关键时刻: {title}")
            logger.warning(f"{message}")
            return False
        
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=10,
                app_name="NBA压哨绝杀提醒"
            )
            logger.info(f"已发送通知: {team1} vs {team2}")
            return True
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return False
    
    def display_game_info(self, game):
        """格式化显示比赛信息"""
        team1 = game.get('team1', '球队1') or '未知球队1'
        team2 = game.get('team2', '球队2') or '未知球队2'
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
        return f"  {team1} {score1} - {score2} {team2} | {period} | 剩余: {time_str} | 分差: {score_diff}分"
    
    def process_games(self, games):
        """处理比赛列表，检查并发送提醒"""
        current_time = datetime.now().strftime("%H:%M:%S")
        logger.info(f"[{current_time}] 检查 {len(games)} 场比赛")
        
        # 显示所有找到的比赛信息
        if games:
            logger.info("=" * 60)
            logger.info("正在进行的比赛:")
            for i, game in enumerate(games, 1):
                game_info = self.display_game_info(game)
                logger.info(f"{i}.{game_info}")
            logger.info("=" * 60)
        
        for game in games:
            if self.check_game_condition(game):
                game_id = self.get_game_id(game)
                
                # 避免重复提醒（同一场比赛在相同状态下）
                if game_id not in self.notified_games:
                    logger.info("🎯 发现满足提醒条件的比赛！")
                    self.send_notification(game)
                    self.notified_games.add(game_id)
                    self.save_state()
                    
                    team1 = game.get('team1', '球队1') or '未知球队1'
                    team2 = game.get('team2', '球队2') or '未知球队2'
                    logger.info(f"✓ 提醒已发送: {team1} vs {team2}")
                else:
                    logger.debug(f"比赛 {game.get('team1')} vs {game.get('team2')} 已提醒过，跳过")
    
    def run(self):
        """运行主循环"""
        logger.info("=" * 50)
        logger.info("NBA压哨绝杀球提醒系统已启动")
        logger.info(f"监控条件: 第四节/加时赛 | 剩余时间 ≤ {self.TIME_THRESHOLD}秒 | 分差 < {self.SCORE_DIFF_THRESHOLD}分")
        logger.info("=" * 50)
        logger.info("按 Ctrl+C 退出程序")
        logger.info("=" * 50)
        
        try:
            while True:
                try:
                    # 获取比赛数据
                    html = self.fetch_games()
                    if html:
                        # 解析比赛信息
                        games = self.parse_game_info(html)
                        
                        if games:
                            logger.info(f"✓ 成功获取 {len(games)} 场比赛数据")
                            self.process_games(games)
                        else:
                            logger.warning("⚠ 未找到比赛数据，可能是页面结构变化或当前没有比赛")
                            logger.info("提示: 请检查 debug_page.html 文件查看获取到的HTML内容")
                    
                    # 等待60秒后再次检查
                    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 等待60秒后再次检查...")
                    time.sleep(60)
                    
                except KeyboardInterrupt:
                    raise  # 重新抛出，让外层捕获
                except Exception as e:
                    logger.error(f"单次检查出错: {e}", exc_info=True)
                    logger.info("60秒后重试...")
                    time.sleep(60)
                    
        except KeyboardInterrupt:
            logger.info("\n程序被用户中断")
        except Exception as e:
            logger.error(f"程序运行出错: {e}", exc_info=True)
        finally:
            self.save_state()
            logger.info("程序已退出，状态已保存")


def main():
    """主函数"""
    reminder = NBAGameReminder()
    reminder.run()


if __name__ == "__main__":
    main()

