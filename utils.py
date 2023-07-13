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
        return full_transcript, 'manual'
    elif automatically_created_transcript_available:
        _transcript_fetch =  _t.fetch()
        full_transcript = ' '.join([seg['text'] for seg in _transcript_fetch])
        full_transcript = full_transcript.replace("\n", '')
        return full_transcript, 'auto'
    
    return None, None

def vertical_spacer(val):
    for _vs in range(val):
        st.write(" ")   


def reset_state_session_for_new_video():
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
    

