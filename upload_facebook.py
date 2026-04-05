import os
import requests

def upload_video_facebook(file_path, title_str, description_str):
    """
    Upload video thẳng lên Facebook Fanpage.
    """
    page_id = os.getenv("FB_PAGE_ID")
    access_token = os.getenv("FB_PAGE_ACCESS_TOKEN")

    if not page_id or not access_token:
        print("   ❌ [FB]: Thiếu biến môi trường FB_PAGE_ID hoặc FB_PAGE_ACCESS_TOKEN!")
        return None

    if not os.path.exists(file_path):
        print(f"   ❌ [FB]: Không tìm thấy file video: {file_path}")
        return None

    # Endpoint chuẩn của Meta Graph API để upload video lên Page
    url = f"https://graph.facebook.com/v19.0/{page_id}/videos"

    # Gắn thêm hashtag chuyên biệt cho FB (FB rất thích hashtag)
    final_desc = f"{description_str}\n\n#Bantintaichinh247 #Chungkhoan #Cophieu #VNIndex"

    payload = {
        'title': title_str[:255], # Tiêu đề FB giới hạn 255 ký tự
        'description': final_desc,
        'access_token': access_token
    }

    print(f"🚀 [FB]: Đang tải video lên Fanpage...")
    try:
        # Upload dạng multipart/form-data
        with open(file_path, 'rb') as video_file:
            files = {'source': video_file}
            response = requests.post(url, data=payload, files=files)

        result = response.json()
        
        # Nếu FB trả về ID tức là thành công
        if 'id' in result:
            video_id = result['id']
            print(f"   ✅ [FB]: Video đã lên sóng! ID: {video_id}")
            # Trả về link video chuẩn của Facebook
            return f"https://www.facebook.com/{page_id}/videos/{video_id}"
        else:
            print(f"   ❌ [FB]: Mark xoăn báo lỗi: {result}")
            return None

    except Exception as e:
        print(f"   ❌ [FB]: Lỗi sập nguồn khi gọi API: {e}")
        return None
