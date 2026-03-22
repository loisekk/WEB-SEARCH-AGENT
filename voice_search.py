"""
voice_search.py  —  Voice input helper for app.py
Uses SpeechRecognition + Google Web Speech API (free, no key needed).
Install: pip install SpeechRecognition pyaudio
Falls back gracefully if mic / library not available.
"""

def voice_input() -> str | None:
    """
    Records from microphone and returns recognised text.
    Returns None if recognition fails or library not installed.
    """
    try:
        import speech_recognition as sr   # pip install SpeechRecognition

        r   = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("[voice_search] 🎙️  Listening …")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=6, phrase_time_limit=8)

        text = r.recognize_google(audio)
        print(f"[voice_search] ✅ Recognised: {text}")
        return text

    except ImportError:
        print("[voice_search] ⚠️  SpeechRecognition not installed. Run: pip install SpeechRecognition pyaudio")
        return None
    except Exception as e:
        print(f"[voice_search] ❌  Error: {e}")
        return None
