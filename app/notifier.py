from typing import List
from app.interfaces import Notifier
from app.models import PhoneNumber
from app.config import Config
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    FlexMessage,
    FlexContainer
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
            flex_content = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "New Free Number",
                            "weight": "bold",
                            "color": "#1DB446",
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": phone.number,
                            "weight": "bold",
                            "size": "xl",
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": phone.country,
                            "size": "xs",
                            "color": "#aaaaaa",
                            "wrap": True
                        },
                        {
                            "type": "separator",
                            "margin": "xxl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "xxl",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {"type": "text", "text": "Added", "size": "sm", "color": "#555555", "flex": 0},
                                        {"type": "text", "text": phone.added_time, "size": "sm", "color": "#111111", "align": "end"}
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {"type": "text", "text": "Relative", "size": "sm", "color": "#555555", "flex": 0},
                                        {"type": "text", "text": phone.relative_time, "size": "sm", "color": "#111111", "align": "end"}
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {"type": "text", "text": "Discovered", "size": "sm", "color": "#555555", "flex": 0},
                                        {"type": "text", "text": phone.discovered_at, "size": "sm", "color": "#111111", "align": "end"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }

            if phone.link:
                flex_content["footer"] = {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "height": "sm",
                            "action": {
                                "type": "uri",
                                "label": "GO TO SMSPVA",
                                "uri": phone.link
                            }
                        }
                    ],
                    "flex": 0
                }

            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=self.target_id,
                        messages=[FlexMessage(
                            alt_text=f"新免費號碼可用！ ({phone.country} {phone.number})",
                            contents=FlexContainer.from_dict(flex_content)
                        )]
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
