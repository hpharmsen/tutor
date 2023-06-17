import os

import gtts
from playsound import playsound

LANGUAGE_CODES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Swedish": "sv",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Hebrew": "he",
    "Turkish": "tr",
    "Danish": "da",
    "Polish": "pl",
    "Greek": "el",
    "Romanian": "ro",
    "Ukrainian": "uk",
    "Czech": "cs",
    "Finnish": "fi",
    "Hungarian": "hu",
    "Norwegian": "no",
    "Bulgarian": "bg",
    "Croatian": "hr",
    "Serbian": "sr",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Estonian": "et",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Thai": "th",
    "Indonesian": "id",
    "Hindi": "hi",
    "Bengali": "bn",
    "Filipino": "tl",
    "Persian": "fa",
    "Urdu": "ur",
    "Vietnamese": "vi",
}

def say(text, language="English"):
    language_code = LANGUAGE_CODES[language]
    filename = "_tmp_sound.mp3"
    tts = gtts.gTTS(text, lang=language_code)
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

if __name__ == "__main__":
    say("Hola, ¿cómo estás?", "Spanish")