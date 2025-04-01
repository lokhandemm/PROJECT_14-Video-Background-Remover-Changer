import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from rembg import remove

# Define background options
backgrounds = {
    "Office": r"C:\Users\hp\Downloads\Office background.jpg",
    "Beach": r"C:\Users\hp\Downloads\Beach.jpg",
    "Mountains": r"C:\Users\hp\Downloads\Mountains.jpg",
    "Cafe": r"C:\Users\hp\Downloads\Cafe.jpg",
    "Plain Color": r"C:\Users\hp\Downloads\Plain color background.jpg"
}

def remove_bg(frame, bg_path):
    """ Remove background and replace it with selected background """
    frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    removed_bg = remove(frame_rgba)

    bg_img = cv2.imread(bg_path)
    bg_img = cv2.resize(bg_img, (frame.shape[1], frame.shape[0]))

    mask = removed_bg[:, :, 3] / 255.0
    mask = np.expand_dims(mask, axis=-1)

    result = (frame * mask + bg_img * (1 - mask)).astype(np.uint8)
    
    return result

def process_video(video_path, bg_path):
    """ Process the video frame by frame """
    cap = cv2.VideoCapture(video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    output_path = "processed_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    progress_bar = st.progress(0)
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame = remove_bg(frame, bg_path)
        out.write(processed_frame)
        
        frame_count += 1
        progress_bar.progress(frame_count / total_frames)

    cap.release()
    out.release()
    return output_path

# Streamlit UI
st.title("🎥 AI Video Background Remover & Changer")

uploaded_file = st.file_uploader("📂 Upload Your Video", type=["mp4"])
bg_choice = st.selectbox("🌆 Select Background", list(backgrounds.keys()))

if st.button("🚀 Process & Download"):
    if uploaded_file and bg_choice:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_file.write(uploaded_file.read())

        st.write(f"Processing video: {temp_file.name}")
        st.write(f"Background image path: {backgrounds[bg_choice]}")
        
        processed_video = process_video(temp_file.name, backgrounds[bg_choice])

        if processed_video:
            st.success("✅ Video Processed! Download below:")
            with open(processed_video, "rb") as file:
                st.download_button("📥 Download Video", data=file, file_name="processed_video.mp4", mime="video/mp4")
    else:
        st.error("⚠️ Please upload a video & select a background.")