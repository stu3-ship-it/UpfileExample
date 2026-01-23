import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# 設定網頁標題
st.title("Google Drive 檔案上傳器")

# 從 Secrets 讀取憑證
def get_gdrive_service():
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive'])
    return build('drive', 'v3', credentials=scoped_credentials)

# 上傳函式
def upload_to_gdrive(uploaded_file, folder_id):
    try:
        service = get_gdrive_service()
        
        file_metadata = {
            'name': uploaded_file.name,
            'parents': [folder_id]
        }
        
        # 轉換 Streamlit 的 UploadedFile 為 Google 可接受的格式
        media = MediaIoBaseUpload(
            io.BytesIO(uploaded_file.getvalue()), 
            mimetype=uploaded_file.type, 
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
            supportsAllDrives=True
        ).execute()
        
        return True
    except Exception as e:
        st.error(f"錯誤詳情: {e}")
        return False

# UI 介面
uploaded_file = st.file_uploader("選擇要上傳的檔案", type=None)

if st.button("確認上傳"):
    if uploaded_file is not None:
        folder_id = st.secrets["google_drive"]["folder_id"]
        
        with st.spinner('上傳中...'):
            success = upload_to_gdrive(uploaded_file, folder_id)
            
        if success:
            st.success("檔案上傳成功")
        else:
            st.error("檔案上傳失敗")
    else:
        st.warning("請先選擇檔案")
