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
# 🔥 TERI API KEYS AUR MULTI-PROFILES 🔥
# ==========================================
ACCESS_KEY = "KQ8KSsu+nj/D1jlMxVppSkWF4xuDSH9BcQ/qNtaMIBxwXbHgQcacrg=="

# 🔥 YAHAN MULTIPLE PROFILES DAAL SAKTE HAIN 🔥
PROFILES_BASE64 = [
    # PROFILE 1 (Purana Wala - DO NOT DELETE)
    "XRrKh2n/sKxtJNYqwc4mAwqGR0gk5eEh4j29EpFXYab2houpSV9OYSlHYYqDFhSAv2oC3o6POanxDwJcXapI90zXXM1EASRglfNYo8kl4ZB/8o8qPMv2si5tJWlUmFDmnkVWc0Vm5DWkGGOQ9HwnB+1jfrbHNPnVTVnTUuFvoPoEpKUsr0jQxZ3s6E4xmE1UYc7tME3DaKMee6VD2Ep5Sepk6kFhPh+60z0jy6vC+6zEgZr0+lDjJagHD7RPA5pm/4sJdTxspPDv+sBvbIstl5DQzkgdBhdGg3N4niVq0RDsv7qR5ctop1fl6nmmgWvL78FsZRYEQ8jD0oyvmrOGaaEMBOSCx8M0DBykrKs4fOQWe2swiiF24npxX9ccPXFMH9m6I8uUUiTgBR/NhNvSTyZ2s5EXp/2GsXNG1RMF8kipyHsoouXYXR+UDvzn930uXLukK4TCcW/lVhc9HIon4OUdSedLqGq2ztrTgu3hLmdLBLudqsT3w39qkO6jQoTNVWGHlT2IcoqPazQUT7JSrxA0dKuTJP4CjeC9V5MS51PDAwyKdm5IimmPaIhERcIMBzDj1xTZSjcEPNWgSSdNpesYNpZ5JkSWkjLxGNB69IVRGC9SRlzkHlIU4j4BjThk4oTKo6DitAnjvHm/Qe90eESP9gfLupadu9x9UTtbJtiV1IkMDDspD4/JRJvoLoa8EwxTu1R24gVlC9LwurA9BUkvygbJJhkgzorBqwu7xZnbG/s2hMbKxz91ofkFA5i/5H8cGV7ejtzSMPIWXT0z9p42RjXZtEUXnFWOZesWrT1NmCqF4DIC7e4/n6egFPufGEnYWrSi8RN7zole99ecqccjIKxnVUfd7xGw931GOvi/otbVckQ+/6+4hCch+lCB62zw/Zy1buH8fRBoU1ZRP0JP5TsqthvifxKwTPvpovV5dvM0THsMt6mLOvUBibzIe/rI4zIjBHINOjQ1Er2pkFU/CzbZCFbWNqhJkmKahGFce3P+Fu8MGQZ4C7w4Y4XZcUwE/ohKtTKX0zyGdjubJa+mcnAreIT5UFl61I+fjbWlyR4GXEWC9+U13hENKeYK5UQa7xJqZMZSgFAcTuZWcYJ22emuDtt2Y8RF11kVO96i/W1kZYa3Tp9lclVl4uP5RKsCHVANgqfc3PKf+pefxejJGcxqnFN1RvGM7fZWy8gWAd00IuLPDRTSne/frCC5zP+3C2vemQ3E3yDpjwIFSKa3XuPvoD6qZha8KdIhmXwEdJdD/9tLuihbVwZJs+JBmd9aun96CbArFuvmboAxv1lUKGteNVRCSDji5n4Y+X20co/FhKyQRchvI3EeWdQpRHOoCKcPJKW7/Rz/R/hcNaJ5fTDxFK2WmOY0GkKWp2Ggkw/FS2Rz6g==",
    
    # PROFILE 2 (Naya Wala Yahan Paste Karna baad mein, quotes ke andar)
    "xzXzs3/XHP8LvO7FY6H+omCHnev5m2hZU9JtyckriTyK6W+tRoAV1WOFEBiyDy3SMKrZKPLil655SHVsWuJTt3AckzIsYAemfGnn/YSB2n50KcBJjmQ6fKHdph4B1KMpG/QzAEbrEoX3h7mCSSfSUqgn4KdOpO35ngJhRYLaMafz9J5SCjVXsjtNeueuvAJR27wsgcNx3YgKFaq2m5OiV19URC0dVINSofWVECEr58LFYPq8acejiBDNCjd4IrLbZm1FNDAT2fKxgHv+E5dwzQliyFOvNjoJx50dew4jNBwXc53fcbX+JlEp4Vx5JgX9XupWRZ6qu0+vHLUBweO79jgvNKWfHMlf2RWZeHCbJheEdwjLVPiBPa1g3n+gtfc8nC2abXvtW/sNuh6p3c6EbDu8GPHrAVzhxuBjHR58SJGlS9Fx7Mz9R0K6F2XxWSgYBxk2SSt9pJDDuTqDL1APdPfm4yuKsIeAX5gErjlfk2tJ/7tFzUe6S+N9k+OC3kUl7gBWzZVv+hqIDISzzuLPvFUBcWReo/GVGHvy9clMf/0AfZQlILBRDFZ7Tyi4ynabRhdieKY1w9i7jw4Hm5dKBjJNdfUAamtYfku3f0H2fHiJbdx3IwMUcOpg53nocJIQ1rlTUETQaItAhbpmxAUE4QAZF0bL8r77fmBNuEN6XKRyOOiC03yU8A8TJsdu2IZUaVt228HLEsnE5WmNr9owr9YsUaBFVdSoxRtnCkZG1yGm7GOJzqc81tDDYCBnZEoZ6ANJgN/Ppo2eMCBJvOkXY2w9FmptCQGcWobGAkHQ4YaRrJWvMbf584zz7hJjcASip7Bf0d6hZcA9nGOC43Ap+faMq0J9ueSHADK1uIAFwCBMll6HxeZClO4RXfKbLR8PkDwJ8ewiA3vXIdc3pE1HnJwpy7UJD/pff5MIJ2OeB3MA+vHvPB8Is5/SNgtSJUqu4SVQzFjuuKueCBVm67UO5q2dDf8LozhvUWocZzONUy2spKvQCmnEWCn8z7mJZN2SxsxdMqqf4vCWKvwzIwFmjVrcxU0zXmVTO3qwfAJhNQANmHE5mQdd5lMmjcM+ad0vPo0O8kEP6WdGwQ3tARR91fai4uJzqj9dx6MAdSTAUrX3N3J/J73SNhfyDXOjlzOyvvmO6FXCi5E0fSmnV0aNpX3k8LefYDvZlAxf041906LXuVZlbv7A6+qPC+0KLoQwWmf05sJ3hDGKTeeW2sTNzErcUkHnAddmvIuNCk3FWhRh3ZxGdGm9LvK9SwgrH+rOR8rWaU6WPKZzXmdXPDxu+PwXwXRJuT8NreXvwAvjeJQvNJkNnGDd3kWhUOaEUbs2aMo10ylHIMRb4Oyp/yCgFmG/qSmBx788VxIES7ANNamv53juQ83bUQ==", 
]

