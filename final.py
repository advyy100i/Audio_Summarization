
import streamlit as st
import os

import yt_dlp
import whisper
from rake_nltk import Rake
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re
import spacy
import io
import feedparser
import base64
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

# Add this line after your imports
add_bg_from_local('microphone.png')  # Adjust path as needed
# Load spaCy's pre-trained English model
nlp = spacy.load("en_core_web_sm")

# Function to extract video ID from URL
def extract_video_id(url):
    video_id = None
    match = re.search(r'(?:youtube\.com\/(?:[^\/\n]+\/[^\n]+\/|(?:v|e(?:mbed)?)\/|\S+?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]+)', url)
    if match:
        video_id = match.group(1)
    return video_id

@st.cache_data
def download_audio(video_url, output_folder="audio"):
    """
    Download audio from the YouTube video and save it with the video ID as the filename.
    """
    # Extract video ID
    video_id = extract_video_id(video_url)
    if not video_id:
        st.error("Unable to extract video ID from the URL")
        return None, None
    
    # Set output path
    output_path = os.path.join(output_folder, f"{video_id}.mp3")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioquality': 1,
        'outtmpl': output_path,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        title = info_dict.get('title', 'Unknown Title')
    
    return output_path, title

@st.cache_data
def extract_podcast_audio(feed_url, episode_title, output_folder="audio"):
    """
    Download audio from the podcast RSS feed and save it with the episode title as the filename.
    """
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        st.error("Unable to parse RSS feed or no entries found")
        return None, None
    
    # Find the selected episode
    episode = next((entry for entry in feed.entries if entry.title == episode_title), None)
    if not episode:
        st.error("Selected episode not found in the RSS feed")
        return None, None
    
    audio_url = episode.enclosures[0].href
    title = re.sub(r'[\\/*?:"<>|]', "", episode.title)  # Clean title for filename
    
    # Set output path
    output_path = os.path.join(output_folder, f"{title}.mp3")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioquality': 1,
        'outtmpl': output_path,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([audio_url])
    
    return output_path, title

@st.cache_data
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcript = result['text']
    segments = result['segments']
    return transcript, segments

def summarize_text(text, level="medium"):
    sentence_count = {"small": 5, "medium": 10, "large": 20}.get(level, 7)
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join([str(sentence) for sentence in summary])

def extract_key_highlights(text, num_highlights=5, max_sentence_length=30):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    keywords = rake.get_ranked_phrases()[:num_highlights]
    highlights = []
    
    # Split the text into sentences
    sentences = text.split('.')
    
    for keyword in keywords:
        for sentence in sentences:
            # Check if keyword is in the sentence and avoid duplicates
            if keyword in sentence and sentence not in highlights:
                # Limit the sentence length
                words = sentence.split()
                if len(words) > max_sentence_length:
                    sentence = ' '.join(words[:max_sentence_length]) + ''
                highlights.append(sentence.strip())
                break
    
    return highlights

def generate_chapters(segments, chapter_duration=120):
    chapters = []
    current_chapter = {"start": 0, "text": ""}
    for segment in segments:
        current_chapter["text"] += " " + segment["text"]
        if segment["start"] - current_chapter["start"] >= chapter_duration:
            chapters.append(current_chapter)
            current_chapter = {"start": segment["start"], "text": ""}
    if current_chapter["text"]:
        chapters.append(current_chapter)
    return chapters

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

def search_transcript(word, segments):
    occurrences = []
    for segment in segments:
        if word.lower() in segment['text'].lower():
            occurrences.append({
                "time": format_time(segment['start']),
                "sentence": segment['text']
            })
    return occurrences

def extract_important_nouns(text):
    """
    Extracts important proper nouns (persons, organizations, locations) from the transcript text using spaCy's NER.
    """
    doc = nlp(text)
    important_nouns = []
    
    # Extract named entities such as PERSON, ORG, GPE (Geo-political entity)
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE"]:  # Important entities like people, organizations, locations
            important_nouns.append(ent.text)
    
    # Return the unique proper nouns found
    return list(set(important_nouns))  # Remove duplicates

def download_transcript(segments):
    # Create a text buffer
    buf = io.StringIO()
    for segment in segments:
        buf.write(f"[{format_time(segment['start'])}] {segment['text']}\n")
    buf.seek(0)
    return buf

