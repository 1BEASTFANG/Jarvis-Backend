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
# 🔐 ADVANCED SECURITY CONFIG (NO KEYS IN CODE)
# ----------------------------------------------------------
# Render dashboard se keys uthayega. Ye sabse safe method hai.
# Agar ye empty milega, toh system initialized nahi hoga.
RAW_KEYS_DATA = os.environ.get("GEMINI_KEYS", "")

# Logic to split comma separated keys into a list
if RAW_KEYS_DATA:
    GEMINI_API_KEYS = [k.strip() for k in RAW_KEYS_DATA.split(",") if k.strip()]
    print(f"📦 SYSTEM BOOT: Loaded {len(GEMINI_API_KEYS)} API Keys from Environment.")
else:
    GEMINI_API_KEYS = []
    print("🚨 CRITICAL WARNING: No GEMINI_KEYS found in Environment Variables!")

# Picovoice Configuration via Environment or Default Backup
PICO_KEY = os.environ.get("PICOVOICE_API_KEY", "KQ8KSsu+nj/D1jlMxVppSkWF4xuDSH9BcQ/qNtaMIBxwXbHgQcacrg==")
RENDER_URL = "https://jarvis-voice-api-uud7.onrender.com"

# Global System State Management
current_key_index = 0
eagle_engine = None
active_enroll_profiler = None

# ----------------------------------------------------------
# ⚙️ GEMINI ENGINE ROTATION LOGIC (ROUND-ROBIN)
# ----------------------------------------------------------
def rotate_gemini_config():
    """Key shift karne ka detailed function jab limit khatam ho jaye"""
    global current_key_index
    if not GEMINI_API_KEYS:
        print("❌ ABORT: Cannot rotate keys. GEMINI_API_KEYS list is empty.")
        return

    try:
        target_key = GEMINI_API_KEYS[current_key_index]
        genai.configure(api_key=target_key)
        
        # Printing system status for Render Logs
        print("--------------------------------------------------")
        print(f"🔄 CLOUD SYNC: Gemini configured with Key Index [{current_key_index}]")
        print(f"📡 Status: Ready for High-Priority AI Tasks")
        print("--------------------------------------------------")
    except Exception as config_err:
        print(f"❌ CONFIG ERROR: Global switch failed: {str(config_err)}")

# Pehli key initialize karo deployment ke waqt
if GEMINI_API_KEYS:
    rotate_gemini_config()

def call_gemini_safely(model_name, contents):
    """Attempt call with auto-retry on multiple keys to prevent downtime"""
    global current_key_index
    
    if not GEMINI_API_KEYS:
        raise Exception("❌ NO KEYS AVAILABLE: Define GEMINI_KEYS in Render.")

    max_attempts = len(GEMINI_API_KEYS)
    attempts = 0
    
    while attempts < max_attempts:
        try:
            # Model creation with currently configured key
            ai_model = genai.GenerativeModel(model_name)
            ai_response = ai_model.generate_content(contents)
            return ai_response
        except Exception as e:
            err_msg = str(e).lower()
            print(f"⚠️ API FAILURE: Attempt {attempts + 1} with Key Index {current_key_index} failed.")
            
            # Google leaked key error handling
            if "403" in err_msg and "leaked" in err_msg:
                print(f"🛑 SECURITY ALERT: Key {current_key_index} was reported as leaked.")
            
            # Common quota/limit errors
            if "429" in err_msg or "403" in err_msg or "quota" in err_msg or "limit" in err_msg:
                print(f"🔄 SHIFTING: Rotating to the next available API key...")
                current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
                rotate_gemini_config()
                attempts += 1
                time.sleep(1.5) # Anti-spam delay
            else:
                print(f"🚨 UNEXPECTED EXCEPTION: {err_msg}")
                raise e
                
    raise Exception("💀 FATAL ERROR: All provided Gemini API keys are currently non-functional.")

# ----------------------------------------------------------
# 🎙️ MULTI-PROFILE BIOMETRIC DATABASE
# ----------------------------------------------------------
VOICE_PROFILES_LIST = [
    "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"
]

