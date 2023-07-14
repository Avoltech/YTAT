import streamlit as st
from utils import get_english_transcript, reset_state_session_for_new_video, vertical_spacer, cvt_str_int_seconds_range, get_token_count, get_clipped_video_section 
from pytube import YouTube
import openai
from annotated_text import annotated_text

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

if 'HOME_SCREEN_NEED_TO_SHOW_SLIDER_FLAG' not in st.session_state:
    st.session_state['HOME_SCREEN_NEED_TO_SHOW_SLIDER_FLAG'] = False

if 'TOKEN_THRESHOLD_DICT' not in st.session_state:
    st.session_state['TOKEN_THRESHOLD_DICT'] = {
        'gpt-3.5-turbo': 3000,
        'gpt-3.5-turbo-16k': 13000,
    }

if 'video_image' not in st.session_state:
    st.session_state['video_image'] = []

if 'video_title' not in st.session_state:
    st.session_state['video_title'] = ''

if 'FULL_TRANSCRIPT' not in st.session_state:
    st.session_state['FULL_TRANSCRIPT'] = ''

def slider_val_on_change_func():
    slider_vals = st.session_state['slider_key']
    st.session_state['slider_vals'] = slider_vals

MODELS = ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']
if 'model' not in st.session_state:
    st.session_state['model'] = MODELS[0]

with st.sidebar:
    with st.expander("API settings"):  
        with st.container():
            apikey = st.text_input(label="API KEY", type='password', key='text_input_apikey', value=st.session_state['apikey'])
            model = st.selectbox(label="Model", key='selectbox_model', options=MODELS, index=MODELS.index(st.session_state['model']))

_token_text_color_dict = ["#afa","#faa"]


# st.write("Paste a youtube url to get started")
_img_col, _vid_title_col = st.columns([2, 6])
with _img_col:
    _img_col_placeholder = st.empty()
    # st.image(st.session_state['video_image'], use_column_width=True)
    
with _vid_title_col:
    # st.subheader(st.session_state['video_title'])
    _vide_title_col_placeholder = st.empty()

youtube_url = st.text_input(label="Paste a youtube url to get started", key="Youtube URL", value=st.session_state['YOUTUBE_VIDEO_URL'])

if ('youtube.com/watch?v=' not in youtube_url) and ((youtube_url != '')):
    st.error("Please enter a valid youtube url")
