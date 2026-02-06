import openai
from typing import Dict, list, Any
import json
from langchain.chains import ConversationChain
from langchain.memory import ConversatinonBufferMemory
from langchain.llms import HuggingFacePipeline
import torch
from transformers import pipeline, AutoModelForCausaLLM, AutoTokenizer
import os
from dotenv import load_dotenv

load_dotenv()

class LLMAssistant:
    def __init__(self, use_openai=True):
        print("Initializing LLM Handler...")
        
        self.use_openai = use_openai
        
        if use_openai:
            # OpenChatGPT
            openai.api_key = os.getenv("OPENAI_API_KEY") # Load your openai api key
            self.model = "gpt-3.5-turbo"
        else:
            # Local Causa LLM
            self.model = self._load_local_model()
            
        # Load conversation
        self.memory = ConversatinonBufferMemory()
        self.conversation_history = []
        
        # Predefined intents
        self.intents = {
            'describe_scene': ['describe', 'what do you see', 'what\s around'],
            'read_text': ['read', 'what does it say', 'text'],
            'recognize_objects': ['objects', 'what things', 'identify'],
            'navigate': ['go to', 'navigate', 'directions to', 'how to get to'],
            'recognize_people': ['who is this', 'identify person', 'do you know this person'],
            'emergency': ['help', 'emergency', 'danger', 'call for help'],
            'general_questions': ['what', 'how', 'why', 'when', 'where']
        }
        
    
    async def understand_intent(self, command: str, context: Dict) -> Dict:
        """Understand user intent from command"""
        if self.use_openai:
            # Use GPT for intent recogintion
            prompt = f"""
            User command: {command}
            Context: {json.dumps(context)}
            
            Clasify the intent and extract parameters
            1. Action (from: {list(self.intents.keys())})
            2. Parameters (key-value pairs)
            
            Return JSON format:
            {{"action": "action_name", "parameters": {{}}}}
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        
        else:
            # Use Local model for intent recognition
            for intent, keywords in self.intents.items():
                for keyword in keywords:
                    if keyword in command.lower():
                        return {
                            "action": intent,
                            "parameters": {"query": command}
                        }
                        
            return {
                "action": "general_questions",
                "parameters": {"query": command}
            }
            
    async def generate_response(self, query: str, context: Dict) -> str:
        """Generate natural language response"""
        if self.use_openai:
            