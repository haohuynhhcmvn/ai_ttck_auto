import os
import requests
import time

def upload_video_facebook(file_path, hook_img_path, title_str, description_str):
    """
    Upload video lên Fanpage và ép Facebook dùng ảnh Hook làm Thumbnail.
    """
    page_id = os.getenv("FB_PAGE_ID")
    access_token = os.getenv("FB_PAGE_ACCESS_TOKEN")

    if not page_id or not access_token:
        print("   ❌ [FB]: Thiếu biến môi trường FB_PAGE_ID hoặc FB_PAGE_ACCESS_TOKEN!")
        return None

    # 1. UPLOAD VIDEO
    url_video = f"https://graph.facebook.com/v19.0/{page_id}/videos"
    payload = {
        'title': title_str[:255],
        'description': f"{description_str}\n\n#Bantintaichinh247 #Shorts #Stock",
        'access_token': access_token
    }

    print(f"🚀 [FB]: Đang tải video lên Fanpage...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(url_video, data=payload, files={'source': f})
        
        res_data = response.json()
        video_id = res_data.get('id')

        if not video_id:
            print(f"   ❌ [FB]: Lỗi upload video: {res_data}")
            return None

        print(f"   ✅ [FB]: Video đã lên (ID: {video_id}).")

        # 2. UPLOAD THUMBNAIL (Nếu có ảnh Hook)
        if hook_img_path and os.path.exists(hook_img_path):
            print(f"🖼️ [FB]: Đang ép Facebook dùng ảnh Hook làm Thumbnail...")
            # Chờ 5s cho server FB nhận diện video ID
            time.sleep(5)
            
            url_thumb = f"https://graph.facebook.com/v19.0/{video_id}/thumbnails"
            with open(hook_img_path, 'rb') as img_f:
                # FB yêu cầu tham số 'is_preferred=True' để chọn làm ảnh chính
                thumb_res = requests.post(
                    url_thumb, 
                    data={'access_token': access_token, 'is_preferred': 'true'}, 
                    files={'source': img_f}
                )
            
            if thumb_res.json().get('success'):
                print("   ✅ [FB]: Thumbnail Hook đã được thiết lập!")
            else:
                print(f"   ⚠️ [FB]: Không set được Thumbnail: {thumb_res.json()}")

        return f"https://www.facebook.com/{page_id}/videos/{video_id}"

    except Exception as e:
        print(f"   ❌ [FB]: Lỗi hệ thống: {e}")
        return None
