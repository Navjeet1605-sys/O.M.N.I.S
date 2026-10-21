
import pygame
import asyncio
import edge_tts
import os
import tempfile
import threading
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-AriaNeural")

tts_lock = threading.Lock()

# Initialize audio mixer once
if not pygame.mixer.get_init():
    pygame.mixer.init()


async def TextToAudioFile(text, file_path):
    communicate = edge_tts.Communicate(
        text,
        AssistantVoice,
        pitch="+5Hz",
        rate="+13%"
    )
    await communicate.save(file_path)


def TTS(Text, func=lambda: True):
    file_path = None

    with tts_lock:
        try:
            # Create a unique file
            fd, file_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

            # Generate speech
            asyncio.run(TextToAudioFile(str(Text), file_path))

            # Play speech
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            clock = pygame.time.Clock()

            while pygame.mixer.music.get_busy():
                if func() is False:
                    pygame.mixer.music.stop()
                    break
                clock.tick(30)

            return True

        except Exception as e:
            print(f"Error in TTS: {e}")
            return False

        finally:
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
            except Exception:
                pass

            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass


def TextToSpeech(Text, func=lambda: True):
    text = str(Text).strip()

    if not text:
        return False

    # Keep voice responses short for faster interaction
    sentences = text.split(".")

    if len(sentences) > 4 and len(text) > 250:
        text = ". ".join(sentences[:2])
        text += ". The rest is on your screen."

    return TTS(text, func)


if __name__ == "__main__":
    try:
        while True:
            user_input = input("Enter the text to speak: ")

            if user_input.lower() in ["exit", "quit", "stop"]:
                break

            TextToSpeech(user_input)
    finally:
        if pygame.mixer.get_init():
            pygame.mixer.quit()
