
# ==============================
# UPLOAD TO YOUTUBE
# ==============================

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

def get_service():
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)
    return build("youtube", "v3", credentials=creds)

def upload_video(file):
    youtube = get_service()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "Tin chứng khoán",
                "description": "Auto video",
                "tags": ["stock"],
                "categoryId": "25"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(file)
    )

    response = request.execute()
    return f"https://youtube.com/watch?v={response['id']}"
