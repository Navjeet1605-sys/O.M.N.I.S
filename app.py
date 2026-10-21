import os
import sys
import json
import glob
import asyncio
import subprocess
import threading
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import dotenv_values

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")
DATA_DIR = os.path.join(BASE_DIR, "Data")
CHAT_LOG_FILE = os.path.join(DATA_DIR, "ChatLog.json")

# Ensure Data folder exists
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(CHAT_LOG_FILE):
    try:
        with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    except Exception:
        pass

# Initialize Flask app
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# Load environment configuration
env_vars = dotenv_values(os.path.join(BASE_DIR, ".env"))
Username = env_vars.get("Username", "Sir")
Assistantname = env_vars.get("Assistantname", "OMNIS")
CohereAPIKey = env_vars.get("CohereAPIKey")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Heuristic DMM fallback when Cohere key is missing or offline
def fallback_dmm(query: str):
    q = query.lower().strip()
    decisions = []
    
    if any(q.startswith(w) for w in ["exit", "bye", "quit", "close assistant"]):
        return ["exit"]
    
    # Automation checks
    if q.startswith("open "):
        decisions.append(q)
    elif q.startswith("close "):
        decisions.append(q)
    elif q.startswith("play "):
        decisions.append(q)
    elif "generate image" in q or q.startswith("generate "):
        decisions.append(f"generate image {q.replace('generate image', '').replace('generate', '').strip()}")
    elif q.startswith("google search") or q.startswith("search on google"):
        topic = q.replace("google search", "").replace("search on google", "").strip()
        decisions.append(f"google search {topic}")
    elif q.startswith("youtube search") or q.startswith("search on youtube"):
        topic = q.replace("youtube search", "").replace("search on youtube", "").strip()
        decisions.append(f"youtube search {topic}")
    elif any(k in q for k in ["volume up", "volume down", "mute", "unmute"]):
        decisions.append(f"volume {q}")
    elif q.startswith("write a") or q.startswith("content "):
        decisions.append(f"content {q}")
        
    # If an action was identified, return it directly
    if decisions:
        return decisions

    # Realtime vs General query classification
    realtime_keywords = [
        "today", "current", "latest", "price", "rate", "news", "weather", 
        "score", "who is", "who won", "prime minister", "president", "stock", "live"
    ]
    if any(k in q for k in realtime_keywords):
        decisions.append(f"realtime {query}")
    else:
        decisions.append(f"general {query}")
            
    return decisions

# Safe execution wrapper for FirstLayerDMM
def execute_dmm(query: str):
    if CohereAPIKey and CohereAPIKey.strip() and CohereAPIKey != "your_cohere_api_key_here":
        try:
            from Backend.Model import FirstLayerDMM
            return FirstLayerDMM(query)
        except Exception as e:
            print(f"[DMM Error] Fallback to heuristic: {e}")
    return fallback_dmm(query)

# Safe execution wrapper for ChatBot
def execute_chatbot(query: str):
    if GroqAPIKey and GroqAPIKey.strip() and GroqAPIKey != "your_groq_api_key_here":
        try:
            from Backend.Chatbot import ChatBot
            return ChatBot(query)
        except Exception as e:
            print(f"[ChatBot Error] {e}")
            return f"I encountered an error connecting to my neural core: {e}"
    return f"Greetings {Username}! I am {Assistantname}. To enable full conversational responses, please add your GroqAPIKey in the .env file. (Query received: '{query}')"

# Safe execution wrapper for RealtimeSearchEngine
def execute_search(query: str):
    if GroqAPIKey and GroqAPIKey.strip() and GroqAPIKey != "your_groq_api_key_here":
        try:
            from Backend.RealtimeSearchEngine import RealtimeSearchEngine
            return RealtimeSearchEngine(query)
        except Exception as e:
            print(f"[Search Error] {e}")
            return f"Search engine error: {e}. Please ensure network and duckduckgo search requirements are satisfied."
    return f"[Realtime Intelligence] Online search for '{query}' requires a valid GroqAPIKey configured in .env."

