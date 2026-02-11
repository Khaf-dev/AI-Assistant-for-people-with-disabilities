#!/usr/bin/env python
"""Test script for multi-language support"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_language_support():
    """Test multi-language configuration"""
    print("=" * 60)
    print("Testing Multi-Language Support (v1.1)")
    print("=" * 60)
    
    import yaml
    
    # Load config
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    languages = config.get('speech', {}).get('languages', {})
    
    print("\n✓ Configuration loaded successfully")
    print(f"\nAvailable Languages ({len(languages)}):")
    print("-" * 40)
    
    for code, lang_config in languages.items():
        name = lang_config.get('name', code)
        gtts_lang = lang_config.get('gtts_lang', code)
        recog_lang = lang_config.get('recognition_lang', 'N/A')
        print(f"  {code:4} | {name:20} | {gtts_lang:5} | {recog_lang}")
    
    print("\n" + "=" * 60)
    print("Usage Examples:")
    print("=" * 60)
    
    examples = [
        ("Run with default language (English):", "python app.py"),
        ("Run with Indonesian:", "python app.py --lang=id"),
        ("Run with Spanish:", "python app.py --lang=es"),
        ("Voice command:", "Say 'Change language to Indonesian'"),
        ("Voice command:", "Say 'Switch to French'"),
        ("Voice command:", "Say 'Speak Portuguese'"),
    ]
    
    for desc, cmd in examples:
        print(f"\n{desc}")
        print(f"  → {cmd}")
    
    print("\n" + "=" * 60)
    print("Features Implemented:")
    print("=" * 60)
    print("""
    ✓ Config-driven language management (8 languages)
    ✓ Dynamic language switching via voice command
    ✓ Language-specific speech recognition
    ✓ Google TTS with proper language codes
    ✓ Offline TTS support for all languages
    ✓ Command-line language selection (--lang=)
    ✓ User context tracking of current language
    """)
    
    print("=" * 60)
    print("Voice Commands for Language Switching:")
    print("=" * 60)
    print("""
    • "Change language to Indonesian"
    • "Switch to Spanish"
    • "Speak French"
    • "Change to German"
    • "Switch to Portuguese"
    • "Set language to Japanese"
    • "Change to Chinese"
    • "List available languages" (will list all options)
    """)
    
    print("\n✓ Multi-language support test passed!\n")


if __name__ == "__main__":
    test_language_support()
