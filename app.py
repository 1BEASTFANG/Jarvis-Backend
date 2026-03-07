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

app = Flask(__name__)

# ==========================================
# 🔥 TERA API KEY ROUND-ROBIN SYSTEM 🔥
# ==========================================
ACCESS_KEY = "KQ8KSsu+nj/D1jlMxVppSkWF4xuDSH9BcQ/qNtaMIBxwXbHgQcacrg=="
RENDER_URL = "https://jarvis-voice-api-uud7.onrender.com"

# 🔥 YAHAN APNI SAARI GEMINI KEYS DAAL 🔥
GEMINI_API_KEYS = [
    "AIzaSyA4653Ot5yXJNaUulMHyAOAjFQxbcMNskM",
    "AIzaSyAUltC2WlOae6hKayp93Xt3InpbT15L4jw",
    "AIzaSyDsBmI1UWKGAObqffPVnV4TDQ5BKXXUKnM"
]

current_key_index = 0

def configure_gemini(key_index):
    try:
        genai.configure(api_key=GEMINI_API_KEYS[key_index])
        print(f"🔄 Gemini configured with Key Index: {key_index}")
    except Exception as e:
        print(f"❌ Failed to configure Gemini with Key Index {key_index}: {e}")

configure_gemini(current_key_index)

def generate_content_with_retry(model_name, contents, max_retries=3):
    global current_key_index
    retries = 0
    while retries < max_retries:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(contents)
            return response
        except Exception as e:
            error_msg = str(e).lower()
            print(f"⚠️ Gemini API Error (Attempt {retries + 1}): {error_msg}")
            
            if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                print("🔄 Key Limit Exhausted! Shifting to the next Gemini Key...")
                current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
                configure_gemini(current_key_index)
                retries += 1
                time.sleep(1) 
            else:
                raise e
    raise Exception("❌ All Gemini API Keys exhausted or failed.")

# ==========================================
# 🔥 MULTI-PROFILES BIOMETRIC DATA 🔥
# ==========================================
PROFILES_BASE64 = [
    "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"
]

eagle = None
active_profiler = None

try:
    print("Loading Boss Voice Profiles...")
    eagle_profiles = []
    
    for b64_str in PROFILES_BASE64:
        if b64_str.strip(): 
            profile_bytes = base64.b64decode(b64_str)
            eagle_profiles.append(pveagle.EagleProfile.from_bytes(profile_bytes))
            
    if eagle_profiles:
        eagle = pveagle.create_recognizer(access_key=ACCESS_KEY, speaker_profiles=eagle_profiles)
        print(f"✅ System Ready! {len(eagle_profiles)} Eagle Biometric Profiles Loaded.")
    else:
        print("❌ No valid profiles found.")
except Exception as e:
    print("❌ Error loading profiles:", str(e))

def keep_awake():
    while True:
        time.sleep(14 * 60)  
        try:
            requests.get(RENDER_URL)
        except Exception:
            pass

threading.Thread(target=keep_awake, daemon=True).start()

