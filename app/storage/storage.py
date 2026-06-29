import json
import os
from typing import Dict
from app.core.interfaces import Storage
from app.core.config import Config

class JsonStorage(Storage):
    def __init__(self, file_path: str = Config.DATA_FILE):
        self.file_path = file_path

    def load_seen(self) -> Dict[str, dict]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # 遷移舊資料，將陣列轉換成字典
                        return {num: {} for num in data}
                    return data
            except Exception:
                return {}
        return {}

    def save_seen(self, seen: Dict[str, dict]) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(seen, f, indent=4, ensure_ascii=False)
