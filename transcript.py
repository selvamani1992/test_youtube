from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
import os


def extract_video_id(url: str) -> str:

    parsed_url = urlparse(url)

    # Case 1: Standard watch URL
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        query = parse_qs(parsed_url.query)
        if 'v' in query:
            return query['v'][0]

    # Case 2: Shortened youtu.be URL
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path.lstrip('/')

    # Case 3: Embed or share formats
    pattern = r"(?:embed/|v/|shorts/|watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)

    raise ValueError("❌ Could not extract YouTube video ID from URL.")


def clean_transcript(text: str) -> str:
    # 1. Remove timestamps [00:00] or (00:00)
    text = re.sub(r'\[?\(?\d{1,2}:\d{2}(?::\d{2})?\)?\]?', ' ', text)

    # 2. Remove speaker labels (e.g., "Speaker 1:")
    text = re.sub(r'\b[A-Z][a-z]+: ', '', text)

    # 3. Remove non-verbal cues like [Music], [Applause]
    text = re.sub(r'\[.*?\]', ' ', text)

    # 4. Remove filler words (optional)
    fillers = r'\b(uh|um|erm|like|you know|i mean|sort of|kind of|basically|Ooh|ooh|OOH|Ah|ah|AH)\b'
    text = re.sub(fillers, ' ', text, flags=re.IGNORECASE)

    # 5. Remove URLs and hashtags
    text = re.sub(r'http\S+|www\S+|#\S+', ' ', text)

    # 6. Remove emojis and symbols
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # 7. Remove excessive punctuation
    text = re.sub(r'([!?.,])\1+', r'\1', text)

    # 8. Replace multiple commas with a single comma
    text = re.sub(r',\s*(,|\s)+', ', ', text)

    # 9. Replace multiple periods (...) with a single period
    text = re.sub(r'\.{2,}', '.', text)

    # 10. Replace multiple question marks or exclamation marks
    text = re.sub(r'([!?])\1+', r'\1', text)

    # 11. Clean up space before punctuation
    text = re.sub(r'\s+([,.!?])', r'\1', text)

    # 12. Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def get_youtube_transcript(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        full_text = ""

        for snippet in fetched_transcript:
            full_text += snippet.text
        cleaned_text = clean_transcript(full_text)

        return cleaned_text
    except TranscriptsDisabled:
        print("❌ Captions are disabled for this video.")
        return False
    except NoTranscriptFound:
        print("❌ No transcript available for this video.")
        return False

