from flask import Flask, request, jsonify
import pveagle
import base64
import wave
import struct
import os
import threading
import time
import requests
import json

# 🔥 EK DUM NAYA LATEST GOOGLE GENAI SDK 🔥
from google import genai
from google.genai import types

# ==========================================================
# 🚀 INITIALIZING JARVIS NEURAL CORE (LIVE STREAM EDITION) 🚀
# ==========================================================
app = Flask(__name__)

# ----------------------------------------------------------
# 🔐 ADVANCED SECURITY CONFIG (NO KEYS IN CODE)
# ----------------------------------------------------------
# Render dashboard se keys uthayega.
RAW_KEYS_DATA = os.environ.get("GEMINI_KEYS", "")

# Logic to split comma separated keys into a list safely
if RAW_KEYS_DATA:
    GEMINI_API_KEYS = [k.strip() for k in RAW_KEYS_DATA.split(",") if k.strip()]
    print("--------------------------------------------------")
    print(f"📦 SYSTEM BOOT: Loaded {len(GEMINI_API_KEYS)} API Keys from Environment.")
    print("--------------------------------------------------")
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
# ⚙️ LATEST GEMINI ENGINE ROTATION LOGIC (SDK v2)
# ----------------------------------------------------------
def get_active_gemini_client():
    """Returns a new Gemini client using the current active API Key"""
    if not GEMINI_API_KEYS:
        raise Exception("❌ NO KEYS AVAILABLE: Define GEMINI_KEYS in Render.")
    
    active_key = GEMINI_API_KEYS[current_key_index]
    # Naye SDK mein aise initialize karte hain
    return genai.Client(api_key=active_key)

def rotate_api_key():
    """Key shift karne ka detailed function jab limit/quota khatam ho jaye"""
    global current_key_index
    if len(GEMINI_API_KEYS) > 1:
        current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
        print("--------------------------------------------------")
        print(f"🔄 DYNAMIC ROUTING: Shifting traffic to Key Index [{current_key_index}]")
        print("--------------------------------------------------")
    else:
        print("⚠️ ROTATION FAILED: Only 1 key is available in the system.")

def execute_gemini_task(model_name, prompt_text, audio_bytes, use_json_mode=False):
    """Wrapper to handle retries and shifting with the NEW SDK"""
    max_attempts = len(GEMINI_API_KEYS)
    attempts = 0
    
    while attempts < max_attempts:
        try:
            client = get_active_gemini_client()
            
            # Prepare contents (Prompt + Audio) using new SDK format
            contents = [
                prompt_text,
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav')
            ]
            
            # JSON mode config for Lecture Ninja
            config_options = types.GenerateContentConfig(
                response_mime_type="application/json" if use_json_mode else "text/plain"
            )
            
            ai_response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config_options
            )
            return ai_response.text
            
        except Exception as e:
            err_msg = str(e).lower()
            print(f"⚠️ API FAILURE: Attempt {attempts + 1} with Key [{current_key_index}] failed.")
            
            if "403" in err_msg and "leaked" in err_msg:
                print(f"🛑 SECURITY ALERT: Key {current_key_index} was reported as leaked.")
            
            if "429" in err_msg or "403" in err_msg or "quota" in err_msg or "limit" in err_msg:
                rotate_api_key()
                attempts += 1
                time.sleep(1.5) # Buffer before retry
            else:
                print(f"🚨 UNEXPECTED EXCEPTION: {err_msg}")
                raise e
                
    raise Exception("💀 FATAL ERROR: All provided Gemini API keys are exhausted or blocked.")

# ----------------------------------------------------------
# 🎙️ MULTI-PROFILE BIOMETRIC DATABASE
# ----------------------------------------------------------
VOICE_PROFILES_LIST = [
    "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"
]

# ----------------------------------------------------------
# 🧠 BIOMETRIC ENGINE LOAD SEQUENCE
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
    """Background thread to prevent Render from going to sleep"""
    while True:
        time.sleep(14 * 60)
        try:
            print("🕒 [Heartbeat] Pinging internal server to maintain uptime...")
            requests.get(RENDER_URL)
        except Exception:
            pass

threading.Thread(target=persistent_ping, daemon=True).start()

