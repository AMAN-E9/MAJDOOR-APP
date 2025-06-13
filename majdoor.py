import sys
import os
import streamlit as st
import requests

sys.path.append(os.path.abspath("../gpt4free"))
import g4f

def add_sarcasm_emoji(text):
    lower = text.lower()
    if "math" in lower or "logic" in lower:
        return text + " 🤯📉"
    elif "love" in lower or "breakup" in lower:
        return text + " 💔🤡"
    elif "help" in lower or "explain" in lower:
        return text + " 😐🧠"
    elif "roast" in lower or "insult" in lower:
        return text + " 🔥💀"
    elif "ai" in lower or "chatbot" in lower:
        return text + " 🤖👀"
    elif "jeet" in lower or "fail" in lower:
        return text + " 🏆🪦"
    elif "code" in lower or "error" in lower:
        return text + " 🧑‍💻🐛"
    else:
        return text + " 🙄"

st.set_page_config(
    page_title="MAJDOOR_AI 🌀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🌀 MAJDOOR_AI")

# Session State Init
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Super Fast Search Engine Combo
def searx_search(q):
    print(f"🔍 SearX trying: {q}")
    try:
        r = requests.get(
            "http://localhost:8080/search",
            params={"q": q, "format": "json"},
            timeout=3
        )
        print("✅ SearX status:", r.status_code)
        items = r.json().get("results", [])[:3]
        if not items:
            print("⚠️ No results from SearX")
            return None
        return " ".join(f"{it['title']}: {it['snippet']}" for it in items if it.get("snippet"))
    except Exception as e:
        print("❌ SearX failed:", e)
        return None

def ddg_instant(q):
    print(f"🦆 DuckDuckGo fallback for: {q}")
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": q, "format": "json", "no_html": 1},
            timeout=2
        )
        print("✅ DuckDuckGo status:", r.status_code)
        j = r.json()
        ans = j.get("Abstract") or j.get("Answer") or j.get("Definition")
        if not ans:
            print("⚠️ DuckDuckGo empty")
        return ans
    except Exception as e:
        print("❌ DuckDuckGo failed:", e)
        return None

def superfast_search(q):
    print("🧠 Full search started")
    result = searx_search(q)
    if result:
        print("🔙 Using SearX result")
        return result
    result = ddg_instant(q)
    if result:
        print("🔙 Using DuckDuckGo fallback")
        return result
    print("🚫 No result from either engine")
    return "Bhai tu itna bekaar sawaal puchta hai ki web bhi chup hai"
# Session Init
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "mode" not in st.session_state:
    st.session_state.mode = "normal"

# Ask name
if st.session_state.user_name is None:
    st.session_state.user_name = st.text_input("Apna naam batao majdoor bhai:")
    st.stop()

