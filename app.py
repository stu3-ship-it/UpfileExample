import cv2
import datetime
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# --- 設定區域 ---
# 請確保你已經從 Google Cloud Console 下載了憑證檔案 (JSON)
SERVICE_ACCOUNT_FILE = 'your-credentials.json' 
PARENT_FOLDER_ID = '1pFAML0LY2BFVBc_vvxN06JPBXoCFLUXZ' # 如果留空則上傳至根目錄

def take_photo():
    # 1. 產生以日期時間命名的檔名
    now = datetime.datetime.now()
    file_name = now.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
    
    # 2. 開啟相機
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    
    if not ret:
        print("無法取得相機畫面")
        return None
    
    # 3. 儲存照片到本地
    cv2.imwrite(file_name, frame)
    cam.release()
    cv2.destroyAllWindows()
    
    print(f"照片已拍攝並儲存為: {file_name}")
    return file_name

def upload_to_drive(file_path):
    # 權限範圍
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    # 身份驗證
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('drive', 'v3', credentials=creds)
    
    # 設定檔案元數據
    file_metadata = {
        'name': file_path,
        'parents': [PARENT_FOLDER_ID] if PARENT_FOLDER_ID else []
    }
    
    media = MediaFileUpload(file_path, mimetype='image/jpeg')
    
    # 執行上傳
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    
    print(f"檔案已成功上傳至雲端！檔案 ID: {file.get('id')}")
    
    # 上傳後可以選擇刪除本地檔案
    # os.remove(file_path)

if __name__ == "__main__":
    photo_file = take_photo()
    if photo_file:
        upload_to_drive(photo_file)
