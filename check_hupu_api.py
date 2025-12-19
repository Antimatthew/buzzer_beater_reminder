#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查虎扑是否有API端点"""

import requests
from bs4 import BeautifulSoup
import re
import json

def check_hupu_api():
    """检查虎扑NBA页面是否有API调用"""
    url = "https://nba.hupu.com/games"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print("正在获取虎扑NBA页面...")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        html = response.text
        
        print(f"页面大小: {len(html)} 字符")
        
        # 查找可能的API端点
        print("\n=== 查找API相关关键词 ===")
        
        # 查找包含api/ajax/json的URL
        api_patterns = [
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*ajax[^"\']*)["\']',
            r'["\']([^"\']*json[^"\']*)["\']',
            r'url\s*[:=]\s*["\']([^"\']*api[^"\']*)["\']',
        ]
        
        found_apis = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, html, re.I)
            found_apis.update(matches)
        
        if found_apis:
            print("找到可能的API端点:")
            for api in sorted(found_apis)[:20]:  # 只显示前20个
                if len(api) < 200:  # 过滤太长的
                    print(f"  - {api}")
        else:
            print("未找到明显的API端点")
        
        # 查找script标签中的API调用
        print("\n=== 检查JavaScript中的API调用 ===")
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script')
        
        api_calls = []
        for script in scripts:
            if script.string:
                # 查找fetch, axios, $.ajax等API调用
                if re.search(r'(fetch|axios|\.ajax|XMLHttpRequest)', script.string, re.I):
                    lines = script.string.split('\n')
                    for i, line in enumerate(lines):
                        if re.search(r'(api|ajax|json)', line, re.I):
                            api_calls.append(line.strip()[:100])  # 只取前100字符
        
        if api_calls:
            print("找到可能的API调用:")
            for call in api_calls[:10]:
                print(f"  - {call}")
        else:
            print("未找到明显的API调用")
        
        # 检查是否有内嵌的JSON数据
        print("\n=== 检查内嵌JSON数据 ===")
        json_pattern = r'<script[^>]*>.*?(\{.*?"games?.*?\}).*?</script>'
        json_matches = re.findall(json_pattern, html, re.I | re.DOTALL)
        if json_matches:
            print(f"找到 {len(json_matches)} 个可能的JSON数据块")
            for i, match in enumerate(json_matches[:3]):
                try:
                    data = json.loads(match[:500])  # 只解析前500字符
                    print(f"  JSON {i+1}: {list(data.keys())[:5]}")
                except:
                    print(f"  JSON {i+1}: (无法解析)")
        else:
            print("未找到内嵌JSON数据")
        
        print("\n=== 结论 ===")
        print("虎扑网站主要通过HTML渲染显示数据，未发现明显的公开API端点。")
        print("建议继续使用网页爬虫方式，或考虑使用其他NBA数据API。")
        
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    check_hupu_api()

