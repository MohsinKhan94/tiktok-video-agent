import os
import time
from runwayml import RunwayML
from dotenv import load_dotenv

# ==============================
# Load env vars
# ==============================
load_dotenv()
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")

if not RUNWAY_API_KEY:
    raise ValueError("❌ RUNWAY_API_KEY not found in environment variables. Please set it in your .env file.")

# ==============================
# Initialize Runway client
# ==============================
client = RunwayML(api_key=RUNWAY_API_KEY)


def generate_video_from_post(post_text: str, duration: int = 8, ratio: str = "720:1280") -> str:
    """
    Sends the generated post text to Runway's video model
    and returns the video URL.
    """

    # ✅ Ensure prompt does not exceed Runway's 1000 char limit
    safe_text = post_text[:600]

    task = client.text_to_video.create(
        prompt_text=f"Create a short social media video for this post: {safe_text}",
        model="veo3",
        ratio=ratio,
        duration=duration,
    )

    task_id = task.id
    print(f"🚀 Task started. ID: {task_id}")

    # Poll until finished
    retries = 0
    max_retries = 20  # ~100 sec wait

    while retries < max_retries:
        task = client.tasks.retrieve(task_id)
        print(f"[{retries}] Status: {task.status}")

        if task.status == "SUCCEEDED":
            print("✅ Video generation succeeded!")
            return task.output[0].asset_url

        if task.status == "FAILED":
            raise Exception(f"❌ Runway task failed: {task.error}")

        time.sleep(5)
        retries += 1

    raise TimeoutError("⏳ Runway task timed out after waiting 100 seconds.")
