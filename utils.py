from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
from chat_utils import get_initial_message

def get_english_transcript(video_id, transcript_type='any'):
    """
    Returns the english transcript for a youtube vide
    input params: 
        video_id: id of the video
        transcript_typ: (either 'manual', 'auto' or 'any') type of transcipt to look for
                        manual: transcript that the video author has inserted into the video
                        auto: transcript generated automatically by youtube
                        any: any one of the above that is available with 'manual' being the priority
    
    return params:
        transcript object
    """
    try:
        if 'youtube.com/watch?v=' in video_id:
            video_id = video_id.split('?v=')[-1]

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        manually_created_transcript_available = False
        automatically_created_transcript_available = False
        
        try:
            _t =  transcript_list.find_manually_created_transcript(['en'])
            manually_created_transcript_available = True
        except Exception as e:
            #Manually created "english" transcript not available
            try:
                _t =  transcript_list.find_generated_transcript(['en'])
                automatically_created_transcript_available = True
            except Exception as e:
                #Automatically created "english" transcript not available
                pass

        if manually_created_transcript_available:
            _transcript_fetch =  _t.fetch()
            full_transcript = ' '.join([seg['text'] for seg in _transcript_fetch])
            full_transcript = full_transcript.replace("\n", '')
            return full_transcript, 'manual', _transcript_fetch
        elif automatically_created_transcript_available:
            _transcript_fetch =  _t.fetch()
            full_transcript = ' '.join([seg['text'] for seg in _transcript_fetch])
            full_transcript = full_transcript.replace("\n", '')
            return full_transcript, 'auto', _transcript_fetch
        
        return None, None, None
    except:
        return None, None, None

def vertical_spacer(val):
    for _vs in range(val):
        st.write(" ")   


def reset_state_session_for_new_video():
    # st.session_state['video_image'] = []
    # st.session_state['video_title'] = ''


    st.session_state['SUMMARY_CREATED'] = False
    st.session_state['SUMMARY_SCREEN_DISPLAYED_ONCE_FLAG'] = False
    st.session_state['TRANSCRIPT_SUBMITTED'] = False
    st.session_state['SUMMARY'] = "{}"
    st.session_state['messages'] = get_initial_message()
    st.session_state['CHAT_SCREEN_ONCE_FLAG'] = True
    st.session_state['query'] = ''
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['MCQ_TRANSCRIPT_PASSED'] = False

    st.session_state['current_question_idx'] = -1
    st.session_state['all_questions'] = []
    st.session_state['total_score'] = 0
    st.session_state['init_fetch_button_allow'] = True
    


def cvt_str_int_seconds_range(slider_response):
    return [int(slider_response[0].split(':')[0])*60 + int(slider_response[0].split(':')[1]) , int(slider_response[1].split(':')[0])*60 + int(slider_response[1].split(':')[1])]


def get_token_count(slider_response, _transcript_fetch):
    a = cvt_str_int_seconds_range(slider_response)

    transcripts = list(_transcript_fetch)
    # print(slider_response)
    start = [i['start'] for i in transcripts]
    end = [i['start'] + i['duration'] for i in transcripts]

    start_index = 0
    end_index = 0
    for i in range(len(transcripts)):
        if a[0] > transcripts[i]['start']:
            start_index = i
        if a[1] > transcripts[i]['start'] + transcripts[i]['duration']:
            end_index = i


    final = transcripts[start_index : end_index+1]
    desired_transcript = ' '.join([seg['text'] for seg in final])
    return int(len(desired_transcript.split(' '))/0.72)


def get_clipped_video_section(slider_response, _transcript_fetch):
    a = cvt_str_int_seconds_range(slider_response)

    transcripts = list(_transcript_fetch)
    # print(slider_response)
    start = [i['start'] for i in transcripts]
    end = [i['start'] + i['duration'] for i in transcripts]

    start_index = 0
    end_index = 0
    for i in range(len(transcripts)):
        if a[0] > transcripts[i]['start']:
            start_index = i
        if a[1] > transcripts[i]['start'] + transcripts[i]['duration']:
            end_index = i


    final = transcripts[start_index : end_index+1]
    desired_transcript = ' '.join([seg['text'] for seg in final])
    return desired_transcript
