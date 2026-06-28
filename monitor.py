import json
import os
import re
import time
from dotenv import load_dotenv
from DrissionPage import ChromiumPage, ChromiumOptions
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)

load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')

configuration = None
if LINE_CHANNEL_ACCESS_TOKEN:
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

DATA_FILE = "seen_numbers.json"
CHECK_INTERVAL_SECONDS = 300  # 檢查間隔：5分鐘

def load_seen():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    # 遷移舊資料，將陣列轉換成字典
                    return {num: {} for num in data}
                return data
        except Exception:
            return {}
    return {}

def save_seen(seen):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(seen, f, indent=4, ensure_ascii=False)

def notify_line(number, country):
    if not configuration or not LINE_USER_ID:
        print("LINE Bot 尚未設定 (請檢查 .env)，略過通知。")
        return
        
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.push_message(
                PushMessageRequest(
                    to=LINE_USER_ID,
                    messages=[TextMessage(text=f"新免費號碼可用！\n國家: {country}\n號碼: {number}")]
                )
            )
            print("LINE 通知發送成功！")
    except Exception as e:
        print(f"LINE 通知發送失敗: {e}")

def check_numbers(page, seen):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 正在檢查新號碼...")
    page.get('https://smspva.com/free-phone-numbers')
    time.sleep(3)  # 等待 Vue 渲染
    
    ul = page.ele('.free_numbers_number_list')
    if not ul:
        print("未找到號碼列表元素。")
        return

    items = ul.children()
    new_found = 0
    
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
        if number in seen:
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
                    full_link = f"https://smspva.com{href}" if href else ""
                    
                    formatted_added = f"Added {relative_time} ({date_str})"
                    print(f"發現新號碼: {number} ({country}) - {formatted_added}")
                    notify_line(number, country)
                    
                    seen[number] = {
                        "number": number,
                        "country": country,
                        "link": full_link,
                        "added_time": date_str,
                        "relative_time": relative_time,
                        "discovered_at": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    new_found += 1
                
    if new_found > 0:
        save_seen(seen)
    else:
        print("沒有發現新的號碼。")

def main():
    seen = load_seen()
    
    co = ChromiumOptions()
    co.headless(True)  # 無頭模式，不干擾使用者
    page = ChromiumPage(co)
    
    print("啟動免費號碼提醒器...")
    print(f"已載入 {len(seen)} 個歷史號碼。")
    print("請保持此終端機開啟以持續監控，或按下 Ctrl+C 結束。")
    print("-" * 30)
    
    try:
        while True:
            try:
                check_numbers(page, seen)
            except Exception as e:
                print(f"檢查過程中發生錯誤: {e}")
            
            # 等待下一次檢查
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n提醒器已停止。")
    finally:
        page.quit()

if __name__ == "__main__":
    main()
