import openai
import re
import ast


ENGINEERED_PROMPTS = [
    'Use this transcript to answer my questions that I will ask you ',
    'For given TRANSCRIPT, return a structured JSON list of the summary with',
    '"TRANSCRIPT:',
    'Create 5 mcq questions with 4 options based on the TRANSCRIPT',
    'Create 5 mcq questions with 4 options based on content of the last TRANSCRIPT alone',
    'Create 5 more new mcq questions with 4 options',
]


ENGINEERED_PROMPTS_SCREENWISE_DICT = { 
    'chat' : [],
    'summary' : [
        'For given TRANSCRIPT, return a structured JSON list of the summary with'
        ],
    'test': [
        'Create 5 mcq questions with 4 options based on the TRANSCRIPT',
        'Create 5 mcq questions with 4 options based on content of the last TRANSCRIPT alone',
        'Create 5 more new mcq questions with 4 options'
        ]
    }

def check_if_part_of_engineered_prompt(text):
    for i in ENGINEERED_PROMPTS:
        if i in text:
            return True
    else:
        return False

def dedup_transcript_message(messages, specific_screen=False, screen_name=''):
    if specific_screen == True:
        _prompts_to_remove = list(ENGINEERED_PROMPTS_SCREENWISE_DICT.keys())
        _prompts_to_remove.remove(screen_name)
        _prompts_to_remove = [j for i in _prompts_to_remove for j in ENGINEERED_PROMPTS_SCREENWISE_DICT[i]]
    processed_messages = []
    once_flag = True
    for i in range(len(messages)-2, -1, -2):
        msg = messages[i]
        if msg["role"] == "user":
            if specific_screen:
                for _p in _prompts_to_remove:
                    if _p in msg['content']:
                        continue
            if 'You are a helpful AI Tutor.' in msg['content']:
                processed_messages.append(msg) 
                processed_messages.append(messages[i+1])
                break
            if "TRANSCRIPT:" in msg['content']:
                if once_flag:
                    once_flag == True
                else:
                    continue
        processed_messages.append(msg) 
        processed_messages.append(messages[i+1]) 
    return processed_messages

def get_initial_message():
    messages=[
            # {"role": "system", "content": "You are a helpful AI Tutor. Who anwers brief questions about the a transcript that I will share with you shortly"},
            # {"role": "assistant", "content": "Sure, I will wait for the TRANSCRIPT"}
        ]
    return messages

def get_chatgpt_response(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
    return  response['choices'][0]['message']['content']

def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages

def find_dictionary_from_gpt_response(text, keys=["points", "mcqs"]):
    print(f"printing {text}")
    if re.search('({.+})', text) == None:
        print("None, dict obj")
        return False, {}
    x = ast.literal_eval(re.search('({.+})', text).group(0))
    print(f"printing x {x}")
    print(x.keys())
    for i in keys:
        if i in x.keys():
            return True, x
    print("Default Return")
    return False, {}

def find_dictionary_from_gpt_response_v2(text, keys=["points", "qs"]):
    try:
        print(f"printing {text}")
        _st_idx = text.index('{')
        try:
            _end_idx = text.rindex('}')
            if text.count('{') > text.count('}'):
                _end_idx = len(text)-1
        except:
            text = text + '}'
            _end_idx = text.rindex('}')

        return ast.literal_eval(text[_st_idx:_end_idx + 1])
    except Exception as e:
        print(e)
        print(text)
    
    # if re.search('({.+})', text) == None:
    #     print("None, dict obj")
    #     return False, {}
    # x = ast.literal_eval(re.search('({.+})', text).group(0))
    # print(f"printing x {x}")
    # print(x.keys())
    # for i in keys:
    #     if i in x.keys():
    #         return True, x
    # print("Default Return")
    # return False, {}



