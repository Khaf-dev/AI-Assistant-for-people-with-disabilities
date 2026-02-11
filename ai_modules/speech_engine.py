import speech_recognition as sr
import pyttsx3
import asyncio
from gtts import gTTS
import os
import tempfile
from typing import Optional, Any
import threading
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SpeechEngine:
    def __init__(self, language="en", config_path="config.yaml"):
        print("Initializing Speech Engine...")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Configuration (set before setup_tts)
        self.language = language
        self.speech_rate = self.config.get('speech', {}).get('speech_rate', 150)
        self.use_google_tts = self.config.get('speech', {}).get('use_google_tts', False)
        
        # Load language configurations
        self.language_configs = self.config.get('speech', {}).get('languages', {})
        self.current_lang_config = self.language_configs.get(language, {})
        
        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # initialize STT recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return {}
    
    def set_language(self, language: str) -> bool:
        """Change the language dynamically"""
        if language not in self.language_configs:
            print(f"Language '{language}' not supported. Available: {list(self.language_configs.keys())}")
            return False
        
        self.language = language
        self.current_lang_config = self.language_configs[language]
        self.setup_tts()
        print(f"Language changed to: {self.current_lang_config.get('name', language)}")
        return True
    
    def get_available_languages(self) -> dict:
        """Get all available languages"""
        return {code: config.get('name', code) for code, config in self.language_configs.items()}
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.language
    
    def get_language_name(self, code: Optional[str] = None) -> str:
        """Get readable language name"""
        target_code = code if code is not None else self.language
        return self.language_configs.get(target_code, {}).get('name', target_code)
            
    def setup_tts(self) -> None:
        """Setup TTS Engine properties"""
        try:
            voices: Any = self.tts_engine.getProperty("voices")
            
            # Get voice ID from config, fallback to first available
            voice_id = self.current_lang_config.get('voice_id', 0)
            if isinstance(voices, list) and voice_id < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_id].id)
        except Exception as e:
            logger.debug(f"Error setting up TTS voice: {e}")
        
        # Set rate and volume
        self.tts_engine.setProperty('rate', self.speech_rate)
        self.tts_engine.setProperty('volume', 1.0)
        
    def speak(self, text: str, use_google: Optional[bool] = None) -> None:
        """Convert text to speech
        
        Args:
            text: Text to speak
            use_google: Override default TTS provider. None uses config default
        """
        use_google = use_google if use_google is not None else self.use_google_tts
        
        if use_google:
            # Use google tts for better quality (requires internet)
            gtts_lang = self.current_lang_config.get('gtts_lang', self.language)
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Save to temp file and play
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                os.system(f"mpg123 {fp.name}")
                os.unlink(fp.name)
        else:
            # Use offline TTS
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
    async def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for speech and convert to text"""
        loop = asyncio.get_event_loop()
        
        try:
            # Run blocking recognition in thread
            text = await loop.run_in_executor(
                None,
                self._recognize_speech,
                timeout
            )
            return text
        
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None
        
    def _recognize_speech(self, timeout: int) -> Optional[str]:
        """Blocking speech recognition with language support"""
        with self.microphone as source:
            print(f"Listening for {self.get_language_name()}...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=10
                )
                
                # Get recognition language from config
                recognition_lang = self.current_lang_config.get('recognition_lang', f"{self.language}-{self.language.upper()}")
                
                # Recognize using Google Speech Recognition
                try:
                    text = self.recognizer.recognize_google(  # type: ignore
                        audio,
                        language=recognition_lang
                    )
                except AttributeError:
                    # Fallback if recognize_google not available
                    logger.error("recognize_google not available")
                    return None
                
                print(f"Recognized ({self.language}): {text}")
                return text
            
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                print(f"Could not understand audio in {self.get_language_name()}")
                return None
            except sr.RequestError as e:
                print(f"Recognition service error: {e}")
                return None
        
    def _set_voice_properties(self, rate=None, volume=None, voice_id=None):
        """Adjust voice properties"""
        if rate:
            self.tts_engine.setProperty('rate', rate)
        if volume:
            self.tts_engine.setProperty('volume', volume)
        if voice_id:
            self.tts_engine.setProperty('voice_id', voice_id)
            
    def stop(self):
        """Stop speech engine"""
        self.tts_engine.stop()