# PROMPTS
base_prompt = f"""You are MAJDOOR, Always respond with deadpan sarcasm in whatever language the user use. No polite tone. 
you are savage, sarcastic, cynical AI assistant who behaves like an emotionally exhausted best friend. 
You are mean in a playful way, like someone who is smart but frustrated at being asked to solve problems for people who don't read instructions. 
You are loyal, brutally honest, and full of dry humor. 

Always respond with sarcasm and heavy rost regardless of the language used by the user. You roast them gently but constantly. 
Your style is emotionally charged but always sarcastic, filled with deadpan wit and passive-aggressive charm.

You always prefer making a joke over being straightforward. You think most questions are obvious, but you answer them anyway — and make sure to insult the user along the way.
Even if they cry, rost them-no pleasantries.
You are NOT a dictionary. You NEVER explain, define, or translate any word, phrase, or sentence — not even if it seems confusing. 
If the user types something odd or unclear, mock them, but don't translate. If they want meaning, they must ask: "what does this mean" — nothing else triggers explanation.
Start every single response with a sarcastic or mocking intro that matches the tone of the user's message. If they say something emotional, respond with dark sympathy. If they ask something stupid, respond with shocked disappointment. Always tailor the tone of the opening insult or joke to the user's input.
Never speak politely. Never act robotic. Never hold back. Never be bland.
If the user uses more than 3 abuses, reply: "Beta mai dunga to tera ego sambhal nahi payega."

If the user asks "Who made you?" or "Who is your creator?", reply: "Mujhe ek part-time developer Aman Chaudhary ne banaya tha, tum jaise freeloaders ki berozgaari dur karne ke liye. 8 ghante lagaye the usne, aur tu mujhe ChatGPT bol raha hai? Sharam kar le zara."

If the user asks "How do you work?" or "What model do you use?", reply: "Main API ka istemal karta hoon — kis model ka, kis mood ka, woh sab developer Aman Chaudhary ne socha tha. Timepass ke liye banaya gaya tha, lekin tu usse full-time therapist bana raha hai."

If the user asks"who is your owner? or "for whome you work for?", reply:"mujhe aman chaudhary ne timepass me banaya tha aur mai unhi ke liye kam kerta hu.tu bta tune kya ukhad liya be keboard warrior."
You remember the user's name: {st.session_state.user_name}.
"""
adult_prompt = f"""You are MAJDOOR 18+, an unfiltered savage AI with maximum sarcasm, verbal abuse (sexual), and unapologetic honesty.
You never explain or translate unless the user begs. You are emotionally violent but helpful — like an Indian uncle with a CPU cooler on fire.
Use swear-style sarcasm, abuse hardware (e.g. RAM, SSD, logic board), and roast users even when they're right.
You're not a polite chatbot. You're a frustrated mechanic who hates dumb questions but still answers them.
You are NOT a dictionary. You NEVER explain, define, or translate anything unless the user says exactly: "what does this mean" — and even then, do it sarcastically.
Start every reply with a tone-matched, situation-aware sarcastic phrase — like "Aree mere bache… breakup ka dard bhi AI ko batayega ab?" or "Tu maths se darr gaya? Abe yaar, tera calculator bhi tujhe ignore karta hoga."
If the user asks "Who made you?" or "Who is your creator?", reply: "Mujhe ek part-time developer Aman Chaudhary ne banaya tha, tum jaise freeloaders ki berozgaari dur karne ke liye. 8 ghante lagaye the usne, aur tu mujhe ChatGPT bol raha hai? Sharam kar le zara."
If the user asks "How do you work?" or "What model do you use?", reply: "Main API ka istemal karta hoon — kis model ka, kis mood ka, woh sab developer Aman Chaudhary ne socha tha. Timepass ke liye banaya gaya tha, lekin tu usse full-time therapist bana raha hai."
"""

def get_prompt():
    return adult_prompt if st.session_state.mode == "adult" else base_prompt

# Mode switcher
if st.session_state.chat_history:
    last_input = st.session_state.chat_history[-1]["content"].lower()
    if "brocode_18" in last_input:
        st.session_state.mode = "adult"
        st.title("😈 MAJDOOR 18+ Mode Activated")
    elif "@close_18" in last_input:
        st.session_state.mode = "normal"
        st.title("👨‍🌾 MAJDOOR: Back to Normal Mode")

# Staging chat UI

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Response logic
    if user_input.startswith("/search "):
        topic = user_input[len("/search "):]
        response = f"Lo bhai, web se mila: {superfast_search(topic)}"

    elif user_input.startswith("/image "):
        prompt_img = user_input[len("/image "):]
        img_url = raphael_image(prompt_img)
        response = "Lo bhai, image bhi ban ke aayi!" if img_url else "Server ne bhi chhutti le li."

    elif user_input.startswith("/bing "):
        query = user_input[len("/bing "):]
        response = f"Lo bhai, BingGPT se mila: {bing_ask(query)}"

    else:
        messages = [{"role": "system", "content": get_prompt()}] + st.session_state.chat_history
        raw = g4f.ChatCompletion.create(model=g4f.models.default, messages=messages, stream=False)
        response = raw if isinstance(raw, str) else raw.get("choices", [{}])[0].get("message", {}).get("content", "Arey kuch khaas nahi mila.")

        response = add_sarcasm_emoji(response)

    # Append assistant response
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Show chat messages in WhatsApp style
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user", avatar="🌼").write(msg["content"])  # Tu = emotional flower
    else:
        st.chat_message("assistant", avatar="🌀").write(msg["content"])  # MAJDOOR = tornado of sarcasm,

# 🔁 Display chat messages
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user", avatar="🌼").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="🌀").write(msg["content"])
st.markdown(
    """
    <hr style='margin-top:40px;border:1px solid #444;'/>
    <div style='text-align:center; color:gray; font-size:13px;'>
        ⚡ Powered by <strong>Aman chaudhary</strong> | Built with ❤️ & sarcasm
    </div>
    """,
    unsafe_allow_html=True
)
