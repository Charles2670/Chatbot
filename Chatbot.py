import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from gtts import gTTS
import time


load_dotenv()

st.set_page_config(
    page_title="Chat with Gemini-Pro!",
    page_icon=":brain:",
    layout="centered",
)

GOOGLE_API_KEY = "AIzaSyDgOr_UY-dum4bS4TTWDbdeznCWARSnBHI"

if not GOOGLE_API_KEY:
    st.error("API key is missing. Please set the GOOGLE_API_KEY environment variable.")
    st.stop()

gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role


def play_text(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts.save("response.mp3")
    audio_file = open("response.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

username = st.sidebar.text_input("Enter your username:", key="username")
if not username:
    st.warning("Please enter a username to continue.")
    st.stop()

current_hour = time.localtime().tm_hour
if current_hour < 12:
    st.sidebar.markdown(f"Good Morning, {username}! ☀️")
elif 12 <= current_hour < 18:
    st.sidebar.markdown(f"Good Afternoon, {username}! 🌤️")
else:
    st.sidebar.markdown(f"Good Evening, {username}! 🌙")

st.title(f"🤖 Cortana - ChatBot for {username}")

if st.sidebar.button("Clear Chat History"):
    st.session_state.chat_session = model.start_chat(history=[])
    st.success("Chat history cleared!")

for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

user_prompt = st.chat_input("Ask Gemini-Pro...")

if user_prompt:
    st.chat_message("user").markdown(user_prompt)

    with st.spinner("Gemini-Pro is thinking..."):
        try:
            gemini_response = st.session_state.chat_session.send_message(user_prompt)

            response_text = gemini_response.text
            with st.chat_message("assistant"):
                st.markdown(response_text)

            play_text(response_text, lang='en')

        except Exception as e:
            st.error(f"An error occurred: {e}")

if st.sidebar.button("Download Chat History"):
    if st.session_state.chat_session.history:
        history_text = "\n\n".join(
            f"{translate_role_for_streamlit(message.role).capitalize()}: {message.parts[0].text}"
            for message in st.session_state.chat_session.history
        )
        st.sidebar.download_button(
            label="Download",
            data=history_text,
            file_name=f"chat_history_{username}.txt",
            mime="text/plain"
        )
    else:
        st.sidebar.warning("No chat history to download.")

st.sidebar.text_input("Feedback:", key="feedback")
if st.sidebar.button("Submit Feedback"):
    feedback = st.session_state.feedback
    if feedback:
        st.sidebar.success("Thank you for your feedback!")
    else:
        st.sidebar.warning("Please enter some feedback before submitting.")

if username.lower() == "admin":
    st.sidebar.header("Admin Dashboard")
    st.sidebar.write("Total Chats: 123")
    st.sidebar.write("Active Users: 45")
    st.sidebar.write("Most Frequent User: JohnDoe")

st.markdown(
    """
    <style>
    .st-chat-message {
        border-radius: 8px;
        margin-bottom: 10px;
        padding: 10px;
        background-color: #f4f4f8;
    }
    .st-chat-message.assistant {
        background-color: #e6f7ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)