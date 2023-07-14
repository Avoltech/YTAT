
import os, sys
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))


import streamlit as st
from st_click_detector import click_detector
from text_utils import sample_questions
from utils import vertical_spacer
from utils import get_english_transcript
from chat_utils import get_initial_message, get_chatgpt_response, update_chat, check_if_part_of_engineered_prompt, find_dictionary_from_gpt_response_v2
import openai




def reinject_transcript():
    st.session_state['MCQ_TRANSCRIPT_PASSED'] = False



if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = get_initial_message()

if 'MCQ_TRANSCRIPT_PASSED' not in st.session_state:
    st.session_state['MCQ_TRANSCRIPT_PASSED'] = False

if 'current_question_idx' not in st.session_state:
    st.session_state['current_question_idx'] = -1

if 'all_questions' not in st.session_state:
    st.session_state['all_questions'] = []

if 'total_score' not in st.session_state:
    st.session_state['total_score'] = 0

if 'init_fetch_button_allow' not in st.session_state:
    st.session_state['init_fetch_button_allow'] = True

def fetch_questions():
    _current_question_count = len(st.session_state['all_questions'])

    if _current_question_count == 0:
        if (st.session_state['TRANSCRIPT_SUBMITTED'] == False):
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

        mcq_prompt = f'Create 5 mcq questions with 4 options based on content of the last TRANSCRIPT alone, send the question in a structured json format as follows: {{"qs":["q": question 1 here, "o":[option1, option2, option3, option4], "c": correct option index, "q": question 2 here...... and so on]}}. End your output with the word "COMPLETE!"'

        with st.spinner("Generating questions..."):
            messages = st.session_state['messages']
            messages = update_chat(messages, "user", mcq_prompt)
            response = get_chatgpt_response(messages, st.session_state['model'])
            messages = update_chat(messages, "assistant", response)
            st.session_state.past.append(mcq_prompt)
            st.session_state.generated.append(response)
            _dict_response = find_dictionary_from_gpt_response_v2(response)
            # print(_dict_response)
            st.session_state['all_questions'] += _dict_response['qs']

    else:
        transcript = st.session_state['TRANSCRIPT']
        mcq_prompt = f'Create 5 more new mcq questions that you did not generate previously with 4 options based on content of the last TRANSCRIPT alone, send the question in a structured json format as follows: {{"qs":["q": question 1 here, "o":[option1, option2, option3, option4], "c": correct option index, "q": question 2 here...... and so on]}}. End your output with the word "COMPLETE!"'

        with st.spinner("Generating more questions..."):
            messages = st.session_state['messages']
            messages = update_chat(messages, "user", mcq_prompt)
            response = get_chatgpt_response(messages, st.session_state['model'])
            messages = update_chat(messages, "assistant", response)
            st.session_state.past.append(mcq_prompt)
            st.session_state.generated.append(response)
            _dict_response = find_dictionary_from_gpt_response_v2(response)
            # print(_dict_response)

            st.session_state['all_questions'] += _dict_response['qs']



    # _new_fetched_question = sample_questions['qs'][_current_question_count:_current_question_count+5]
    # st.session_state['all_questions'] += _new_fetched_question
    # if (len(st.session_state['all_questions']) > 0) and (st.session_state['current_question_idx'] == -1):
        # st.session_state['current_question_idx'] = 0

def init_fetch_button_click_func():
    if 'TRANSCRIPT' in st.session_state:
        if st.session_state['TRANSCRIPT'] == '':
            st.error("Plug the youtube video on the homepage to get started!")
        else:
            st.session_state['init_fetch_button_allow'] = False
            fetch_questions()
            st.session_state['current_question_idx'] += 1
    else:
        st.error("Plug the youtube video on the homepage to get started!")


def fetch_next_question():
    if ((st.session_state['current_question_idx']+1) >= len(st.session_state['all_questions'])):
        fetch_questions()
    st.session_state['current_question_idx'] += 1
    reset_for_next_question()
    
