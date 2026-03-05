from flask import Flask, request, jsonify
import pveagle
import base64
import wave
import struct
import os
import threading
import time
import requests

app = Flask(__name__)

# ==========================================
# 🔥 TERI API KEYS AUR PROFILE 🔥
# ==========================================
ACCESS_KEY = "KQ8KSsu+nj/D1jlMxVppSkWF4xuDSH9BcQ/qNtaMIBxwXbHgQcacrg=="

# TERA PHONE WALA NAYA BASE64 STRING
PROFILE_BASE64 = "XRrKh2n/sKxtJNYqwc4mAwqGR0gk5eEh4j29EpFXYab2houpSV9OYSlHYYqDFhSAv2oC3o6POanxDwJcXapI90zXXM1EASRglfNYo8kl4ZB/8o8qPMv2si5tJWlUmFDmnkVWc0Vm5DWkGGOQ9HwnB+1jfrbHNPnVTVnTUuFvoPoEpKUsr0jQxZ3s6E4xmE1UYc7tME3DaKMee6VD2Ep5Sepk6kFhPh+60z0jy6vC+6zEgZr0+lDjJagHD7RPA5pm/4sJdTxspPDv+sBvbIstl5DQzkgdBhdGg3N4niVq0RDsv7qR5ctop1fl6nmmgWvL78FsZRYEQ8jD0oyvmrOGaaEMBOSCx8M0DBykrKs4fOQWe2swiiF24npxX9ccPXFMH9m6I8uUUiTgBR/NhNvSTyZ2s5EXp/2GsXNG1RMF8kipyHsoouXYXR+UDvzn930uXLukK4TCcW/lVhc9HIon4OUdSedLqGq2ztrTgu3hLmdLBLudqsT3w39qkO6jQoTNVWGHlT2IcoqPazQUT7JSrxA0dKuTJP4CjeC9V5MS51PDAwyKdm5IimmPaIhERcIMBzDj1xTZSjcEPNWgSSdNpesYNpZ5JkSWkjLxGNB69IVRGC9SRlzkHlIU4j4BjThk4oTKo6DitAnjvHm/Qe90eESP9gfLupadu9x9UTtbJtiV1IkMDDspD4/JRJvoLoa8EwxTu1R24gVlC9LwurA9BUkvygbJJhkgzorBqwu7xZnbG/s2hMbKxz91ofkFA5i/5H8cGV7ejtzSMPIWXT0z9p42RjXZtEUXnFWOZesWrT1NmCqF4DIC7e4/n6egFPufGEnYWrSi8RN7zole99ecqccjIKxnVUfd7xGw931GOvi/otbVckQ+/6+4hCch+lCB62zw/Zy1buH8fRBoU1ZRP0JP5TsqthvifxKwTPvpovV5dvM0THsMt6mLOvUBibzIe/rI4zIjBHINOjQ1Er2pkFU/CzbZCFbWNqhJkmKahGFce3P+Fu8MGQZ4C7w4Y4XZcUwE/ohKtTKX0zyGdjubJa+mcnAreIT5UFl61I+fjbWlyR4GXEWC9+U13hENKeYK5UQa7xJqZMZSgFAcTuZWcYJ22emuDtt2Y8RF11kVO96i/W1kZYa3Tp9lclVl4uP5RKsCHVANgqfc3PKf+pefxejJGcxqnFN1RvGM7fZWy8gWAd00IuLPDRTSne/frCC5zP+3C2vemQ3E3yDpjwIFSKa3XuPvoD6qZha8KdIhmXwEdJdD/9tLuihbVwZJs+JBmd9aun96CbArFuvmboAxv1lUKGteNVRCSDji5n4Y+X20co/FhKyQRchvI3EeWdQpRHOoCKcPJKW7/Rz/R/hcNaJ5fTDxFK2WmOY0GkKWp2Ggkw/FS2Rz6g=="

# 🔥 TERI GROQ API KEY YAHAN DAALNA MAT BHOOLNA 🔥
GROQ_API_KEY = "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"

# 🔥 TERA RENDER LINK 🔥
RENDER_URL = "https://jarvis-voice-api-uud7.onrender.com"

eagle = None

