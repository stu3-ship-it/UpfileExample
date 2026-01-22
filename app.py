import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 設定存取權限範圍
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_gdrive():
    #creds = dict(st.secrets["gcp_service_account"])
    # token.json 儲存使用者的登入資訊
    #if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file(dict(st.secrets["gcp_service_account"]), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def upload_file(file_path):
    # 1. 檢查檔案大小 (10MB = 10 * 1024 * 1024 Bytes)
    max_size = 10 * 1024 * 1024
    file_size = os.path.getsize(file_path)

    if file_size > max_size:
        print(f"檔案超過 10MB (目前大小: {file_size / 1024 / 1024:.2f} MB)，無法上傳。")
        return

    try:
        # 2. 身份驗證並建立 API 服務
        creds = authenticate_gdrive()
        service = build('drive', 'v3', credentials=creds)

        # 3. 設定檔案後設資料
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, resumable=True)

        # 4. 執行上傳
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        if file.get('id'):
            print("檔案上傳成功")
        else:
            print("檔案上傳失敗")

    except Exception as e:
        print(f"檔案上傳失敗: {e}")

if __name__ == '__main__':
    # 請在此輸入你想上傳的檔案路徑
    target_file = 'your_file_path_here.pdf' 
    
    if os.path.exists(target_file):
        upload_file(target_file)
    else:
        print("錯誤：找不到指定的檔案。")
