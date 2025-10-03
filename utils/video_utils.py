import requests

def get_video_bytes(video_url: str) -> bytes | None:
    """
    Fetch video content from a URL for download.
    """
    try:
        response = requests.get(video_url, timeout=60)
        if response.status_code == 200:
            return response.content
        else:
            print(f"❌ Failed to fetch video. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"❌ Error fetching video: {e}")
        return None
