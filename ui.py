import streamlit as st
import requests

# ==========================
# Streamlit UI Setup
# ==========================
st.set_page_config(page_title="🎬 AI Video Generator", layout="wide")
st.title("🎬 AI Video Generation Agent (Veo3 - Development)")
st.markdown("""
Create high-quality videos using **RunwayML's Veo3** model.  
This Streamlit app connects directly to your **FastAPI backend** for automated video generation.
""")

# ==========================
# Backend API URL
# ==========================
API_URL = "http://127.0.0.1:8000"  # local backend (FastAPI)

# ==========================
# Input Section
# ==========================

# ==========================
# Tabs for Text-to-Video and Image-to-Video
# ==========================
tab1, tab2 = st.tabs(["Text-to-Video", "Image-to-Video"])

with tab1:
    st.subheader("🧠 Enter Your Prompt")
    prompt = st.text_area("Enter the topic or idea for your video:")
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox(
            "🎨 Choose a style",
            ["cinematic", "realistic", "vibrant", "moody", "dramatic", "anime"],
            index=0
        )
    with col2:
        resolution = st.selectbox(
            "📺 Select resolution",
            ["720p", "1080p", "480p"],
            index=1
        )
    if st.button("🚀 Generate Video", key="text2video"):
        if not prompt.strip():
            st.warning("⚠️ Please enter a valid prompt!")
        else:
            with st.spinner("⏳ Generating video... this may take a few minutes."):
                try:
                    payload = {
                        "prompt": prompt,
                        "style": style,
                        "resolution": resolution
                    }
                    response = requests.post(f"{API_URL}/generate-video", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        st.success("✅ Video generated successfully!")
                        st.markdown("### ✨ Enhanced Prompt")
                        st.code(data["enhanced_prompt"], language="markdown")
                        st.markdown("### 🎬 Generated Video")
                        st.video(data["video_url"])
                    else:
                        st.error(f"❌ Failed: {response.text}")
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")

with tab2:
    st.subheader("🖼️ Upload Image for Image-to-Video")
    uploaded_file = st.file_uploader("Upload an image (jpg/png)", type=["jpg", "jpeg", "png"])
    image_prompt = st.text_area("Enter the topic or idea for your video (image-to-video):")
    col3, col4 = st.columns(2)
    with col3:
        image_style = st.selectbox(
            "🎨 Choose a style (image-to-video)",
            ["cinematic", "realistic", "vibrant", "moody", "dramatic", "anime"],
            index=0,
            key="image_style"
        )
    with col4:
        image_resolution = st.selectbox(
            "📺 Select resolution (image-to-video)",
            ["720p", "1080p", "480p"],
            index=1,
            key="image_resolution"
        )
    if st.button("🚀 Generate Video from Image", key="image2video"):
        if uploaded_file is None:
            st.warning("⚠️ Please upload an image file!")
        elif not image_prompt.strip():
            st.warning("⚠️ Please enter a valid prompt!")
        else:
            with st.spinner("⏳ Generating video from image... this may take a few minutes."):
                try:
                    files = {"image": uploaded_file}
                    data = {
                        "prompt": image_prompt,
                        "style": image_style,
                        "resolution": image_resolution
                    }
                    response = requests.post(
                        f"{API_URL}/generate-image-video",
                        files=files,
                        data=data
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Image-to-video generated successfully!")
                        st.markdown("### ✨ Enhanced Prompt")
                        st.code(result.get("enhanced_prompt", ""), language="markdown")
                        st.markdown("### 🎬 Generated Video")
                        st.video(result["video_url"])
                    else:
                        st.error(f"❌ Failed: {response.text}")
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
