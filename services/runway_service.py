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
try:
    client = RunwayML(api_key=RUNWAY_API_KEY)
    print("✅ RunwayML client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize RunwayML client: {e}")
    raise

def generate_video(prompt: str, duration: int, resolution: str) -> str | None:
    """
    Generate video using RunwayML SDK
    """
    return generate_video_with_polling(prompt, duration, resolution)

def generate_video_with_polling(prompt: str, duration: int, resolution: str) -> str | None:
    """
    Sends the prompt to Runway's video model and returns the video URL.
    """
    # Clean and validate prompt
    clean_prompt = prompt.replace("Enhanced Prompt:", "").strip()
    
    # Ensure prompt does not exceed Runway's 1000 char limit
    if len(clean_prompt) > 1000:
        clean_prompt = clean_prompt[:1000]
        print(f"⚠️ Prompt truncated to 1000 characters")

    # Map resolution to ratio
    resolution_map = {
        "720p": "1280:720",
        "1080p": "1920:1080",
        "480p": "854:480"
    }
    ratio = resolution_map.get(resolution, "1280:720")
    
    # Veo3 requires exactly 8 seconds
    veo3_duration = 8
    if duration != 8:
        print(f"⚠️ Veo3 requires exactly 8 seconds. Using 8s instead of {duration}s")

    try:
        print("🔧 Starting Veo3 video generation via SDK...")
        print(f"📝 Prompt: {clean_prompt}")
        print(f"📝 Length: {len(clean_prompt)}/1000 characters")
        print(f"⏱️ Duration: {veo3_duration}s")
        print(f"📺 Resolution: {resolution} (ratio: {ratio})")
        print(f"🎯 Model: Veo3")

        # Create the video generation task
        task = client.text_to_video.create(
            prompt_text=clean_prompt,
            model="veo3",
            ratio=ratio,
            duration=veo3_duration,
        )

        task_id = task.id
        print(f"🆔 Task ID: {task_id}")

        # Poll until finished
        max_retries = 300  # ~25 minutes
        retries = 0
        last_status = ""

        while retries < max_retries:
            # Retrieve the current task status
            current_task = client.tasks.retrieve(task_id)
            task_status = getattr(current_task, 'status', 'UNKNOWN')
            
            # Only print status when it changes
            if task_status != last_status:
                print(f"[{retries}] Status: {task_status}")
                last_status = task_status

            if task_status == "SUCCEEDED":
                print("✅ Video generation succeeded!")
                
                # Extract video URL from the task using the FIXED method
                video_url = extract_video_url_from_task_fixed(current_task)
                if video_url:
                    print(f"🎬 Video URL: {video_url}")
                    return video_url
                else:
                    print("❌ Task succeeded but no video URL found")
                    return None

            if task_status == "FAILED":
                error_msg = getattr(current_task, 'error', 'Unknown error')
                print(f"❌ Runway task failed: {error_msg}")
                return None
                
            if task_status == "THROTTLED":
                if retries % 10 == 0:
                    print(f"⏳ Still in queue... ({retries * 5} seconds waited)")
                time.sleep(10)
            else:
                time.sleep(5)

            retries += 1

        print("⏳ Runway task timed out after waiting 25 minutes.")
        return None

    except Exception as e:
        print(f"❌ Error in video generation: {e}")
        return None

def extract_video_url_from_task_fixed(task) -> str | None:
    """
    FIXED VERSION: Extract video URL from task object
    Based on the debug output showing output is a list
    """
    try:
        print("🔍 Extracting video URL from task (FIXED VERSION)...")
        
        # Method 1: Direct inspection of task.output list
        if hasattr(task, 'output') and task.output:
            print(f"📦 task.output type: {type(task.output)}")
            
            if isinstance(task.output, list) and len(task.output) > 0:
                print(f"📦 task.output length: {len(task.output)}")
                
                # Inspect each item in the output list
                for i, output_item in enumerate(task.output):
                    print(f"📦 Output item {i}: {type(output_item)}")
                    
                    # If it's a string, it might be the URL directly
                    if isinstance(output_item, str):
                        print(f"🎯 Found string output: {output_item}")
                        if output_item.startswith(('http://', 'https://')):
                            print(f"🎯 This looks like a URL!")
                            return output_item
                    
                    # If it's an object, check for URL attributes
                    elif hasattr(output_item, '__dict__'):
                        print(f"📦 Output item {i} attributes: {output_item.__dict__}")
                        # Check common URL attributes
                        for attr, value in output_item.__dict__.items():
                            if isinstance(value, str) and value.startswith(('http://', 'https://')):
                                print(f"🎯 Found URL in {attr}: {value}")
                                return value
                    
                    # If it's a dictionary
                    elif isinstance(output_item, dict):
                        print(f"📦 Output item {i} keys: {output_item.keys()}")
                        for key, value in output_item.items():
                            if isinstance(value, str) and value.startswith(('http://', 'https://')):
                                print(f"🎯 Found URL in {key}: {value}")
                                return value
        
        # Method 2: Convert entire task to dict and search for URLs
        print("🔄 Converting task to dict to search for URLs...")
        try:
            if hasattr(task, 'dict'):
                task_dict = task.dict()
                print(f"📋 All task keys: {task_dict.keys()}")
                
                # Recursively search for URLs in the entire task structure
                def find_url_in_dict(obj, path=""):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            if isinstance(value, str) and value.startswith(('http://', 'https://')):
                                print(f"🎯 Found URL at {current_path}: {value}")
                                return value
                            elif isinstance(value, (dict, list)):
                                result = find_url_in_dict(value, current_path)
                                if result:
                                    return result
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            current_path = f"{path}[{i}]"
                            result = find_url_in_dict(item, current_path)
                            if result:
                                return result
                    return None
                
                url = find_url_in_dict(task_dict)
                if url:
                    return url
                    
        except Exception as e:
            print(f"⚠️ Error searching task dict: {e}")
        
        # Method 3: Try the wait_for_task_output with proper handling
        try:
            print("🔄 Trying wait_for_task_output with proper handling...")
            final_output = task.wait_for_task_output()
            if final_output:
                print(f"📦 wait_for_task_output type: {type(final_output)}")
                
                # Recursively search for URL in the final output
                def find_url(obj):
                    if isinstance(obj, str) and obj.startswith(('http://', 'https://')):
                        return obj
                    elif hasattr(obj, '__dict__'):
                        for attr, value in obj.__dict__.items():
                            if isinstance(value, str) and value.startswith(('http://', 'https://')):
                                return value
                    elif isinstance(obj, dict):
                        for key, value in obj.items():
                            if isinstance(value, str) and value.startswith(('http://', 'https://')):
                                return value
                    elif isinstance(obj, list):
                        for item in obj:
                            result = find_url(item)
                            if result:
                                return result
                    return None
                
                url = find_url(final_output)
                if url:
                    print(f"🎯 Found URL via wait_for_task_output: {url}")
                    return url
                    
        except Exception as e:
            print(f"⚠️ wait_for_task_output failed: {e}")
        
        print("❌ No video URL found after exhaustive search")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting video URL: {e}")
        return None

# Keep the old function for backward compatibility
def extract_video_url_from_task(task) -> str | None:
    """Alias for the fixed function"""
    return extract_video_url_from_task_fixed(task)