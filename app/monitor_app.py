import time
from typing import List
from app.core.interfaces import Storage, Scraper, Notifier
from app.core.config import Config
from app.core.browser import BrowserManager

class MonitorApp:
    def __init__(self, scrapers: List[Scraper], storage: Storage, notifier: Notifier, browser_manager: BrowserManager):
        self.scrapers = scrapers
        self.storage = storage
        self.notifier = notifier
        self.browser_manager = browser_manager
        self.seen = self.storage.load_seen()

    def run(self):
        print("啟動免費號碼提醒器...")
        print(f"已載入 {len(self.seen)} 個歷史號碼。")
        print("請保持此終端機開啟以持續監控，或按下 Ctrl+C 結束。")
        print("-" * 30)
        
        try:
            while True:
                try:
                    self.check_once()
                except Exception as e:
                    print(f"檢查過程中發生錯誤: {e}")
                
                # 等待下一次檢查
                time.sleep(Config.CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\n提醒器已停止。")
        finally:
            if self.browser_manager:
                self.browser_manager.close()

    def check_once(self):
        for scraper in self.scrapers:
            new_phones = scraper.fetch_new_numbers(self.seen)
            
            if new_phones:
                for phone in new_phones:
                    self.notifier.notify(phone)
                    self.seen[phone.number] = phone.to_dict()
                
                self.storage.save_seen(self.seen)
            else:
                print(f"{scraper.__class__.__name__}: 沒有發現新的號碼。")