# st.write(st.session_state['all_questions'])
st.markdown("<h1 style='text-align: center; font-weight: 300; font-family: 'Roboto', sans-serif;'>Test Me!</h1>", unsafe_allow_html=True)

def reset_for_next_question():
    st.session_state['current_mcq_option_status_ls'] = ['allow', 'allow', 'allow', 'allow']
    st.session_state['user_selected_option_idx'] = -1
    st.session_state['question_answered_flag'] = False
    pass

def show_mcq_option_true_values(correct_answer_idx):
    _current_mcq_option_status_ls = ['wrong'] * 4  
    _current_mcq_option_status_ls[correct_answer_idx] = 'correct'
    st.session_state['current_mcq_option_status_ls'] = _current_mcq_option_status_ls
    st.session_state['question_answered_flag'] = True


def option_clicked_func(idx, correct_answer_idx):
    st.session_state['user_selected_option_idx'] = idx
    show_mcq_option_true_values(correct_answer_idx)


if st.session_state['current_question_idx'] == -1:
    vertical_spacer(1)
    st.markdown("<h4 style='color: grey; text-align: center;'>📚 Ready to test your knowledge on this video?</h4>", unsafe_allow_html=True)

    # st.markdown("<h2 style='text-align: center; color: black;'>📚 Ready to test your knowledge on this video?</h2>", unsafe_allow_html=True)
    vertical_spacer(3)
    if ('TRANSCRIPT' not in st.session_state) or (st.session_state['TRANSCRIPT'] == ''):
        st.warning("Plug in the video link on homepage to get started!", icon="🎬")
    else:
        vertical_spacer(2)
        with st.columns(5)[2]:
            if st.session_state['init_fetch_button_allow'] == True:
                st.button("I am ready!", on_click=init_fetch_button_click_func)
            else:
                with st.spinner("Generating Questions"):
                    st.write("")
else:
    if 'current_mcq_option_status_ls' not in st.session_state:
        #allow, correct, wrong
        st.session_state['current_mcq_option_status_ls'] = ['allow', 'allow', 'allow', 'allow']

    if 'user_selected_option_idx' not in st.session_state:
        st.session_state['user_selected_option_idx'] = -1

    if 'question_answered_flag' not in st.session_state:
        st.session_state['question_answered_flag'] = False

    mcq_question = st.session_state['all_questions'][st.session_state['current_question_idx']]['q']
    mcq_option_ls = st.session_state['all_questions'][st.session_state['current_question_idx']]['o']
    mcq_correct_answer_idx = st.session_state['all_questions'][st.session_state['current_question_idx']]['c']
    
    with st.columns(3)[2]:
        st.subheader(f"Score : {st.session_state['total_score']}/{len(st.session_state['all_questions'])}")

    st.subheader(st.session_state['all_questions'][st.session_state['current_question_idx']]['q'])
        
    for i, option in enumerate(mcq_option_ls):
        _button_status = st.session_state['current_mcq_option_status_ls'][i]

        if _button_status == 'allow':
            st.button(option, on_click=option_clicked_func, args=(i,mcq_correct_answer_idx))
        elif _button_status == 'wrong':
            if st.session_state['user_selected_option_idx'] == i:
                _icon = '❌'
                st.error(option, icon=_icon)
            else:
                st.error(option)
        elif _button_status == 'correct':
            if st.session_state['user_selected_option_idx'] == i:
                _icon = '✅'
                st.session_state['total_score'] += 1
                st.success(option, icon=_icon)
            else:
                st.success(option)

    
    with st.columns(5)[4]:
        if ((st.session_state['current_question_idx']+1) >= len(st.session_state['all_questions'])):
            _next_btn_text = "Generate More"
        else:
            _next_btn_text = "Next"

        st.button(_next_btn_text, on_click=fetch_next_question)
     
    # with st.expander("Show Messages"):
    #     messages = st.session_state['messages']
    #     st.write(messages)