# ==========================================================
# 🛡️ ROUTE 1: VERIFY IDENTITY (RESTRICTED AUTH FOR COMMANDS)
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
        
        with wave.open(audio_obj, 'rb') as wav_file:
            if wav_file.getframerate() != 16000:
                return jsonify({"status": "ERROR", "message": "Sample rate must be 16k"}), 400
                
            raw_pcm_data = wav_file.readframes(wav_file.getnframes())
            pcm_shorts = struct.unpack(f"{len(raw_pcm_data) // 2}h", raw_pcm_data)
            
            f_len = eagle_engine.frame_length
            peak_score = 0.0
            
            for start in range(0, len(pcm_shorts) - f_len, f_len):
                chunk_frame = pcm_shorts[start : start + f_len]
                batch_scores = eagle_engine.process(chunk_frame)
                max_in_batch = max(batch_scores)
                if max_in_batch > peak_score:
                    peak_score = max_in_batch
            
            print(f"📊 FINAL SCORE: {peak_score * 100:.2f}% Match Detected.")
            
            if peak_score < 0.60:
                print("🔴 DENIED: Identity mismatch or high background noise.")
                return jsonify({"status": "ACCESS_DENIED", "score": peak_score, "text": ""})
            
            print("🟢 GRANTED: Nikhil confirmed. Sending to Gemini 2.5 Flash STT...")

        audio_obj.seek(0)
        final_audio_stream = audio_obj.read()
        
        transcription_prompt = """
        You are the Voice Processor for J.A.R.V.I.S.
        Listen to the spoken audio and transcribe it perfectly. 
        Speaker: Nikhil. Target Contacts: Harsh, Ranjan, Papa, Arvind, Pankaj Bhaiya, Citron.
        RULES: Clean output only. No conversational filler.
        """
        
        # New SDK wrapper call
        final_text = execute_gemini_task('gemini-2.5-flash', transcription_prompt, final_audio_stream, use_json_mode=False)
        print(f"📝 COMMAND CAPTURED: {final_text.strip()}")
            
        return jsonify({
            "status": "ACCESS_GRANTED", 
            "score": peak_score, 
            "text": final_text.strip()
        })
                
    except Exception as server_err:
        print(f"❌ SYSTEM ERROR IN AUTH ROUTE: {str(server_err)}")
        return jsonify({"status": "ERROR", "message": str(server_err)}), 500

# ==========================================================
# 🚀 ROUTE 2: LECTURE NINJA (LIVE STREAM & STRICT FORMAT)
# ==========================================================
@app.route('/analyze-lecture', methods=['POST'])
def process_class_lecture():
    if 'audio' not in request.files:
        return jsonify({"status": "ERROR", "message": "Missing audio input stream"}), 400
    
    lecture_audio_file = request.files['audio']
    
    try:
        lecture_buffer = lecture_audio_file.read()
        chunk_size_mb = len(lecture_buffer) / (1024 * 1024)
        
        print("--------------------------------------------------")
        print(f"⏳ LIVE CHUNK RECEIVED: Size {chunk_size_mb:.2f} MB")
        print("🧠 LECTURE NINJA: Deep-Processing Audio Segment...")
        print("--------------------------------------------------")
        
        # 🔥 THE STRICT "PROPER NOTES FORMAT" PROMPT 🔥
        strict_logic = """
        You are 'Citron', a highly intelligent AI Note-Taker.
        You are receiving a short AUDIO CHUNK from a live, continuous college lecture.
        
        STRICT MISSION:
        Extract ONLY the educational concepts discussed in THIS specific audio clip. 
        Do not make up information that is not in the audio.
        
        STRICT FORMATTING RULES (PROPER NOTES FORMAT ONLY):
        1. TONE: Hinglish (Hindi + English), "Indian College Student" vibe.
        2. STRUCTURE: You MUST use a standard, professional study-note format (Bullet points, Headings). Do not write paragraphs.
        3. HTML TAGS: Use ONLY <b> for bolding important terms/headings and <br> for line breaks. Do NOT use Markdown (* or #).
        4. EMOJIS: Add relevant educational emojis at the start of points (🚀, 💡, 🧠, 📊, ⚙️).
        5. DETAIL: Even if the chunk is short, explain whatever was said thoroughly as if preparing for an exam.
        
        OUTPUT SCHEMA: Return ONLY valid JSON matching this exact structure:
        {
          "short_summary": "1-2 line energetic summary of THIS specific chunk.",
          "detailed_notes": "Properly formatted bulleted notes using <b> and <br>.",
          "important_keywords": "Comma-separated list of top 3-4 terms, ending with 🔥."
        }
        """
        
        # Execute with JSON mode enforced via the new SDK
        response_text = execute_gemini_task('gemini-2.5-flash', strict_logic, lecture_buffer, use_json_mode=True)
        
        # Parse JSON
        raw_text_clean = response_text.strip().replace('```json', '').replace('```', '').strip()
        json_notes_final = json.loads(raw_text_clean)
        
        print("✅ SUCCESS: Structured study notes generated for this chunk.")
        return jsonify({
            "status": "SUCCESS",
            "short_summary": json_notes_final.get("short_summary", "Summary missing 😢"),
            "detailed_notes": json_notes_final.get("detailed_notes", "Notes missing 😢"),
            "important_keywords": json_notes_final.get("important_keywords", "Keywords missing 😢")
        })

    except Exception as ninja_err:
        print(f"❌ CHUNK PROCESSING FAILED: {str(ninja_err)}")
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
    return f"Citron Live-Stream Engine: 100% | Auth: Bio-Locked | Active Keys: {len(GEMINI_API_KEYS)} 🚀"

if __name__ == '__main__':
    deployment_port = int(os.environ.get("PORT", 5000))
    print(f"🚀 JARVIS NEURAL NETWORK: Online on port {deployment_port}")
    app.run(host='0.0.0.0', port=deployment_port, debug=False)
