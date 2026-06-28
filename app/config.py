import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CHECK_INTERVAL_SECONDS = 300  # 檢查間隔：5分鐘
    DATA_FILE = "seen_numbers.json"
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_USER_ID = os.getenv('LINE_USER_ID')