# ----------------------------------------------------------
# 🧠 BIOMETRIC ENGINE LOAD sequence
# ----------------------------------------------------------
try:
    print("💎 JARVIS BIOMETRIC ENGINE: Scanning Ident-Profiles...")
    loaded_profiles = []
    for b_data in VOICE_PROFILES_LIST:
        if b_data.strip():
            profile_obj = pveagle.EagleProfile.from_bytes(base64.b64decode(b_data))
            loaded_profiles.append(profile_obj)
            
    if loaded_profiles:
        eagle_engine = pveagle.create_recognizer(access_key=PICO_KEY, speaker_profiles=loaded_profiles)
        print(f"✅ BOOT SUCCESS: Ident-Profiles linked and active.")
    else:
        print("⚠️ SYSTEM DEGRADED: No biometric profiles found.")
except Exception as bio_err:
    print(f"❌ PICOVOICE ENGINE FAILED: {str(bio_err)}")

# ----------------------------------------------------------
# 🕒 SERVER PERSISTENCE LOOP
# ----------------------------------------------------------
def persistent_ping():
    """Background thread to prevent Render from going to sleep mode"""
    while True:
        time.sleep(14 * 60)
        try:
            print("🕒 [Heartbeat] Pinging internal server to maintain uptime...")
            requests.get(RENDER_URL)
        except Exception:
            pass

threading.Thread(target=persistent_ping, daemon=True).start()

# ==========================================================
# 🛡️ ROUTE 1: VERIFY IDENTITY (RESTRICTED AUTH FOR WHATSAPP)
# ==========================================================
@app.route('/verify-voice', methods=['POST'])
def verify_voice_identity():
    if not eagle_engine:
        return jsonify({"status": "ERROR", "message": "Biometric Core Offline"}), 500
        
    if 'audio' not in request.files:
        print("⚠️ REJECTED: Client submitted request without audio payload.")
        return jsonify({"status": "ERROR", "message": "No audio file received"}), 400
        
    audio_obj = request.files['audio']
    
    try:
        print("🎙️ IDENTITY CHECK: Analyzing biometric signature...")
        
        # Identity scoring via Picovoice Engine
        with wave.open(audio_obj, 'rb') as wav_file:
            if wav_file.getframerate() != 16000:
                return jsonify({"status": "ERROR", "message": "Standard sample rate 16k required"}), 400
                
            raw_pcm_data = wav_file.readframes(wav_file.getnframes())
            pcm_shorts = struct.unpack(f"{len(raw_pcm_data) // 2}h", raw_pcm_data)
            
            f_len = eagle_engine.frame_length
            peak_score = 0.0
            
            # Step-processing for granular accuracy
            for start in range(0, len(pcm_shorts) - f_len, f_len):
                chunk_frame = pcm_shorts[start : start + f_len]
                batch_scores = eagle_engine.process(chunk_frame)
                max_in_batch = max(batch_scores)
                if max_in_batch > peak_score:
                    peak_score = max_in_batch
            
            print(f"📊 FINAL SCORE: {peak_score * 100:.2f}% Match Detected.")
            
            # The Secure Vault Gate (60%)
            if peak_score < 0.60:
                print("🔴 DENIED: Identity mismatch or high background noise.")
                return jsonify({"status": "ACCESS_DENIED", "score": peak_score, "text": ""})
            
            print("🟢 GRANTED: Nikhil confirmed. Switching to Gemini STT engine.")

        # Audio Transcription via the latest Gemini model
        audio_obj.seek(0)
        final_audio_stream = audio_obj.read()
        
        transcription_prompt = """
        You are the Voice Processor for J.A.R.V.I.S.
        Listen to the spoken audio and transcribe it perfectly. 
        Language: Hinglish/Hindi/English.
        Speaker: Nikhil.
        Target Contacts: Harsh, Ranjan, Papa, Arvind, Pankaj Bhaiya, Citron.
        RULES: Clean output only. No conversational filler.
        """
        
        input_payload = [
            transcription_prompt, 
            {"mime_type": "audio/wav", "data": final_audio_stream}
        ]
        
        gemini_response = call_gemini_safely('gemini-2.5-flash', input_payload)
        transcribed_text = gemini_response.text.strip()
        
        print(f"📝 COMMAND CAPTURED: {transcribed_text}")
            
        return jsonify({
            "status": "ACCESS_GRANTED", 
            "score": peak_score, 
            "text": transcribed_text 
        })
                
    except Exception as server_err:
        print(f"❌ SYSTEM ERROR IN AUTH ROUTE: {str(server_err)}")
        return jsonify({"status": "ERROR", "message": str(server_err)}), 500

