# Copilot Agent Onboarding Guide

## Vision Assistant for Visually Impaired

<Goals>

1. Reduce PR rejection rate by ensuring code passes CI builds, validation pipelines, and behaves correctly.
2. Minimize bash command and build failures through validated sequences.
3. Accelerate agent work by eliminating exploratory searches for basic information.

</Goals>

<Limitations>

- This document is limited to 2 pages (approximately 2000 words).
- Instructions are task-agnostic and focus on project-wide patterns only.

</Limitations>

<WhatToAdd>

Add the following high level details about the codebase to reduce the amount of searching the agent has to do to understand the codebase each time:

<HighLevelDetails>

## Project Summary

AI-Powered assistant that enables visually impaired people to "see" their environment through computer vision, voice interaction, and intellegent scene description.

## Repository Characteristics

- **Type**: Python AI/ML application with accessibility focus
- **Size**: ~20 core files, 5 directories, 2,500+ LOC
- **Primary Language**: Python 3.8+
- **Key Frameworks**:
  - AI/ML : PyTorch, Transformers, OpenCV, YOLOv8, EasyOCR
  - Backend : FastAPI (optional), SQLAlchemy, AsyncIO
  - Voice : SpeechRecognition, pyttsx3, gTTS
- **Target Runtime**: Desktop (Windows/Linux/macOS) with future mobile support
- **Accessibility** : Voice-first interface, no visual UI required
- **Deployment** : Virtual environment + Docker-ready architecture

  </HighLevelDetails>

Add information about how to build and validate changes so the agent does not need to search and find it each time.
<BuildInstructions>

## Environment Setup (ALWAYS REQUIRED IN THIS ORDER)

### Step 1: Virtual Environment Creation

```bash
python -m venv venv
# Windows activation:
venv\Scripts\activate
# Unix activation:
source venv/bin/activate

```

Validation : Run which python or where python - must show venv path
Failure Case : If activation fails on Windows, run Set-ExecutionPolicy-ExecutionPolicy RemoteSigned-Scope CurrentUser

### Step 2: Dependency Installation:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt

```

Time Estimate: 5-10 minutes (includes ~1GB model downloads)

Known Issues & Workarounds:

1. PyAudio fails on Linux: sudo apt-get install portaudio 19-dev python3 -pyaudio
2. OpenCV import error: pip install opencv-python-headless
3. CUDA out of memory: Use device='cpu' in torchmodels
4. Model download timeout: Add --no-cache-dir flag

### Step 3: Environment Configuration

```bash
cp .env.example .env
# Edit .env with API keys (OpenAI, Goggle Maps optional for basic functionally)

Critical: Never commit .env file.Only.env.example is tracked.

```

Build & Validation Commands

Bootstrap Validation (Run Sequentially)

```bash
# 1. Core imports (must pass)
python -c "import torch, cv2, transformers, sqlalchemy; print('✓ Core OK')"

# 2. Hardware check (camera optional for development)
python -c "
import cv2
cap = cv2.VideoCapture(0)
status = cap.isOpened()
cap.release()
print(f'Camera: {\"✓\" if status else \"✗ (optional)\"}')
"

# 3. Module initialization
python -c "
from ai_modules.vision_processor import VisionProcessor
from ai_modules.speech_engine import SpeechEngine
print('✓ Module imports OK')
"

# 4. Configuration validation
python -c "
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)
assert 'app' in config and 'speech' in config
print('✓ Config structure OK')
"
```

Test Execution

bash

# No formal test suite yet - use these validation steps

python app.py --test # Basic smoke test (30 second timeout)

# Expected: Voice says "Vision Assistant initialized"

# Manual module testing

python -m ai_modules.vision_processor --test-capture

Linting & Code Quality

```bash
# Optional but recommended
pip install black flake8 mypy
black . --check  # Format validation
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
mypy . --ignore-missing-imports

```

Run Application

```bash
# Production mode
python app.py

# Debug mode (with verbose logging)
python app.py --debug

# Test specific command
python app.py --command "describe scene"

