from typing import List
from app.interfaces import Notifier
from app.models import PhoneNumber
from app.config import Config
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)

class ConsoleNotifier(Notifier):
    def notify(self, phone: PhoneNumber) -> None:
        print(f"[{phone.discovered_at}] 終端機通知 - 發現新號碼: {phone.number} ({phone.country}) - 於 {phone.relative_time} 加入")

class LineNotifier(Notifier):
    def __init__(self, channel_access_token: str = Config.LINE_CHANNEL_ACCESS_TOKEN, target_id: str = None):
        self.target_id = target_id or Config.LINE_GROUP_ID or Config.LINE_USER_ID
        self.configuration = None
        if channel_access_token:
            self.configuration = Configuration(access_token=channel_access_token)

    def notify(self, phone: PhoneNumber) -> None:
        if not self.configuration or not self.target_id:
            print("LINE Bot 尚未設定 (請檢查 .env 的 LINE_GROUP_ID 或 LINE_USER_ID)，略過 LINE 通知。")
            return
            
        try:
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=self.target_id,
                        messages=[TextMessage(text=f"新免費號碼可用！\n國家: {phone.country}\n號碼: {phone.number}")]
                    )
                )
                print("LINE 通知發送成功！")
        except Exception as e:
            print(f"LINE 通知發送失敗: {e}")

class CompositeNotifier(Notifier):
    def __init__(self, notifiers: List[Notifier]):
        self.notifiers = notifiers

    def notify(self, phone: PhoneNumber) -> None:
        for notifier in self.notifiers:
            try:
                notifier.notify(phone)
            except Exception as e:
                print(f"Notifier {notifier.__class__.__name__} 發送失敗: {e}")