# ==========================================================
# 1. PURE GEMINI STT (Voice to Text Engine)
# ==========================================================
@app.route('/verify-voice', methods=['POST'])
def verify_voice():
    if not eagle:
        return jsonify({"status": "ERROR", "message": "Biometric Engine Offline"}), 500
        
    if 'audio' not in request.files:
        return jsonify({"status": "ERROR", "message": "No audio file received"}), 400
        
    audio_file = request.files['audio']
    
    try:
        with wave.open(audio_file, 'rb') as f:
            if f.getframerate() != 16000 or f.getnchannels() != 1:
                return jsonify({"status": "ERROR", "message": "Invalid audio format"}), 400
            
            pcm_data = f.readframes(f.getnframes())
            pcm_shorts = struct.unpack(f"{len(pcm_data) // 2}h", pcm_data)
            
            frame_length = eagle.frame_length
            max_match_score = 0.0
            
            for i in range(0, len(pcm_shorts) - frame_length, frame_length):
                chunk = pcm_shorts[i : i + frame_length]
                scores = eagle.process(chunk)
                highest_in_chunk = max(scores) 
                if highest_in_chunk > max_match_score:
                    max_match_score = highest_in_chunk
            
            print(f"Match Score: {max_match_score * 100:.2f}%")
            
            if max_match_score < 0.60:
                print("🔴 ACCESS DENIED (Score too low)...")
                return jsonify({"status": "ACCESS_DENIED", "score": max_match_score, "text": ""})
            
            print("🟢 ACCESS GRANTED! Using Gemini 2.5 Flash for STT...")

        audio_file.seek(0) 
        audio_bytes = audio_file.read()
        
        prompt = """
        You are a highly accurate transcriber. Listen to the attached audio. 
        The speaker is named Nikhil. 
        Other potential names in the audio are: Harsh, Ranjan, Papa, Arvind, Pankaj Bhaiya, Citron, Saurabh, Vicky, Piyush Kumar, Aryan, Atul, Rahul, Abhijit, Shabad, Ruby, Harshit, Shivam.

        RULES:
        1. Transcribe EXACTLY what is spoken.
        2. Keep Hinglish/Hindi words in Devnagari OR English script as naturally spoken.
        3. Only output the transcribed text, absolutely nothing else.
        """
        
        contents = [prompt, {"mime_type": "audio/wav", "data": audio_bytes}]
        response = generate_content_with_retry('gemini-2.5-flash', contents)
        
        spoken_text = response.text.strip()
        print(f"📝 Gemini Transcribed Text: {spoken_text}")
            
        return jsonify({
            "status": "ACCESS_GRANTED", 
            "score": max_match_score, 
            "text": spoken_text 
        })
                
    except Exception as e:
        print(f"❌ Verification Error: {str(e)}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

# ==========================================================
# 2. EAGLE ENROLLMENT ENGINE
# ==========================================================
@app.route('/enroll-voice', methods=['POST'])
def enroll_voice():
    global active_profiler 
    
    audio_file = request.files['audio']
    with wave.open(audio_file, 'rb') as f:
        pcm_data = f.readframes(f.getnframes())
        pcm_shorts = struct.unpack(f"{len(pcm_data) // 2}h", pcm_data)
        
        if active_profiler is None:
            print("🆕 Starting NEW voice profile session...")
            active_profiler = pveagle.create_profiler(access_key=ACCESS_KEY)
            
        percentage, feedback = active_profiler.enroll(pcm_shorts)
        print(f"📈 Current Training: {percentage}% | Feedback: {feedback.name}")
        
        if percentage >= 100.0:
            profile = active_profiler.export()
            new_base64 = base64.b64encode(profile.to_bytes()).decode('utf-8')
            print("\n🔥 NEW PHONE-BASED PROFILE READY! 🔥")
            active_profiler = None 
            return jsonify({"status": "SUCCESS", "new_profile": new_base64})
        else:
            return jsonify({"status": "NEED_MORE_AUDIO", "progress": percentage})

# ==========================================================
# 🚀 3. LECTURE NINJA (GEMINI 2.5 FLASH) 🚀
# ==========================================================
@app.route('/analyze-lecture', methods=['POST'])
def analyze_lecture():
    # 🔥 YAHAN KOI BIOMETRIC AUTH NAHI HAI 🔥
    # Koi bhi phone ke paas bolega, notes ban jayenge!
    if 'audio' not in request.files:
        return jsonify({"status": "ERROR", "message": "No audio file received"}), 400
        
    audio_file = request.files['audio']
    
    try:
        print("🧠 Sending Lecture Audio directly to Gemini 2.5 Flash for Detailed Notes...")
        audio_bytes = audio_file.read()
        
        # 🔥 THE ULTIMATE CARTOONISH/FUN PROMPT 🔥
        prompt = """
        You are 'Citron', a super cool, highly intelligent, and fun AI Note-Taker for a college student named Nikhil.
        Listen to the attached lecture audio. 
        
        RULES FOR GENERATING NOTES:
        1. Be EXTREMELY detailed. Do not skip any core concept taught in the lecture.
        2. Use a fun, engaging, "Indian College Student" tone (Hinglish/Hindi mixed with English).
        3. Use ALOT of relevant emojis (e.g., 🚀, 💡, 🤯, 🧠, 📚, ⚙️).
        4. Structure the notes beautifully with bold tags (<b>text</b>), bullet points, and subheadings using basic HTML tags like <br>, <b>, <i>, <ul>, <li>.
        5. Explain complex topics as if you are explaining them to a friend a night before the exam.
        
        Create a highly structured JSON response with EXACTLY these three keys:
        1. "short_summary": A fun, energetic 3-4 line summary of the lecture with emojis.
        2. "detailed_notes": Very long, detailed, and beautifully formatted HTML-like text (using <b>, <br>, etc.) explaining everything step-by-step.
        3. "important_keywords": A comma-separated list of the 5 most important terms with a 🔥 emoji at the end of each.

        OUTPUT ONLY VALID JSON. Do not use markdown blocks like ```json.
        """
        
        contents = [prompt, {"mime_type": "audio/wav", "data": audio_bytes}]
        response = generate_content_with_retry('gemini-2.5-flash', contents)
        
        clean_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        notes_data = json.loads(clean_text)
        
        print("✅ Colorful Notes Generated Successfully!")
        return jsonify({
            "status": "SUCCESS",
            "short_summary": notes_data.get("short_summary", "Summary missing 😢"),
            "detailed_notes": notes_data.get("detailed_notes", "Notes missing 😢"),
            "important_keywords": notes_data.get("important_keywords", "Keywords missing 😢")
        })

    except Exception as e:
        print("❌ Gemini Lecture Error:", str(e))
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Jarvis Backend is Running (100% Powered by Gemini 2.5 Flash)!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask Server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