```

Validation Pipeline Steps

1. Pre-commit: Core imports must work
2. Post-install: Camera/microphone accessibility check
3. Runtime: Application starts without exceptions
4. Feature: Basic voice command processing works

Common Failure Patterns & Solutions

Failure Root Cause Immediate Fix Permanent Solution
ImportError: libGL.so.1 Missing OpenGL libraries sudo apt install libgl1-mesa-glx Add to system dependencies
ALSA lib pcm.c errors Audio system configuration Check microphone permissions Use pyaudio wheel
Camera permission denied User not in video group sudo usermod -a -G video $USER Add udev rules
CUDA out of memory GPU memory insufficient Set device='cpu' Implement batch processing
Model download timeout Network/slow connection Increase timeout, retry Use local model cache

Timing Information

· Full setup: 10-15 minutes (including model downloads)
· Application startup: 2-3 seconds after initialization
· Object detection: 100-200ms per image (CPU)
· Voice command processing: 1-2 seconds total

  </BuildInstructions>

List key facts about the layout and architecture of the codebase to help the agent find where to make changes with minimal searching.
<ProjectLayout>

## Architectural Overview

Hierarchical Structure:
app.py (Main) → AI Modules → Features → External Services
│ │ │ │
│ ├─ Vision ───┼─ Object Detection
│ ├─ Speech ───┼─ Voice I/O
│ └─ LLM ──────┼─ Command Understanding
│
├─ Database ───────────────┼─ User State
└─ API Integration ────────┼─ External Services

Critical File Locations

Root Level (Highest Priority)

app.py # MAIN ENTRY POINT - Contains VisionAssistant class
requirements.txt # DEPENDENCY MANIFEST - Always check before adding
config.yaml # APPLICATION CONFIG - Edit for behavior changes
.env.example # ENVIRONMENT TEMPLATE - Copy to .env
deploy.py # SETUP AUTOMATION - Use for fresh installations

AI Modules (Most Changes Here)

ai_modules/
├── vision_processor.py # COMPUTER VISION (YOLOv8, OpenCV, EasyOCR)
│ ├── capture_image() - Camera interface
│ ├── detect_objects() - Object detection
│ └── extract_text() - OCR functionality
├── speech_engine.py # VOICE INTERFACE (TTS/STT)
│ ├── speak() - Text-to-speech
│ └── listen() - Speech-to-text
├── llm_handler.py # AI INTELLIGENCE (Command understanding)
│ ├── understand_intent() - Command parsing
│ └── generate_response() - LLM responses
└── neural_core.py # MODEL MANAGEMENT

Feature Implementations

features/
├── navigation.py # GPS & DIRECTION
│ ├── get_current_location()
│ └── get_directions()
├── object_detection.py # OBJECT RECOGNITION LOGIC
├── text_reader.py # OCR PIPELINE
└── face_recognition.py # FACE DETECTION

Data Persistence

database/
├── models.py # SQLAlchemy ORM MODELS
│ ├── User - User preferences
│ ├── SceneMemory - Historical data
│ └── ConversationHistory - Chat logs
└── db_handler.py # DATABASE OPERATIONS

Configuration Files

config.yaml # Primary configuration (YAML format)
├── app: debug, version, name
├── ai: model selections, providers
├── speech: language, rate, engine
└── user: preferences, emergency contacts

.env # Environment variables (NOT COMMITTED)
├── API keys (OpenAI, Google Maps, etc.)
└── Database connection strings

Validation Checks

Pre-Checkin Validation (Run in Order)

1. Import Test: All modules must import without error
2. Config Test: Configuration files must be valid YAML/JSON
3. Hardware Test: Camera/microphone accessible (optional for CI)
4. Voice Test: Basic TTS/STT functionality works

GitHub Workflows (When Implemented)

```yaml
# Expected CI pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with: { python-version: "3.9" }
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Test imports
        run: python -c "import app; import ai_modules"
      - name: Lint
        run: |
          pip install black flake8
          black --check .
          flake8 . --count
