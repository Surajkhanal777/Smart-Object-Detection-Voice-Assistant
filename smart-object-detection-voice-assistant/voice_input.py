# Importing the speech_recognition library for capturing and recognizing speech
import speech_recognition as sr
# Importing pyttsx3 for text-to-speech conversion
import pyttsx3


def speak(text):
    """
    Initializing the speech engine and speaking the given text aloud.

    Args:
        text (str): Text to be spoken.
    """
    # Initializing the text-to-speech engine
    engine = pyttsx3.init()
    # Queuing the text to be spoken
    engine.say(text)
    # Running the speech engine and waiting for speaking to finish
    engine.runAndWait()


def listen():
    """
    Listening to audio input from the microphone and converting it to text.

    Returns:
        str: Recognized text in lowercase, or empty string if recognition fails.
    """
    # Creating a speech recognizer instance
    recognizer = sr.Recognizer()
    # Opening the microphone as the audio source
    with sr.Microphone() as source:
        # Printing a prompt indicating listening has started
        print("Listening for your response...")
        # Capturing audio from the microphone
        audio = recognizer.listen(source)

    try:
        # Recognizing speech using Google's online API
        text = recognizer.recognize_google(audio)
        # Printing the recognized text
        print(f"You said: {text}")
        # Returning the recognized text converted to lowercase
        return text.lower()
    except sr.UnknownValueError:
        # Handling case when speech is unintelligible
        print("Sorry, I could not understand your voice.")
        # Returning empty string on recognition failure
        return ""
    except sr.RequestError:
        # Handling case when Google API request fails
        print("Could not request results from Google Speech Recognition.")
        # Returning empty string on request failure
        return ""
