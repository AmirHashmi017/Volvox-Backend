import webbrowser
import speech_recognition as sr
import custom_buttons
import Nova_music
import ai_engine



import threading
import win32com.client as wincl


# Voice Engine Setup
speaker = wincl.Dispatch("SAPI.SpVoice")
speaker.Rate = 2

for voice in speaker.GetVoices():
    if "zira" in voice.GetDescription().lower():
        speaker.Voice = voice
        break

# Speak Function
def speak(text: str):
    def _speak():
        try:
            speaker.Speak(text)
        except Exception as e:
            print(f"TTS Error: {e}")

    threading.Thread(target=_speak, daemon=True).start()





recognizer = sr.Recognizer()


speak_lines: str
speak_lines2: str



# -------------------------------
#   Helper Filters
# -------------------------------
def filter_music(word):
    return word in speak_lines

def filter_tabs(word):
    return word in speak_lines2





# -------------------------------
#   Process Voice Commands
# -------------------------------
def ProcessCommandd(command: str):

    command = command.lower()


    # ----------- Tab Closing -----------1
    if "tab" in command:
        speak("Sure")
        global speak_lines2
        speak_lines2 = command
        tab_list = list(filter(filter_tabs, Nova_music.list_web))

        if tab_list:
            custom_buttons.name_web = tab_list[0]
            custom_buttons.cliking()

        return




    # ----------- Website Shortcuts -----------2
    websites = {
        "google": "https://www.google.com/",
        "whatsapp": "https://web.whatsapp.com/",
        "facebook": "https://www.facebook.com/",
        "instagram": "https://www.instagram.com/",
        "youtube": "https://www.youtube.com/",
        "fi": "https://www.fiverr.com/",
        "linkdin": "https://www.linkedin.com/",
        "twitter": "https://twitter.com/",
        "amazon": "https://www.amazon.com/",
        "gmail": "https://mail.google.com/",
        "w3school": "https://www.w3schools.com/"
    }

    for site, url in websites.items():
        if site in command:
            speak("Sure")
            webbrowser.open(url)
            return

    # ----------- Creator Info -----------3
    if any(word in command for word in ["developer", "creator", "owner", "maker","bnayaa"]):
        speak("Nova is created by Agha Essa Khan")
        return



    # ----------- Duplication Mode -----------4
    if "duplication" in command or "mimicry" in command:
        speak("Nova ab ap ki mimicry kare ga bolo bahi  . Say exit to terminate.")
        while True:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    talk = recognizer.recognize_google(audio, language='en-US').lower()

                    if "exit" in talk:
                        speak("Exiting duplication stage.")
                        break
                    speak(talk)
            except  :
                continue
        return

    # ----------- Music Mode -----------5
    if "music" in command:
        speak("Which music would you like to play?")
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                music_command = recognizer.recognize_google(audio, language='en-US').lower()

            global speak_lines
            speak_lines = music_command
            music_list = list(filter(filter_music, Nova_music.list_essa))

            if music_list:
                song = music_list[0]
                link = Nova_music.musk[song]
                speak(f"Enjoy {song}")
                webbrowser.open(link)
            else:
                speak("No music found.")
        except Exception:
            speak("I could not process the music command.")
        return

    # ----------- Mouse Control Mode -----------6
    if "mouse" in command:
        speak("Nova is in your mouse action control. Give me your command.")
        while True:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=5)
                    mouse_cmd = recognizer.recognize_google(audio, language='en-US').lower()

                    if "minimize" in mouse_cmd:
                        custom_buttons.min_fun()
                    elif "play" in mouse_cmd or "band" in mouse_cmd or "stop" in mouse_cmd or "pause" in mouse_cmd:
                        custom_buttons.pau_play_fun()
                    elif "mute" in mouse_cmd or "unmute" in mouse_cmd:
                        custom_buttons.mute_fun()
                    elif "exit full screen" in mouse_cmd or "exit the full screen" in mouse_cmd:
                        custom_buttons.exit_the_full_screen_fun()
                    elif "full screen" in mouse_cmd:
                        custom_buttons.fullscreen_fun()
                    elif "close" in mouse_cmd:
                        custom_buttons.desktop_fun()
                    elif "mouse" in mouse_cmd:
                        speak("Exiting mouse control.")
                        break
            except :
                continue
        return

    # ----------- AI Assistant Mode -----------7
    if "nova" in command:
        ai_response = ai_engine.Ai_answer(command)
        speak(ai_response)
        return

    speak("I didn't understand that command.")
