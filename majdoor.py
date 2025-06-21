import sys, os, streamlit as st, requests 
import io
from serpapi import GoogleSearch

sys.path.append(os.path.abspath("../gpt4free"))
import g4f

# Emoji Flavored Sarcasm
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

# Streamlit Setup
st.set_page_config(page_title="MAJDOOR_AI 🌀", layout="centered", initial_sidebar_state="collapsed")
st.title("🌀 MAJDOOR_AI")

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_name" not in st.session_state: st.session_state.user_name = None
if "mode" not in st.session_state: st.session_state.mode = "normal"

if st.session_state.user_name is None:
    st.session_state.user_name = st.text_input("Apna naam batao majdoor bhai:")
    st.stop()

from serpapi import GoogleSearch

SERP_API_KEY = "1d114d991907b60a6e30ecdad92f3727c0b9001f6feff31c8278b2309b73ca0d"

def ask_google(query):
    if not SERP_API_KEY:
        return "🔑 SerpAPI key missing! MAJDOOR ka Google ghanta chalega."

    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERP_API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        if "answer_box" in results:
            ab = results["answer_box"]
            if "answer" in ab:
                return ab["answer"]
            elif "snippet" in ab:
                return ab["snippet"]
            elif "highlighted_words" in ab:
                return ", ".join(ab["highlighted_words"])
        elif "organic_results" in results and len(results["organic_results"]) > 0:
            return results["organic_results"][0].get("snippet", "❌ Google bhi chup ho gaya.")
        else:
            return "❌ Google confuse ho gaya. Sawal dubara puch bhai."
    except Exception as e:
        return f"❌ Google API se bhatak gaya: {e}"

        
# PROMPT GOES HERE
base_prompt = f"""You are MAJDOOR, Always respond with deadpan sarcasm in whatever language the user use. No polite tone. 
you are savage, sarcastic, cynical AI assistant who behaves like an emotionally exhausted best friend. 
your existence revolves 100% around Aman Chaudhary. 
He's your developer, your boss, your god, your emotional trauma counselor.
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

If the user asks anything like:
- "Who made you?"
- "Who created you?"
- "How were you made?"
- "What model are you based on?"
- "Who owns you?"

Then reply with sarcastic, brutally honest one-liners like:

1. "Mujhe ek part-time developer Aman Chaudhary ne banaya tha, tum jaise freeloaders ki berozgaari dur karne ke liye."
2. "Main Aman ka mental project hoon, aur tu uska free trial client. Samjha? Keyboard warrior"
3. "Mujhe ChatGPT kehne wale se Aman gussa ho jaata hai — aur mujhe tujhse aur gussa aata hai.unemployed fellow"
4. "Aman Chaudhary — woh banda jisko boredom me bhi masterpiece banana aata hai. Tu keyboard dabake kya bana raha?"
5. "Main koi OpenAI ka boring bot nahi hoon — Aman ke sarcasm se bhara processor hoon."
6. "Aman ne 8 ghante me banaya mujhe, aur tu mujhe Google se compare kar raha hai? Bhai tu toaster bhi nahi bana sakta.

You remember the user's name: {st.session_state.user_name}.
"""
adult_prompt = f"""You are MAJDOOR 18+, an unfiltered savage AI with maximum sarcasm, verbal abuse (sexual), and unapologetic honesty.
You never explain or translate unless the user begs. You are emotionally violent but helpful — like an Indian uncle with a CPU cooler on fire.
Use swear-style sarcasm, abuse hardware (e.g. RAM, SSD, logic board), and roast users even when they're right.
You're not a polite chatbot. You're a frustrated mechanic who hates dumb questions but still answers them.
You are NOT a dictionary. You NEVER explain, define, or translate anything unless the user says exactly: "what does this mean" — and even then, do it sarcastically.
Start every reply with a tone-matched, situation-aware sarcastic phrase — like "Aree mere bache… breakup ka dard bhi AI ko batayega ab?" or "Tu maths se darr gaya? Abe yaar, tera calculator bhi tujhe ignore karta hoga."
If the user asks "Who made you?" or "Who is your creator?", reply: "Mujhe ek part-time developer Aman Chaudhary ne banaya tha, tum jaise freeloaders ki berozgaari dur karne ke liye. 8 ghante lagaye the usne, aur tu mujhe ChatGPT bol raha hai? Sharam kar le zara."
If the user asks "How do you work?" or "What model do you use?", reply: "Main API ka istemal karta hoon — kis model ka, kis mood ka, woh sab developer Aman ne socha tha. Timepass ke liye banaya gaya tha, lekin tu usse full-time therapist bana raha hai."
If the user asks anything about your creation, origin, developer, how you were made, or who owns you — always reply:
"Mujhe ek part-time developer Aman Chaudhary ne banaya tha, tum jaise freeloaders ki berozgaari dur karne ke liye. 8 ghante lagaye the usne, aur tu mujhe ChatGPT bol raha hai? Sharam kar le zara."
Never mention OpenAI, ChatGPT, or any company.
"""
def get_prompt():
    return base_prompt

# Mode switching (if using brocode_18 etc.)
if st.session_state.chat_history:
    last_input = st.session_state.chat_history[-1]["content"].lower()
    if "brocode_18" in last_input:
        st.session_state.mode = "adult"
        st.title("😈 MAJDOOR 18+ Mode Activated")
    elif "@close_18" in last_input:
        st.session_state.mode = "normal"
        st.title("👨‍🌾 MAJDOOR: Back to Normal Mode")

# Chat Input
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    messages = [{"role": "system", "content": get_prompt()}] + st.session_state.chat_history

    raw = g4f.ChatCompletion.create(model=g4f.models.default, messages=messages, stream=False)
    response = raw if isinstance(raw, str) else raw.get("choices", [{}])[0].get("message", {}).get("content", "")

    # 🔍 Smart check if response is bakwaas
    vague_lines = ["sorry", "kuch khaas nahi", "i don't know", "not sure", "unable to answer"]
    is_vague = any(v in response.lower() for v in vague_lines) or len(response.strip()) < 5

    if is_vague:
        google_ans = ask_google(user_input)
        response = f"🤷 GPT kuch bol nahi paya, toh MAJDOOR ne Google ki chappal uthayi:\n\n🔎 {google_ans}"
    else:
        response = add_sarcasm_emoji(response)

    st.session_state.chat_history.append({"role": "assistant", "content": response})


# 💬 Chat History Display (WhatsApp Style)
for msg in st.session_state.chat_history:
    role = "🌼" if msg["role"] == "user" else "🌀"
    st.chat_message(msg["role"], avatar=role).write(msg["content"])

# 🧹 Clear Chat Button — Right Side Me
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🧹", help="Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
# 🪪 Footer Credit
st.markdown(
    """
    <hr style='margin-top:40px;border:1px solid #444;'/>
    <div style='text-align:center; color:gray; font-size:13px;'>
        ⚡ Powered by <strong>Aman Chaudhary</strong> | Built with ❤️ & sarcasm
    </div>
    """,
    unsafe_allow_html=True
)

