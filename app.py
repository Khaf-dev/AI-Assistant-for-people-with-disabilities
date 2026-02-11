"""Vision Assistant - Main Application Entry Point"""
import sys
import os
import asyncio
import logging
import yaml
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VisionAssistant:
    """Main Vision Assistant Application"""
    
    def __init__(self, language: Optional[str] = None):
        """Initialize Vision Assistant
        
        Args:
            language: Language code (en, id, es, fr, de, pt, ja, zh). Defaults to config.yaml
        """
        logger.info("Initializing Vision Assistant for Visually Impaired...")
        
        try:
            # Load configuration
            self.config = self._load_config()
            
            # Determine language
            if language is None:
                language = self.config.get('speech', {}).get('language', 'en')
            self.language: str = language if isinstance(language, str) else 'en'
            
            # Import modules
            from ai_modules.vision_processor import VisionProcessor
            from ai_modules.speech_engine import SpeechEngine
            from ai_modules.llm_handler import LLMHandler
            from ai_modules.sound_localization import SoundLocalizer
            from features.navigation import NavigationAssistant
            from features.face_recognition import FaceRecognizer
            from database.db_handler import DatabaseHandler
            
            # Initialize core modules with language support
            self.vision = VisionProcessor()
            self.speech = SpeechEngine(language=self.language)
            self.llm = LLMHandler()
            self.navigation = NavigationAssistant()
            self.face_recognizer = FaceRecognizer(enable_recognition=True)
            self.sound_localizer = SoundLocalizer()
            self.db = DatabaseHandler()
            
            # State management
            self.is_listening = False
            self.is_processing = False
            self.enrollment_mode = False
            self.enrollment_person_name = None
            self.user_context = {
                'language': self.language,
                'language_name': self.speech.get_language_name()
            }
            
            # Initialize services
            self._setup_services()
            
            logger.info("Vision Assistant initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vision Assistant: {e}")
            raise
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            config_file = Path(__file__).parent / 'config.yaml'
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
            return {}
        
    def _setup_services(self):
        """Setup all required services"""
        logger.info("Setting up services...")
        
        try:
            # Load user preferences
            self.user_context = self.db.get_user_preferences()
            
            # Initialize voice
            self.speech.speak("Vision Assistant initialized. How can I assist you today?")
            
            logger.info("Services setup complete!")
            
        except Exception as e:
            logger.warning(f"Warning during service setup: {e}")
        
    async def continuous_assistant(self):
        """Main assistant event loop"""
        logger.info("Starting continuous assistant mode...")
        
        try:
            while True:
                try:
                    # Listen for voice command
                    command = await self.speech.listen()
                    
                    if command:
                        logger.info(f"Command received: {command}")
                        await self.process_command(command)
                    
                    # Continuous scene description if enabled
                    if self.user_context.get('continuous_mode', False):
                        await self.describe_environment()
                    
                    await asyncio.sleep(0.5)
                    
                except KeyboardInterrupt:
                    logger.info("User exit detected. Shutting down...")
                    break
                except Exception as e:
                    logger.error(f"Error in assistant loop: {e}")
        
        except Exception as e:
            logger.error(f"Fatal error in continuous assistance: {e}")
                
    async def process_command(self, command: str):
        """Process user voice commands"""
        logger.info(f"Processing command: {command}")
        
        # Give immediate feedback
        self.speech.speak(f"Processing your request: {command}")
        
        try:
            # Check for language switching command
            if any(phrase in command.lower() for phrase in ['change language', 'switch language', 'language to', 'speak']):
                await self._handle_language_switch(command)
                return
            
            # Check for face enrollment commands
            if any(phrase in command.lower() for phrase in ['enroll', 'register face', 'teach', 'learn my face', 'save face', 'remember', 'add person']):
                await self._handle_face_enrollment(command)
                return
            
            # Check for face management commands
            if any(phrase in command.lower() for phrase in ['forget', 'remove person', 'delete face', 'forget face', 'who do you know', 'list people']):
                await self._handle_face_management(command)
                return
            
            # Check for audio assistance commands
            if any(phrase in command.lower() for phrase in ['listen', 'sound', 'audio', 'what do you hear', 'detect sounds', 'obstacle', 'check ahead', 'scan audio']):
                await self._handle_audio_assistance(command)
                return
            
            # Parse intent
            intent = await self.llm.understand_intent(command, self.user_context)
            
            # Give feedback on what will be done
            if intent.get('action') == 'describe_scene':
                self.speech.speak("Analyzing your surroundings...")
                await self.describe_environment(detailed=True)
            
            elif intent.get('action') == 'read_text':
                self.speech.speak("Looking for text in your environment...")
                await self.read_text_around()
            
            elif intent.get('action') == 'recognize_objects':
                self.speech.speak("Identifying objects around you...")
                await self.identify_objects()
            
            elif intent.get('action') == 'navigate':
                self.speech.speak("Getting navigation information...")
                await self.assist_navigation(intent.get('parameters', {}))
            
            elif intent.get('action') == 'recognize_people':
                self.speech.speak("Scanning for faces...")
                await self.recognize_faces()
            
            elif intent.get('action') == 'emergency':
                self.speech.speak("Activating emergency alert...")
                await self.handle_emergency()
            
            elif intent.get('action') == 'exit':
                await self.handle_exit()
                raise KeyboardInterrupt("User requested exit")
            
            elif intent.get('action') == 'general_question':
                response = await self.llm.generate_response(command)
                self.speech.speak(response)
            
            else:
                self.speech.speak("I didn't quite understand that. Could you repeat?")
        
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.speech.speak("I encountered an error processing your request. Please try again.")
            
    async def describe_environment(self, detailed=False):
        """Describe the current environment"""
        try:
            # Capture image from camera
            image = self.vision.capture_image()
            
            if image is not None:
                # Provide feedback that processing is happening
                if detailed:
                    self.speech.speak("Analyzing scene in detail...")
                else:
                    self.speech.speak("Scanning environment...")
                
                # Get description
                if detailed:
                    description = await self.vision.describe_scene_detailed(image)
                else:
                    description = await self.vision.describe_scene_brief(image)
                
                # Speak description
                if description:
                    self.speech.speak(description)
                    logger.info(f"Scene: {description}")
                else:
                    self.speech.speak("Unable to analyze scene at this moment.")
                
                # Store in context
                self.user_context['last_scene'] = description
            else:
                self.speech.speak("Camera is not available. Please check your camera connection.")
                logger.warning("No camera feed available")
        
        except Exception as e:
            logger.error(f"Error describing environment: {e}")
            self.speech.speak("I encountered an error analyzing the scene.")
        
    async def read_text_around(self):
        """Read any text in the environment"""
        try:
            image = self.vision.capture_image()
            if image is not None:
                self.speech.speak("Scanning for text...")
                texts = await self.vision.extract_text(image)
                
                if texts:
                    self.speech.speak(f"I found {len(texts)} text regions. Reading them now.")
                    for i, text in enumerate(texts[:5], 1):
                        self.speech.speak(f"Text {i}: {text}")
                        logger.info(f"Extracted text {i}: {text}")
                else:
                    self.speech.speak("I don't see any readable text around you.")
            else:
                self.speech.speak("Camera not available for text reading.")
        except Exception as e:
            logger.error(f"Error reading text: {e}")
            self.speech.speak("I couldn't read text from the scene.")
            
    async def identify_objects(self):
        """Identify objects in view"""
        try:
            image = self.vision.capture_image()
            if image is not None:
                self.speech.speak("Identifying objects in your surroundings...")
                objects = await self.vision.detect_objects(image)
                
                if objects:
                    object_list = ", ".join([obj.get('name', 'Unknown') for obj in objects[:5]])
                    self.speech.speak(f"I can see the following objects: {object_list}")
                    logger.info(f"Detected objects: {object_list}")
                else:
                    self.speech.speak("I don't detect any specific objects nearby.")
            else:
                self.speech.speak("Camera not available for object detection.")
        except Exception as e:
            logger.error(f"Error identifying objects: {e}")
            self.speech.speak("I couldn't identify objects in the scene.")
            
    async def recognize_faces(self):
        """Recognize faces and identify people using trained model"""
        try:
            image = self.vision.capture_image()
            if image is not None:
                self.speech.speak("Scanning for faces...")
                
                # Detect faces and get encodings
                detected_faces = self.face_recognizer.detect_faces(image)
                
                if detected_faces:
                    # Recognize/identify the faces
                    identified_faces = self.face_recognizer.recognize_faces(detected_faces)
                    
                    # Generate description
                    description = self.face_recognizer.get_face_description(identified_faces)
                    self.speech.speak(description)
                    
                    # Provide detailed info for each recognized person
                    for face in identified_faces:
                        if face.get('identity') != 'Unknown':
                            confidence = face.get('confidence', 0)
                            self.speech.speak(f"{face['identity']} detected with {confidence:.0%} confidence")
                    
                    logger.info(f"Face recognition complete: {len(identified_faces)} faces detected")
                else:
                    self.speech.speak("I don't see any faces around you.")
            else:
                self.speech.speak("Camera not available for face recognition.")
        except Exception as e:
            logger.error(f"Error recognizing faces: {e}")
            self.speech.speak("I couldn't detect faces in the scene.")
            
    async def assist_navigation(self, parameters):
        """Assist with navigation"""
        try:
            destination = parameters.get('destination')
            
            if destination:
                self.speech.speak(f"Getting directions to {destination}...")
                
                # Get current location
                location = await self.navigation.get_current_location()
                if location:
                    self.speech.speak(f"Your current location is {location}")
                
                # Get directions
                route = await self.navigation.get_directions(
                    location,
                    destination
                )
                
                # Speak directions
                if route and 'steps' in route:
                    self.speech.speak(f"I found a route to {destination}. Here are the first few directions.")
                    for step in route['steps'][:3]:
                        instruction = step.get('instruction', '')
                        if instruction:
                            self.speech.speak(instruction)
                            logger.info(f"Direction: {instruction}")
                else:
                    self.speech.speak(f"I couldn't find directions to {destination}.")
            else:
                self.speech.speak("Please tell me where you want to go.")
        except Exception as e:
            logger.error(f"Error navigating: {e}")
            self.speech.speak("I encountered an error during navigation.")
            
    async def handle_emergency(self):
        """Handle emergency situations"""
        try:
            # Send emergency alert
            if hasattr(self.db, 'send_emergency_alert'):
                contacts = self.user_context.get('emergency_contacts', [])
                if not isinstance(contacts, list):
                    contacts = [contacts] if contacts else []
                await self.db.send_emergency_alert(contacts)
            else:
                logger.warning("Emergency alert method not available")
            
            # Get current location
            location = await self.navigation.get_current_location()
            
            # Speak reassurance
            self.speech.speak(
                f"Emergency alert sent. Your location is {location}. Help is on the way."
            )
        except Exception as e:
            logger.error(f"Error handling emergency: {e}")
    
    async def _handle_language_switch(self, command: str):
        """Handle language switching"""
        try:
            available_langs = self.speech.get_available_languages()
            
            # Extract requested language from command
            requested_lang = None
            command_lower = command.lower()
            
            # Check command for language names
            lang_mapping = {
                'english': 'en',
                'indonesian': 'id',
                'spanish': 'es',
                'french': 'fr',
                'german': 'de',
                'portuguese': 'pt',
                'japanese': 'ja',
                'chinese': 'zh',
                'mandarin': 'zh',
            }
            
            for lang_name, lang_code in lang_mapping.items():
                if lang_name in command_lower:
                    requested_lang = lang_code
                    break
            
            if requested_lang and requested_lang in available_langs:
                # Switch language
                success = self.speech.set_language(requested_lang)
                if success:
                    self.user_context['language'] = requested_lang
                    self.user_context['language_name'] = self.speech.get_language_name()
                    lang_name = available_langs[requested_lang]
                    self.speech.speak(f"Language changed to {lang_name}")
                    logger.info(f"Language switched to: {requested_lang} ({lang_name})")
            else:
                # List available languages
                self.speech.speak("Available languages are:")
                for code, name in available_langs.items():
                    self.speech.speak(name)
                self.speech.speak("Which language would you like?")
                
        except Exception as e:
            logger.error(f"Error switching language: {e}")
            self.speech.speak("I couldn't change the language. Please try again.")
    
    async def _handle_face_enrollment(self, command: str):
        """Handle face enrollment/training commands"""
        try:
            command_lower = command.lower()
            
            # Extract person's name from command
            # Try patterns like "enroll [name]", "register [name]", etc.
            import re
            match = re.search(r'(?:enroll|register|teach|save|remember|add|learn)\s+(?:as|face of|face of\s+)?(.+?)(?:\s+face)?$', command_lower)
            
            if match:
                person_name = match.group(1).strip()
                
                # Check max people constraint
                known_people = self.face_recognizer.get_known_people()
                self.speech.speak(f"Preparing to enroll {person_name}. Please look at the camera.")
                
                # Capture image and enroll
                image = self.vision.capture_image()
                if image is not None:
                    success = self.face_recognizer.enroll_from_image(person_name, image)
                    
                    if success:
                        self.speech.speak(f"Successfully enrolled {person_name}. I will recognize you next time.")
                        logger.info(f"Enrolled face: {person_name}")
                    else:
                        self.speech.speak(f"Could not detect a clear face. Please try again.")
                else:
                    self.speech.speak("Camera is not available. Please check your camera connection.")
            else:
                # No name provided, ask for it
                self.speech.speak("I can enroll your face. Please tell me your name.")
                
        except Exception as e:
            logger.error(f"Error enrolling face: {e}")
            self.speech.speak("I encountered an error during face enrollment. Please try again.")
    
    async def _handle_face_management(self, command: str):
        """Handle face management commands (remove, list, etc.)"""
        try:
            command_lower = command.lower()
            
            if any(phrase in command_lower for phrase in ['who do you know', 'list people', 'list known']):
                # List all enrolled people
                known_people = self.face_recognizer.get_known_people()
                
                if known_people:
                    self.speech.speak(f"I know {len(known_people)} people:")
                    for person in known_people:
                        self.speech.speak(person)
                else:
                    self.speech.speak("I don't know anyone yet. Let's enroll some people!")
            
            elif any(phrase in command_lower for phrase in ['forget', 'remove', 'delete', 'forget face']):
                # Extract name to remove
                import re
                match = re.search(r'(?:forget|remove|delete)\s+(?:face of\s+)?(.+?)$', command_lower)
                
                if match:
                    person_name = match.group(1).strip()
                    success = self.face_recognizer.remove_person(person_name)
                    
                    if success:
                        self.speech.speak(f"I've forgotten about {person_name}.")
                        logger.info(f"Removed person: {person_name}")
                    else:
                        self.speech.speak(f"I don't have {person_name} in my database.")
                else:
                    self.speech.speak("Who would you like me to forget?")
            
            elif any(phrase in command_lower for phrase in ['face statistics', 'face status', 'enrollment status']):
                # Show enrollment statistics
                stats = self.face_recognizer.get_statistics()
                self.speech.speak(f"I know {stats['total_known_people']} people with {stats['total_encodings']} face samples.")
                
        except Exception as e:
            logger.error(f"Error managing faces: {e}")
            self.speech.speak("I encountered an error. Please try again.")
    
    async def _handle_audio_assistance(self, command: str):
        """Handle audio/sound localization commands"""
        try:
            command_lower = command.lower()
            
            if any(phrase in command_lower for phrase in ['what do you hear', 'listen', 'detect sounds', 'scan audio']):
                # Start listening and detecting sounds
                self.speech.speak("Listening for sounds...")
                
                if self.sound_localizer.start_listening():
                    import time
                    # Listen for 3-5 seconds
                    audio_chunk = self.sound_localizer.get_audio_chunk()
                    time.sleep(0.5)
                    
                    if audio_chunk is not None:
                        # Detect sounds
                        sounds = self.sound_localizer.detect_sounds(audio_chunk)
                        
                        if sounds:
                            # Get description
                            description = self.sound_localizer.get_audio_description(sounds)
                            self.speech.speak(description)
                            
                            # Try to localize
                            localization = self.sound_localizer.localize_sound(audio_chunk)
                            if localization:
                                location_desc = self.sound_localizer.get_localization_summary(localization)
                                self.speech.speak(location_desc)
                        else:
                            self.speech.speak("No significant sounds detected.")
                    
                    self.sound_localizer.stop_listening()
                else:
                    self.speech.speak("Audio system not available.")
            
            elif any(phrase in command_lower for phrase in ['obstacle', 'check ahead', 'detect obstacle']):
                # Detect obstacles using sound
                self.speech.speak("Scanning for obstacles...")
                
                if self.sound_localizer.start_listening():
                    audio_chunk = self.sound_localizer.get_audio_chunk()
                    
                    if audio_chunk is not None:
                        obstacles = self.sound_localizer.detect_obstacles(audio_chunk)
                        
                        if obstacles:
                            warning = await self.navigation.assist_with_obstacles(obstacles)
                            if warning:
                                self.speech.speak(warning)
                        else:
                            self.speech.speak("No obstacles detected. Path appears clear.")
                    
                    self.sound_localizer.stop_listening()
                else:
                    self.speech.speak("Audio system not available.")
            
            elif any(phrase in command_lower for phrase in ['classify sound', 'identify sound', 'what sound']):
                # Classify the detected sound
                self.speech.speak("Analyzing sound...")
                
                if self.sound_localizer.start_listening():
                    audio_chunk = self.sound_localizer.get_audio_chunk()
                    
                    if audio_chunk is not None:
                        classification = self.sound_localizer.classify_sound(audio_chunk)
                        
                        if classification:
                            sound_type = classification.get('primary_sound', 'Unknown')
                            confidence = classification.get('confidence', 0)
                            self.speech.speak(f"Detected {sound_type} with {confidence:.0%} confidence.")
                        else:
                            self.speech.speak("Could not classify the sound.")
                    
                    self.sound_localizer.stop_listening()
                else:
                    self.speech.speak("Audio system not available.")
            
            elif any(phrase in command_lower for phrase in ['audio statistics', 'audio status']):
                # Show audio system status
                stats = self.sound_localizer.get_statistics()
                if stats['library_available']:
                    self.speech.speak(f"Sound localization enabled. Using {stats['method']} method at {stats['sample_rate']} Hz.")
                else:
                    self.speech.speak("Audio libraries not available. Please install required packages.")
        
        except Exception as e:
            logger.error(f"Error in audio assistance: {e}")
            self.speech.speak("I encountered an error with audio processing. Please try again.")
    
    async def handle_exit(self):
        """Handle user exit/goodbye command"""
        try:
            logger.info("User requested exit")
            
            # Provide farewell message
            self.speech.speak("Thank you for using Vision Assistant. Goodbye!")
            
            # Cleanup resources
            self.vision.cleanup()
            self.db.close()
            
            logger.info("Vision Assistant stopped gracefully")
        
        except Exception as e:
            logger.error(f"Error during exit: {e}")
            self.speech.speak("Shutting down. Goodbye!")
    
    def stop(self):
        """Stop the assistant"""
        logger.info("Stopping Vision Assistant...")
        self.is_listening = False


async def main():
    """Main entry point"""
    try:
        # Check for command-line arguments
        language = None
        
        if len(sys.argv) > 1:
            if sys.argv[1] == '--test':
                logger.info("Running in test mode...")
                assistant = VisionAssistant()
                # Test a simple command
                await assistant.process_command("describe the scene")
                return True
            elif sys.argv[1] == '--test-import':
                logger.info("Import test passed!")
                return True
            elif sys.argv[1] == '--debug':
                logger.info("Debug mode enabled")
            elif sys.argv[1].startswith('--lang='):
                language = sys.argv[1].split('=')[1]
                logger.info(f"Using language: {language}")
        
        assistant = VisionAssistant(language=language if language else None)
        
        # Run continuous assistance
        await assistant.continuous_assistant()
        
    except KeyboardInterrupt:
        logger.info("Shutting down Vision Assistant...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # For Python 3.13, use asyncio.run()
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)