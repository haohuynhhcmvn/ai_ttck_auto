import os
import pickle
import base64
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from datetime import datetime

def get_service():
    token_file = "token.pickle"
    token_b64 = os.getenv("YOUTUBE_TOKEN_PICKLE")
    
    if not token_b64:
        raise Exception("❌ YOUTUBE_TOKEN_PICKLE không tồn tại trong Secrets!")

    # Giải mã Token
    with open(token_file, "wb") as f:
        f.write(base64.b64decode(token_b64))

    with open(token_file, "rb") as token:
        creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title_str, description_str):
    """
    Upload video lên YouTube với tiêu đề và mô tả khớp với Telegram.
    """
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file: {file_path}")
        return None

    try:
        youtube = get_service()

        # YouTube Shorts yêu cầu tiêu đề < 100 ký tự và nên có #Shorts
        # Chúng ta lấy title_str (header_title) làm gốc
        final_title = f"{title_str} #Shorts #Stock247"
        if len(final_title) > 100:
            final_title = final_title[:90] + "... #Shorts"

        body = {
            "snippet": {
                "title": final_title,
                "description": description_str, # description_str chính là social_post
                "tags": ["chungkhoan", "taichinh", "vneconomy", "shorts"],
                "categoryId": "25" 
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        print(f"🚀 Đang đẩy video lên YouTube: {final_title}")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"📊 YouTube Progress: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        return f"https://youtube.com/watch?v={video_id}"

    except Exception as e:
        print(f"❌ YouTube Upload Error: {e}")
        return None
    finally:
        if os.path.exists("token.pickle"): os.remove("token.pickle")
