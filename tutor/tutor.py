""" The main program for the language tutor """
import json
import sys
from pathlib import Path

import justai
from justai import Agent, Repl, CommandHandler, get_prompt, set_prompt_file, add_prompt_file
from justai.tools.display import color_print, print_message, SYSTEM_COLOR

try:
    import tutor.settings as settings
except ImportError:
    import settings
# from synthesize import say

STATUS_NEXT_QUESTION = 1
STATUS_ANSWER = 2

OUTPUT_TEXT = 1
OUTPUT_HTML = 2


class Tutor(Agent):
    def __init__(self, model_name: str = 'gpt-4-turbo-preview'):
        super().__init__(model_name)
        set_prompt_file(Path(__file__).resolve().parent / "prompts.toml")
        self.system = settings.system_message()
        self.hard_concepts = []
        self.message_memory = 4
        self.last_question = ''
        self.last_answer = ''
        self.status = STATUS_NEXT_QUESTION
        self.output_format = OUTPUT_TEXT

    def autoprompt(self):
        if self.status != STATUS_NEXT_QUESTION:
            return
        # Auto advance to the next prompt
        s = settings.get_settings()
        if len(self.hard_concepts) > 2:
            hard_concept = self.hard_concepts.pop(0)
            p = get_prompt("REPEAT_HARD_CONCEPT", question=hard_concept['question'],
                           answer=hard_concept['answer'], analysis=hard_concept['analysis'],
                           target_language=s['target_language'])
        else:
            p = get_prompt("NEXT_SENTENCE")
        p += get_prompt("INCLUDE_WORD", word=settings.random_word(), native_language=s['native_language'],
                        target_language=s['target_language']
                        )
        return p

    def get_prompt(self):
        p = self.autoprompt()
        while not p:
            # Ask the user for a prompt
            p = input(f"{settings.get_settings()['target_language']}: ")

        # print('VVVVVVVVVV')
        # print(self.system())
        # print('----------' )
        # print(p)
        # print('^^^^^^^^^^')
        return p

    def chat(self, p):
        reply = super().chat(p)
        if type(reply) == str:
            if reply.count('{') and reply.count('}'):
                reply = json.loads('{' + reply.split('{',1)[1].rsplit('}',1)[0] + '}')
            else:
                reply = {'type': 'sentence', 'response': reply}

        match reply['type']:
            case 'sentence':
                self.status = STATUS_ANSWER
                self.last_question = reply['response']
            case 'other':
                self.status = STATUS_ANSWER
            case 'analysis':
                self.last_answer = p  # Save last answer given by the user in order to play audio if it is correct
                if reply['verdict'] == 'wrong':
                    hard_concept = {'question': self.last_question, 'answer': p, 'analysis': reply['response']}
                    self.hard_concepts.append(hard_concept)
                self.status = STATUS_NEXT_QUESTION
                self.messages = self.messages[-1:]  # Truncate message history. Old sentences only increase token count
        return reply

    def after_response(self):
        message = self.messages[-1]
        text = json.loads(message.content)['response']
        print_message(text, 'assistant')


def handle_level(level: str):
    level = level.upper()
    accepted_levels = settings.WORDS_PER_LEVEL.keys()
    if level not in accepted_levels:
        color_print(f"Error: level must be one of {', '.join(accepted_levels)}",
                                color=SYSTEM_COLOR)
    else:
        settings.get_settings()['level'] = level
        color_print(f'Level set to {level}', color=SYSTEM_COLOR)
    return True


if __name__ == "__main__":
    s = settings.get_settings()
    color_print(f"Hello, I am your {s['target_language']} tutor on {s['level']} level. " +
                            f"I will help you learn {s['target_language']}.\n" +
                            f"I will give you sentences in English " +
                            f"and you will have to translate them into {s['target_language']}.\n" +
                            f"Here's your first sentence:\n", color=SYSTEM_COLOR)
    agent = Tutor(s['model'])
    agent.debug = int(s['debug'])
    agent.language = s['target_language']
    keys = justai.tools.prompts._prompts.keys()
    extra_prompts = Path(__file__).resolve().parent / "prompts.toml"
    add_prompt_file(extra_prompts)
    keys = justai.tools.prompts._prompts.keys()

    # Load session if passed as a command line argument
    if len(sys.argv) > 1:
        agent.load(sys.argv[1])

    # Add a command handler that handles special commands like model parameters and system settings
    command_handler = CommandHandler(agent)
    command_handler.add_command('level', handle_level, ":level - Set the language level (A1..C2)")

    # Start the interactive prompt
    repl = Repl(agent, command_handler.handle_command)
    repl.get_prompt = agent.get_prompt  # partial(gpt.get_prompt, repl=repl)
    # repl.show_token_count = True  # Display how many tokens were used in each call
    repl.run()
