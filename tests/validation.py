"""Validation script - Tests core functionality"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

import asyncio


def test_imports():
    """Test core imports"""
    try:
        print("Testing core imports...")
        import torch
        import cv2
        import transformers
        import sqlalchemy
        print("✓ Core imports OK")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_config():
    """Test configuration file"""
    try:
        print("Testing configuration...")
        import yaml
        with open('config.yaml') as f:
            config = yaml.safe_load(f)
        
        assert 'app' in config, "Missing 'app' section"
        assert 'speech' in config, "Missing 'speech' section"
        assert 'ai' in config, "Missing 'ai' section"
        
        print("✓ Config structure OK")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False


def test_module_initialization():
    """Test module imports"""
    try:
        print("Testing module initialization...")
        from ai_modules.vision_processor import VisionProcessor
        from ai_modules.speech_engine import SpeechEngine
        from ai_modules.llm_handler import LLMAssistant
        from features.navigation import NavigationAssistant
        from database.db_handler import DatabaseHandler
        
        print("✓ Module imports OK")
        return True
    except ImportError as e:
        print(f"✗ Module import error: {e}")
        return False


def main():
    """Run all validation tests"""
    print("=" * 50)
    print("Vision Assistant - Bootstrap Validation")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_module_initialization,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
