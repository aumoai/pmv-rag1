import asyncio
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class SpeechToText:
    """
    Speech-to-text processor using Whisper (supports multiple implementations)
    """

    def __init__(self):
        self.model: Any = None
        self.model_name: str = "base"  # Can be "tiny", "base", "small", "medium", "large"
        self.whisper_type: str | None = None  # "openai", "faster", or "whisperx"

    async def load_model(self, model_name: str = "base", whisper_type: str = "auto"):
        """
        Load Whisper model asynchronously
        """
        try:
            if (
                self.model is None
                or self.model_name != model_name
                or self.whisper_type != whisper_type
            ):
                logger.info(f"Loading Whisper model: {model_name} (type: {whisper_type})")

                # Auto-detect available Whisper implementation
                if whisper_type == "auto":
                    whisper_type = self._detect_whisper_implementation()

                self.whisper_type = whisper_type
                self.model_name = model_name

                if whisper_type == "faster":
                    await self._load_faster_whisper(model_name)
                elif whisper_type == "openai":
                    await self._load_openai_whisper(model_name)
                elif whisper_type == "whisperx":
                    await self._load_whisperx(model_name)
                else:
                    raise ValueError(f"Unsupported Whisper type: {whisper_type}")

                logger.info(f"Whisper model {model_name} loaded successfully ({whisper_type})")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise

    def _detect_whisper_implementation(self) -> str:
        """
        Auto-detect available Whisper implementation
        """
        from importlib.util import find_spec

        if find_spec("faster_whisper"):
            return "faster"
        elif find_spec("whisper"):
            return "openai"
        elif find_spec("whisperx"):
            return "whisperx"
        else:
            raise ImportError(
                "No Whisper implementation found. Install faster-whisper, openai-whisper, or whisperx"
            )

    async def _load_faster_whisper(self, model_name: str):
        """
        Load faster-whisper model
        """
        import faster_whisper  # pyright: ignore[reportMissingImports]

        self.model = await asyncio.to_thread(faster_whisper.WhisperModel, model_name)

    async def _load_openai_whisper(self, model_name: str):
        """
        Load OpenAI Whisper model
        """
        import whisper  # pyright: ignore[reportMissingImports]

        self.model = await asyncio.to_thread(whisper.load_model, model_name)

    async def _load_whisperx(self, model_name: str):
        """
        Load WhisperX model
        """
        import whisperx  # pyright: ignore[reportMissingImports]

        self.model = await asyncio.to_thread(whisperx.load_model, model_name)

    async def transcribe(self, audio_file_path: str, model_name: str = "base") -> str:
        """
        Transcribe audio file to text
        """
        try:
            # Load model if not loaded
            await self.load_model(model_name)

            # Check if file exists
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

            # Transcribe audio based on implementation
            logger.info(f"Transcribing audio file: {audio_file_path}")

            if self.whisper_type == "faster":
                result = await self._transcribe_faster_whisper(audio_file_path)
            elif self.whisper_type == "openai":
                result = await self._transcribe_openai_whisper(audio_file_path)
            elif self.whisper_type == "whisperx":
                result = await self._transcribe_whisperx(audio_file_path)
            else:
                raise ValueError(f"Unsupported Whisper type: {self.whisper_type}")

            # Extract transcription text
            transcription = result.get("text", "").strip()

            if not transcription:
                logger.warning("No transcription generated from audio file")
                return ""

            logger.info(f"Transcription completed: {len(transcription)} characters")
            return transcription

        except Exception as e:
            logger.error(f"Error transcribing audio {audio_file_path}: {str(e)}")
            raise

    async def _transcribe_faster_whisper(self, audio_file_path: str) -> dict[str, Any]:
        """
        Transcribe using faster-whisper
        """
        segments, _ = await asyncio.to_thread(self.model.transcribe, audio_file_path)
        text = " ".join([segment.text for segment in segments])
        return {"text": text}

    async def _transcribe_openai_whisper(self, audio_file_path: str) -> dict[str, Any]:
        """
        Transcribe using OpenAI Whisper
        """
        return await asyncio.to_thread(self.model.transcribe, audio_file_path)

    async def _transcribe_whisperx(self, audio_file_path: str) -> dict[str, Any]:
        """
        Transcribe using WhisperX
        """
        result = await asyncio.to_thread(self.model.transcribe, audio_file_path)
        return {"text": result["segments"][0]["text"] if result["segments"] else ""}

    async def transcribe_with_timestamps(
        self, audio_file_path: str, model_name: str = "base"
    ) -> dict[str, Any]:
        """
        Transcribe audio with timestamps
        """
        try:
            # Load model if needed
            await self.load_model(model_name)

            # Check if file exists
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

            # Transcribe with word-level timestamps
            logger.info(f"Transcribing audio with timestamps: {audio_file_path}")
            result = await asyncio.to_thread(
                self.model.transcribe, audio_file_path, word_timestamps=True
            )

            return result

        except Exception as e:
            logger.error(f"Error transcribing audio with timestamps {audio_file_path}: {str(e)}")
            raise

    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported languages for transcription
        """
        return [
            "en",
            "zh",
            "de",
            "es",
            "ru",
            "ko",
            "fr",
            "ja",
            "pt",
            "tr",
            "pl",
            "ca",
            "nl",
            "ar",
            "sv",
            "it",
            "id",
            "hi",
            "fi",
            "vi",
            "he",
            "uk",
            "el",
            "ms",
            "cs",
            "ro",
            "da",
            "hu",
            "ta",
            "no",
            "th",
            "ur",
            "hr",
            "bg",
            "lt",
            "la",
            "mi",
            "ml",
            "cy",
            "sk",
            "te",  # codespell:ignore
            "fa",
            "lv",
            "bn",
            "sr",
            "az",
            "sl",
            "kn",
            "et",
            "mk",
            "br",
            "eu",
            "is",
            "hy",
            "ne",
            "mn",
            "bs",
            "kk",
            "sq",
            "sw",
            "gl",
            "mr",
            "pa",
            "si",
            "km",
            "sn",
            "yo",
            "so",
            "af",
            "oc",
            "ka",
            "be",
            "tg",
            "sd",
            "gu",
            "am",
            "yi",
            "lo",
            "uz",
            "fo",  # codespell:ignore
            "ht",
            "ps",
            "tk",
            "nn",
            "mt",
            "sa",
            "lb",
            "my",
            "bo",
            "tl",
            "mg",
            "as",
            "tt",
            "haw",
            "ln",
            "ha",
            "ba",
            "jw",
            "su",
        ]

    def get_model_info(self) -> dict[str, Any]:
        """
        Get information about the loaded model
        """
        return {
            "model_name": self.model_name,
            "model_loaded": self.model is not None,
            "supported_languages": self.get_supported_languages(),
        }

    def synthesize_speech(
        self, text: str, output_path: str, voice: str | None = None, rate: int | None = None
    ) -> bool:
        """
        Synthesize speech from text and save to output_path (Text-to-Speech)
        Uses pyttsx3 for cross-platform TTS.
        """
        try:
            import pyttsx3  # pyright: ignore[reportMissingImports]

            engine = pyttsx3.init()
            if voice:
                engine.setProperty("voice", voice)
            if rate:
                engine.setProperty("rate", rate)
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            logger.info(f"Synthesized speech saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            return False
