import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.llm_service import enhance_prompt, create_basic_prompt
from services.runway_service import generate_video, generate_video_from_image
import requests
from fastapi import UploadFile, File, Form
from dotenv import load_dotenv

load_dotenv()

# ===============================
# Logging Configuration
# ===============================
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ===============================
# FastAPI App
# ===============================
app = FastAPI(
    title="AI Video Generation Agent",
    description="Enhance prompts and generate 8-second cinematic videos using RunwayML Veo3 model",
    version="1.0.0",
)

# ===============================
# CORS Settings
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Request Model
# ===============================


class VideoRequest(BaseModel):
    prompt: str
    style: str
    resolution: str

class ImageVideoRequest(BaseModel):
    image_path: str  # Local path to image file
    prompt: str
    style: str
    resolution: str

    class ImageVideoRequest(BaseModel):
        image_path: str  # Local path to image file
        prompt: str
        style: str
        resolution: str
# ===============================
# Routes
# ===============================
@app.get("/")
def home():
    logger.info("🏠 Root endpoint accessed")
    return {"message": "AI Video Generation Agent API is running!"}



@app.post("/generate-video")
def generate_video_api(request: VideoRequest):
    """
    Endpoint that enhances a prompt and generates a video.
    """
    logger.info(f"🎬 Received video generation request: prompt='{request.prompt}', style='{request.style}', resolution='{request.resolution}'")
    prompt = request.prompt.strip()
    if not prompt:
        logger.warning("⚠️ Empty prompt received")
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    if not os.getenv("RUNWAY_API_KEY"):
        logger.error("❌ Runway API key missing")
        raise HTTPException(
            status_code=500,
            detail="Runway API key missing. Please set RUNWAY_API_KEY in your .env file.",
        )
    try:
        logger.info("🧠 Enhancing prompt...")
        enhanced_prompt = enhance_prompt(prompt, request.style)
        logger.info(f"✅ Enhanced prompt: {enhanced_prompt}")
    except Exception as e:
        logger.error(f"❌ Prompt enhancement failed: {e}")
        enhanced_prompt = create_basic_prompt(prompt, request.style)
    try:
        logger.info("🚀 Generating video using RunwayML...")
        video_url = generate_video(enhanced_prompt, 8, request.resolution)
        if not video_url:
            logger.error("❌ Video generation failed on RunwayML.")
            raise HTTPException(status_code=500, detail="Video generation failed on RunwayML.")
        logger.info(f"✅ Video generated successfully: {video_url}")
        return {
            "status": "success",
            "video_url": video_url,
            "enhanced_prompt": enhanced_prompt,
        }
    except Exception as e:
        logger.exception("💥 Exception occurred during video generation")
        raise HTTPException(status_code=500, detail=str(e))


# ===============================
# Image-to-Video Endpoint
# ===============================
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

@app.post("/generate-image-video")
async def generate_image_video_api(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    style: str = Form(...),
    resolution: str = Form(...)
):
    logger.info(f"🖼️ Received image-to-video request: prompt='{prompt}', style='{style}', resolution='{resolution}'")
    
    # Upload image to IMGBB
    try:
        image_bytes = await image.read()
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            files={"image": image_bytes}
        )
        data = response.json()
        if not data.get("success"):
            logger.error(f"❌ IMGBB upload failed: {data}")
            raise HTTPException(status_code=400, detail="Image upload to IMGBB failed.")
        image_url = data["data"]["url"]
        logger.info(f"✅ Uploaded image to IMGBB: {image_url}")
    except Exception as e:
        logger.error(f"❌ Exception during IMGBB upload: {e}")
        raise HTTPException(status_code=500, detail="Image upload failed.")

    # Enhance prompt (if needed)
    enhanced_prompt = enhance_prompt(prompt, style)
    logger.info(f"🧠 Enhanced prompt: {enhanced_prompt}")

    # Generate video from image URL
    video_url = generate_video_from_image(
        image_url,  # Pass HTTPS URL, not local path
        enhanced_prompt,
        duration=8,
        resolution=resolution
    )
    if not video_url:
        logger.error("❌ Image-to-video generation failed on RunwayML.")
        raise HTTPException(status_code=500, detail="Image-to-video generation failed on RunwayML.")

    logger.info(f"🎬 Generated video URL: {video_url}")
    return {"video_url": video_url}
