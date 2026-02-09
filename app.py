"""Vision Assistant - Main Application Entry Point"""
import sys
import os
import asyncio
import logging
from pathlib import Path

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
    
    def __init__(self):
        """Initialize Vision Assistant"""
        logger.info("Initializing Vision Assistant for Visually Impaired...")
        
        try:
            # Import modules
            from ai_modules.vision_processor import VisionProcessor
            from ai_modules.speech_engine import SpeechEngine
            from ai_modules.llm_handler import LLMHandler
            from features.navigation import NavigationAssistant
            from database.db_handler import DatabaseHandler
            
            # Initialize core modules
            self.vision = VisionProcessor()
            self.speech = SpeechEngine()
            self.llm = LLMHandler()
            self.navigation = NavigationAssistant()
            self.db = DatabaseHandler()
            
            # State management
            self.is_listening = False
            self.is_processing = False
            self.user_context = {}
            
            # Initialize services
            self._setup_services()
            
            logger.info("Vision Assistant initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vision Assistant: {e}")
            raise
        
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
                    logger.info("Shutting down...")
                    break
                except Exception as e:
                    logger.error(f"Error in assistant loop: {e}")
        
        except Exception as e:
            logger.error(f"Fatal error in continuous assistance: {e}")
                
    async def process_command(self, command: str):
        """Process user voice commands"""
        logger.info(f"Processing command: {command}")
        
        try:
            # Parse intent
            intent = await self.llm.understand_intent(command, self.user_context)
            
            # Route to appropriate handler
            if intent.get('action') == 'describe_scene':
                await self.describe_environment(detailed=True)
            elif intent.get('action') == 'read_text':
                await self.read_text_around()
            elif intent.get('action') == 'recognize_object':
                await self.identify_objects()
            elif intent.get('action') == 'navigate':
                await self.assist_navigation(intent.get('parameters', {}))
            elif intent.get('action') == 'recognize_person':
                await self.recognize_faces()
            elif intent.get('action') == 'emergency':
                await self.handle_emergency()
            elif intent.get('action') == 'general_question':
                response = await self.llm.generate_response(command)
                self.speech.speak(response)
        
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.speech.speak("I encountered an error processing your request.")
            
    async def describe_environment(self, detailed=False):
        """Describe the current environment"""
        try:
            # Capture image
            image = self.vision.capture_image()
            
            if image is not None:
                # Get description
                if detailed:
                    description = await self.vision.describe_scene_detailed(image)
                else:
                    description = await self.vision.describe_scene_brief(image)
                
                # Speak description
                self.speech.speak(description)
                
                # Store in context
                self.user_context['last_scene'] = description
        except Exception as e:
            logger.error(f"Error describing environment: {e}")
        
    async def read_text_around(self):
        """Read any text in the environment"""
        try:
            image = self.vision.capture_image()
            if image is not None:
                texts = await self.vision.extract_text(image)
                
                if texts:
                    for text in texts:
                        self.speech.speak(f"I see text that says: {text}")
                else:
                    self.speech.speak("I don't see any readable text around.")
        except Exception as e:
            logger.error(f"Error reading text: {e}")
            
    async def identify_objects(self):
        """Identify objects in view"""
        try:
            image = self.vision.capture_image()
            if image is not None:
                objects = await self.vision.detect_objects(image)
                
                if objects:
                    object_list = ", ".join([obj['name'] for obj in objects[:5]])
                    self.speech.speak(f"I can see: {object_list}")
                else:
                    self.speech.speak("I don't detect any objects nearby.")
        except Exception as e:
            logger.error(f"Error identifying objects: {e}")
            
    async def recognize_faces(self):
        """Recognize faces and identify people"""
        try:
            image = self.vision.capture_image()
            if image is not None:
                faces = await self.vision.recognize_faces(image)
                
                if faces:
                    for face in faces:
                        name = face.get('name', 'Unknown person')
                        emotion = face.get('emotion', 'neutral')
                        self.speech.speak(f"I see {name} who looks {emotion}")
                else:
                    self.speech.speak("I don't see any faces")
        except Exception as e:
            logger.error(f"Error recognizing faces: {e}")
            
    async def assist_navigation(self, parameters):
        """Assist with navigation"""
        try:
            destination = parameters.get('destination')
            
            if destination:
                # Get current location
                location = await self.navigation.get_current_location()
                
                # Get directions
                route = await self.navigation.get_directions(
                    location,
                    destination
                )
                
                # Speak directions
                if route and 'steps' in route:
                    for step in route['steps'][:3]: 
                        self.speech.speak(step.get('instruction', ''))
            else:
                self.speech.speak("Please tell me where you want to go.")
        except Exception as e:
            logger.error(f"Error navigating: {e}")
            
    async def handle_emergency(self):
        """Handle emergency situations"""
        try:
            # Send emergency alert
            await self.db.send_emergency_alert(
                self.user_context.get('emergency_contacts', [])
            )
            
            # Get current location
            location = await self.navigation.get_current_location()
            
            # Speak reassurance
            self.speech.speak(
                f"Emergency alert sent. Your location is {location}. Help is on the way."
            )
        except Exception as e:
            logger.error(f"Error handling emergency: {e}")
    
    def stop(self):
        """Stop the assistant"""
        logger.info("Stopping Vision Assistant...")
        self.is_listening = False


async def main():
    """Main entry point"""
    try:
        assistant = VisionAssistant()
        
        # Check for command-line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == '--test':
                logger.info("Running in test mode...")
                # Test a simple command
                await assistant.process_command("describe the scene")
                return True
            elif sys.argv[1] == '--test-import':
                logger.info("Import test passed!")
                return True
            elif sys.argv[1] == '--debug':
                logger.info("Debug mode enabled")
        
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