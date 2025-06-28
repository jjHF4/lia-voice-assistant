import streamlit as st
import sqlite3
import cohere
import pygame
import tempfile
import time
from gtts import gTTS
import re
import os
import speech_recognition as sr

# Initialize Cohere
co = cohere.Client(os.environ["COHERE_API_KEY"])
# Page config
st.set_page_config(page_title="LIA - Voice Agent", layout="centered")
st.title("🩺 LIA - Hospital Voice Assistant")
st.write("Talk to LIA using voice or text. Enjoy voice-to-voice interaction like a real assistant!")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "patient_name" not in st.session_state:
    st.session_state.patient_name = None
if "last_reply" not in st.session_state:
    st.session_state.last_reply = ""

# Speak function with avatar trigger
def speak(text, avatar_placeholder):
    tts = gTTS(text=text, lang='en')
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_path = tmp_file.name
    tmp_file.close()
    tts.save(temp_path)
    pygame.mixer.init()
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()

    # Show avatar while speaking
    avatar_placeholder.image("avatar.gif", width=180)

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()
    avatar_placeholder.empty()
    os.remove(temp_path)

# Voice to text
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Please speak now.")
        audio = recognizer.listen(source)
        st.success("✅ Voice captured. Converting to text...")

    try:
        text = recognizer.recognize_google(audio)
        st.text(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        st.warning("❗ Could not understand audio.")
    except sr.RequestError:
        st.error("❗ Speech Recognition service error.")
    return None

# Database lookup
def get_history(patient_name):
    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()
    cursor.execute("SELECT consultation_date, consultation_notes FROM consultations WHERE lower(patient_name) = ?", (patient_name.lower(),))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get AI reply
def get_ai_reply(user_msg, patient_name, history):
    history_text = "\n".join([f"{d}: {n}" for d, n in history]) if history else "No history available."
    chat_log = "\n".join([f"User: {msg['user']}\nAI: {msg['ai']}" for msg in st.session_state.chat_history])
    prompt = f"""
You are a polite and helpful hospital voice assistant named LIA.
Patient Name: {patient_name}
Patient History:
{history_text}

Chat so far:
{chat_log}

Now continue the conversation based on this new message:
User: {user_msg}
AI:
"""
    response = co.chat(model="command-r", message=prompt)
    return response.text.strip()

# Input section (voice or text)
user_input = None
avatar_placeholder = st.empty()

if st.button("🎤 Speak to LIA"):
    user_input = get_voice_input()

if not user_input:
    user_input = st.text_input("💬 You (or type here):", placeholder="Hi, I am Rahul. Can you tell my vaccine date?")

if user_input:
    # Try to extract name
    if st.session_state.patient_name is None:
        match = re.search(r"i am ([a-zA-Z0-9 ]+)[.?,]*", user_input.lower())
        if match:
            st.session_state.patient_name = match.group(1).strip().title()

    name = st.session_state.patient_name

    if name:
        history = get_history(name)
        reply = get_ai_reply(user_input, name, history)
        st.session_state.chat_history.append({"user": user_input, "ai": reply})
        st.session_state.last_reply = reply

        st.markdown(f"**🧑 You:** {user_input}")
        st.markdown("**🤖 LIA:**")

        placeholder = st.empty()
        placeholder.markdown("🕐 Typing response...")

        # Speak + show avatar
        speak(reply, avatar_placeholder)

        # Typing effect
        displayed_text = ""
        for char in reply:
            displayed_text += char
            placeholder.markdown(displayed_text)
            time.sleep(0.02)

        # Appointment suggestion
        if "vaccine" in reply.lower() or "follow-up" in reply.lower():
            if st.button("📅 Book Appointment"):
                st.success("✅ Appointment booked! Confirmation will be emailed shortly.")
    else:
        st.warning("❗ Please introduce yourself by saying 'I am [Your Name]'")

# Conversation history
if st.session_state.chat_history:
    with st.expander("📜 Conversation History"):
        for i, chat in enumerate(st.session_state.chat_history):
            st.markdown(f"**You {i+1}:** {chat['user']}")
            st.markdown(f"**LIA {i+1}:** {chat['ai']}")

# Bottom tools
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔄 Change Patient"):
        st.session_state.patient_name = None
        st.success("Patient reset. Please reintroduce yourself.")
with col2:
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.patient_name = None
        st.session_state.last_reply = ""
        st.experimental_rerun()
with col3:
    if st.button("💾 Export Chat to File"):
        with open("chat_log.txt", "w") as f:
            for entry in st.session_state.chat_history:
                f.write(f"You: {entry['user']}\nLIA: {entry['ai']}\n\n")
        st.success("Chat log saved as chat_log.txt")