# Safe execution wrapper for TextToSpeech
def execute_tts(text: str):
    try:
        from Backend.TextToSpeech import TextToSpeech
        threading.Thread(target=TextToSpeech, args=(text,), daemon=True).start()
        return True
    except Exception as e:
        print(f"[TTS Error] {e}")
        return False

# Safe execution for Automation
def execute_automation(decision_list):
    try:
        from Backend.Automation import Automation
        asyncio.run(Automation(decision_list))
        return True
    except Exception as e:
        print(f"[Automation Error] {e}")
        return False

# Trigger Image Generation
def trigger_image_gen(prompt: str):
    try:
        data_file = os.path.join(BASE_DIR, "ImageGeneration.data")
        with open(data_file, "w", encoding="utf-8") as f:
            f.write(f"{prompt},True")
        
        # Launch ImageGeneration.py as background worker
        subprocess.Popen(
            [sys.executable, os.path.join(BASE_DIR, "Backend", "ImageGeneration.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except Exception as e:
        print(f"[ImageGen Error] {e}")
        return False

# Helper: Append to chat log
def log_interaction(query, answer, decision):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": query,
        "assistant": answer,
        "decision": decision
    }
    try:
        logs = []
        if os.path.exists(CHAT_LOG_FILE):
            with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        logs.append(entry)
        with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs[-100:], f, indent=2) # Keep last 100 entries
    except Exception as e:
        print(f"[Log Error] {e}")

# ==================== ROUTES ====================

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    has_cohere = bool(CohereAPIKey and CohereAPIKey != "your_cohere_api_key_here")
    has_groq = bool(GroqAPIKey and GroqAPIKey != "your_groq_api_key_here")
    
    # Check system telemetry
    cpu_percent = 18.4
    mem_percent = 42.1
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem_percent = psutil.virtual_memory().percent
    except Exception:
        pass

    return jsonify({
        "status": "ONLINE",
        "system_name": Assistantname,
        "user_name": Username,
        "modules": {
            "dmm_cohere": "ACTIVE" if has_cohere else "STANDBY (HEURISTIC)",
            "llm_groq": "ACTIVE" if has_groq else "STANDBY (KEY NEEDED)",
            "speech_tts": "READY",
            "automation_engine": "READY",
            "image_gen": "READY"
        },
        "telemetry": {
            "cpu": cpu_percent,
            "memory": mem_percent,
            "uptime": "ACTIVE",
            "server_time": datetime.now().strftime("%H:%M:%S")
        }
    })

def resolve_automation_url(decision_list):
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chatgpt.com",
        "github": "https://github.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "whatsapp": "https://web.whatsapp.com",
        "linkedin": "https://www.linkedin.com",
        "amazon": "https://www.amazon.in",
        "spotify": "https://open.spotify.com",
        "netflix": "https://www.netflix.com",
        "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://www.reddit.com",
        "x": "https://x.com",
        "twitter": "https://x.com"
    }
    for d in decision_list:
        cmd = d.lower().strip()
        if cmd.startswith("open "):
            target = cmd[5:].strip()
            if target in websites:
                return websites[target]
            if target.startswith("http://") or target.startswith("https://"):
                return target
            if any(target.endswith(tld) for tld in [".com", ".org", ".net", ".in", ".io", ".ai", ".co"]):
                return f"https://{target}"
        elif cmd.startswith("google search ") or cmd.startswith("search on google "):
            topic = cmd.replace("google search ", "").replace("search on google ", "").strip()
            import urllib.parse
            return f"https://www.google.com/search?q={urllib.parse.quote(topic)}"
        elif cmd.startswith("youtube search ") or cmd.startswith("search on youtube ") or cmd.startswith("play "):
            topic = cmd.replace("youtube search ", "").replace("search on youtube ", "").replace("play ", "").strip()
            import urllib.parse
            return f"https://www.youtube.com/results?search_query={urllib.parse.quote(topic)}"
    return None

