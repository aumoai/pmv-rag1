import os
import uuid
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from pmv_rag1.config import Config
from pmv_rag1.processors.speech_to_text import SpeechToText
from pmv_rag1.services.orchestrator import Orchestrator
from pmv_rag1.utils.audio_utils import convert_audio_format, validate_audio_file

router = APIRouter()


class SpeechResponse(BaseModel):
    transcription: str
    response: str
    audio_file_id: str


# Initialize services
speech_to_text = SpeechToText()
orchestrator = Orchestrator()


@router.post("/speech", response_model=SpeechResponse)
async def handle_speech(audio_file: Annotated[UploadFile, File(...)]):
    """
    Handle speech input: convert to text and process with RAG
    """
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    if not audio_file.size:
        raise HTTPException(status_code=400, detail="Empty file provided")

    try:
        # Validate audio file
        if not validate_audio_file(audio_file.filename):
            raise HTTPException(
                status_code=400, detail="Invalid audio file format. Supported: .wav, .mp3, .m4a"
            )

        # Check file size
        if audio_file.size and audio_file.size > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Audio file too large. Maximum size: {Config.MAX_FILE_SIZE // (1024 * 1024)}MB",
            )

        # Generate unique file ID
        audio_file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(audio_file.filename)[1]

        # Save audio file temporarily
        temp_audio_path = os.path.join(Config.TEMP_AUDIO_DIR, f"{audio_file_id}{file_extension}")

        with open(temp_audio_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)

        wav_path = None
        try:
            # Convert audio to WAV if needed for Whisper
            wav_path = await convert_audio_format(temp_audio_path)

            # Transcribe audio to text
            transcription = await speech_to_text.transcribe(wav_path)

            if not transcription.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Could not transcribe audio. Please ensure clear speech.",
                )

            # Process the transcribed text with RAG
            response = await orchestrator.handle_text(transcription)

            return SpeechResponse(
                transcription=transcription, response=response, audio_file_id=audio_file_id
            )

        finally:
            # Clean up temporary files
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            if wav_path and os.path.exists(wav_path) and wav_path != temp_audio_path:
                os.remove(wav_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing speech: {str(e)}") from e


@router.post("/speech-stream")
async def handle_speech_stream():
    """
    Handle streaming speech input (placeholder for future implementation)
    """
    return {"message": "Streaming speech feature coming soon"}