# ------------------------------------------
# 1. EAGLE BIOMETRIC ENGINE LOAD
# ------------------------------------------
try:
    print("Loading Boss Voice Profile...")
    profile_bytes = base64.b64decode(PROFILE_BASE64)
    eagle_profile = pveagle.EagleProfile.from_bytes(profile_bytes)
    eagle = pveagle.create_recognizer(access_key=ACCESS_KEY, speaker_profiles=[eagle_profile])
    print("✅ System Ready! Eagle Biometric Engine is Online.")
except Exception as e:
    print("❌ Error loading profile:", str(e))


# ------------------------------------------
# 2. ANTI-SLEEP PING LOOP (Knock-Knock)
# ------------------------------------------
def keep_awake():
    while True:
        time.sleep(14 * 60)  # Har 14 minute mein ping karega
        try:
            print("🕒 [Anti-Sleep] Knocking on Render's door...")
            requests.get(RENDER_URL)
        except Exception as e:
            print("⚠️ Ping failed:", e)

# Start the background ping thread
threading.Thread(target=keep_awake, daemon=True).start()


# ------------------------------------------
# 3. ONE-SHOT: VOICE VERIFY + SPEECH TO TEXT
# ------------------------------------------
@app.route('/verify-voice', methods=['POST'])
def verify_voice():
    if not eagle:
        return jsonify({"status": "ERROR", "message": "Biometric Engine Offline"}), 500
        
    if 'audio' not in request.files:
        return jsonify({"status": "ERROR", "message": "No audio file received"}), 400
        
    audio_file = request.files['audio']
    
    try:
        # A. VOICE VERIFICATION (EAGLE)
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
                if scores[0] > max_match_score:
                    max_match_score = scores[0]
            
            print(f"Match Score: {max_match_score * 100:.2f}%")
            
            # Agar Match score 40% se kam hai, toh access denied aur text empty bhejo
            if max_match_score < 0.40:
                print("🔴 ACCESS DENIED BHEJ RAHA HOON...")
                return jsonify({"status": "ACCESS_DENIED", "score": max_match_score, "text": ""})
            
            print("🟢 ACCESS GRANTED! Ab audio ko Text mein badal rahe hain...")

        # B. SPEECH TO TEXT (GROQ WHISPER)
        # File pointer ko wapas 0 pe laana padega warna empty file jayegi
        audio_file.seek(0) 
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        files = {'file': ('auth.wav', audio_file, 'audio/wav')}
        data = {
            'model': 'whisper-large-v3',
            'language': 'hi' # Hindi/Hinglish ke liye set hai
        }
        
        # Groq se transcription maango
        response = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=headers, files=files, data=data)
        
        spoken_text = ""
        if response.status_code == 200:
            spoken_text = response.json().get("text", "").strip()
            print(f"📝 Transcribed Text: {spoken_text}")
        else:
            print(f"⚠️ Groq STT Error: {response.text}")
            
        # Pura package wapas phone ko bhejo
        return jsonify({
            "status": "ACCESS_GRANTED", 
            "score": max_match_score, 
            "text": spoken_text 
        })
                
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ------------------------------------------
# 4. ENROLL ROUTE (Temporary Backup)
# ------------------------------------------
@app.route('/enroll-voice', methods=['POST'])
def enroll_voice():
    audio_file = request.files['audio']
    with wave.open(audio_file, 'rb') as f:
        pcm_data = f.readframes(f.getnframes())
        pcm_shorts = struct.unpack(f"{len(pcm_data) // 2}h", pcm_data)
        
        profiler = pveagle.create_profiler(access_key=ACCESS_KEY)
        percentage, feedback = profiler.enroll(pcm_shorts)
        
        if percentage >= 100.0:
            profile = profiler.export()
            new_base64 = base64.b64encode(profile.to_bytes()).decode('utf-8')
            print("\n🔥 NEW PHONE-BASED PROFILE READY! 🔥")
            return jsonify({"status": "SUCCESS", "new_profile": new_base64})
        else:
            return jsonify({"status": "NEED_MORE_AUDIO", "progress": percentage})


# ------------------------------------------
# 5. SERVER HEALTH CHECK (Used by Ping)
# ------------------------------------------
@app.route('/', methods=['GET'])
def home():
    return "Jarvis Backend is Running!"


# ------------------------------------------
# 6. RENDER START COMMAND
# ------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask Server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)

