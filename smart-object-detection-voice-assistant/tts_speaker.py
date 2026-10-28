# Importing the pyttsx3 text-to-speech library
import pyttsx3

# Initializing the speech engine
engine = pyttsx3.init()

def speak(text):
    """
    Speaking the given text aloud using pyttsx3 engine.

    Args:
        text (str): Text string to be spoken.
    """
    # Queuing the text for speech synthesis
    engine.say(text)
    # Running the speech engine and waiting for speech to finish
    engine.runAndWait()
