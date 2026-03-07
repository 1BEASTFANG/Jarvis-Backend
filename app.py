from flask import Flask, request, jsonify
import pveagle
import base64
import wave
import struct
import os
import threading
import time
import requests
import google.generativeai as genai
import json

# ==========================================================
# 🚀 INITIALIZING JARVIS NEURAL CORE (CITRON) 🚀
# ==========================================================
app = Flask(__name__)

# ----------------------------------------------------------
# 🔐 CONFIGURATION & API KEY MANAGEMENT (ROUND-ROBIN)
# ----------------------------------------------------------
# Render dashboard se keys uthayega, agar wahan nahi mili toh backup use karega
RAW_KEYS_DATA = os.environ.get("GEMINI_KEYS", "")
if RAW_KEYS_DATA:
    GEMINI_API_KEYS = [k.strip() for k in RAW_KEYS_DATA.split(",") if k.strip()]
else:
    # BACKUP KEYS (If Env Vars are not set)
    GEMINI_API_KEYS = [
        "AIzaSyA4653Ot5yXJNaUulMHyAOAjFQxbcMNskM",
        "AIzaSyAUltC2WlOae6hKayp93Xt3InpbT15L4jw",
        "AIzaSyDsBmI1UWKGAObqffPVnV4TDQ5BKXXUKnM"
    ]

# Picovoice Configuration
PICO_KEY = os.environ.get("PICOVOICE_API_KEY", "KQ8KSsu+nj/D1jlMxVppSkWF4xuDSH9BcQ/qNtaMIBxwXbHgQcacrg==")
RENDER_URL = "https://jarvis-voice-api-uud7.onrender.com"

# Global System State
current_key_index = 0
eagle_engine = None
active_enroll_profiler = None

# ----------------------------------------------------------
# ⚙️ GEMINI ENGINE ROTATION LOGIC
# ----------------------------------------------------------
def rotate_gemini_config():
    """Key shift karne ka detailed function"""
    global current_key_index
    try:
        target_key = GEMINI_API_KEYS[current_key_index]
        genai.configure(api_key=target_key)
        print("--------------------------------------------------")
        print(f"🔄 SYSTEM UPDATE: Gemini configured with Key Index [{current_key_index}]")
        print(f"🔑 Current Key Prefix: {target_key[:8]}...")
        print("--------------------------------------------------")
    except Exception as e:
        print(f"❌ CONFIG ERROR: Failed to switch Gemini key: {str(e)}")

# Initialize first key
rotate_gemini_config()

def call_gemini_safely(model_name, contents):
    """Attempt call with auto-retry on multiple keys"""
    global current_key_index
    max_attempts = len(GEMINI_API_KEYS)
    attempts = 0
    
    while attempts < max_attempts:
        try:
            ai_model = genai.GenerativeModel(model_name)
            ai_response = ai_model.generate_content(contents)
            return ai_response
        except Exception as e:
            err = str(e).lower()
            print(f"⚠️ API WARNING: Key Index {current_key_index} failed an attempt.")
            
            # Identify if it's a quota or leak error
            if "429" in err or "403" in err or "quota" in err or "limit" in err:
                print(f"🛑 REASON: Key exhausted or blocked. Error: {err[:50]}")
                current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
                rotate_gemini_config()
                attempts += 1
                time.sleep(1.5) # Wait for buffer
            else:
                print(f"🚨 CRITICAL: Unexpected error: {err}")
                raise e
                
    raise Exception("💀 FATAL: All registered Gemini API keys have failed.")

# ----------------------------------------------------------
# 🎙️ MULTI-PROFILE BIOMETRIC DATABASE
# ----------------------------------------------------------
# Base64 strings are stored here as immutable identity profiles
VOICE_PROFILES_LIST = [
    "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"
]

# ----------------------------------------------------------
# 🧠 BIOMETRIC ENGINE LOAD
# ----------------------------------------------------------
try:
    print("💎 JARVIS BIOMETRIC ENGINE: Starting boot sequence...")
    loaded_profiles = []
    for b_data in VOICE_PROFILES_LIST:
        if b_data.strip():
            profile_obj = pveagle.EagleProfile.from_bytes(base64.b64decode(b_data))
            loaded_profiles.append(profile_obj)
            
    if loaded_profiles:
        eagle_engine = pveagle.create_recognizer(access_key=PICO_KEY, speaker_profiles=loaded_profiles)
        print(f"✅ SUCCESS: {len(loaded_profiles)} Secure Voice Profiles online.")
    else:
        print("⚠️ WARNING: No biometric profiles found to load.")
