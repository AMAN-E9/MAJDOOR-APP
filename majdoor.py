import sys, os, streamlit as st, requests 
import io
from PIL import Image
import wolframalpha  # pip install wolframalpha
from docext.extract import get_text_from_image

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
# 📂 APK Cleaner Feature Starts Here
from apk_modder_advanced import mod_apk
import os

st.markdown("---")
st.markdown("### 🔧 APK Cleaner - Majdoor AI")

apk_file = st.file_uploader("📂 Upload a Modded APK", type=["apk"])

if apk_file:
    st.success("📦 APK received. Starting deep cleaning... 🔍")

    input_path = "input.apk"
    with open(input_path, "wb") as f:
        f.write(apk_file.read())

    try:
        cleaned_apk = mod_apk(input_path)
        st.success("✅ APK cleaned successfully!")

        # 🛡️ Show trackers/logs if they exist
        if os.path.exists("detected_trackers.txt"):
            with open("detected_trackers.txt", "r") as log:
                logs = log.read()
            st.text_area("🛡️ Removed Trackers & Dangerous Permissions:", logs, height=200)
        else:
            st.info("No known trackers or malware found.")

        # 📥 Final download
        with open(cleaned_apk, "rb") as f:
            st.download_button("⬇️ Download Cleaned APK", f, file_name="Majdoor_Cleaned.apk")

    except Exception as e:
        st.error(f"❌ Cleaning failed: {e}")
# 📂 APK Cleaner Feature Ends Here
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
    response = raw if isinstance(raw, str) else raw.get("choices", [{}])[0].get("message", {}).get("content", "Arey kuch khaas nahi mila.")
    response = add_sarcasm_emoji(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
# 🔑 WolframAlpha API Key Setup
WOLFRAM_APPID = "TL2RRR-H227VPEX28"
client = wolframalpha.Client(WOLFRAM_APPID)

# 🧠 Wolfram Answer Function
def answer_wolfram(question):
    try:
        res = client.query(question)
        for pod in res.results:
            return pod.text  # ✔️ Correct indent
        return "❌ Kuch result nahi mila Wolfram se."
    except StopIteration:
        return "❌ Wolfram confuse ho gaya, kuch nahi mila."
    except Exception as e:
        return f"❌ Wolfram error: {e}"

# 🧠 Content Classifier: Math / Science / Document
def classify_ocr_content(text):
    t = text.lower()
    if any(op in text for op in ["+", "-", "*", "/", "=", "^", "√"]) and len(text) < 100:
        return "math"
    elif any(word in t for word in ["velocity", "mole", "reaction", "displacement", "gravity", "current", "joule", "newton", "molarity"]):
        return "science_problem"
    elif any(word in t for word in ["aadhar", "pan", "invoice", "certificate", "passport", "dob", "gender", "govt", "address"]):
        return "document"
    else:
        return "unknown"
# 👁️ Camera Toggle Button — full switch behavior
col1, col2 = st.columns([1, 6])
with col1:
  if "show_camera" not in st.session_state:
    st.session_state.show_camera = False

toggle_clicked = st.button("👁️", help="Click to toggle camera", key="camera_toggle")

if toggle_clicked:
    st.session_state.show_camera = not st.session_state.show_camera
# 🧠 Camera OCR Section + Smart Handling

if st.session_state.get("show_camera", False):
    st.markdown("## 📷 Photo se OCR aur MAJDOOR ki Bhasha")

    img = st.camera_input("📸 Kheench le photo jisme dard chhupa ho")

    if img is not None:
        st.image(img, caption="📸 Teri captured image", use_container_width=True)

        try:
            # 🖼️ Save image
            img_bytes = img.getvalue()
            img_pil = Image.open(io.BytesIO(img_bytes))
            img_pil.save("camera_input.png")

            # 🧾 OCR using docext
            extracted = get_text_from_image("camera_input.png")
            text = extracted.get("text", "").strip()

            if not text:
                st.warning("📄 Image me kuch likha hi nahi mila bhai.")
            else:
                st.success(f"🧾 MAJDOOR ne padha: `{text}`")
                ctype = classify_ocr_content(text)

                if ctype == "math":
                    st.info("📐 Math mila... Wolfram ko kaam pe lagaya")
                    answer = answer_wolfram(text)
                    st.success(f"📊 Jawab: `{answer}`")

                elif ctype == "science_problem":
                    st.info("🔬 Science ka jhanjhat... Wolfram se dard bhara jawab le")
                    answer = answer_wolfram(text)
                    st.success(f"📚 MAJDOOR ka dimaag: `{answer}`")

                elif ctype == "document":
                    st.info("📄 Lagta hai koi document hai... samjha jaa raha hai")

                    st.session_state.chat_history.append({"role": "user", "content": f"Yeh document hai:\n\n{text}\n\nYeh kis type ka document ho sakta hai aur isme kya likha hai?"})
                    messages = [{"role": "system", "content": get_prompt()}] + st.session_state.chat_history
                    raw = g4f.ChatCompletion.create(model=g4f.models.default, messages=messages, stream=False)
                    response = raw if isinstance(raw, str) else raw.get("choices", [{}])[0].get("message", {}).get("content", "Arey kuch khaas nahi mila.")
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.markdown(f"📃 MAJDOOR ne samjhaya:\n\n{response}")

                else:
                    st.info("😐 Kuch samajh nahi aaya... normal sarcasm response de raha hoon")
                    st.session_state.chat_history.append({"role": "user", "content": text})
                    messages = [{"role": "system", "content": get_prompt()}] + st.session_state.chat_history
                    raw = g4f.ChatCompletion.create(model=g4f.models.default, messages=messages, stream=False)
                    response = raw if isinstance(raw, str) else raw.get("choices", [{}])[0].get("message", {}).get("content", "Kuch khaas nahi mila.")
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.markdown(f"🤖 MAJDOOR: {response}")

        except Exception as e:
            st.error(f"❌ OCR ya answer fetch karte waqt error: {e}")

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

