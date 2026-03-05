from flask import Flask, request, jsonify
import pveagle
import base64
import wave
import struct

app = Flask(__name__)

# 🔥 TERA PICOVOICE KEY
ACCESS_KEY = "KQ8KSsu+nj/D1jlMxVppSkWF4xuDSH9BcQ/qNtaMIBxwXbHgQcacrg=="

# 🔥 TERA BASE64 STRING (Tune jo diya hai wahi rakha hai)
PROFILE_BASE64 = "XRrKh2n/sKxtJNYqwc4mAwqGR0gk5eEh4j29EpFXYab2houpSV9OYSlHYYqDFhSAv2oC3o6POanxDwJcXapI90zXXM1EASRglfNYo8kl4ZB/8o8qPMv2si5tJWlUmFDmnkVWc0Vm5DWkGGOQ9HwnB+1jfrbHNPnVTVnTUuFvoPoEpKUsr0jQxZ3s6E4xmE1UYc7tME3DaKMee6VD2Ep5Sepk6kFhPh+60z0jy6vC+6zEgZr0+lDjJagHD7RPA5pm/4sJdTxspPDv+sBvbIstl5DQzkgdBhdGg3N4niVq0RDsv7qR5ctop1fl6nmmgWvL78FsZRYEQ8jD0oyvmrOGaaEMBOSCx8M0DBykrKs4fOQWe2swiiF24npxX9ccPXFMH9m6I8uUUiTgBR/NhNvSTyZ2s5EXp/2GsXNG1RMF8kipyHsoouXYXR+UDvzn930uXLukK4TCcW/lVhc9HIon4OUdSedLqGq2ztrTgu3hLmdLBLudqsT3w39qkO6jQoTNVWGHlT2IcoqPazQUT7JSrxA0dKuTJP4CjeC9V5MS51PDAwyKdm5IimmPaIhERcIMBzDj1xTZSjcEPNWgSSdNpesYNpZ5JkSWkjLxGNB69IVRGC9SRlzkHlIU4j4BjThk4oTKo6DitAnjvHm/Qe90eESP9gfLupadu9x9UTtbJtiV1IkMDDspD4/JRJvoLoa8EwxTu1R24gVlC9LwurA9BUkvygbJJhkgzorBqwu7xZnbG/s2hMbKxz91ofkFA5i/5H8cGV7ejtzSMPIWXT0z9p42RjXZtEUXnFWOZesWrT1NmCqF4DIC7e4/n6egFPufGEnYWrSi8RN7zole99ecqccjIKxnVUfd7xGw931GOvi/otbVckQ+/6+4hCch+lCB62zw/Zy1buH8fRBoU1ZRP0JP5TsqthvifxKwTPvpovV5dvM0THsMt6mLOvUBibzIe/rI4zIjBHINOjQ1Er2pkFU/CzbZCFbWNqhJkmKahGFce3P+Fu8MGQZ4C7w4Y4XZcUwE/ohKtTKX0zyGdjubJa+mcnAreIT5UFl61I+fjbWlyR4GXEWC9+U13hENKeYK5UQa7xJqZMZSgFAcTuZWcYJ22emuDtt2Y8RF11kVO96i/W1kZYa3Tp9lclVl4uP5RKsCHVANgqfc3PKf+pefxejJGcxqnFN1RvGM7fZWy8gWAd00IuLPDRTSne/frCC5zP+3C2vemQ3E3yDpjwIFSKa3XuPvoD6qZha8KdIhmXwEdJdD/9tLuihbVwZJs+JBmd9aun96CbArFuvmboAxv1lUKGteNVRCSDji5n4Y+X20co/FhKyQRchvI3EeWdQpRHOoCKcPJKW7/Rz/R/hcNaJ5fTDxFK2WmOY0GkKWp2Ggkw/FS2Rz6g=="

eagle = None

# Server start hote hi Voice Profile Load karenge
try:
    print("Loading Boss Voice Profile...")
    profile_bytes = base64.b64decode(PROFILE_BASE64)
    eagle_profile = pveagle.EagleProfile.from_bytes(profile_bytes)
    eagle = pveagle.create_recognizer(access_key=ACCESS_KEY, speaker_profiles=[eagle_profile])
    print("✅ System Ready! Eagle Biometric Engine is Online.")
except Exception as e:
    print("❌ Error loading profile:", str(e))

# Ye API endpoint Android app se aawaz receive karega
@app.route('/verify-voice', methods=['POST'])
def verify_voice():
    if not eagle:
        return jsonify({"status": "ERROR", "message": "Biometric Engine Offline"}), 500
        
    if 'audio' not in request.files:
        return jsonify({"status": "ERROR", "message": "No audio file received"}), 400
        
    audio_file = request.files['audio']
    
    try:
        # Audio file read karo (16kHz, 16-bit Mono WAV format chahiye)
        with wave.open(audio_file, 'rb') as f:
            if f.getframerate() != 16000 or f.getnchannels() != 1:
                return jsonify({"status": "ERROR", "message": "Invalid audio format"}), 400
            
            pcm_data = f.readframes(f.getnframes())
            # Raw bytes ko short array (numbers) mein convert karo
            pcm_shorts = struct.unpack(f"{len(pcm_data) // 2}h", pcm_data)
            
            # Eagle ko 512 frames ke tukdo (chunks) mein aawaz khilao
            frame_length = eagle.frame_length
            max_match_score = 0.0
            
            for i in range(0, len(pcm_shorts) - frame_length, frame_length):
                chunk = pcm_shorts[i : i + frame_length]
                scores = eagle.process(chunk)
                if scores[0] > max_match_score:
                    max_match_score = scores[0]
            
            # Faisla karo! (Score 0.0 se 1.0 ke beech hota hai. 0.50 matlab 50% match)
            print(f"Match Score: {max_match_score * 100:.2f}%")
            
            # Threshold humne 0.40 par set kiya hai
            if max_match_score >= 0.40:
                print("🟢 ACCESS GRANTED BHEJ RAHA HOON...")
                return jsonify({"status": "ACCESS_GRANTED", "score": max_match_score})
            else:
                print("🔴 ACCESS DENIED BHEJ RAHA HOON...")
                return jsonify({"status": "ACCESS_DENIED", "score": max_match_score})
                
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/enroll-voice', methods=['POST'])
def enroll_voice():
    # Ye endpoint phone ki aawaz se NAYI profile banayega
    audio_file = request.files['audio']
    with wave.open(audio_file, 'rb') as f:
        pcm_data = f.readframes(f.getnframes())
        pcm_shorts = struct.unpack(f"{len(pcm_data) // 2}h", pcm_data)
        
        profiler = pveagle.create_profiler(access_key=ACCESS_KEY)
        # Poori aawaz ko enroll karo
        percentage, feedback = profiler.enroll(pcm_shorts)
        
        if percentage >= 100.0:
            profile = profiler.export()
            new_base64 = base64.b64encode(profile.to_bytes()).decode('utf-8')
            print("\n🔥 NEW PHONE-BASED PROFILE READY! 🔥")
            return jsonify({"status": "SUCCESS", "new_profile": new_base64})
        else:
            return jsonify({"status": "NEED_MORE_AUDIO", "progress": percentage})

@app.route('/', methods=['GET'])
def home():
    return "Jarvis Backend is Running!"

# 🔥 YE SABSE ZAROORI LINE HAI JISKE BINA SERVER BAND HO JATA HAI 🔥
import os

if __name__ == '__main__':
    # Render PORT environment variable use karta hai, default 5000
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask Server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)