elif ((youtube_url != '')):
    st.session_state['YOUTUBE_VIDEO_URL'] = youtube_url
    try:
        transcript, transcript_type, transcript_fetch_obj = get_english_transcript(st.session_state['YOUTUBE_VIDEO_URL'])
    except Exception as e:
        print(e)
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
            if st.session_state['FULL_TRANSCRIPT'] != transcript:
                st.session_state['FULL_TRANSCRIPT'] = transcript
            
            st.session_state['video_image'] = get_thumbnail(st.session_state['YOUTUBE_VIDEO_URL'])
            st.session_state['video_title'] = get_title(st.session_state['YOUTUBE_VIDEO_URL'])
            _img_col_placeholder.image(image = st.session_state['video_image'] , use_column_width=True)
            _vide_title_col_placeholder.subheader(st.session_state['video_title'] )

            total_vid_seconds = get_duration(st.session_state['YOUTUBE_VIDEO_URL'])

            if (st.session_state['prev_video_url'] != st.session_state['YOUTUBE_VIDEO_URL']):
                # _img_col_placeholder.image(image = st.session_state['video_image'] , use_column_width=True)
                # _vide_title_col_placeholder.subheader(st.session_state['video_title'] )
                st.session_state['slider_vals'] = ("0:0",str(total_vid_seconds//60) + ':' + str(total_vid_seconds%60))

            # st.session_state['video_image'] = get_thumbnail(youtube_url)
            # st.session_state['video_title'] = get_title(youtube_url)
            
            # _img_col_placeholder.image(image = get_thumbnail(youtube_url), use_column_width=True)
            # _vide_title_col_placeholder.subheader(get_title(youtube_url))
            
            if 'slider_vals' not in st.session_state:
                st.session_state['slider_vals'] = ("0:0",str(total_vid_seconds//60) + ':' + str(total_vid_seconds%60))

            # st.write(st.session_state['slider_vals'])

            estimated_token_count = get_token_count(st.session_state['slider_vals'], transcript_fetch_obj)

            if (estimated_token_count > st.session_state['TOKEN_THRESHOLD_DICT'][st.session_state['model']]) or (st.session_state['HOME_SCREEN_NEED_TO_SHOW_SLIDER_FLAG'] == True):

                st.session_state['HOME_SCREEN_NEED_TO_SHOW_SLIDER_FLAG'] = True
                if (estimated_token_count > st.session_state['TOKEN_THRESHOLD_DICT'][st.session_state['model']]):
                    st.error('The selected video is too big to process. Please select a smaller section', icon='✂️')
                
                tlist = []
                for i in range(0, total_vid_seconds, 10):
                    tlist.append(str(i//60) + ':' + str(i%60))
            
                i = total_vid_seconds
                tlist.append(str(i//60) + ':' + str(i%60))
                # st.write(tlist)
                # st.write(total_vid_seconds)
                # st.write(tlist)
                # st.write(st.session_state['slider_vals'])
                slider_vals = st.select_slider("Select range", tlist, value=st.session_state['slider_vals'], on_change=slider_val_on_change_func, key="slider_key")
                estimated_token_count = get_token_count(st.session_state['slider_vals'], transcript_fetch_obj)


                # annotated_text(
                #     "Maxiumum tokens you can have with current selected model: ",
                #     (str(st.session_state['TOKEN_THRESHOLD_DICT'][st.session_state['model']]), "", "#8ef"),
                # )
                # st.write(f"Total tokens in selected section : {estimated_token_count}")

                if (estimated_token_count > st.session_state['TOKEN_THRESHOLD_DICT'][st.session_state['model']]):
                     annotated_text(
                        "Total tokens in selected section: ",
                        (str(estimated_token_count), "", _token_text_color_dict[1]),
                    )
                else:
                    annotated_text(
                        "Total tokens in selected section: ",
                        (str(estimated_token_count), "", _token_text_color_dict[0]),
                    )

                # st.write(f"Maxiumum tokens you can have with current selected model: {}")
                annotated_text(
                    "Maxiumum tokens you can have with current selected model: ",
                    (str(st.session_state['TOKEN_THRESHOLD_DICT'][st.session_state['model']]), "", "#8ef"),
                )

                if (estimated_token_count <= st.session_state['TOKEN_THRESHOLD_DICT'][st.session_state['model']]):
                    transcript = get_clipped_video_section(st.session_state['slider_vals'], transcript_fetch_obj)
                    st.session_state['TRANSCRIPT'] = transcript
                    st.success("Huston to Apollo, you are set to go!!", icon="🚀")
                    
            else:
                transcript = get_clipped_video_section(st.session_state['slider_vals'], transcript_fetch_obj)

                st.session_state['TRANSCRIPT'] = transcript
                st.success("Huston to Apollo, you are set to go!!!", icon="🚀")

                # st.write(estimated_token_count > st.session_state['TOKEN_THRESHOLD_DICT'][st.session_state['model']])
                # st.write(st.session_state['HOME_SCREEN_NEED_TO_SHOW_SLIDER_FLAG'] == True)
                
        if st.session_state['prev_video_url'] != st.session_state['YOUTUBE_VIDEO_URL']:
            if st.session_state['prev_video_url'] != '':
                st.session_state['HOME_SCREEN_NEED_TO_SHOW_SLIDER_FLAG'] = False
            st.session_state['prev_video_url'] = st.session_state['YOUTUBE_VIDEO_URL']
            reset_state_session_for_new_video()
        # if st.session_state['video_image'] == []:
        #     st.session_state['video_image'] = get_thumbnail(st.session_state['YOUTUBE_VIDEO_URL'])
        # if st.session_state['video_title'] == '':
        #     st.session_state['video_title'] = get_title(st.session_state['YOUTUBE_VIDEO_URL'])

        # st.write(type(get_thumbnail(youtube_url)))
        # st.write(get_thumbnail(youtube_url))
        # st.write((st.session_state['prev_video_url'] != st.session_state['YOUTUBE_VIDEO_URL']) or (st.session_state['prev_video_url'] == ''))
        # st.write(st.session_state['prev_video_url'] == '')

        # st.write(st.session_state['video_image'])
        # st.write(st.session_state['video_title'])

