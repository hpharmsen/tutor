# GPT chat

Basic REPL to chat with the GPT models and a specific implemention that uses these models to help you learn a new language.

## Installation

1. Install dependencies:
```bash
python -m pip install -r requirements.in
```
2. Create an OpenAI acccount [here](chat.openai.com/auth/login)
3. Create OpenAI api keys [here](https://beta.openai.com/account/api-keys)
4. Create a .env file with the following content:
```bash
OPENAI_API_KEY=your-openai-api-key
OPENAI_ORGANIZATION=your-openai-organization-id
```

## Language tutor
```bash
python tutor.py
```
Generates sentences in English and lets you translate them. 
The program then checks if your translation is correct and gives you feedback.

## Other languages
The current implementation is for Spanish but you can easily set a new language in settings.ini.

Just make sure you include a section with the same name as the language and translate the [Spanish] section into that language.

## Special commands
You can also use these special commands which each start with a colon:

| Syntax                            | Description                                                         |
|-----------------------------------|---------------------------------------------------------------------|
| :reset                            | resets the conversation                                             |
| :load _name_                      | loads the saved conversation with the specified name                |
| :save _name_                      | saves the conversation under the specified name                     |
| :input _filename_                 | loads an input from the specified file                              |
| :model _gpt-4_                    | Sets the AI model                                                   |
| :max_tokens _800_                 | The maximum number of tokens to generate in the completion          |
| :temperature _0.9_                | What sampling temperature to use, between 0 and 2                   |
| :n _1_                            | Specifies the number answers given                                  |
| :stop _["\n", " Human:", " AI:"]_ | Up to 4 sequences where the API will stop generating further tokens |
| :bye                              | quits but saves the conversation first                              |
| :exit or :quit                    | quits the program                                                   |

