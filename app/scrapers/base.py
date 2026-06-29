import time
from functools import wraps
from DrissionPage.errors import PageDisconnectedError, BrowserConnectError

def auto_reconnect_browser(func):
    """
    Decorator for Scraper methods to automatically handle browser disconnections.
    Requires the scraper instance to have a `browser_manager` attribute.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (PageDisconnectedError, BrowserConnectError) as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 檢測到瀏覽器連線斷開 ({e.__class__.__name__})，正在重新啟動瀏覽器...")
            if hasattr(self, 'browser_manager') and self.browser_manager:
                self.browser_manager.reconnect()
                # 重新執行一次
                return func(self, *args, **kwargs)
            else:
                raise
    return wrapper
