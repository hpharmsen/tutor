""" The main program for the language tutor """
import sys

from gpteasy import GPT, Repl, CommandHandler
import gpteasy.display as gpt_display
try:
    import tutor.settings as settings
except:
    import settings
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
            prompt += f"\ninclude the word {settings.random_word()}"
        else:
            # Ask the user for a prompt
            prompt = ''
            while not prompt:
                prompt = input(f"{settings.get_settings()['language']}: ")
        return prompt

    def chat(self, prompt, add_to_messages=True):
        # Modify prompt here...
        # Check if there's a concept that went wrong last time. If so, include it in the prompt.

        message = super().chat(prompt, add_to_messages=add_to_messages)

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
                self.messages = [] # Clear the message history. Old sentences only increase token count
        message.text = reply['response']
        return message

    def after_response(self, message):
        reply = message.content()
        if reply['type'] == 'analysis' and settings.get_settings().get('play_audio') == '1':
            sentence = self.last_answer if reply['verdict'] == 'right' else reply['right_answer']
            # say(sentence, language=settings.get_settings()['language'])


def handle_level(level: str):
    level = level.upper()
    accepted_levels = settings.WORDS_PER_LEVEL.keys()
    if level not in accepted_levels:
        gpt_display.color_print(f"Error: level must be one of {', '.join(accepted_levels)}",
                                color=gpt_display.SYSTEM_COLOR)
    else:
        settings.get_settings()['level'] = level
        gpt_display.color_print(f'language level set to {level}', color=gpt_display.SYSTEM_COLOR)
    return True


if __name__ == "__main__":
    s = settings.get_settings()
    gpt_display.color_print(f"Hello, I am your {s['language']} tutor on {s['level']} level. " +
                            f"I will help you learn {s['language']}.\n" +
                            f"I will give you sentences in English " +
                            f"and you will have to translate them into {s['language']}.\n" +
                            f"Here's your first sentence:\n", color=gpt_display.SYSTEM_COLOR)
    gpt = Tutor()
    gpt.model = s['model']
    gpt.debug = True

    # Load session if passed as a command line argument
    if len(sys.argv) > 1:
        gpt.load(sys.argv[1])

    # Add a command handler that handles special commands like model parameters and system settings
    command_handler = CommandHandler(gpt)
    command_handler.add_command('level', handle_level, ":level - Set the language level (A1..C2)")


    # Start the interactive prompt
    repl = Repl(gpt, command_handler.handle_command)
    repl.get_prompt = gpt.get_prompt  # partial(gpt.get_prompt, repl=repl)
    repl.run()
