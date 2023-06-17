""" The main program for the language tutor """
import sys

import settings
from commands import CommandHandler
from display import SYSTEM_COLOR, color_print, DEBUG_COLOR2, DEBUG_COLOR1
from gpt import GPT
from repl import Repl
from settings import get_settings, random_word, WORDS_PER_LEVEL
from synthesize import say

STATUS_NEXT_QUESTION = 1
STATUS_ANSWER = 2


class Tutor(GPT):
    def __init__(self):
        super().__init__()
        self.system = settings.system_message
        self.hard_concepts = []
        self.message_memory = 4
        self.last_question = ''
        self.last_answer = ''
        self.status = STATUS_NEXT_QUESTION

    def get_prompt(self):
        if self.status == STATUS_NEXT_QUESTION:
            # Auto advance to the next prompt
            if len(self.hard_concepts) > 2:
                hard_concept = self.hard_concepts.pop(0)
                prompt = f"""You previously asked "{hard_concept['question']}" and I answered "{hard_concept['answer']}"
                Your analysis was: "{hard_concept['analysis']}"

                Generate a new sentence that includes one or more of the concepts I got wrong"""
            else:
                prompt = "Generate a new sentence"
            prompt += f"\ninclude the word {random_word()}"
            if get_settings()['debug'] == '1':
                color_print(prompt, color=DEBUG_COLOR2)
        else:
            # Ask the user for a prompt
            s = get_settings()
            prompt = ''
            while not prompt:
                prompt = input(f"{s['language']}: ")
        return prompt

    def chat(self, prompt, add_to_messages=True):
        # Modify prompt here...
        # Check if there's a concept that went wrong last time. If so, include it in the prompt.

        message = super().chat(prompt, add_to_messages=add_to_messages)

        s = get_settings()
        if get_settings()['debug'] == '1':
            color_print(message.text, color=DEBUG_COLOR1)

        reply = message.content()
        match reply['type']:
            case 'sentence':
                self.status = STATUS_ANSWER
                self.last_question = reply['response']
            case 'other':
                self.status = STATUS_ANSWER
            case 'analysis':
                self.last_answer = prompt  # Save last answer given by the user in order to play audio if it is correct
                if reply['verdict'] == 'wrong':
                    hard_concept = {'question': self.last_question, 'answer': prompt, 'analysis': reply['response']}
                    self.hard_concepts.append(hard_concept)
                self.status = STATUS_NEXT_QUESTION
        message.text = reply['response']
        return message

    def after_response(self, message):
        reply = message.content()
        if reply['type'] == 'analysis' and get_settings().get('play_audio') == '1':
            sentence = self.last_answer if reply['verdict'] == 'right' else reply['right_answer']
            say(sentence, language=get_settings()['language'])

def handle_level(level: str):
    level = level.upper()
    accepted_levels = WORDS_PER_LEVEL.keys()
    if level not in accepted_levels:
        color_print(f"Error: level must be one of {', '.join(accepted_levels)}", color=SYSTEM_COLOR)
    else:
        s = get_settings()
        s['level'] = level
        color_print(f'language level set to {level}', color=SYSTEM_COLOR)
    return True

def handle_debug(debug: str):
    s = get_settings()
    s['debug'] = debug
    color_print(f'debug set to {debug}', color=SYSTEM_COLOR)
    return True

if __name__ == "__main__":
    s = get_settings()
    color_print(f"Hello, I am your {s['language']} tutor on {s['level']} level. " +
                f"I will help you learn {s['language']}.\n" +
                f"I will give you sentences in English and you will have to translate them into {s['language']}.\n" +
                "Here's your first sentence:\n", color=SYSTEM_COLOR)
    gpt = Tutor()
    gpt.model = s['model']

    # Load session if passed as a command line argument
    if len(sys.argv) > 1:
        gpt.load(sys.argv[1])

    # Add a command handler that handles special commands like model parameters and system settings
    command_handler = CommandHandler(gpt)
    command_handler.add_command('level', handle_level, ":level - Set the language level (A1..C2)")
    command_handler.add_command('debug', handle_debug, ":debug - set to 1 displays all prompts and model replies")

    # Start the interactive prompt
    repl = Repl(gpt, command_handler.handle_command)
    repl.get_prompt = gpt.get_prompt  # partial(gpt.get_prompt, repl=repl)
    repl.run()
