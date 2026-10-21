import os
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import json
import sys

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocesses = []
Functions = ["open", "close", "play", "volume","content", "google search", "youtube search", "search on google", "search on youtube"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT_LOG_PATH = os.path.join(BASE_DIR, "Data", "ChatLog.json")


def ReadChatLogJson():
    with open(r'CHAT_LOG_PATH', 'r', encoding='utf-8') as file:
        chatlog_data = json. load(file)
        return chatlog_data


def MainExecution():

    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    print("listening...")
    Query = SpeechRecognition()
    print(Query)
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision : {Decision}")
    print("")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)


    Mearged_query = " and ".join(
        ["".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            TextToSpeech(f"ok sir please wait Image is generating")
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            run(Automation(Decision))
            TaskExecution = True

    if ImageExecution == True:
        with open(r"ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(
                ['python', r'Backend/ImageGeneration.py'], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=True
            )
            subprocesses.append(p1)
            p1.wait()  # Ensures the subprocess completes before continuing
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
            if p1.stderr:
                print("Full error output:", p1.stderr.read().decode())


    if G and R:
        Answer = RealtimeSearchEngine(Mearged_query)
        print(Answer)
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:

            if "general" in Queries:
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryFinal)
                TextToSpeech(Answer)
                print(Answer)
                return True

            elif "realtime" in Queries:
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryFinal)
                TextToSpeech(Answer)
                print(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryFinal)
                TextToSpeech(Answer)
                print(Answer)
                sys.exit(1)

if __name__ == "__main__":
    TextToSpeech("Hello everyone, how may I assist you today?")
    while True:
        MainExecution()