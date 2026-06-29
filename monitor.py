from app.storage.storage import JsonStorage
from app.scrapers.factory import ScraperFactory
# 引入特定的爬蟲實作，以觸發 @ScraperFactory.register
import app.scrapers.smspva 
from app.notifiers.notifiers import CompositeNotifier, ConsoleNotifier, LineNotifier
from app.core.browser import BrowserManager
from app.monitor_app import MonitorApp

def main():
    # 1. 建立儲存層 (Storage)
    storage = JsonStorage()
    
    # 2. 建立通知層 (Notifier)，可以同時印在終端機並發送 LINE 通知
    notifier = CompositeNotifier([
        ConsoleNotifier(),
        LineNotifier()
    ])
    
    # 3. 建立共用的瀏覽器管理員
    browser_manager = BrowserManager()

    # 4. 建立爬蟲層 (Scrapers)
    # 這裡可以透過 Factory 建立多個不同的爬蟲
    scrapers = [
        ScraperFactory.create("smspva", browser_manager)
    ]
    
    # 5. 組合並啟動應用程式
    app = MonitorApp(scrapers=scrapers, storage=storage, notifier=notifier, browser_manager=browser_manager)
    app.run()

if __name__ == "__main__":
    main()
