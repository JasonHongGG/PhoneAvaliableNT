import re
import time
from functools import wraps
from typing import List, Dict
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.errors import PageDisconnectedError, BrowserConnectError
from app.interfaces import Scraper
from app.models import PhoneNumber

def auto_reconnect_browser(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (PageDisconnectedError, BrowserConnectError) as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 檢測到瀏覽器連線斷開 ({e.__class__.__name__})，正在重新啟動瀏覽器...")
            try:
                self.close()
            except Exception:
                pass
            self._init_browser()
            return func(self, *args, **kwargs)
    return wrapper

class SmspvaScraper(Scraper):
    def __init__(self):
        self._init_browser()

    def _init_browser(self):
        co = ChromiumOptions()
        co.headless(True)  # 無頭模式，不干擾使用者
        self.page = ChromiumPage(co)
        self.url = 'https://smspva.com/free-phone-numbers'

    @auto_reconnect_browser
    def fetch_new_numbers(self, seen_numbers: Dict[str, dict]) -> List[PhoneNumber]:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 正在檢查新號碼...")
        self.page.get(self.url)
        time.sleep(3)  # 等待 Vue 渲染
        
        ul = self.page.ele('.free_numbers_number_list')
        if not ul:
            print("未找到號碼列表元素。")
            return []

        items = ul.children()
        new_phones: List[PhoneNumber] = []
        
        for item in items:
            text = item.text
            if "receive free sms" not in text.lower():
                continue
                
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if not lines:
                continue
                
            number = lines[0]
            country = "Unknown"
            added_line = ""
            
            for line in lines:
                if line.startswith("Country:"):
                    country = line.replace("Country:", "").strip()
                elif line.startswith("Added:"):
                    added_line = line
                    
            # 如果已經看過這個號碼，跳過
            if number in seen_numbers:
                continue
                
            # 檢查是否在一天內 (包含 hour, minute, second 或是 Just now)
            if added_line:
                date_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', added_line)
                if date_match:
                    date_str = date_match.group(1)
                    relative_time = added_line[date_match.end():].strip()
                    
                    is_within_a_day = re.search(r'(hour|minute|second)s?\s+ago', relative_time, re.IGNORECASE) or "just now" in relative_time.lower()
                    
                    if is_within_a_day:
                        link_elem = item.ele('tag:a')
                        href = link_elem.attr('href') if link_elem else ""
                        full_link = href if href.startswith('http') else (f"https://smspva.com{href}" if href else "")
                        
                        phone = PhoneNumber(
                            number=number,
                            country=country,
                            link=full_link,
                            added_time=date_str,
                            relative_time=relative_time,
                            discovered_at=time.strftime('%Y-%m-%d %H:%M:%S')
                        )
                        new_phones.append(phone)
                        
        return new_phones

    def close(self):
        """Close the browser instance"""
        self.page.quit()
