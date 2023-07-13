import streamlit as st
from utils import get_english_transcript, reset_state_session_for_new_video, vertical_spacer
from pytube import YouTube
import openai


streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap');
            html, body, [class*="css"]  {
			font-family: 'Roboto', sans-serif;
			}
			</style>
			"""
st.markdown(streamlit_style, unsafe_allow_html=True)


# st.title("Youtube Anatomy")
st.markdown("<h1 style='text-align: center; font-weight: 300; font-family: 'Roboto', sans-serif;'>Youtube Anatomy</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color: grey;'>🥇 Summarise a video 🥈 Clear your doubts 🥉 Test your knowledge</h4>", unsafe_allow_html=True)
vertical_spacer(2)

def get_title(url):
    yt = YouTube(url)
    return yt.title

def get_thumbnail(url):
    yt = YouTube(url)
    return yt.thumbnail_url

def get_duration(url):
    yt = YouTube(url)
    seconds = yt.length
    return seconds

if 'apikey' not in st.session_state:
    st.session_state['apikey'] = ''
if 'YOUTUBE_VIDEO_URL' not in st.session_state:
    st.session_state['YOUTUBE_VIDEO_URL'] = ''

if 'prev_video_url' not in st.session_state:
    st.session_state['prev_video_url'] = ''


with st.sidebar:
    with st.expander("API settings"):  
        with st.container():
            apikey = st.text_input(label="API KEY", type='password', key='text_input_apikey', value=st.session_state['apikey'])
            model = st.selectbox(label="Model", key='selectbox_model', options=['gpt-3.5-turbo', 'gpt-3.5-turbo-16k'], index=0)



# st.write("Paste a youtube url to get started")
_img_col, _vid_title_col = st.columns([2, 6])
with _img_col:
    _img_col_placeholder = st.empty()
with _vid_title_col:
    _vide_title_col_placeholder = st.empty()
youtube_url = st.text_input(label="Paste a youtube url to get started", key="Youtube URL", value=st.session_state['YOUTUBE_VIDEO_URL'])

if ('youtube.com/watch?v=' not in youtube_url) and ((youtube_url != '')):
    st.error("Please enter a valid youtube url")
elif ((youtube_url != '')):
    st.session_state['YOUTUBE_VIDEO_URL'] = youtube_url
    try:
        transcript, transcript_type = get_english_transcript(st.session_state['YOUTUBE_VIDEO_URL'])
    except:
        st.error("Unable to fetch transcript.\nPlease recheck the video link and try again.", icon="🥶")

    if (apikey == ''):
        st.error("Please enter a valid api key", icon="🤖")
    else:
        st.session_state['apikey'] = apikey
        st.session_state['model'] = model
        openai.api_key = apikey

        if (transcript == None):
            st.error("Looks like the video does not contain a 'English' transcript.\nTry a different video.", icon="😭")
        elif (transcript.count(' ') < 100):
            st.error("Hmmm...The video transcript is too short.\nTry a different video.", icon="🌱")
        else:
            st.session_state['TRANSCRIPT'] = transcript
            _img_col_placeholder.image(image = get_thumbnail(youtube_url), use_column_width=True)
            _vide_title_col_placeholder.subheader(get_title(youtube_url))

            st.success("Huston to Apollo, you are set to go!!", icon="🚀")
        if st.session_state['prev_video_url'] != st.session_state['YOUTUBE_VIDEO_URL']:
            st.session_state['prev_video_url'] = st.session_state['YOUTUBE_VIDEO_URL']
            reset_state_session_for_new_video()
