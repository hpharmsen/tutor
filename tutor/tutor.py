""" The main program for the language tutor """
import json
import sys
from dataclasses import dataclass

from dataclasses_jsonschema import JsonSchemaMixin
from gpteasy import GPT, Repl, CommandHandler, prompt
import gpteasy.display as gpt_display

import settings


@dataclass
class Answer(JsonSchemaMixin):
    type: str
    verdict: bool
    response: str


# from synthesize import say

STATUS_NEXT_QUESTION = 1
STATUS_ANSWER = 2

OUTPUT_TEXT = 1
OUTPUT_HTML = 2


class Tutor(GPT):
    def __init__(self):
        super().__init__()
        self.system = settings.system_message
        self.hard_concepts = []
        self.message_memory = 4
        self.last_question = ''
        self.last_answer = ''
        self.status = STATUS_NEXT_QUESTION
        self.output_format = OUTPUT_TEXT
        self.set_return_type(Answer)

    def autoprompt(self):
        if self.status != STATUS_NEXT_QUESTION:
            return
        # Auto advance to the next prompt
        if len(self.hard_concepts) > 2:
            hard_concept = self.hard_concepts.pop(0)
            prmpt = prompt("REPEAT_HARD_CONCEPT", question=hard_concept['question'], answer=hard_concept['answer'],
                           analysis=hard_concept['analysis'], language=s['language'])
        else:
            prmpt = prompt("NEXT_SENTENCE", language=s['language'], level=s['level'])
        if settings.get_settings().get('past_tenses') == '1':
            prmpt += "\n" + prompt("PAST_TENSES")
        prmpt += "\n" + prompt("USE_WORD", word=settings.random_word())
        return prmpt

    def get_prompt(self):
        prompt = self.autoprompt()
        while not prompt:
            # Ask the user for a prompt
            prompt = input(f"{settings.get_settings()['language']}: ")
        return prompt

    def chat(self, prompt, add_to_messages=True):
        # Modify prompt here...
        # Check if there's a concept that went wrong last time. If so, include it in the prompt.

        reply = super().chat(prompt, add_to_messages=add_to_messages)

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
                self.messages = self.messages[-1:]  # Truncate message history. Old sentences only increase token count
        return reply

    def after_response(self):
        message = self.messages[-1]
        text = json.loads(message.text)['response']
        gpt_display.print_message(text, 'assistant')


def handle_level(level: str):
    level = level.upper()
    accepted_levels = settings.WORDS_PER_LEVEL.keys()
    if level not in accepted_levels:
        gpt_display.print_message(f"Error: level must be one of {', '.join(accepted_levels)}", 'system')
    else:
        settings.get_settings()['level'] = level
        gpt_display.print_message(f'language level set to {level}', 'system')
    return True


if __name__ == "__main__":
    s = settings.get_settings()
    gpt = Tutor()
    gpt.model = s['model']
    gpt.debug = int(s['debug'])
    gpt.language = s['language']

    # Load session if passed as a command line argument
    if len(sys.argv) > 1:
        gpt.load(sys.argv[1])

    # Add a command handler that handles special commands like model parameters and system settings
    command_handler = CommandHandler(gpt)
    command_handler.add_command('level', handle_level, ":level - Set the language level (A1..C2)")

    intro = prompt('INTRO', language=s['language'], level=s['level'])
    gpt_display.print_message(intro, 'system')

    # Start the interactive prompt
    repl = Repl(gpt, command_handler.handle_command)
    repl.get_prompt = gpt.get_prompt  # partial(gpt.get_prompt, repl=repl)
    # repl.show_token_count = True  # Display how many tokens were used in each call
    repl.run()
