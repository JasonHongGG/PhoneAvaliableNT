import time
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.errors import PageDisconnectedError, BrowserConnectError

class BrowserManager:
    def __init__(self):
        self.page = None
        self._init_browser()

    def _init_browser(self):
        co = ChromiumOptions()
        co.headless(True)  # 無頭模式，不干擾使用者
        self.page = ChromiumPage(co)

    def get_page(self) -> ChromiumPage:
        return self.page

    def reconnect(self):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 重新啟動瀏覽器...")
        self.close()
        self._init_browser()

    def close(self):
        if self.page:
            try:
                self.page.quit()
            except Exception:
                pass
            finally:
                self.page = None
