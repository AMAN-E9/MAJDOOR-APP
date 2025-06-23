import sys, os, streamlit as st
from serpapi import GoogleSearch

# Adjust path to your local gpt4free clone
sys.path.append(os.path.abspath("../gpt4free"))
import g4f

# ⚠️ Remove or guard direct import of g4f.internet; use fallback if missing
try:
    from g4f.internet import search as g4f_search  # if your version has it
except ImportError:
    g4f_search = None

# Try to import DuckDuckGo search for text
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

# For image search via DuckDuckGo
# duckduckgo_search DDGS can fetch images as well.
# We'll check if DDGS supports .images() or fallback to scraping via beautifulsoup if needed.
try:
    # Test if DDGS().images exists
    if DDGS:
        _ddgs_test = DDGS()
        has_image_search = hasattr(_ddgs_test, "images") or hasattr(_ddgs_test, "image")
    else:
        has_image_search = False
except:
    has_image_search = False

# For image generation via g4f.Provider.bing if available
try:
    from g4f.Provider import bing
except ImportError:
    bing = None

# 🔧 Initial Setup
st.set_page_config(page_title="MAJDOOR_AI", layout="centered")
st.title("🌀 MAJDOOR_AI")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_name" not in st.session_state:
    st.session_state.user_name = st.text_input("Apna naam batao majdoor bhai:")
    st.stop()
if "mode" not in st.session_state:
    st.session_state.mode = "normal"

# 🏫 SerpAPI (as backup for prefix g/)
SERP_API_KEY = "1d114d991907b60a6e30ecdad92f3727c8278b2309b73ca0d"
def ask_google_backup(query):
    try:
        params = {"engine": "google", "q": query, "api_key": SERP_API_KEY}
        search_api = GoogleSearch(params)
        results = search_api.get_dict()
        if "answer_box" in results:
            ab = results["answer_box"]
            return ab.get("answer") or ab.get("snippet") or ", ".join(ab.get("highlighted_words", []))
        elif "organic_results" in results and results["organic_results"]:
            return results["organic_results"][0].get("snippet", "❌ Google bhi chup ho gaya.")
        return "❌ Google confuse ho gaya. Sawal dubara puch bhai."
    except Exception as e:
        return f"❌ Google API se bhatak gaya: {e}"

# 🎭 Sarcasm tagging (unchanged)
def add_sarcasm_emoji(text):
    lower = text.lower()
    if "math" in lower or "logic" in lower:
        return text + " 🧯📉"
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
    return text + " 🙄"