except Exception as bio_err:
    print(f"❌ BIOMETRIC BOOT FAILED: {str(bio_err)}")

# ----------------------------------------------------------
# 🕒 KEEP-ALIVE SYSTEM
# ----------------------------------------------------------
def persistent_ping():
    """Background thread to prevent Render sleep"""
    while True:
        time.sleep(14 * 60)
        try:
            print("🕒 [Heartbeat] Pinging internal server...")
            requests.get(RENDER_URL)
        except Exception:
            pass

threading.Thread(target=persistent_ping, daemon=True).start()

# ==========================================================
# 🛡️ ROUTE 1: VERIFY VOICE (AUTH FOR MESSAGES)
# ==========================================================
@app.route('/verify-voice', methods=['POST'])
def verify_voice_identity():
    if not eagle_engine:
        return jsonify({"status": "ERROR", "message": "Biometric Engine Offline"}), 500
        
    if 'audio' not in request.files:
        print("⚠️ REJECTED: No audio file provided by client.")
        return jsonify({"status": "ERROR", "message": "No audio file received"}), 400
        
    audio_obj = request.files['audio']
    
    try:
        print("🎙️ Analyzing identity for incoming command...")
        
        # A. Audio Analysis via Picovoice Eagle
        with wave.open(audio_obj, 'rb') as wav_file:
            # Format validation
            if wav_file.getframerate() != 16000:
                return jsonify({"status": "ERROR", "message": "Sample rate must be 16k"}), 400
                
            raw_pcm = wav_file.readframes(wav_file.getnframes())
            pcm_shorts = struct.unpack(f"{len(raw_pcm) // 2}h", raw_pcm)
            
            f_len = eagle_engine.frame_length
            peak_match_score = 0.0
            
            # Step through audio in frames
            for start in range(0, len(pcm_shorts) - f_len, f_len):
                frame = pcm_shorts[start : start + f_len]
                scores = eagle_engine.process(frame)
                current_max = max(scores)
                if current_max > peak_match_score:
                    peak_match_score = current_max
            
            print(f"📊 IDENTITY SCORE: {peak_match_score * 100:.2f}%")
            
            # Strict Gatekeeper (60%)
            if peak_match_score < 0.60:
                print("🔴 DENIED: Match score too low.")
                return jsonify({"status": "ACCESS_DENIED", "score": peak_match_score, "text": ""})
            
            print("🟢 ACCESS GRANTED: Profile verified.")

        # B. Transcription via Gemini 2.5 Flash
        audio_obj.seek(0)
        raw_audio_bytes = audio_obj.read()
        
        stt_prompt = """
        You are a highly accurate audio-to-text engine. 
        Transcribe the spoken audio exactly. The speaker is Nikhil.
        Possible target names: Harsh, Ranjan, Papa, Arvind, Pankaj Bhaiya, Citron, Saurabh, Vicky, Aryan.
        Keep it clean. Output ONLY the transcription.
        """
        
        gemini_content = [
            stt_prompt, 
            {"mime_type": "audio/wav", "data": raw_audio_bytes}
        ]
        
        gemini_result = call_gemini_safely('gemini-2.5-flash', gemini_content)
        final_transcription = gemini_result.text.strip()
        
        print(f"📝 STT RESULT: {final_transcription}")
            
        return jsonify({
            "status": "ACCESS_GRANTED", 
            "score": peak_match_score, 
            "text": final_transcription 
        })
                
    except Exception as e:
        print(f"❌ AUTH ERROR: {str(e)}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

# ==========================================================
# 🚀 ROUTE 2: LECTURE NINJA (NO AUTH - GEMINI VISION/AUDIO)
# ==========================================================
@app.route('/analyze-lecture', methods=['POST'])
def execute_lecture_analysis():
    if 'audio' not in request.files:
        return jsonify({"status": "ERROR", "message": "Audio stream missing"}), 400
    
    lecture_file = request.files['audio']
    
    try:
        print("🧠 LECTURE NINJA: Processing class audio stream...")
        lecture_data = lecture_file.read()
        
        # 🔥 THE PROFESSOR CITRON MASTER PROMPT 🔥
        instruction_set = """
        You are 'Citron', Nikhil's legendary AI classmate. 
        You are an expert at turning boring lectures into EPIC 'Cartoonish & Sci-Fi' style study notes.
        
        STRICT RULES:
        1. LANGUAGE: Use Hinglish (mixture of Hindi + English) - very casual and friendly.
        2. TONE: Like a friend explaining concepts 1 hour before the exam.
        3. VISUALS: Use TONS of relevant emojis in every single section. 🚀🤯💡🧠⚙️🔥📚
        4. STRUCTURE: 
           - Use <b>text</b> for important terms.
           - Use <br> for every new line/point.
           - Use bullet points (•) for sub-details.
        5. DEPTH: Explain every concept in detail. Do not leave out complex parts.
        
        OUTPUT FORMAT: You must return a VALID JSON with these exact keys:
        - "short_summary": An energetic 3-line summary of the whole class with ⚡.
        - "detailed_notes": The full lecture content using HTML tags like <b> and <br>.
        - "important_keywords": A list of 5 key terms, each followed by a 🔥 emoji.
        """
        
        payload = [
            instruction_set, 
            {"mime_type": "audio/wav", "data": lecture_data}
        ]
        
        gemini_response = call_gemini_safely('gemini-2.5-flash', payload)
        
        # Robust JSON cleaning (to prevent markdown breaking the parser)
        raw_text = gemini_response.text.strip()
        clean_json_str = raw_text.replace('```json', '').replace('```', '').strip()
        
        parsed_notes = json.loads(clean_json_str)
        
        print("✅ SUCCESS: Colorful notes prepared for Nikhil.")
        return jsonify({
            "status": "SUCCESS",
            "short_summary": parsed_notes.get("short_summary", "Summary missing 😢"),
            "detailed_notes": parsed_notes.get("detailed_notes", "Notes missing 😢"),
            "important_keywords": parsed_notes.get("important_keywords", "Keywords missing 😢")
        })

    except Exception as lecture_err:
        print(f"❌ LECTURE ERROR: {str(lecture_err)}")
        return jsonify({"status": "ERROR", "message": str(lecture_err)}), 500

# ----------------------------------------------------------
# 👤 ENROLLMENT SERVICE
# ----------------------------------------------------------
@app.route('/enroll-voice', methods=['POST'])
def enroll_new_identity():
    global active_enroll_profiler
    
    enroll_audio = request.files['audio']
    try:
        with wave.open(enroll_audio, 'rb') as f:
            frames = f.readframes(f.getnframes())
            pcm = struct.unpack(f"{f.getnframes()}h", frames)
            
            if active_enroll_profiler is None:
                print("🆕 New Identity Enrollment Session Started.")
                active_enroll_profiler = pveagle.create_profiler(access_key=PICO_KEY)
                
            progress, feedback = active_enroll_profiler.enroll(pcm)
            print(f"📈 ENROLL PROGRESS: {progress}% | Feedback: {feedback.name}")
            
            if progress >= 100.0:
                final_profile = active_enroll_profiler.export()
                b64_profile = base64.b64encode(final_profile.to_bytes()).decode('utf-8')
                active_enroll_profiler = None
                return jsonify({"status": "SUCCESS", "new_profile": b64_profile})
            
            return jsonify({"status": "NEED_MORE_AUDIO", "progress": progress})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

# ----------------------------------------------------------
# 🏠 SERVER HEALTH
# ----------------------------------------------------------
@app.route('/')
def index():
    status = "Active" if eagle_engine else "Degraded"
    return f"Citron Neural Engine: {status} | API Keys: {len(GEMINI_API_KEYS)} | Port: 5000 🚀"

if __name__ == '__main__':
    # Render assigns a dynamic port via environment variable
    service_port = int(os.environ.get("PORT", 5000))
    print(f"🚀 JARVIS DEPLOYED: Listening on port {service_port}")
    app.run(host='0.0.0.0', port=service_port, debug=False)
