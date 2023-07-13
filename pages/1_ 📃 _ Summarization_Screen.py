
import os, sys
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))


import openai
import streamlit as st
from streamlit_chat import message
import  streamlit_toggle as tog
from chat_utils import get_initial_message, get_chatgpt_response, update_chat, check_if_part_of_engineered_prompt, find_dictionary_from_gpt_response, find_dictionary_from_gpt_response_v2, dedup_transcript_message
from utils import get_english_transcript, vertical_spacer




# st.set_page_config(layout="wide")


def refetch_summary():
    st.session_state['SUMMARY_CREATED'] = False
    # st.session_state['SUMMARY_SCREEN_DISPLAYED_ONCE_FLAG'] = False

# st.title("Summarization with GPT")
st.markdown("<h1 style='text-align: center; font-weight: 300; font-family: 'Roboto', sans-serif;'>Summarise It!</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color: grey; text-align: center;'>🔫 Just the bullet points please.</h4>", unsafe_allow_html=True)


st.session_state['n_key_points'] = 5
st.session_state['n_complexity_of_point'] = 1

def get_complexity_prompt(val):
    _complexity_prompts = {
        1: ".Make the points is easy to understand with least amount of details.",
        2: ".Make the points with moderate complexity.",
        3: ".Make the points with as many detailed as required."
    }
    return _complexity_prompts[val]

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['n_key_points'] = st.slider('Number of points:', min_value=1, max_value=15, value=5, step=1, on_change=refetch_summary)
    with col2:
        st.session_state['n_complexity_of_point'] = st.slider('Complexity of point:', min_value=1, max_value=3, value=2, step=1, on_change=refetch_summary)

vertical_spacer(3)

if ('TRANSCRIPT' not in st.session_state) or (st.session_state['TRANSCRIPT'] == ''):
    st.warning("Plug in the video link on homepage to get started!", icon="🎬")
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = get_initial_message()

if 'SUMMARY_CREATED' not in st.session_state:
    st.session_state['SUMMARY_CREATED'] = False

if 'SUMMARY_SCREEN_DISPLAYED_ONCE_FLAG' not in st.session_state:
    st.session_state['SUMMARY_SCREEN_DISPLAYED_ONCE_FLAG'] = False


if 'TRANSCRIPT_SUBMITTED' not in st.session_state:
    st.session_state['TRANSCRIPT_SUBMITTED'] = False


if ('SUMMARY_CREATED' in st.session_state) and (st.session_state['SUMMARY_CREATED'] == False):
    if ('TRANSCRIPT' in st.session_state) and (st.session_state['TRANSCRIPT'] != None) and (len(st.session_state['TRANSCRIPT']) > 100):
        if st.session_state['TRANSCRIPT_SUBMITTED'] == False:
            transcript = st.session_state['TRANSCRIPT']
            passing_transcript_prompt = f'You are a helpful AI Tutor. Who anwers brief questions about the a following transcript. "TRANSCRIPT: {transcript}"'

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

       
        if ('TRANSCRIPT' in st.session_state) and (st.session_state['TRANSCRIPT'] != None) and (len(st.session_state['TRANSCRIPT']) > 100):
            transcript = st.session_state['TRANSCRIPT']
            n_key_points = st.session_state['n_key_points'] 
            n_complexity_of_point = st.session_state['n_complexity_of_point']
            summary_prompt = f'For given TRANSCRIPT, return a structured JSON list of the summary with {n_key_points} key points in this format: {{"points": [point, point, ...]}}' + get_complexity_prompt(n_complexity_of_point)

            with st.spinner("generating..."):
                messages = st.session_state['messages']
                _messages = dedup_transcript_message(messages)
                _messages = update_chat(_messages, "user", summary_prompt)
                response = get_chatgpt_response(_messages, st.session_state['model'])
                messages = update_chat(_messages, "assistant", response)
                st.session_state.past.append(summary_prompt)
                st.session_state.generated.append(response)
                st.session_state['SUMMARY'] = response
                st.session_state['SUMMARY_CREATED'] = True


if ('SUMMARY_CREATED' in st.session_state) and (st.session_state['SUMMARY_CREATED'] == True) and (True or (st.session_state['SUMMARY_SCREEN_DISPLAYED_ONCE_FLAG'] == False)):
    try:
        # _summary_dict_present, summary_dict = find_dictionary_from_gpt_response(st.session_state['SUMMARY'])
        summary_dict = find_dictionary_from_gpt_response_v2(st.session_state['SUMMARY'])

        for i in summary_dict['points']:
            _point = f"<h5>👉  {i}</h5>" 
            st.markdown(_point, unsafe_allow_html=True)
            # st.text("👉  " + i)
        # st.session_state['SUMMARY_SCREEN_DISPLAYED_ONCE_FLAG'] = True

    except Exception as e:
        print("ERRRRRRR")
        print(e)
        print(st.session_state['SUMMARY_CREATED'])
        print(st.session_state['SUMMARY'])
        print("========\n\n")


    # with st.expander("Show Messages"):
    #     st.write(messages)

    