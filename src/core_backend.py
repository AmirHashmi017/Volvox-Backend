import speech_recognition as sr
import utils

def Activation_N_E():
    utils.speak("Nova, your personal assistant, is now active and ready to help you")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                command = recognizer.recognize_google(audio, language='en-US')
                command = command.strip()
                if "exit" in command.lower() or "stop" in command.lower():
                    utils.speak("Shutting down Nova Assistant.")
                    break
                if command:
                    utils.ProcessCommandd(command)
                else:
                    utils.speak("No command detected. Try speaking again")
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue