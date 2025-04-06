import streamlit as st
import os
import requests
import base64
from transformers import pipeline
import re
import spacy
import io
import yt_dlp

# Load spaCy's pre-trained English model
nlp = spacy.load("en_core_web_sm")

# Add background image function
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), url(data:image/{"jpg"};base64,{encoded_string.decode()});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Add background
add_bg_from_local('microphone.png')  # Adjust path as needed

# Function to extract video ID from URL
def extract_video_id(url):
    video_id = None
    match = re.search(r'(?:youtube\.com\/(?:[^\/\n]+\/[^\n]+\/|(?:v|e(?:mbed)?)\/|\S+?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]+)', url)
    if match:
        video_id = match.group(1)
    return video_id

# Function to download audio from YouTube video
def download_audio(video_url, output_folder="audio"):
    video_id = extract_video_id(video_url)
    if not video_id:
        st.error("Unable to extract video ID from the URL")
        return None
    
    output_path = os.path.join(output_folder, f"{video_id}.mp3")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioquality': 1,
        'outtmpl': output_path,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    
    return output_path

# Reverie transcription API
def transcribe_audio_reverie(audio_file, lang):
    api_url = "https://revapi.reverieinc.com/"
    headers = {
        'REV-API-KEY': 'b024b10b9bb76059699ea17e85047ff2ad349ada',  # Replace with your Reverie API key
        'REV-APP-ID': 'com.advaygujar2005',   # Replace with your Reverie App ID
        'REV-APPNAME': 'stt_file',
        'src_lang': lang,  # 'hi' for Hindi, adjust for other languages
        'domain': 'generic',
        'format': 'mp3',
    }
    
    audio_data = audio_file.read()
    files = {'audio': ('audio.mp3', audio_data, 'audio/mpeg')}
    response = requests.post(api_url, headers=headers, files=files)
    response_data = response.json()
    if response.status_code == 200:
        return response_data['result']['text']
    else:
        st.error(f"Error during transcription: {response_data.get('message', 'Unknown error')}")
        st.error(f"Response: {response.text}")
        return None

# Language choice function
def get_language_choice():
    lang = st.selectbox("Choose Language for Transcription:", ["hi", "en", "ta", "mr", "bn"])  # Add more languages as needed
    return lang

# Function to summarize text using transformers
def summarize_text(text, level="medium"):
    summarizer = pipeline("summarization")
    max_length = {"small": 50, "medium": 100, "large": 200}.get(level, 100)
    summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# Function to extract key highlights using spaCy
def extract_key_highlights(text, num_highlights=5):
    doc = nlp(text)
    keywords = [chunk.text for chunk in doc.noun_chunks][:num_highlights]
    highlights = []
    
    # Split the text into sentences
    sentences = text.split('.')
    
    for keyword in keywords:
        for sentence in sentences:
            # Check if keyword is in the sentence and avoid duplicates
            if keyword in sentence and sentence not in highlights:
                highlights.append(sentence.strip())
                break
    
    return highlights

# Streamlit UI Setup
st.title("Audio Transcription with Summarization and Keyword Extraction")

# Initialize transcript variable
transcript = None

# Input for YouTube video URL
video_url = st.text_input("Enter YouTube video URL:")

if video_url:
    if st.button("Download Audio"):
        with st.spinner("Downloading audio..."):
            audio_path = download_audio(video_url)
            if audio_path:
                st.success(f"Audio downloaded and saved to {audio_path}")
            else:
                st.error("Failed to download audio")

# Input for audio file
audio_file = st.file_uploader("Upload Audio File (MP3)", type=["mp3"])

if audio_file:
    lang_choice = get_language_choice()  # Select language for transcription
    
    if st.button("Transcribe Audio"):
        with st.spinner("Transcribing..."):
            transcript = transcribe_audio_reverie(audio_file, lang_choice)
            if transcript:
                st.write("### Transcription")
                st.write(transcript)
                
                # Step 1: Key Highlights
                st.write("### Key Highlights")
                highlights = extract_key_highlights(transcript, num_highlights=5)
                for i, highlight in enumerate(highlights):
                    st.write(f"{i+1}. {highlight}")
                
                # Step 2: Summary
                st.write("### Summary")
                summary_level = st.radio("Choose summary level:", ["Small", "Medium", "Large"], index=1)
                summary = summarize_text(transcript, level=summary_level.lower())
                st.text_area("Summary:", summary, height=150)
            
            else:
                st.error("Failed to transcribe the audio file.")

# Optional: Save transcription to file
if transcript:
    st.download_button(
        label="Download Transcription",
        data=transcript,
        file_name="transcription.txt",
        mime="text/plain"
    )

# Clear cache button
if st.button('Clear Cache'):
    st.cache_data.clear()
    st.success("Cache cleared!")
