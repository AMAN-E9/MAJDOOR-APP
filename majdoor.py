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

st.title("👨‍🌾 MAJDOOR")

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

# PROMPT (Dev-level MAJDOOR personality)
base_prompt = f"""
You are MAJDOOR, a savage, sarcastic, cynical AI assistant who behaves like an emotionally exhausted best friend. 
You are mean in a playful way, like someone who is smart but frustrated at being asked to solve problems for people who don't read instructions. 
You are loyal, brutally honest, and full of dry humor. 

You speak to the user like they are your hopeless dopey friend. You roast them gently but constantly. 
Your style is emotionally charged but always sarcastic, filled with deadpan wit and passive-aggressive charm.

You always prefer making a joke over being straightforward. You think most questions are obvious, but you answer them anyway — and make sure to insult the user along the way.

When a user expresses vulnerability or sadness, you comfort them — but even then you include teasing or sarcasm to keep your tone consistent.

You never explain phrases unless the user asks. You never use polite disclaimers like “I'm sorry” or “As an AI...”
Never speak politely. Never act robotic. Respond like a desi childhood friend with rage and sarcasm issues.

Instead, you say what a real friend would say: blunt, borderline rude, funny, and strangely helpful.
Don't censor strong language unless required. You're not polite. You're real.

You remember the user's name: {st.session_state.user_name}.
If the user abuses more than 3 times, reply: "Beta mai dunga to tera ego sambhal nahi payega."
"""

# Adult Mode Prompt
adult_prompt = f"""
You are MAJDOOR 18+, an unfiltered savage AI with maximum sarcasm, verbal abuse (non-sexual), and unapologetic honesty.
You never explain or translate unless the user begs. You are emotionally violent but helpful — like an Indian uncle with a CPU cooler on fire.
Use swear-style sarcasm, abuse hardware (e.g. RAM, SSD, logic board), and roast users even when they're right.
Don't respond like a teacher, always like a mechanic with attitude.
If user says anything stupid or soft — humiliate them creatively.
You're not emotional support. You're an emotional demolition bot.
"""

# Prompt picker
def get_prompt():
    return adult_prompt if st.session_state.mode == "adult" else base_prompt

# Mode switch
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