# ==========================================================
# 🚀 ROUTE 2: LECTURE NINJA (NO AUTH - MULTIMODAL GEMINI)
# ==========================================================
@app.route('/analyze-lecture', methods=['POST'])
def process_class_lecture():
    if 'audio' not in request.files:
        return jsonify({"status": "ERROR", "message": "Missing audio input stream"}), 400
    
    lecture_audio_file = request.files['audio']
    
    try:
        print("🧠 LECTURE NINJA CORE: Deep-Processing class audio...")
        lecture_buffer = lecture_audio_file.read()
        
        # 🔥 THE ULTIMATE PROFESSOR CITRON INSTRUCTIONS 🔥
        citron_logic = """
        You are 'Citron', the world's smartest AI student. 
        Transform this audio lecture into EPIC 'Cartoonish & Sci-Fi' study notes.
        
        MANDATORY RULES:
        1. STYLE: Use fun Hinglish. Be funny but highly accurate.
        2. FORMATTING: 
           - Use <b>Bold</b> for technical terms.
           - Use <br> for spacing.
           - Use <u>Underlines</u> for sub-headings.
        3. EMOJIS: Overload the notes with relevant emojis (minimum 3 per block). 🚀🧪🧠💡
        4. STRUCTURE: Point-wise bullet points ONLY.
        
        JSON KEYS REQUIRED:
        - "short_summary": Energetic 3-line breakdown with ⚡.
        - "detailed_notes": Complete class explanation in HTML (<b>, <br>).
        - "important_keywords": 5 main topics followed by 🔥.
        """
        
        ninja_payload = [
            citron_logic, 
            {"mime_type": "audio/wav", "data": lecture_buffer}
        ]
        
        ai_response = call_gemini_safely('gemini-2.5-flash', ninja_payload)
        
        # Cleaning and parsing JSON from Gemini
        raw_ai_text = ai_response.text.strip()
        filtered_json = raw_ai_text.replace('```json', '').replace('```', '').strip()
        
        json_notes_final = json.loads(filtered_json)
        
        print("✅ SUCCESS: Classroom insights generated and formatted.")
        return jsonify({
            "status": "SUCCESS",
            "short_summary": json_notes_final.get("short_summary", "No summary found."),
            "detailed_notes": json_notes_final.get("detailed_notes", "No detailed notes found."),
            "important_keywords": json_notes_final.get("important_keywords", "No keywords extracted.")
        })

    except Exception as ninja_err:
        print(f"❌ NINJA PROCESSING FAILED: {str(ninja_err)}")
        return jsonify({"status": "ERROR", "message": str(ninja_err)}), 500

# ----------------------------------------------------------
# 👤 ENROLLMENT SERVICE (IDENTITY TRAINING)
# ----------------------------------------------------------
@app.route('/enroll-voice', methods=['POST'])
def register_new_biometric_id():
    global active_enroll_profiler
    
    enroll_stream = request.files['audio']
    try:
        with wave.open(enroll_stream, 'rb') as f:
            pcm_frames = struct.unpack(f"{f.getnframes()}h", f.readframes(f.getnframes()))
            
            if active_enroll_profiler is None:
                print("🆕 ENROLLMENT: Starting a new secure identity session.")
                active_enroll_profiler = pveagle.create_profiler(access_key=PICO_KEY)
                
            pct_complete, feedback_info = active_enroll_profiler.enroll(pcm_frames)
            print(f"📈 PROGRESS: {pct_complete}% | FEEDBACK: {feedback_info.name}")
            
            if pct_complete >= 100.0:
                final_exported_id = active_enroll_profiler.export()
                identity_b64 = base64.b64encode(final_exported_id.to_bytes()).decode('utf-8')
                active_enroll_profiler = None
                return jsonify({"status": "SUCCESS", "new_profile": identity_b64})
            
            return jsonify({"status": "NEED_MORE_AUDIO", "progress": pct_complete})
    except Exception as fatal_e:
        return jsonify({"status": "ERROR", "message": str(fatal_e)}), 500

# ----------------------------------------------------------
# 🏠 JARVIS ENGINE STATUS
# ----------------------------------------------------------
@app.route('/')
def system_status():
    return f"Citron Engine: 100% | Auth: Bio-Locked | Keys: {len(GEMINI_API_KEYS)} 🚀"

if __name__ == '__main__':
    # Listen on Render-provided port or local fallback
    deployment_port = int(os.environ.get("PORT", 5000))
    print(f"🚀 JARVIS NEURAL NETWORK: Online on port {deployment_port}")
    app.run(host='0.0.0.0', port=deployment_port, debug=False)
