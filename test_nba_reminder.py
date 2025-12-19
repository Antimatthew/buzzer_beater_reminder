#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本 - 快速检查NBA提醒系统是否能正常获取比赛数据
"""

import sys
import io

# 设置标准输出编码为UTF-8（Windows控制台支持）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from nba_game_reminder import NBAGameReminder
import logging

# 设置日志级别为DEBUG以便看到更多信息
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def test():
    """测试函数"""
    print("=" * 60)
    print("开始测试NBA压哨绝杀提醒系统")
    print("=" * 60)
    
    reminder = NBAGameReminder()
    
    print(f"\n正在从 {reminder.url} 获取比赛数据...")
    html = reminder.fetch_games()
    
    if html:
        print(f"[成功] 成功获取HTML数据 (长度: {len(html)} 字符)")
        
        print("\n正在解析比赛信息...")
        games = reminder.parse_game_info(html)
        
        if games:
            print(f"\n[成功] 成功解析到 {len(games)} 场比赛！")
            print("\n" + "=" * 60)
            print("比赛详情:")
            print("=" * 60)
            
            for i, game in enumerate(games, 1):
                game_info = reminder.display_game_info(game)
                print(f"{i}.{game_info}")
                
                # 检查是否满足提醒条件
                if reminder.check_game_condition(game):
                    print(f"   [满足条件] 满足提醒条件！")
            
            print("=" * 60)
            
            # 如果解析的数据不完整，保存HTML用于分析
            if any(not g.get('team1') or not g.get('period') for g in games):
                print("\n[提示] 部分比赛信息不完整（球队名称或节次缺失）")
                print("正在保存HTML用于调试...")
                try:
                    with open('test_debug.html', 'w', encoding='utf-8') as f:
                        f.write(html)
                    print("已保存HTML到 test_debug.html")
                except Exception as e:
                    print(f"保存HTML失败: {e}")
        else:
            print("\n[警告] 未能解析到比赛数据")
            print("\n可能的原因:")
            print("1. 当前没有正在进行的NBA比赛")
            print("2. 虎扑网站页面结构发生变化，需要更新解析逻辑")
            print("3. 网页内容加载方式不同（如JavaScript动态加载）")
            
            # 尝试保存HTML用于分析
            try:
                with open('test_debug.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"\n已保存HTML内容到 test_debug.html，可以打开查看")
            except Exception as e:
                print(f"\n保存HTML失败: {e}")
    else:
        print("\n[错误] 无法获取HTML数据")
        print("\n可能的原因:")
        print("1. 网络连接问题")
        print("2. 虎扑网站无法访问")
        print("3. 网站返回错误")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test()

