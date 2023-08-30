""" Settings object for the language tutor. Main purpose is to provide the system message for the AI. """
import configparser
import json
import random
from pathlib import Path

from gpteasy import prompt, set_prompt_file

WORDS_PER_LEVEL = {'A1': 500, 'A2': 1000, 'B1': 2000, 'B2': 4000, 'C1': 8000, 'C2': 16000}
set_prompt_file(Path(__file__).resolve().parent / "prompts.toml")

_settings = None
def get_settings():
    global _settings
    if _settings is None:
        config_object = configparser.ConfigParser()
        with open(Path(__file__).resolve().parent / "settings.ini", "r") as f:
            config_object.read_file(f)
        _settings = {t[0]: t[1] for t in config_object.items('general')}
        #language = _settings['language']
        #_settings.update({t[0]: t[1] for t in config_object.items('examples')})
    return _settings


def system_message():
    def analysis_json(verdict, analysis, right_anwer=""):
        data = {"type": "analysis", "verdict": verdict, "response": analysis}
        if right_anwer:
            data['right_answer'] = right_anwer
        return json.dumps(data, ensure_ascii=False)

    def other_json(text):
        return json.dumps({"type": "other", "response": text}, ensure_ascii=False)

    def sentence_json(text):
        return json.dumps({"type": "sentence", "response": text}, ensure_ascii=False)

    s = get_settings()
    text_about_diacriticals = prompt('TEXT_ABOUT_DIACRITICALS') if s.get('ignore_diacriticals') == '1' else ''
    past_tenses = prompt('PAST_TENSES') if s.get('past_tenses') == '1' else ''

    question1 = sentence_json(prompt('question1'))
    question2 = sentence_json(prompt('question2'))
    question3 = sentence_json(prompt('question3'))
    question4 = sentence_json(prompt('question4'))

    answer1 = prompt('answer1')
    answer2 = prompt('answer2')
    answer3 = prompt('answer3')
    answer4 = prompt('answer4')

    special_question = prompt('special_question')
    special_answer = other_json(prompt('special_answer'))

    analysis1 = analysis_json('wrong', prompt('analysis1'), prompt('right_answer1'))
    analysis2 = analysis_json('right', prompt('analysis2'))
    analysis3 = analysis_json('wrong', prompt('analysis3'), prompt('right_answer3'))
    analysis4 = analysis_json('wrong', prompt('analysis3'), prompt('right_answer4'))

    right_answer1 = prompt('right_answer1')
    right_answer2 = prompt('right_answer2')
    right_answer3 = prompt('right_answer3')
    right_answer4 = prompt('right_answer4')

    system_message = prompt('SYSTEM', language=s['language'], level=s['level'],
                            question1=question1, question2=question2, question3=question3, question4=question4,
                            answer1=answer1, answer2=answer2, answer3=answer3, answer4=answer4,
                            analysis1=analysis1, analysis2=analysis2, analysis3=analysis3, analysis4=analysis4,
                            right_answer1=right_answer1, right_answer2=right_answer2, right_answer3=right_answer3,
                            right_answer4=right_answer4, special_question=special_question,
                            special_answer=special_answer, text_about_diacriticals=text_about_diacriticals,
                            past_tenses=past_tenses)
    return system_message


_words = []
def random_word():
    global _words
    if not _words:
        s = get_settings()
        # How many words we include in the list depends on the level of the user
        max_words = WORDS_PER_LEVEL[s['level']]
        with open(Path(__file__).resolve().parent / "words.txt", 'r') as f:
            _words = f.read().splitlines()[:max_words]
    return random.choice(_words)
