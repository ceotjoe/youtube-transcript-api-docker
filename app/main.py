# app/main.py
from fastapi import FastAPI, HTTPException, Query, Security, Depends
from fastapi.security import APIKeyHeader, APIKeyQuery
# Corrected import: Removed NoVideosGiven
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, CouldNotRetrieveTranscript
from typing import List, Optional

# --- API Key Configuration ---
API_KEYS = {
    "my-secret-api-key-123", # Replace with your actual keys
    "another-secret-key-456" # Add more as needed
}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

async def get_api_key(
    header_api_key: Optional[str] = Security(api_key_header),
    query_api_key: Optional[str] = Security(api_key_query)
) -> str:
    if header_api_key in API_KEYS:
        return header_api_key
    if query_api_key in API_KEYS:
        return query_api_key
    
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
    return {"message": "Welcome to the YouTube Transcript API Service! Use /transcript/{video_id} endpoint."}

@app.get("/transcript/{video_id}")
async def get_video_transcript(
    video_id: str,
    api_key: str = Depends(get_api_key),
    lang: Optional[str] = Query(None, description="Specify a preferred language code (e.g., 'en', 'de', 'es'). If not found, it will try to find other languages. If multiple, it will try to find the first one in the list."),
    all_langs: bool = Query(False, description="Set to true to return all available language transcripts' metadata instead of just one transcript."),
    plain_text: bool = Query(False, description="Set to true to receive the transcript as a single block of plain text, without timestamps or segments.")
):
    """
    Fetches the transcript for a given YouTube video ID.
    Requires a valid API Key in 'X-API-Key' header or 'api_key' query parameter.

    - **video_id**: The ID of the YouTube video.
    - **lang** (optional): Preferred language code (e.g., 'en', 'de').
    - **all_langs** (optional): If true, returns metadata for all available transcript languages.
    - **plain_text** (optional): If true, returns transcript as plain text string.
    """
    print(f"API Key used: {api_key}")

    if not video_id:
        raise HTTPException(status_code=400, detail="Video ID cannot be empty.")

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

            if plain_text:
                full_text_transcript = " ".join([segment['text'] for segment in transcript_data])
                return {
                    "video_id": video_id,
                    "type": "plain_text_transcript",
                    "language": lang if lang else "auto-detected",
                    "transcript": full_text_transcript
                }
            else:
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
    except CouldNotRetrieveTranscript:
        # Catch a more general error if YouTube's scraping fails for other reasons
        raise HTTPException(status_code=500, detail="Could not retrieve transcript. This may be due to a temporary issue with YouTube or aggressive scraping detection.")
    except Exception as e:
        # A catch-all for any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")
