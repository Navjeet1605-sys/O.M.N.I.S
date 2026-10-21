import os

from ddgs import DDGS # 1. Pehle duckduckgo library ko import karo (pip install ddgs)
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT_LOG_PATH = os.path.join(BASE_DIR, "Data", "ChatLog.json")


# Initialize the Groq client with the provided API key.
client = Groq(api_key=GroqAPIKey)

# System Prompt me thoda aur clear instruction de diya hai
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional, very short and direct way. ***
*** Avoid extra conversational filler or website links. Just give the exact factual answer or price from the provided data. ***"""

try:
    with open(r"CHAT_LOG_PATH", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"CHAT_LOG_PATH", "w") as f:
        dump([], f)
# 2. Free, Fast aur Stable Search Engine Function using ddgs
# Updated GoogleSearch Function with Smart Query Injection
def GoogleSearch(query):
    # Agar query me gold, bitcoin ya price jaise words hain, toh query ko optimize karo
    optimized_query = query
    lower_query = query.lower()
    
    if "gold" in lower_query or "price" in lower_query or "rate" in lower_query:
        if "today" not in lower_query:
            optimized_query += " live price today in INR"
            
    Answer = f"The search results for '{optimized_query}' are:\n[start]\n"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(optimized_query, max_results=5)
            if results:
                for item in results:
                    Answer += f"Title: {item['title']}\nDescription: {item['body']}\n\n"
            else:
                Answer += "No results found on the internet.\n"
    except Exception as e:
        Answer += f"Search Error: {e}\n"
        
    Answer += "[end]"
    return Answer


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds. \n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load the chat log from the JSON file.
    with open(r"CHAT_LOG_PATH", "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": f"{prompt}"})

    SystemChatBot.append({"role": "user", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )
    Answer = ""

    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(r"CHAT_LOG_PATH", "w") as f:
        dump(messages, f, indent=4)
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