# Streamlit UI Setup
st.title("YouTube and Podcast Chapterizer with Key Highlights and Searchable Transcript")

# Button to clear cache
if st.button('Clear Cache'):
    st.cache_data.clear()
    st.success("Cache cleared!")

# Rest of the code as before
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "segments" not in st.session_state:
    st.session_state.segments = None
if "title" not in st.session_state:
    st.session_state.title = None
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None
if "episodes" not in st.session_state:
    st.session_state.episodes = None

input_type = st.radio("Select Input Type:", ["YouTube Video URL", "Podcast RSS Feed URL"])

if input_type == "YouTube Video URL":
    url = st.text_input("Enter YouTube video URL:")
    if url:
        if st.session_state.title is None:
            with st.spinner("Downloading audio..."):
                audio_path, title = download_audio(url)
                st.session_state.audio_path = audio_path
                st.session_state.title = title
                st.success(f"Downloaded: {title}")

elif input_type == "Podcast RSS Feed URL":
    url = st.text_input("Enter Podcast RSS Feed URL:")
    if url:
        if st.session_state.episodes is None:
            with st.spinner("Fetching episodes..."):
                feed = feedparser.parse(url)
                st.session_state.episodes = [entry.title for entry in feed.entries]
        
        episode_title = st.selectbox("Select Episode", st.session_state.episodes)
        if episode_title and st.session_state.title is None:
            with st.spinner("Downloading audio..."):
                audio_path, title = extract_podcast_audio(url, episode_title)
                st.session_state.audio_path = audio_path
                st.session_state.title = title
                st.success(f"Downloaded: {title}")

if st.session_state.title:
    st.write(f"### Title: {st.session_state.title}")

    if st.session_state.transcript is None:
        with st.spinner("Transcribing audio..."):
            transcript, segments = transcribe_audio(st.session_state.audio_path)
            st.session_state.transcript = transcript
            st.session_state.segments = segments
            st.success("Transcription completed!")

    st.write("### Chapters")
    chapter_duration = st.slider("Chapter Duration (in seconds):", 60, 1800, 120)
    chapters = generate_chapters(st.session_state.segments, chapter_duration)
    for i, chapter in enumerate(chapters):
        with st.expander(f"Chapter {i+1} ({format_time(chapter['start'])} onwards):"):
            st.write(chapter["text"])  # Show full chapter text

    # Step 4: Key Highlights for Each Chapter
    st.write("### Key Highlights")
    for i, chapter in enumerate(chapters):
        st.write(f"**Chapter {i+1} Highlights ({format_time(chapter['start'])}):**")
        highlights = extract_key_highlights(chapter["text"], num_highlights=3)
        for j, highlight in enumerate(highlights):
            st.write(f"{j+1}. {highlight}")

    # Step 5: Overall Summary
    st.write("### Summary")
    summary_level = st.radio("Choose summary level:", ["Small", "Medium", "Large"], index=1)
    summary = summarize_text(st.session_state.transcript, level=summary_level.lower())
    st.text_area("Summary:", summary, height=150)

    # Step 6: Searchable Transcript
    st.write("### Searchable Transcript")
    search_query = st.text_input("Enter a word or phrase to search in the transcript:")
    if search_query:
        results = search_transcript(search_query, st.session_state.segments)
        if results:
            st.write(f"Found {len(results)} occurrences of '{search_query}':")
            for result in results:
                st.write(f"- **{result['time']}:** {result['sentence']}")
        else:
            st.warning(f"No occurrences of '{search_query}' found.")

    # Step 7: Extract Important Keywords (Proper Nouns)
    st.write("### Important Keywords (Proper Nouns)")
    important_keywords = extract_important_nouns(st.session_state.transcript)

    if important_keywords:
        st.write(", ".join(important_keywords))
    else:
        st.write("No important proper nouns found.")

    # Step 8: Download Transcript
    if st.session_state.segments:
        st.download_button(
            label="Download Transcript",
            data=download_transcript(st.session_state.segments).getvalue(),
            file_name="transcript.txt",
            mime="text/plain"
        )
    else:
        st.warning("No transcript available to download.")
