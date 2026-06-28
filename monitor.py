from app.storage import JsonStorage
from app.scraper import SmspvaScraper
from app.notifier import CompositeNotifier, ConsoleNotifier, LineNotifier
from app.monitor_app import MonitorApp

def main():
    # 1. 建立儲存層 (Storage)
    storage = JsonStorage()
    
    # 2. 建立通知層 (Notifier)，可以同時印在終端機並發送 LINE 通知
    notifier = CompositeNotifier([
        ConsoleNotifier(),
        LineNotifier()
    ])
    
    # 3. 建立爬蟲層 (Scraper)
    scraper = SmspvaScraper()
    
    # 4. 組合並啟動應用程式
    app = MonitorApp(scraper=scraper, storage=storage, notifier=notifier)
    app.run()

if __name__ == "__main__":
    main()
