""" Settings object for the language tutor. Main purpose is to provide the system message for the AI. """
import os
import configparser
import random
from pathlib import Path

from gpteasy import prompt, set_prompt_file

WORDS_PER_LEVEL = {'A1': 500, 'A2': 1000, 'B1': 2000, 'B2': 4000, 'C1': 8000, 'C2': 16000}
set_prompt_file(os.path.join(os.path.dirname(__file__), 'prompts.toml'))

_settings = None
def get_settings():
    global _settings
    if _settings is None:
        config_object = configparser.ConfigParser()
        with open(Path(__file__).resolve().parent / "settings.ini", "r") as f:
            config_object.read_file(f)
        _settings = {t[0]: t[1] for t in config_object.items('general')}
    return _settings


def system_message():
    s = get_settings()
    return prompt('SYSTEM', language=s['language'], level=s['level'])


_words = []
def random_word(language="nl"):
    global _words
    if not _words:
        s = get_settings()
        # How many words we include in the list depends on the level of the user
        max_words = WORDS_PER_LEVEL[s['level']]
        with open(Path(__file__).resolve().parent / f"words_{language}.txt", 'r') as f:
            _words = f.read().splitlines()[:max_words]
    return random.choice(_words)
