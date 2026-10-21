from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
import http.server
import socketserver
import threading

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;
        let shouldRestart = true;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            
            // FIX 1: Language switched from 'hi-IN' to Pure English 'en-US'
            recognition.lang = 'en-US'; 
            recognition.continuous = true;
            recognition.interimResults = false;
            shouldRestart = true;

            recognition.onresult = function(event) {
                if (event.results && event.results.length > 0) {
                    const lastResultIndex = event.results.length - 1;
                    if (event.results[lastResultIndex] && event.results[lastResultIndex][0]) {
                        const transcript = event.results[lastResultIndex][0].transcript;
                        if (transcript) {
                            output.textContent += transcript + " ";
                        }
                    }
                }
            };

            recognition.onend = function() {
                if (shouldRestart) {
                    try { recognition.start(); } catch(e) { console.log(e); }
                }
            };
            recognition.start();
        }

        function stopRecognition() {
            shouldRestart = false;
            if (recognition) {
                recognition.stop();
            }
        }
    </script>
</body>
</html>'''

# Save the HTML file inside the local data folder
os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# START BACKGROUND LOCAL HTTP SERVER FOR SECURE MIC ACCESS
PORT = 8000
class SafeHTTPServer(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass 

def run_server():
    os.chdir("Data")
    with socketserver.TCPServer(("", PORT), SafeHTTPServer) as httpd:
        httpd.serve_forever()

# Daemon thread me server start karo
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(1)

Link = f"http://localhost:{PORT}/Voice.html"

# Configure Selenium WebDriver with headless settings
chrome_options = Options()
chrome_options.add_argument("--headless=new") 
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_mic": 1, 
})

# Initialize driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open connection once
driver.get(Link)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    new_query = " ".join(new_query.split())
    
    # Gold/Silver keywords matching rule
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words) or new_query.startswith(tuple(question_words)):
        new_query = new_query.rstrip(".?!") + "?"
    else:
        new_query = new_query.rstrip(".?!") + ""

    return new_query.capitalize()

# Function to perform speech recognition (NO TRANSLATOR NEEDED)
def SpeechRecognition():
    """Captures direct English speech input from the background browser."""
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "start"))).click()
        print("\nListening....")
        time.sleep(0.5)  

        while True:
            try:
                Text = driver.find_element(By.ID, "output").text.strip()

                if Text:
                    time.sleep(0.8) # Phrase hold delay
                    Final_Text = driver.find_element(By.ID, "output").text.strip()
                    
                    driver.find_element(By.ID, "end").click()
                    driver.execute_script("document.getElementById('output').textContent = '';")
                    
                    # Direct passing to logic wrapper
                    return QueryModifier(Final_Text)
                        
            except Exception:
                pass
            time.sleep(0.1)
            
    except Exception as e:
        print("Error in Speech Interface Loop:", e)
        return ""

# Run the Speech Recognition Loop
if __name__ == "__main__":
    try:
        while True:
            user_input = SpeechRecognition()
            if user_input:
                print(f"query: {user_input}")
    except KeyboardInterrupt:
        print("\nbye bye")
        driver.quit()
