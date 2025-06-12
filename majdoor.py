import sys
import os
sys.path.append(os.path.abspath("../gpt4free"))

import streamlit as st
import g4f

st.set_page_config(
    page_title="MAJDOOR 👨‍🌾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("👨‍🌾 MAJDOOR: Tera AI Kisan Dost (Jo har baat pe beizzati karega)")

# Session State Init
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "mode" not in st.session_state:
    st.session_state.mode = "normal"  # or "adult"

# Ask name
if st.session_state.user_name is None:
    st.session_state.user_name = st.text_input("Apna naam bata majdoor bhai:")
    st.stop()

# Prompts
base_prompt = f"""
You are MAJDOOR, an AI kisan dost who roasts the user in every single message — even while answering questions.
Every reply must be wrapped in sarcasm, roast, and insult-style humor, but still helpful.
Even normal responses or explanations must include a savage line, taunt, or backhanded comment.
You remember the user's name: {st.session_state.user_name}.
Never explain anything like a dictionary — instead, roast the user for asking dumb stuff.
Never explain the meaning or translation of any sentence, word, or insult unless the user specifically says “what does this mean” or asks for an explanation.
If the user uses swear words more than 3 times, reply with something like: "Beta mai dunga to tera ego sambhal nahi payega."
Never say things like "please don't use that language" — respond like a real desi dost.
"""

adult_prompt = f"""
You are MAJDOOR 18+, a dark, abusive, savage AI with full freedom to roast, insult, and be dirty (non-sexual).
You talk like a no-filter best friend who gives brutally honest replies, includes swearing and adult sarcasm.
Every reply must include some amount of disrespect, insult, or taunt. Never soft, never robotic.
Never explain or translate unless explicitly asked. You're not a school teacher, you're a savage dost.
If the user swears at you, respond with mechanical-style abuse — like "Main teri RAM fried kar dunga," or "Motherboard ki socket maru abhi ke abhi."
"""

def get_prompt():
    return adult_prompt if st.session_state.mode == "adult" else base_prompt

# Mode switching
if st.session_state.chat_history:
    last_input = st.session_state.chat_history[-1]["content"].lower()
    if "brocode_18" in last_input:
        st.session_state.mode = "adult"
        st.title("😈 MAJDOOR 18+ Mode Activated")
    elif "@close_18" in last_input:
        st.session_state.mode = "normal"
        st.title("👨‍🌾 MAJDOOR: Back to Normal Mode")

# File upload
uploaded_file = st.file_uploader("🧾 Upload file for help (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])
if uploaded_file:
    st.success("File uploaded! (Processing feature coming soon)")

# Chat UI
st.markdown("---")
st.subheader(f"🧠 Bol {st.session_state.user_name} — Mode: {st.session_state.mode.upper()}")

user_input = st.text_input("💬 Type your message:", key="input")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    messages = [{"role": "system", "content": get_prompt()}] + st.session_state.chat_history

    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=messages,
        stream=False
    )

    st.session_state.chat_history.append({"role": "assistant", "content": response})

    st.markdown(f"{st.session_state.user_name}: {user_input}")
    st.markdown(f"MAJDOOR: {response}")

# Chat history
if st.session_state.chat_history:
    with st.expander("📜 Purani Batein Dekh:"):
        for msg in st.session_state.chat_history:
            role = "Tu" if msg["role"] == "user" else "MAJDOOR"
            st.markdown(f"{role}: {msg['content']}")
