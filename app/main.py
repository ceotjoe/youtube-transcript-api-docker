# app/main.py
from fastapi import FastAPI, HTTPException, Query, Security, Depends
from fastapi.security import APIKeyHeader, APIKeyQuery
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, NoVideosGiven
from typing import List, Optional

# --- API Key Configuration ---
# In a real application, these keys would come from:
# - Environment variables (RECOMMENDED for production)
# - A database
# - A configuration file (less secure if committed to git)

# For this PoC, we'll use a hardcoded set.
# DO NOT hardcode API keys in a production environment!
# Example: export API_KEY_1="your_secret_key_1"
# API_KEYS = {os.getenv("API_KEY_1"), os.getenv("API_KEY_2")} etc.
# For simplicity in this PoC:
API_KEYS = {
    "my-secret-api-key-123", # Replace with your actual keys
    "another-secret-key-456" # Add more as needed
}

# Define where the API key is expected:
# 1. In a header named 'X-API-Key'
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
# 2. As a query parameter named 'api_key' (less secure for production but useful for quick testing)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    header_api_key: Optional[str] = Security(api_key_header),
    query_api_key: Optional[str] = Security(api_key_query)
) -> str:
    """
    Dependency function to validate API key from header or query parameter.
    """
    if header_api_key in API_KEYS:
        return header_api_key
    if query_api_key in API_KEYS:
        return query_api_key
    
    # If no valid key is found, raise an HTTPException
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API Key. Provide it in 'X-API-Key' header or 'api_key' query parameter."
    )

# --- End API Key Configuration ---


app = FastAPI(
    title="YouTube Transcript API Service",
    description="An API to fetch transcripts for YouTube videos.",
    version="1.0.0"
)

@app.get("/")
async def root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to the YouTube Transcript API Service! Use /transcript/{video_id} endpoint."}

# Protect the /transcript endpoint with API key authentication
@app.get("/transcript/{video_id}")
async def get_video_transcript(
    video_id: str,
    api_key: str = Depends(get_api_key), # Add this line to require API key
    lang: Optional[str] = Query(None, description="Specify a preferred language code (e.g., 'en', 'de', 'es'). If not found, it will try to find other languages. If multiple, it will try to find the first one in the list."),
    all_langs: bool = Query(False, description="Set to true to return all available language transcripts' metadata instead of just one transcript.")
):
    """
    Fetches the transcript for a given YouTube video ID.
    Requires a valid API Key in 'X-API-Key' header or 'api_key' query parameter.

    - **video_id**: The ID of the YouTube video.
    - **lang** (optional): Preferred language code (e.g., 'en', 'de').
    - **all_langs** (optional): If true, returns metadata for all available transcript languages.
    """
    # The API key has already been validated by the Depends(get_api_key) dependency
    # You can optionally use the 'api_key' variable here if you need to log or track which key was used.
    print(f"API Key used: {api_key}") # For logging/debugging purposes

    try:
        if all_langs:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_transcripts = []
            for transcript in transcript_list:
                available_transcripts.append({
                    "language": transcript.language,
                    "language_code": transcript.language_code,
                    "is_generated": transcript.is_generated,
                    "is_translatable": transcript.is_translatable,
                })
            return {
                "video_id": video_id,
                "type": "available_languages",
                "available_transcripts": available_transcripts
            }
        else:
            languages = [lang] if lang else []
            
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            return {
                "video_id": video_id,
                "type": "transcript_content",
                "language": lang if lang else "auto-detected",
                "transcript": transcript_data
            }

    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found for this video in the specified language or any available language.")
    except TranscriptsDisabled:
        raise HTTPException(status_code=403, detail="Transcripts are disabled for this video by the video owner.")
    except NoVideosGiven:
        raise HTTPException(status_code=400, detail="Invalid request: No video ID provided or invalid format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")=f"An unexpected server error occurred: {str(e)}")
