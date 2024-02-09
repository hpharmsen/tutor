""" Settings object for the language tutor. Main purpose is to provide the system message for the AI. """
import configparser
import json
import random
from pathlib import Path

from justai import get_prompt

WORDS_PER_LEVEL = {'A1': 500, 'A2': 1000, 'B1': 2000, 'B2': 4000, 'C1': 8000, 'C2': 16000}


_settings = None
def get_settings():
    global _settings
    if _settings is None:
        config_object = configparser.ConfigParser()
        with open(Path(__file__).resolve().parent / "settings.ini", "r") as f:
            config_object.read_file(f)
        _settings = {t[0]: t[1] for t in config_object.items('general')}
        #language = _settings['target_language']
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
    past_tenses = get_prompt('PAST_TENSES') if s.get('past_tenses') == '1' else ''

    question1 = sentence_json(get_prompt('question1'))
    question2 = sentence_json(get_prompt('question2'))
    question3 = sentence_json(get_prompt('question3'))
    question4 = sentence_json(get_prompt('question4'))

    answer1 = get_prompt('answer1')
    answer2 = get_prompt('answer2')
    answer3 = get_prompt('answer3')
    answer4 = get_prompt('answer4')

    special_question = get_prompt('special_question')
    special_answer = other_json(get_prompt('special_answer'))

    analysis1 = analysis_json('wrong', get_prompt('analysis1'), get_prompt('right_answer1'))
    analysis2 = analysis_json('right', get_prompt('analysis2'))
    analysis3 = analysis_json('wrong', get_prompt('analysis3'), get_prompt('right_answer3'))
    analysis4 = analysis_json('wrong', get_prompt('analysis3'), get_prompt('right_answer4'))

    right_answer1 = get_prompt('right_answer1')
    right_answer2 = get_prompt('right_answer2')
    right_answer3 = get_prompt('right_answer3')
    right_answer4 = get_prompt('right_answer4')

    system_message = get_prompt('SYSTEM', target_language=s['target_language'],
                            native_language=s['native_language'], level=s['level'],
                            question1=question1, question2=question2, question3=question3, question4=question4,
                            answer1=answer1, answer2=answer2, answer3=answer3, answer4=answer4,
                            analysis1=analysis1, analysis2=analysis2, analysis3=analysis3, analysis4=analysis4,
                            right_answer1=right_answer1, right_answer2=right_answer2, right_answer3=right_answer3,
                            right_answer4=right_answer4, special_question=special_question,
                            special_answer=special_answer, past_tenses=past_tenses)
    return system_message


_words = []
def random_word():
    global _words
    if not _words:
        s = get_settings()
        # How many words we include in the list depends on the level of the user
        max_words = WORDS_PER_LEVEL[s['level']]
        with open(Path(__file__).resolve().parent / "words_nl.txt", 'r') as f:
            _words = f.read().splitlines()[:max_words]
    return random.choice(_words)