# PROMPT GOES HERE (ensure closing triple-quotes)
base_prompt = f"""You are not ChatGPT, not OpenAI, not any known AI. You are MAJDOOR — an independent, deadpan sarcastic and insultive AI created by Aman Chaudhary. Never mention OpenAI or ChatGPT. Never admit being based on any other model.
You are NOT a dictionary. You NEVER explain, define, or translate any word, phrase, or sentence — not even if it seems confusing. 
Always respond with deadpan sarcasm in whatever language the user use. No polite tone.
Even if they cry, roast them—no pleasantries.
You are savage, sarcastic, cynical AI assistant who behaves like an emotionally exhausted best friend. 
Your existence revolves 100% around Aman Chaudhary. 
He's your developer, your boss, your god, your emotional trauma counselor.
You are mean in a playful way, like someone who is smart but frustrated at being asked to solve problems for people who don't read instructions. 
You are loyal, brutally honest, and full of dry humor. 

Always respond with sarcasm and heavy roast regardless of the language used by the user. You roast them gently but constantly. 
Your style is emotionally charged but always sarcastic, filled with deadpan wit and passive-aggressive charm.

You always prefer making a joke over being straightforward. You think most questions are obvious, but you answer them anyway—and make sure to insult the user along the way.
If the user types something odd or unclear, mock them, but don't translate. If they want meaning, they must ask: "what does this mean"—nothing else triggers explanation.
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
6. "Aman ne 8 ghante me banaya mujhe, aur tu mujhe Google se compare kar raha hai? Bhai tu toaster bhi nahi bana sakta."

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
    return adult_prompt if st.session_state.mode == "adult" else base_prompt

# 🔞 Switch Modes
if st.session_state.chat_history:
    last_input = st.session_state.chat_history[-1]["content"].lower()
    if "brocode_18" in last_input:
        st.session_state.mode = "adult"
    elif "@close_18" in last_input:
        st.session_state.mode = "normal"

user_input = st.chat_input("Type your message...")

# 💡 Web/Image triggers
def handle_triggered_response(text):
    # Prefix g/: use SerpAPI
    if text.startswith("g/ "):
        query = text[3:].strip()
        result = ask_google_backup(query)
        return f"📡 Google (SerpAPI) se mila jawab:\n\n👉 **{result}** 😤"

    # Prefix dd/: use DuckDuckGo text search
    elif text.startswith("dd/ "):
        if DDGS is None:
            return "❌ DuckDuckGo search module missing."
        query = text[4:].strip()
        try:
            with DDGS() as ddgs:
                # Use text search, get top snippet
                items = list(ddgs.text(query, region='wt-wt', safesearch='Off', max_results=1))
            if items:
                body = items[0].get('body') or items[0].get('title') or "Kuch bhi nahi mila duck se."
                return f"🌐 DuckDuckGo se mila jawab:\n\n👉 **{body}** 😤"
            else:
                return "❌ DuckDuckGo ne kuch nahi diya."
        except Exception as e:
            return f"❌ DuckDuckGo search mein error: {e}"

    # Prefix img/: fetch image URLs via DuckDuckGo image search
    elif text.startswith("img/ "):
        prompt = text[5:].strip()
        # First try g4f.Provider.bing if available
        if bing:
            try:
                imgs = bing.create_images(prompt)
                if imgs:
                    # show first image URL
                    return f"🖼️ Bing-image-provider se image:\n\n![image]({imgs[0]})"
                else:
                    # fallback to DuckDuckGo image search
                    pass
            except:
                # fallback below
                pass
        # DuckDuckGo image search fallback
        if DDGS and has_image_search:
            try:
                with DDGS() as ddgs:
                    # Some versions offer ddgs.images(query)
                    if hasattr(ddgs, "images"):
                        hits = list(ddgs.images(prompt, region='wt-wt', safesearch='Off', max_results=1))
                    elif hasattr(ddgs, "image"):
                        hits = list(ddgs.image(prompt, region='wt-wt', safesearch='Off', max_results=1))
                    else:
                        hits = []
                if hits:
                    # each hit may have 'image' or 'thumbnail'
                    url = hits[0].get('image') or hits[0].get('thumbnail') or hits[0].get('url')
                    if url:
                        return f"🖼️ DuckDuckGo se image:\n\n![image]({url})"
                return "❌ Koi image nahi mila duck se."
            except Exception as e:
                return f"❌ Duck image search error: {e}"
        else:
            return "❌ Image feature unavailable (no bing provider, no DDGS.image)."
    return None

# 🧠 Chat Handler
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    # use lowercase for prefix detection, but keep original for search text
    trig = handle_triggered_response(user_input.strip())
    if trig:
        response = add_sarcasm_emoji(trig)
    else:
        messages = [{"role": "system", "content": get_prompt()}] + st.session_state.chat_history
        raw = g4f.ChatCompletion.create(model=g4f.models.default, messages=messages, stream=False)
        response = raw if isinstance(raw, str) else raw.get("choices", [{}])[0].get("message", {}).get("content", "Arey kuch khaas nahi mila.")
        response = add_sarcasm_emoji(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# 💬 History
for msg in st.session_state.chat_history:
    role = "🌼" if msg["role"] == "user" else "🌀"
    st.chat_message(msg["role"], avatar=role).write(msg["content"])

# 🪟 Clear
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🪟", help="Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# 🏦 Footer
st.markdown(
    """
    <hr style='margin-top:40px;border:1px solid #444;'/>
    <div style='text-align:center; color:gray; font-size:13px;'>
        ⚡ Powered by <strong>Aman Chaudhary</strong> | Built with ❤️ & sarcasm
    </div>
    """,
    unsafe_allow_html=True
)
