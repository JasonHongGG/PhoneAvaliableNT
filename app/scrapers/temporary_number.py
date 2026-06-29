import re
import time
from datetime import datetime, timedelta
from typing import List, Dict
from app.core.interfaces import Scraper
from app.core.models import PhoneNumber
from app.core.browser import BrowserManager
from app.scrapers.base import auto_reconnect_browser
from app.scrapers.factory import ScraperFactory

def _parse_relative_time_to_timedelta(relative_time_str: str) -> timedelta:
    """將相對時間字串 (例如: 21h ago) 轉換成 timedelta"""
    rt_lower = relative_time_str.lower().strip()
    if "just now" in rt_lower:
        return timedelta(seconds=0)
        
    match = re.search(r'(\d+)\s*([a-z]+)', rt_lower)
    if not match:
        return timedelta(seconds=0)
        
    val = int(match.group(1))
    unit = match.group(2)
    
    if unit.startswith('h'):
        return timedelta(hours=val)
    elif unit.startswith('m') and 'mo' not in unit: # min, mins, minute, minutes
        return timedelta(minutes=val)
    elif unit.startswith('s'):
        return timedelta(seconds=val)
    elif unit.startswith('d'):
        return timedelta(days=val)
    elif unit.startswith('w'):
        return timedelta(weeks=val)
    return timedelta(seconds=0)

@ScraperFactory.register("temporary_number")
class TemporaryNumberScraper(Scraper):
    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.url = 'https://temporarynumber.com/en#numbers'

    @auto_reconnect_browser
    def fetch_new_numbers(self, seen_numbers: Dict[str, dict]) -> List[PhoneNumber]:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 正在檢查 temporarynumber.com 新號碼...")
        page = self.browser_manager.get_page()
        page.get(self.url)
        time.sleep(3)  # 等待渲染
        
        # 尋找號碼列表的 grid 容器
        grid_container = page.ele('xpath://div[contains(@class, "grid-cols-1") and contains(@class, "md:grid-cols-2")]')
        if not grid_container:
            print("未找到 temporarynumber.com 的號碼列表元素。")
            return []

        items = grid_container.children()
        new_phones: List[PhoneNumber] = []
        now = datetime.now()
        
        for item in items:
            a_tag = item.ele('tag:a')
            if not a_tag:
                continue

            # 從 <a> 標籤取得 href
            href = a_tag.attr('href')
            full_link = href if href.startswith('http') else f"https://temporarynumber.com{href}"
            
            # 尋找國家
            country = "Unknown"
            # 尋找相對時間 (如 21h ago, 5 mins ago)
            relative_time = ""
            number = ""
            
            # 根據結構與 class 抓取資料
            try:
                # 取得所有的 text-text-secondary (第一個通常是國家名稱)
                secondary_spans = item.eles('.text-text-secondary')
                if secondary_spans:
                    country = secondary_spans[0].text
                
                # 取得電話號碼
                p_elem = item.ele('tag:p')
                number = p_elem.text.replace('\n', '').replace(' ', '')
                if not number.startswith('+'):
                    number = '+' + number
                    
            except Exception as e:
                print(f"解析項目結構時發生錯誤: {e}")
                continue

            # 解析相對時間
            text = item.text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for i, line in enumerate(lines):
                if "added" in line.lower() and i + 1 < len(lines):
                    # 有些格式可能是 Added \n 21h ago
                    relative_time = lines[i+1]
                    break
                elif line.lower().startswith("added "):
                    # 也有可能是同在一行 Added 21h ago
                    relative_time = line[6:].strip()
                    break

            if not relative_time:
                # 若抓不到，用正則備用
                time_match = re.search(r'(\d+\s*(?:h|m|s|min|mins|hour|hours|day|days)\s*ago|just now)', text, re.IGNORECASE)
                if time_match:
                    relative_time = time_match.group(1)

            # 如果這個號碼已經通知過了就跳過
            if number in seen_numbers:
                continue

            # 判斷是否在 24 小時內
            is_within_a_day = False
            if relative_time:
                rt_lower = relative_time.lower()
                if re.search(r'(h|m|s|min|hour|second)', rt_lower) and not re.search(r'(d|day|days)', rt_lower):
                    is_within_a_day = True
                elif "just now" in rt_lower:
                    is_within_a_day = True

            if is_within_a_day:
                # 推算 added_time
                td = _parse_relative_time_to_timedelta(relative_time)
                added_time_dt = now - td
                added_time_str = added_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                
                phone = PhoneNumber(
                    number=number,
                    country=country,
                    link=full_link,
                    added_time=added_time_str,
                    relative_time=relative_time,
                    discovered_at=now.strftime('%Y-%m-%d %H:%M:%S')
                )
                new_phones.append(phone)
                
        return new_phones