GROQ_API_KEY = "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"
RENDER_URL = "https://jarvis-voice-api-uud7.onrender.com"

eagle = None

# 🔥 NAYA MEMORY VARIABLE: Ye teri pichli aawaz ko yaad rakhega 🔥
active_profiler = None

# ------------------------------------------
# 1. EAGLE BIOMETRIC ENGINE LOAD (Multi-Profile)
# ------------------------------------------
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


# ------------------------------------------
# 2. ANTI-SLEEP PING LOOP (Knock-Knock)
# ------------------------------------------
def keep_awake():
    while True:
        time.sleep(14 * 60)  
        try:
            requests.get(RENDER_URL)
        except Exception as e:
            pass

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
        # A. VOICE VERIFICATION (EAGLE MULTI-CHECK)
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
            
            # 🔥 60% Strictness Rule Maintained 🔥
            if max_match_score < 0.60:
                print("🔴 ACCESS DENIED (Score too low or too much background noise)...")
                return jsonify({"status": "ACCESS_DENIED", "score": max_match_score, "text": ""})
            
            print("🟢 ACCESS GRANTED! Nikhil's voice confirmed. Processing text...")

        # B. SPEECH TO TEXT (GROQ WHISPER)
        audio_file.seek(0) 
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        files = {'file': ('auth.wav', audio_file, 'audio/wav')}
        
      # 🔥 WHISPER HALLUCINATION FIX (No more double names like Harsh हर्ष) 🔥
        data = {
            'model': 'whisper-large-v3',
            'language': 'hi',
            'prompt': 'मेरा नाम Nikhil है। Harsh, Ranjan, Papa, Arvind, Pankaj Bhaiya, Citron, Saurabh, Vicky, Piyush Kumar, Aryan, Atul, Rahul, Abhijit, Shabad, Ruby, Harshit, Shivam को मैसेज भेजो।',
            'temperature': '0.0' 
        }
        
        response = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=headers, files=files, data=data)
        
        spoken_text = ""
        if response.status_code == 200:
            spoken_text = response.json().get("text", "").strip()
            print(f"📝 Transcribed Text: {spoken_text}")
        else:
            print(f"⚠️ Groq STT Error: {response.text}")
            
        return jsonify({
            "status": "ACCESS_GRANTED", 
            "score": max_match_score, 
            "text": spoken_text 
        })
                
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ------------------------------------------
# 4. ENROLL ROUTE (Fixed: Memory Feature Added)
# ------------------------------------------
@app.route('/enroll-voice', methods=['POST'])
def enroll_voice():
    global active_profiler # 🔥 MEMORY FIX: Ab pichli aawaz yaad rakhega 🔥
    
    audio_file = request.files['audio']
    with wave.open(audio_file, 'rb') as f:
        pcm_data = f.readframes(f.getnframes())
        pcm_shorts = struct.unpack(f"{len(pcm_data) // 2}h", pcm_data)
        
        # Agar pehli baar record ho raha hai (Memory khali hai)
        if active_profiler is None:
            print("🆕 Starting NEW voice profile session...")
            active_profiler = pveagle.create_profiler(access_key=ACCESS_KEY)
            
        percentage, feedback = active_profiler.enroll(pcm_shorts)
        print(f"📈 Current Training: {percentage}% | Feedback: {feedback.name}")
        
        if percentage >= 100.0:
            profile = active_profiler.export()
            new_base64 = base64.b64encode(profile.to_bytes()).decode('utf-8')
            print("\n🔥 NEW PHONE-BASED PROFILE READY! 🔥")
            
            # Training poori ho gayi, agli baar ke liye memory clear kar do
            active_profiler = None 
            
            return jsonify({"status": "SUCCESS", "new_profile": new_base64})
        else:
            return jsonify({"status": "NEED_MORE_AUDIO", "progress": percentage})


# ------------------------------------------
# 5. SERVER HEALTH CHECK
# ------------------------------------------
@app.route('/', methods=['GET'])
def home():
    return "Jarvis Backend is Running!"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask Server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)