```

Hidden Dependencies

1. System Libraries: ALSA, PortAudio, OpenGL (required for audio/video)
2. Camera Permissions: User must be in video group (Linux)
3. Model Files: Auto-downloaded to ~/.cache/ on first run
4. Database: SQLite file created at database/vision_assistant.db

File Inventory by Priority

Root Directory (Complete List)

app.py # Main application class VisionAssistant
requirements.txt # Python dependencies with pinned versions
config.yaml # YAML configuration
.env.example # Environment template (copy to .env)
deploy.py # Automated setup script
setup.py # Package configuration
README.md # Project documentation
CONTRIBUTING.md # Contribution guidelines
LICENSE # MIT License
.gitignore # Standard Python ignores

ai_modules/ Directory Contents

vision*processor.py # Computer vision pipeline (most complex)
speech_engine.py # Voice interface (user interaction)
llm_handler.py # AI command processing
neural_core.py # Model loading/inference
\_init*.py # Module exports

Key Source Code Snippets

app.py - Main Class Structure:

```python
class VisionAssistant:
    def _init_(self):
        self.vision = VisionProcessor()      # Computer vision
        self.speech = SpeechEngine()         # Voice I/O
        self.llm = LLMAssistant()            # AI intelligence
        self.navigation = NavigationAssistant()  # GPS/directions
        self.db = DatabaseHandler()          # Database

    async def continuous_assistance(self):   # Main event loop
        while True:
            command = await self.speech.listen()
            if command:
                await self.process_command(command)

    async def process_command(self, command: str):
        intent = await self.llm.understand_intent(command)
        # Route to appropriate handler based on intent
```

config.yaml - Key Sections:

```yaml
app:
  name: "Vision Assistant"
  debug: true # Set to false in production
  version: "1.0.0"

speech:
  language: "en" # Change to "id" for Indonesian
  speech_rate: 150
  use_google_tts: false

ai:
  llm_provider: "openai" # or "local"
  vision_model: "yolov8n"
  text_model: "easyocr"
```

requirements.txt - Critical Dependencies:

# AI/ML Core

torch>=2.0.1
torchvision>=0.15.2
transformers>=4.31.0
ultralytics>=8.0.124 # YOLOv8

# Computer Vision

opencv-python-headless>=4.8.0
easyocr>=1.7.0

# Voice Processing

speechrecognition>=3.10.0
pyttsx3>=2.90
gtts>=2.3.2

# Backend

fastapi>=0.100.0
sqlalchemy>=2.0.19

  </ProjectLayout>

<StepsToFollow>

## Agent Implementation Guidelines

Before Starting Any Task

1. ALWAYS activate virtual environment - Verify with which python
2. Check requirements.txt - Ensure all dependencies are documented
3. Review config.yaml - Understand current configuration
4. Test basic functionality - Run python app.py --test

When Making Changes

1. Follow existing patterns - Use async/await for I/O, type hints, docstrings
2. Update configuration - Add new options to config.yaml and .env.example
3. Handle errors gracefully - Provide voice feedback for user
4. Maintain accessibility - All features must work without visual UI
5. Test offline capability - Core features should work without internet

Change Location Guidelines

· New voice command: llm_handler.py (intent) → app.py (handler)
· New vision feature: vision_processor.py → new method
· New user feature: features/ → new module
· Configuration change: config.yaml + app.py (loading)
· Database change: database/models.py + migration

Validation Sequence for Changes

```bash
# 1. Import test
python -c "from app import VisionAssistant"

# 2. Configuration test
python -c "
import yaml
with open('config.yaml') as f:
    yaml.safe_load(f)
"

# 3. Runtime test (quick)
timeout 10 python app.py --test-import

# 4. Feature test (if applicable)
python -c "
from ai_modules.vision_processor import VisionProcessor
vp = VisionProcessor()
print('VisionProcessor initialized')
"
```

Error Recovery Protocol

If a command fails:

1. Check virtual environment is active
2. Verify all dependencies installed (pip list | grep -E "torch|opencv")
3. Check hardware permissions (camera/microphone)
4. Review error logs in logs/ directory
5. Fall back to mock implementations for testing

Trust This Documentation

· These instructions have been validated against the current codebase
· Follow sequences exactly as documented
· Only perform additional searches if:
a) Information is missing from this guide
b) A documented command fails and isn't covered in troubleshooting
c) Implementing a feature not covered by existing patterns

Quick Reference Commands

```bash
# Setup from scratch (10-15 min)
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Daily development start (30 sec)
source venv/bin/activate && python app.py

# Validation suite (2 min)
python -c "import app, ai_modules, features" && python app.py --test

# Clean rebuild (3 min)
rm -rf venv && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

```

Performance Targets

· Application startup: <5 seconds
· Voice command response: <2 seconds
· Object detection: <200ms per image
· Memory usage: <500MB idle, <1GB processing
· Battery impact: Optimize for mobile use

Security & Privacy Requirements

· NEVER commit .env or API keys
· Process data locally when possible
· Anonymize usage data before transmission
· Provide opt-out for all data collection
· Encrypt sensitive user data at rest

</StepsToFollow>
