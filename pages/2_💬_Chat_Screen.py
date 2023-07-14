
import os, sys
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))


import openai
import streamlit as st
from streamlit_chat import message
import  streamlit_toggle as tog
from chat_utils import get_initial_message, get_chatgpt_response, update_chat, check_if_part_of_engineered_prompt, find_dictionary_from_gpt_response, dedup_transcript_message
from utils import get_english_transcript, vertical_spacer



# st.title("Answer Me")
st.markdown("<h1 style='text-align: center; font-weight: 300; font-family: 'Roboto', sans-serif;'>I have a doubt!</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color: grey; text-align: center;'>🤔 Chat with GPT to clear your doubts</h4>", unsafe_allow_html=True)




if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'TRANSCRIPT_SUBMITTED' not in st.session_state:
    st.session_state['TRANSCRIPT_SUBMITTED'] = False

if 'messages' not in st.session_state:
    st.session_state['messages'] = get_initial_message()

if 'CHAT_SCREEN_ONCE_FLAG' not in st.session_state:
    st.session_state['CHAT_SCREEN_ONCE_FLAG'] = True

if st.session_state['CHAT_SCREEN_ONCE_FLAG'] == True:
    if ('TRANSCRIPT' in st.session_state) and (st.session_state['TRANSCRIPT'] != None) and (st.session_state['TRANSCRIPT_SUBMITTED'] == False):
        transcript = st.session_state['TRANSCRIPT']
        passing_transcript_prompt = f'You are a helpful AI Tutor. Who anwers questions about the following transcript. "TRANSCRIPT: {transcript}"'

        with st.spinner("Submitting Transcript..."):
            # print("GOING HERE")
            messages = st.session_state['messages']
            messages = update_chat(messages, "user", passing_transcript_prompt)
            response = get_chatgpt_response(messages, st.session_state['model'])
            messages = update_chat(messages, "assistant", response)
            st.session_state.past.append(passing_transcript_prompt)
            st.session_state.generated.append(response)
            st.session_state['CHAT_SCREEN_ONCE_FLAG'] = False
            st.session_state['TRANSCRIPT_SUBMITTED'] = True

def question_submit_click_func():
    st.session_state['query'] = st.session_state['input_text_key']
    st.session_state['input_text_key'] = ""

if ('TRANSCRIPT_SUBMITTED' in st.session_state) and (st.session_state['TRANSCRIPT_SUBMITTED'] == True):
    global_search_toggle_button = tog.st_toggle_switch(label="Global Search", 
        key="global_search_toggle", 
        default_value=False, 
        label_after = False, 
        inactive_color = '#D3D3D3', 
        active_color="#33cc33", 
        track_color="#66ff33"
    )
    with st.form("query_form"):
        _text_input_col, _sumbit_button_col = st.columns([4, 1])
        with _text_input_col:
            st.text_input(label="Ask Away!", key="input_text_key")
        with _sumbit_button_col:
            vertical_spacer(2)
            submit_click = st.form_submit_button("Submit", on_click=question_submit_click_func)

    if ('query' in st.session_state) and (st.session_state['query'] != ''):
        with st.spinner("Thinking..."):
            query = st.session_state['query']
            if query.strip() != "":
                if global_search_toggle_button == False:
                    # prompt_to_pass = query + ".Do not include sentences in the answer that say you are basing your information on the transcript.  Never provide information beyond the scope of the transcript.  Its very important that you never provide information beyond the scope of the transcript."
                    prompt_to_pass = query + ".Answer concisely. Never provide information beyond the scope of the transcript. Its very important that you never provide information beyond the scope of the transcript."
                    
                    # prompt_to_pass = f'Based on the information from the TRANSCRIPT that I gave you earlier, answer : {query}'
                    # prompt_to_pass = query

                else:
                    prompt_to_pass = query + '.Answer concisely. Answer based on your general knowledge.'
                    # prompt_to_pass = f'Based on the information that you know, answer : {query}'
                    # prompt_to_pass = query

                # print("hERE")
                messages = st.session_state['messages']
                _messages = dedup_transcript_message(messages, specific_screen=True, screen_name="chat")
                st.session_state['_messages'] = _messages
                messages = update_chat(messages, "user", prompt_to_pass)
                _messages = update_chat(_messages, "user", prompt_to_pass)
                response = get_chatgpt_response(_messages, st.session_state['model'])
                messages = update_chat(messages, "assistant", response)
                st.session_state.past.append(query)
                st.session_state.generated.append(response)
            st.session_state['query'] = ''
        #Clear query text input
        # st.session_state['input_query'] = ""

    if st.session_state['generated']:

        for i in range(len(st.session_state['generated'])-1, -1, -1):
            if check_if_part_of_engineered_prompt(st.session_state['past'][i]):
                continue
            # if find_dictionary_from_gpt_response(st.session_state["generated"][i]):
            #     continue
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))

        # with st.expander("Show Messages"):
        #     st.write(st.session_state['messages'])
        #     if '_messages' in st.session_state:
        #         st.write(st.session_state['_messages'])


else:
    if ('TRANSCRIPT' not in st.session_state) or (st.session_state['TRANSCRIPT'] == ''):
        vertical_spacer(3)
        st.warning("Plug in the video link on homepage to get started!", icon="🎬")