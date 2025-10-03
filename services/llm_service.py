from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI() 

def enhance_prompt(prompt: str, style: str) -> str:
    """
    Enhances a user prompt with cinematic details for Veo3 video generation.
    Veo3 requires prompts under 1000 characters.
    """
    # Simple enhancement fallback (no API call needed)
    def simple_enhancement(prompt: str, style: str) -> str:
        """Fallback enhancement without OpenAI API"""
        base_enhancement = f"{prompt}, {style.lower()} style"
        cinematic_elements = [
            "cinematic lighting",
            "professional cinematography", 
            "high quality video",
            "detailed visuals",
            "dynamic camera angles",
            "4K resolution"
        ]
        enhanced = f"{base_enhancement}, {', '.join(cinematic_elements[:3])}"
        
        # Ensure under 800 characters
        if len(enhanced) > 800:
            enhanced = enhanced[:800]
            
        print(f"📝 Using simple enhancement (OpenAI quota exceeded)")
        print(f"📝 Enhanced prompt length: {len(enhanced)}/800 characters")
        return enhanced

    try:
        system_message = (
            "You are an expert in generating prompts for Veo3 video generation AI. "
            "Enhance prompts to include cinematic details, camera angles, lighting, and style. "
            "CRITICAL: Keep the enhanced prompt under 400 characters to allow for Veo3's 1000 character limit. "
            "Be concise and pin to point. Focus on visual elements that can be represented in video."
        )
        
        user_message = f"Original prompt: '{prompt}' | Style: {style}. Keep response under 400 characters."

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # More affordable model
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,  # Even shorter response
            temperature=0.3,
            timeout=30  # Add timeout
        )
        
        enhanced = response.choices[0].message.content.strip()
        
        # Ensure it's under 800 characters (leaving room for Veo3's 1000 limit)
        if len(enhanced) > 800:
            enhanced = enhanced[:800]
            print(f"⚠️ Enhanced prompt truncated to 800 characters")
            
        print(f"📝 Enhanced prompt length: {len(enhanced)}/800 characters")
        return enhanced
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error enhancing prompt: {error_msg}")
        
        # Check if it's a quota issue
        if "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower() or "429" in error_msg:
            print("💡 OpenAI quota exceeded. Using fallback enhancement.")
            return simple_enhancement(prompt, style)
        elif "rate limit" in error_msg.lower():
            print("💡 OpenAI rate limit hit. Using fallback enhancement.")
            return simple_enhancement(prompt, style)
        else:
            print("🔄 Using fallback enhancement due to API error.")
            return simple_enhancement(prompt, style)

def create_basic_prompt(prompt: str, style: str) -> str:
    """
    Create a basic enhanced prompt without using OpenAI API
    Useful when API is unavailable or for testing
    """
    style_keywords = {
        "realistic": "photorealistic, natural lighting, realistic details",
        "cinematic": "cinematic lighting, dramatic angles, film quality", 
        "dramatic": "high contrast, dramatic lighting, intense mood",
        "vibrant": "vibrant colors, bright lighting, lively atmosphere",
        "moody": "moody lighting, atmospheric, emotional tone",
        "anime": "anime style, vibrant colors, stylized animation"
    }
    
    style_desc = style_keywords.get(style.lower(), "cinematic style, high quality")
    
    basic_prompt = f"{prompt}, {style_desc}, professional video quality, 4K resolution"
    
    # Ensure under 800 characters
    if len(basic_prompt) > 800:
        basic_prompt = basic_prompt[:800]
        
    return basic_prompt