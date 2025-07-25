import time
import speech_recognition as sr
import pywhatkit
import random
import tkinter as tk
import asyncio
import edge_tts
import playsound
import os
import signal
import sys
import threading

overlay_root = None
blink_running = False

CUTE_REACTIONS = [
    "Wow~ this melody feels so beautiful and sweet~ sugoi yo~!",
    "Kyaa~ this song is sooo lovely~ daisuki da yo~!",
    "Mmm~ I can feel the cuteness overflowing~ kawaii ne~!",
    "Yatta~ this tune is making me so happy~ tanoshii yo~!",
    "Sugoi~ this music is like a dream~ utsukushii desu~!"
]

async def momoi_voice(text, filename="momoi_temp.mp3"):
    voice = "en-US-AnaNeural"
    tts = edge_tts.Communicate(text, voice)
    await tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

def speak(text):
    asyncio.run(momoi_voice(text))

def blink_loop():
    global overlay_root, blink_running
    if overlay_root is None:
        overlay_root = tk.Tk()
        overlay_root.attributes("-fullscreen", True)
        overlay_root.attributes("-topmost", True)
        overlay_root.overrideredirect(True)
        overlay_root.attributes("-alpha", 0.3)

        def esc_close(event=None):
            stop_rgb_blink()

        overlay_root.bind("<Escape>", esc_close)

    def change_color():
        if not blink_running:
            return
        color = "#%02x%02x%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        overlay_root.configure(bg=color)
        overlay_root.after(200, change_color)

    blink_running = True
    change_color()
    overlay_root.mainloop()

def start_rgb_blink():
    global blink_running
    if blink_running:
        return
    t = threading.Thread(target=blink_loop, daemon=True)
    t.start()

def stop_rgb_blink():
    global overlay_root, blink_running
    blink_running = False
    if overlay_root is not None:
        try:
            overlay_root.destroy()
        except:
            pass
        overlay_root = None

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening for command...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print("✅ Heard:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("❌ Didn't catch that...")
        return ""
    except sr.RequestError:
        print("⚠️ Speech recognition API unavailable")
        return ""

def handle_command(command):
    if command.startswith("play "):
        song = (
            command.replace("play", "")
            .replace("on youtube", "")
            .strip()
        )
        if song:
            intro = f"Yay~! I’m going to play {song} for you!"
            speak(intro)
            pywhatkit.playonyt(song)
            time.sleep(5)
            after_comment = random.choice(CUTE_REACTIONS)
            speak(after_comment)
            start_rgb_blink()
        else:
            speak("Hmm~ I couldn’t catch the song name, mou ichido onegai ne~!")
    else:
        print("💤 Waiting for a Play command...")

def signal_handler(sig, frame):
    print("\n🛑 Ctrl+C detected! Exiting program...")
    stop_rgb_blink()
    sys.exit(0)

def main():
    greet = (
        "Konnichiwa~! I’m Momoi, your cute assistant desu~! Just say Play and the song name, onegai ne~!"
    )
    speak(greet)

    print("🚀 Momoi Anime Voice Assistant Started!")
    print("Say: 'Play [song name] on YouTube'")
    print("After playing, fullscreen RGB will blink. Press ESC to close only RGB overlay. Press Ctrl+C to exit.")

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        command = listen_command()
        handle_command(command)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        stop_rgb_blink()
        os._exit(0)