@app.route("/api/query", methods=["POST"])
def process_query():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    voice_enabled = data.get("voice", True)

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # 1. Decision Making
    decision = execute_dmm(query)
    answer = ""
    query_type = "general"
    image_prompt = None

    # Check for image generation
    for d in decision:
        if "generate " in d or "generate image" in d:
            image_prompt = d.replace("generate image", "").replace("generate", "").strip()
            answer = f"Initiating neural render protocol for: '{image_prompt}'. Synthesizing image layers now, {Username}."
            query_type = "image_generation"
            trigger_image_gen(image_prompt)
            break

    # Check for exit
    if not answer and any(d == "exit" for d in decision):
        answer = f"Standing by. All subsystems entering idle power mode. Goodbye, {Username}."
        query_type = "exit"

    # Check for automation tasks
    automation_functions = ["open", "close", "play", "volume", "content", "google search", "youtube search"]
    has_automation = any(any(d.startswith(func) for func in automation_functions) for d in decision)
    target_url = None
    if has_automation and not answer:
        target_url = resolve_automation_url(decision)
        threading.Thread(target=execute_automation, args=(decision,), daemon=True).start()
        if target_url:
            answer = f"Opening {target_url}."
        else:
            answer = f"Executing requested automation sequence: {', '.join(decision)}."
        query_type = "automation"

    # Check for search vs general
    if not answer:
        has_general = any(d.startswith("general") for d in decision)
        has_realtime = any(d.startswith("realtime") for d in decision)

        if has_general and has_realtime:
            merged = " and ".join([" ".join(d.split()[1:]) for d in decision if d.startswith("general") or d.startswith("realtime")])
            answer = execute_search(merged)
            query_type = "realtime_hybrid"
        elif has_realtime:
            target = next((d.replace("realtime ", "") for d in decision if d.startswith("realtime")), query)
            answer = execute_search(target)
            query_type = "realtime"
        else:
            target = next((d.replace("general ", "") for d in decision if d.startswith("general")), query)
            answer = execute_chatbot(target)
            query_type = "general"

    # Trigger backend TTS if enabled
    audio_spoken = False
    if voice_enabled and answer:
        audio_spoken = execute_tts(answer)

    # Log to chat
    log_interaction(query, answer, decision)

    return jsonify({
        "success": True,
        "query": query,
        "answer": answer,
        "decision": decision,
        "type": query_type,
        "image_prompt": image_prompt,
        "target_url": target_url,
        "audio_spoken": audio_spoken,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

@app.route("/api/speak", methods=["POST"])
def speak_text():
    data = request.get_json() or {}
    text = data.get("text", "")
    if text:
        success = execute_tts(text)
        return jsonify({"success": success})
    return jsonify({"error": "Text is empty"}), 400

@app.route("/api/chatlog", methods=["GET"])
def get_chatlog():
    try:
        if os.path.exists(CHAT_LOG_FILE):
            with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
                return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify([])

@app.route("/api/clear_chatlog", methods=["POST"])
def clear_chatlog():
    try:
        with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return jsonify({"success": True, "message": "Chat log cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/images", methods=["GET"])
def list_images():
    try:
        image_files = []
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            image_files.extend(glob.glob(os.path.join(DATA_DIR, ext)))
        
        # Sort by modification time descending
        image_files.sort(key=os.path.getmtime, reverse=True)
        results = []
        for img_path in image_files[:12]:
            filename = os.path.basename(img_path)
            stat = os.stat(img_path)
            results.append({
                "filename": filename,
                "url": f"/data/images/{filename}",
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/data/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(DATA_DIR, filename)

if __name__ == "__main__":
    PORT = 5000
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print("\n" + "="*60)
    print(" [ONLINE] O.M.N.I.S NEURAL INTERFACE ONLINE")
    print(f" [WEB HUD] Access Web HUD at: http://localhost:{PORT}")
    print(f" [ENGINE]  Connected to O.M.N.I.S Engine ({Assistantname})")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=PORT, debug=False)
