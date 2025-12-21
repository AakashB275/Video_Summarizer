import streamlit as st
import tempfile
import time
from pathlib import Path
import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
assert API_KEY, "GOOGLE_API_KEY not set"

client = genai.Client(api_key=API_KEY)
# models = list(client.models.list())
# print("AVAILABLE MODELS:")
# for m in models:
#     print("-", m.name)

st.set_page_config(
    page_title="Gemini Video Analyzer",
    page_icon="📹",
    layout="wide",
)

st.title("📹 Gemini Video Analyzer")
st.caption("Powered by Google Gemini (official SDK)")

# FILE UPLOAD
video_file = st.file_uploader(
    "Upload a video file",
    type=["mp4", "mov", "avi"],
    help="Upload a video for AI analysis",
)

if video_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(video_file.read())
        video_path = tmp.name

    st.video(video_path)

    user_query = st.text_area(
        "What insights are you seeking from the video?",
        placeholder="Summarize, extract insights, detect events, explain scenes…",
        height=100,
    )

    if st.button("🔍 Analyze Video"):
        if not user_query.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("Uploading & analyzing video..."):
                    # Upload video to Gemini
                    uploaded_video = client.files.upload(file=video_path)

                    # Wait until processing completes
                    while uploaded_video.state == "PROCESSING":
                        time.sleep(1)
                        uploaded_video = client.files.get(name=uploaded_video.name)


                    # Gemini prompt
                    prompt = f"""
Analyze the uploaded video carefully.

User question:
{user_query}

Rules:
- Use only what is visible or inferable from the video
- Be clear, structured, and actionable
"""

                    # Generate response
                    response = client.models.generate_content(
                        model="models/gemini-2.5-flash",
                        contents=[uploaded_video, prompt],
                    )

                st.subheader("🧠 Analysis Result")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Analysis failed: {e}")

            finally:
                Path(video_path).unlink(missing_ok=True)

else:
    st.info("Upload a video to begin analysis.")
