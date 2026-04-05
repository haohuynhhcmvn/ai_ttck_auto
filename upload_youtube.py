import os
import pickle
import base64
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

def get_service():
    """
    Khôi phục thông tin xác thực từ GitHub Secrets và khởi tạo YouTube Service.
    """
    token_file = "token.pickle"
    token_b64 = os.getenv("YOUTUBE_TOKEN_PICKLE")
    
    if not token_b64:
        raise Exception("❌ Lỗi: YOUTUBE_TOKEN_PICKLE không tồn tại trong Secrets!")

    # Giải mã và tạo file token.pickle tạm thời
    try:
        with open(token_file, "wb") as f:
            f.write(base64.b64decode(token_b64))
    except Exception as e:
        raise Exception(f"❌ Lỗi giải mã Token: {e}")

    with open(token_file, "rb") as token:
        creds = pickle.load(token)

    # Tự động làm mới token nếu hết hạn
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Đang làm mới YouTube Access Token...")
            creds.refresh(Request())
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)

def upload_video_with_thumbnail(file_path, hook_img_path, title_str, description_str):
    """
    Upload video lên YouTube và dùng ảnh Hook làm hình nền đại diện (Thumbnail).
    """
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file video: {file_path}")
        return None

    try:
        youtube = get_service()

        # YouTube Shorts yêu cầu tiêu đề < 100 ký tự
        # Thêm hashtag #Shorts để YouTube nhận diện đúng định dạng
        final_title = f"{title_str} #Shorts #Bantintaichinh247"
        if len(final_title) > 100:
            final_title = final_title[:90] + "... #Shorts"

        body = {
            "snippet": {
                "title": final_title,
                "description": description_str,
                "tags": ["chungkhoan", "taichinh", "shorts", "vnindex", "vneconomy"],
                "categoryId": "25" # News & Politics
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        # --- BƯỚC 1: UPLOAD VIDEO ---
        print(f"🚀 [YT]: Đang tải video lên: {final_title}")
        media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"📊 [YT]: Tiến độ upload: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        print(f"✅ [YT]: Video đã lên sàn! ID: {video_id}")

        # --- BƯỚC 2: CHỜ XỬ LÝ & SET THUMBNAIL ---
        if hook_img_path and os.path.exists(hook_img_path):
            print("⏳ [YT]: Chờ 15s để YouTube xử lý video trước khi đặt Thumbnail...")
            time.sleep(15) 
            
            try:
                print(f"🖼️ [YT]: Đang thiết lập ảnh Hook làm Thumbnail: {hook_img_path}")
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(hook_img_path, mimetype="image/png")
                ).execute()
                print("✅ [YT]: Đã cập nhật ảnh bìa Hook thành công!")
            except HttpError as thumb_err:
                print(f"⚠️ [YT]: Không thể set Thumbnail (Có thể video quá ngắn hoặc YouTube chưa xử lý kịp): {thumb_err}")
        
        return f"https://youtube.com/watch?v={video_id}"

    except Exception as e:
        print(f"❌ [YT]: Lỗi nghiêm trọng khi upload: {e}")
        return None
    finally:
        # Xóa file token tạm để bảo mật
        if os.path.exists("token.pickle"):
            os.remove("token.pickle")
