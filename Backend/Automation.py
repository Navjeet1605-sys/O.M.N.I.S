from AppOpener import close, open as appopen, give_appnames
from webbrowser import open as webopen  # Open web URLs
from pywhatkit import search, playonyt  # Google search & YouTube
from dotenv import dotenv_values  # Load environment variables
from bs4 import BeautifulSoup  # HTML parsing
from rich import print
from Backend.TextToSpeech import TextToSpeech
# from TextToSpeech import TextToSpeech
from groq import Groq  # AI chat
import webbrowser  # Open URLs
import subprocess  # System interactions
import requests  # HTTP requests
import keyboard  # Keyboard actions
import asyncio  # Async programming
import os  # OS functions

# Load environment variables from .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define CSS classes for parsing specific elements
classes = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "ZØLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

# User-agent for HTTP requests
useragent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' 
             '(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36')

# Initialize Groq AI client
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

# Chatbot messages storage
messages = []

# System message for chatbot
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {os.getenv('Username', 'User')}, You're a content writer. You create various content forms like letters, codes, applications, essays, notes, songs, and poems."
}]

# Function for Google Search
def GoogleSearch(Topic):
    search(Topic)
    TextToSpeech(f"Searching {Topic} on Google")
    return True

# Function to create content using AI and save to a file
def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(["notepad.exe", File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b", messages=SystemChatBot + messages,
            max_tokens=2048, temperature=0.7, top_p=1, stream=True, stop=None
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})
        TextToSpeech("have a look at the content I have created for you")
        return answer

    Topic = Topic.replace("Content ", "").strip()
    content_by_ai = ContentWriterAI(Topic)
    file_path = os.path.join("Data", f"{Topic.lower().replace(' ', '_')}.txt")
    os.makedirs("Data", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content_by_ai)
    OpenNotepad(file_path)
    return True

# Function to search on YouTube
def youtubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    TextToSpeech(f"Searching {Topic} on YouTube")
    return True

# Function to play a video on YouTube
def PlayYoutube(query):
    playonyt(query)
    TextToSpeech(f"playing {query} on YouTube")
    return True


# Function to open a Windows application or website
def OpenApp(app):
    try:
        app = app.lower().strip()
        if app in ["chrome", "google chrome", "browser"]:
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(
                    r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
                )
            ]

            for path in chrome_paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    TextToSpeech("Opening Chrome")
                    return True

            # Fallback if Chrome is installed in a custom location
            webbrowser.open_new_tab("https://www.google.com")
            TextToSpeech("Chrome executable not found. Opening your default browser")
            return True
        # Step 1: Check installed Windows applications
        available_apps = give_appnames()
        installed_apps = [name.lower() for name in available_apps]

        if app in installed_apps:
            appopen(app, match_closest=True)
            TextToSpeech(f"Opening {app}")
            return True

        # Step 2: If app is not found, open its website
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
            "x": "https://x.com"
        }

        if app in websites:
            webbrowser.open_new_tab(websites[app])
            TextToSpeech(f"Opening {app}")
            return True

        # Step 3: If no matching website exists, Google search
        search_url = (
            "https://www.google.com/search?q="
            + requests.utils.quote(app)
        )
        webbrowser.open_new_tab(search_url)
        TextToSpeech(f"Opening {app}")
        return True

    except Exception as e:
        print(f"Error opening {app}: {e}")
        return False

def CloseApp(app):
    if "chrome" in app.lower():
        return True

    try:
        close(app, match_closest=True)
        TextToSpeech(f"Closing {app}")
        return True
    except Exception:
        return False
# Function to execute system commands
def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "up": lambda: keyboard.press_and_release("volume up"),
        "down": lambda: keyboard.press_and_release("volume down"),
        "shutdown": lambda: os.system("shutdown /s /t 0"),
        "sleep": lambda: os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0"),
        "restart": lambda: os.system("shutdown /r /t 0"),
        "cancel shutdown": lambda: os.system("shutdown /a"),
    }
    if command in actions:
        actions[command]()
        return True
    return False

# Asynchronous function to translate and execute user commands
async def TranslateAndExecute(commands):
    tasks = []
    for command in commands:
        cmd = command.lower().strip()
        if cmd.startswith("open "):
            tasks.append(asyncio.to_thread(OpenApp, cmd[5:]))
        elif cmd.startswith("close "):
            tasks.append(asyncio.to_thread(CloseApp, cmd[6:]))
        elif cmd.startswith("play "):
            tasks.append(asyncio.to_thread(PlayYoutube, cmd[5:]))
        elif cmd.startswith("content "):
            tasks.append(asyncio.to_thread(Content, cmd[8:]))
        elif cmd.startswith("google search "):
            tasks.append(asyncio.to_thread(GoogleSearch, cmd[14:]))
        elif cmd.startswith("search on google "):
            tasks.append(asyncio.to_thread(GoogleSearch, cmd[14:]))
        elif cmd.startswith("youtube search "):
            tasks.append(asyncio.to_thread(youtubeSearch, cmd[15:]))
        elif cmd.startswith("search on youtube "):
            tasks.append(asyncio.to_thread(youtubeSearch, cmd[18:]))
        elif cmd.startswith("volume "):
            tasks.append(asyncio.to_thread(System, cmd[7:]))
        elif cmd.startswith("go to "):
            tasks.append(asyncio.to_thread(System, cmd[6:]))
        elif cmd.startswith("system "):
            tasks.append(asyncio.to_thread(System, cmd[7:]))
        else:
            print(f"No function found for: {command}")
    results = await asyncio.gather(*tasks)
    return results

# Main automation function
async def Automation(commands):
    await TranslateAndExecute(commands)
    return True

if __name__ == "__main__":
    test_commands = [
        "search on youtube python programming",
    ]
    asyncio.run(Automation(test_commands))