import streamlit as st
from services.llm_service import enhance_prompt, create_basic_prompt
from services.runway_service import generate_video
from utils.video_utils import get_video_bytes
import os

# ==========================
# Streamlit UI Setup
# ==========================
st.set_page_config(page_title="AI Video Generator", layout="wide")
st.title("🎬 AI Video Generation Agent (Veo3)")
st.markdown("""
Create high-quality videos using RunwayML's Veo3 model!  

**Veo3 Requirements:**
- 🕐 **Fixed 8 seconds video length** (Veo3 requirement)  
- 📝 Maximum 1000 characters per prompt  
- 🎬 Professional-grade video quality
""")

# User settings
st.sidebar.header("Video Settings")
st.sidebar.markdown("**⚠️ Veo3 requires exactly 8 seconds**")

video_resolution = st.sidebar.selectbox("Video Resolution", ["720p", "1080p"])
video_style = st.sidebar.selectbox("Video Style", ["Realistic", "Cinematic", "Dramatic", "Vibrant", "Moody"])

# Debug info
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.write("API Keys Status:")
    st.sidebar.write(f"OpenAI Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    st.sidebar.write(f"Runway Key: {'✅ Set' if os.getenv('RUNWAY_API_KEY') else '❌ Missing'}")

st.sidebar.info("🎯 Veo3 generates exactly 8-second videos")

# User input
user_prompt = st.text_area(
    "Describe your video idea:", 
    placeholder="e.g., A boy coding on a laptop in a cozy room at night, cinematic lighting",
    max_chars=500
)

if user_prompt:
    st.caption(f"Prompt length: {len(user_prompt)}/500 characters (will be enhanced)")

# ==========================
# Generate Video
# ==========================
if st.button("Generate 8-Second Video with Veo3"):
    if not user_prompt.strip():
        st.warning("Please enter a video prompt!")
    else:
        # Check API keys with better messaging
        if not os.getenv("RUNWAY_API_KEY"):
            st.error("""
            ❌ RunwayML API key is not set. 
            
            **To fix this:**
            1. Get an API key from [RunwayML.com](https://runwayml.com)
            2. Add it to your `.env` file: `RUNWAY_API_KEY=your_key_here`
            3. Restart the app
            """)
            st.stop()
        
        # Enhance prompt with better error handling
        with st.spinner("🎨 Enhancing your prompt..."):
            try:
                enhanced_prompt = enhance_prompt(user_prompt, video_style)
                if enhanced_prompt:
                    st.markdown(f"**Enhanced Prompt:** {enhanced_prompt}")
                    st.caption(f"Final prompt length: {len(enhanced_prompt)}/1000 characters")
                else:
                    st.warning("⚠️ Could not enhance prompt with AI, using basic enhancement.")
                    enhanced_prompt = create_basic_prompt(user_prompt, video_style)
                    st.markdown(f"**Basic Prompt:** {enhanced_prompt}")
            except Exception as e:
                st.warning(f"⚠️ Prompt enhancement failed: {str(e)[:100]}... Using original prompt.")
                enhanced_prompt = user_prompt[:800]  # Truncate if needed
                st.markdown(f"**Using Prompt:** {enhanced_prompt}")

        # Generate video with progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_area = st.empty()
        
        status_text.text("🚀 Starting video generation...")
        progress_bar.progress(10)
        
        try:
            # Generate video - this may take several minutes
            with status_area.container():
                st.info("⏳ Video generation started. This may take 5-15 minutes...")
                st.info("💡 The development API may be slow. Please be patient.")
            
            video_url = generate_video(enhanced_prompt, 8, video_resolution)
            
            if video_url:
                progress_bar.progress(100)
                status_text.text("✅ Video generated successfully!")
                status_area.empty()
                
                st.success("✅ 8-second video generated successfully!")
                st.video(video_url)

                # Download button
                with st.spinner("Preparing video for download..."):
                    video_bytes = get_video_bytes(video_url)
                if video_bytes:
                    st.download_button(
                        label="⬇️ Download Video",
                        data=video_bytes,
                        file_name="ai_generated_video.mp4",
                        mime="video/mp4"
                    )
                    st.success("📥 Video ready for download!")
                else:
                    st.warning("⚠️ Could not prepare video for download, but you can view it above.")
            else:
                progress_bar.progress(0)
                status_text.text("❌ Generation failed")
                status_area.empty()
                
                st.error("""
                ❌ Video generation failed. This could be because:
                
                **Common Issues:**
                - 🕒 **API is throttled** - Try again in a few minutes
                - 💳 **No credits left** - Check your RunwayML account balance
                - 🔑 **API key issues** - Verify your key is active
                - 🌐 **Network issues** - Check your internet connection
                
                **Next Steps:**
                1. Wait a few minutes and try again
                2. Check your [RunwayML account](https://runwayml.com) for credits
                3. Try a simpler, shorter prompt
                """)
                
        except Exception as e:
            progress_bar.progress(0)
            status_text.text("❌ Unexpected error")
            status_area.empty()
            
            st.error(f"""
            ❌ An unexpected error occurred:
            
            **Error:** {str(e)}
            
            **Please try:**
            1. Checking your API keys are correct
            2. Trying a different prompt
            3. Waiting a few minutes before retrying
            """)

# Add helpful information section
with st.expander("💡 Tips for Better Videos"):
    st.markdown("""
    **Prompt Writing Tips:**
    - Be specific about subjects, actions, and settings
    - Include visual details (lighting, colors, camera angles)
    - Keep it under 500 characters for best results
    - Examples:
        - "A astronaut floating in space with Earth in background, cinematic lighting"
        - "A cat playing with yarn in a sunny living room, realistic style"
        - "A car driving through a neon-lit city at night, futuristic style"
    
    **Expected Timelines:**
    - ⏱️ **Queue time**: 2-10 minutes (development API can be slow)
    - 🎬 **Processing time**: 3-8 minutes
    - ⏳ **Total wait**: 5-18 minutes
    
    **Troubleshooting:**
    - If videos fail, try shorter, simpler prompts
    - Development API has limited resources - be patient
    - Check your RunwayML account for credit balance
    """)