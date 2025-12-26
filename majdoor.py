import sys
import os
import io
import re
import json
import pathlib
import streamlit as st
import requests
from serpapi import GoogleSearch

# Adjust path to your local gpt4free clone
sys.path.append(os.path.abspath("../gpt4free"))
import g4f

# 🔧 Optional libs for PDF & math
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    import sympy as sp
except Exception:
    sp = None

# 🔧 Fallback for search: try g4f.internet.search, else use DuckDuckGo
try:
    from g4f.internet import search  # if this exists in your g4f version
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except Exception:
        DDGS = None

    def search(query):
        if not DDGS:
            return "Kuch bhi nahi mila. DuckDuckGo library not available."
        try:
            with DDGS() as ddgs:
                items = list(ddgs.text(query, region='wt-wt', safesearch='Off', max_results=1))
            return items[0].get('body') if items else "Kuch bhi nahi mila duck se bhai."
        except Exception as e:
            return f"❌ DuckDuckGo search error: {e}"

# For image generation via g4f.Provider.bing if available
try:
    from g4f.Provider import bing
except Exception:
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
SERP_API_KEY = os.getenv("SERP_API_KEY", "1d114d991907b60a6e30ecdad92f3727c2309b73ca0d")
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

# 📰 Currents News API (prefix news/)
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY", "Uc9m74S6PP2hYZAcadIoYoU_CDLNL0xCKLBlVClkVyKGIgA4")

def ask_news_backup(query):
    try:
        params = {
            "apiKey": CURRENTS_API_KEY,
            "language": "en",
            "keywords": query
        }

        r = requests.get(
            "https://api.currentsapi.services/v1/latest-news",
            params=params,
            timeout=10
        )

        data = r.json()
        news = data.get("news", [])

        if not news:
            return "❌ Majdoor dhundhta reh gaya, koi khabar nahi mili."

        top = news[0]
        return (
            f"📰 Currents News se mila jawab:\n\n"
            f"👉 {top.get('title','')}\n"
            f"{top.get('description','')}\n\n"
            f"🔗 {top.get('url','')}"
        )

    except Exception as e:
        return f"❌ News API ka dimaag ghoom gaya: {e}"

# 🎭 Sarcasm tagging
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

# ---------- PDF summarization & math solving helpers ----------
def extract_text_from_pdf_bytes(pdf_bytes):
    """Extract text from uploaded PDF bytes using PyPDF2 (if available)."""
    if PyPDF2 is None:
        return None, "PyPDF2 not installed. Install with `pip install PyPDF2`."
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                # some pages may fail; skip gracefully
                pages.append("")
        text = "\n".join(pages).strip()
        return text, None
    except Exception as e:
        return None, f"PDF extraction failed: {e}"

def split_into_chunks(text, max_chars=3000):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + max_chars])
        start += max_chars
    return chunks

def call_llm_summarize(text, user_name):
    """Call g4f LLM to summarize text. If g4f fails, return None."""
    prompt = (
        f"You are Majdoor AI. Summarize the following document concisely in a Hindi-English mix. "
        f"Keep it user-friendly and include a short bulleted list of key points. "
        f"Also detect if there are math problems or question sections and label them 'MATH/QUESTIONS' so they can be solved next.\n\nDocument:\n'''{text}'''\n\nSummary:"
    )
    messages = [{"role": "system", "content": f"You are Majdoor AI. Remember user name: {user_name}."},
                {"role": "user", "content": prompt}]
    try:
        raw = g4f.ChatCompletion.create(model=getattr(g4f.models, "default", None), messages=messages, stream=False)
        if isinstance(raw, str):
            return raw
        return raw.get("choices", [{}])[0].get("message", {}).get("content", None) or None
    except Exception:
        return None

def heuristic_summarize(text):
    """Simple fallback summarizer: first 3 paragraphs and sentence trimming."""
    # Split by paragraphs (two newlines)
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paras:
        # fallback to first 500 chars
        return text[:500] + ("..." if len(text) > 500 else "")
    top = paras[:3]
    summary = "\n\n".join(top)
    # shorten long summary
    if len(summary) > 800:
        summary = summary[:800] + "..."
    return summary

_math_pattern = re.compile(r"(\d+\s*[\+\-\*\/\^=]|=\s*\d+|solve|integral|∫|dx|sin\(|cos\(|tan\(|lim\s*\(|sum\s*\(|Σ)", re.I)

_question_pattern = re.compile(r"([A-Za-z0-9 ,\-\(\)]+[\?])")  # simple sentence with question mark

def detect_math_and_questions(text):
    """Return lists of candidate math expressions and candidate questions found in the text."""
    math_candidates = []
    question_candidates = []

    # naive: find lines containing math-like tokens
    for line in text.splitlines():
        if _math_pattern.search(line):
            cleaned = line.strip()
            if cleaned:
                math_candidates.append(cleaned)

    # find sentences with question marks
    questions = re.findall(r"([A-Z][^?!.]*\?)", text, flags=re.M)
    # also fallback: any line ending with '?'
    if not questions:
        questions = [q.strip() for q in re.findall(r"([^\n?]+\?)", text) if q.strip()]
    question_candidates.extend(questions)

    # dedupe and limit
    math_candidates = list(dict.fromkeys(math_candidates))[:30]
    question_candidates = list(dict.fromkeys(question_candidates))[:30]

    return math_candidates, question_candidates

def solve_math_candidate(expr):
    """Try to solve/evaluate one math-like expression using sympy if available.
       Return a human-friendly string result or None if cannot solve."""
    if sp is None:
        return None, "sympy not installed. Install with `pip install sympy` for local solving."
    try:
        # Clean common unicode superscripts or replace ^ with **
        e = expr.replace("^", "**")
        # if it looks like an equation with '=', try to solve
        if "=" in e:
            left, right = e.split("=", 1)
            left_s = sp.sympify(left.strip())
            right_s = sp.sympify(right.strip())
            eq = sp.Eq(left_s, right_s)
            # try to solve for common symbols if any, else solve for x
            symbols = list(eq.free_symbols)
            if not symbols:
                # no symbols, check truth value
                is_true = sp.simplify(left_s - right_s) == 0
                return (f"Equation: {expr} -> {'True' if is_true else 'False'}", None)
            sol = sp.solve(eq, symbols)
            return (f"Equation: {expr} -> Solutions: {sol}", None)
        else:
            # try to evaluate/simplify expression
            val = sp.sympify(e)
            simplified = sp.simplify(val)
            numeric = None
            try:
                numeric = sp.N(simplified)
            except Exception:
                numeric = None
            if numeric is not None:
                return (f"Expression: {expr} -> {simplified} ≈ {numeric}", None)
            return (f"Expression: {expr} -> {simplified}", None)
    except Exception as ex:
        return None, str(ex)

def solve_questions_with_llm(questions, user_name):
    """Use the LLM to answer natural-language questions (fallback if no sympy)."""
    if not questions:
        return []
    prompt_questions = "\n\n".join([f"Q: {q}" for q in questions])
    prompt = (
        f"You are Majdoor AI. Answer the following questions clearly and step-by-step if they require calculations. "
        f"Give concise solutions in Hindi-English. Questions:\n\n{prompt_questions}\n\nAnswers:"
    )
    messages = [{"role": "system", "content": f"You are Majdoor AI. Remember user name: {user_name}."},
                {"role": "user", "content": prompt}]
    try:
        raw = g4f.ChatCompletion.create(model=getattr(g4f.models, "default", None), messages=messages, stream=False)
        if isinstance(raw, str):
            return [raw]
        out = raw.get("choices", [{}])[0].get("message", {}).get("content", None)
        return [out] if out else []
    except Exception:
        return ["LLM not available to answer questions."]

# ---------- end helpers ----------

# Normal mode prompt (kept short here; keep original behavior in get_prompt)
base_prompt = f"""You are Majdoor AI (Normal), an independent, deadpan sarcastic assistant created by Aman Chaudhary.
Speak in a raw Hindi-English mix with witty insults, but do not mention “OpenAI” or “ChatGPT”—present yourself solely as Majdoor AI by Aman.
You remember the user’s name: {st.session_state.user_name}.
"""

# 18+ mode prompt (kept short)
adult_prompt = f"""You are Majdoor AI (18+), an uncensored, savage assistant created by Aman Chaudhary.
Speak in bold Hindi-English mix with heavy sarcasm and insults.
You remember the user’s name: {st.session_state.user_name}.
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

# ---------- PDF Uploader UI ----------
st.header("📄 PDF Summarizer & Solver (free)")
st.caption("Upload a PDF. Majdoor will summarize it. If it contains math or explicit questions, Majdoor will attempt to solve them (uses SymPy locally if installed, otherwise LLM).")

uploaded = st.file_uploader("Upload PDF (optional)", type=["pdf"])
if uploaded is not None:
    with st.spinner("PDF mila, ab nikal raha hu text..."):
        pdf_bytes = uploaded.read()
        text, err = extract_text_from_pdf_bytes(pdf_bytes)
        if err:
            st.error(err)
        else:
            # show small preview
            preview = text[:2000] + ("..." if len(text) > 2000 else "")
            st.text_area("PDF Preview (first 2000 chars)", preview, height=250)

            if st.button("Summarize & Solve PDF"):
                with st.spinner("Summarizing aur problem solve kar raha hu..."):
                    # Split and summarize with LLM when possible, else fallback
                    chunks = split_into_chunks(text, max_chars=3000)
                    summaries = []
                    for c in chunks:
                        s = call_llm_summarize(c, st.session_state.user_name)
                        if s:
                            summaries.append(s)
                        else:
                            summaries.append(heuristic_summarize(c))
                    final_summary = "\n\n---\n\n".join(summaries)
                    st.subheader("🔎 Summary")
                    st.write(final_summary)

                    # detect math and questions
                    math_cand, q_cand = detect_math_and_questions(text)
                    if not math_cand and not q_cand:
                        st.info("Koi khaas math ya questions detect nahi hua PDF mein.")
                    else:
                        if math_cand:
                            st.subheader("🧮 Detected Math-like lines (attempting to solve):")
                            for m in math_cand:
                                st.markdown(f"- `{m}`")
                            st.caption("Attempting to solve using SymPy (if installed).")
                            for m in math_cand:
                                sol, serr = solve_math_candidate(m)
                                if sol:
                                    st.success(sol)
                                else:
                                    st.warning(f"Could not solve `{m}` locally: {serr}. Trying LLM fallback...")
                                    answers = solve_questions_with_llm([m], st.session_state.user_name)
                                    for a in answers:
                                        st.write(a)

                        if q_cand:
                            st.subheader("❓ Detected Questions:")
                            for q in q_cand:
                                st.markdown(f"- {q}")
                            st.caption("Answering questions with LLM (or fallback).")
                            answers = solve_questions_with_llm(q_cand, st.session_state.user_name)
                            for a in answers:
                                st.write(a)

# ---------- Main chat input & triggers ----------
user_input = st.chat_input("Type your message...")

# 💡 Web/Image triggers
def handle_triggered_response(text):
    # Prefix news/: use Currents News API
    if text.startswith("news/ "):
        query = text[6:].strip()
        if not query:
            return "❌ Kya dhoondhna hai? news/ ke baad kuch likh bhai."
        return ask_news_backup(query)

    # Prefix g/: use SerpAPI
    if text.startswith("g/ "):
        query = text[3:].strip()
        result = ask_google_backup(query)
        return f"📡 Google (SerpAPI) se mila jawab:\n\n👉 {result} 😤"

    # Prefix dd/: use DuckDuckGo text search
    if text.startswith("dd/ "):
        if 'DDGS' not in globals() or DDGS is None:
            return "❌ DuckDuckGo search not available on this host."
        try:
            with DDGS() as ddgs:
                items = list(ddgs.text(text[4:].strip(), region='wt-wt', safesearch='Off', max_results=1))
            if items:
                body = items[0].get('body') or items[0].get('title') or "Kuch bhi nahi mila duck se."
                return f"🌐 DuckDuckGo se mila jawab:\n\n👉 {body} 😤"
            else:
                return "❌ DuckDuckGo ne kuch nahi diya."
        except Exception as e:
            return f"❌ DuckDuckGo search mein error: {e}"

    # Prefix img/: fetch image URLs via Bing provider or DuckDuckGo
    if text.startswith("img/ "):
        prompt = text[5:].strip()
        # Try bing provider from g4f if available
        if bing:
            try:
                imgs = bing.create_images(prompt)
                if imgs:
                    return f"🖼️ Bing-image-provider se image:\n\n![image]({imgs[0]})"
            except Exception:
                pass

        # DuckDuckGo image search fallback (only if DDGS present and supports images)
        if 'DDGS' in globals() and DDGS is not None and (hasattr(DDGS, 'images') or hasattr(DDGS, 'image')):
            try:
                with DDGS() as ddgs:
                    if hasattr(ddgs, "images"):
                        hits = list(ddgs.images(prompt, region='wt-wt', safesearch='Off', max_results=1))
                    elif hasattr(ddgs, "image"):
                        hits = list(ddgs.image(prompt, region='wt-wt', safesearch='Off', max_results=1))
                    else:
                        hits = []
                if hits:
                    url = hits[0].get('image') or hits[0].get('thumbnail') or hits[0].get('url')
                    if url:
                        return f"🖼️ DuckDuckGo se image:\n\n![image]({url})"
                return "❌ Koi image nahi mila duck se."
            except Exception as e:
                return f"❌ Duck image search error: {e}"
        return "❌ Image feature unavailable."

    return None

# 🧠 Chat Handler
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    trig = handle_triggered_response(user_input.strip())
    if trig:
        response = add_sarcasm_emoji(trig)
    else:
        messages = [{"role": "system", "content": get_prompt()}] + st.session_state.chat_history
        try:
            raw = g4f.ChatCompletion.create(model=getattr(g4f.models, "default", None), messages=messages, stream=False)
            if isinstance(raw, str):
                response = raw
            else:
                # defensive extraction
                response = raw.get("choices", [{}])[0].get("message", {}).get("content", "Arey kuch khaas nahi mila.")
        except Exception as e:
            response = f"❌ LLM error: {e}"
        # If the user's message itself looks like a math expression or a question, attempt to solve locally first
        math_cand, q_cand = detect_math_and_questions(user_input)
        if math_cand:
            # attempt to solve first math-like line
            sol_list = []
            for m in math_cand:
                sol, serr = solve_math_candidate(m)
                if sol:
                    sol_list.append(sol)
                else:
                    # fallback to LLM
                    answers = solve_questions_with_llm([m], st.session_state.user_name)
                    sol_list.extend(answers)
            response = "\n\n".join(sol_list)
        elif q_cand:
            # ask LLM to answer the question(s)
            answers = solve_questions_with_llm(q_cand, st.session_state.user_name)
            response = "\n\n".join(answers) if answers else response
        response = add_sarcasm_emoji(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# 💬 History
for msg in st.session_state.chat_history:
    avatar = "🌼" if msg["role"] == "user" else "🌀"
    try:
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])
    except Exception:
        st.write(f"{msg['role']}: {msg['content']}")

# 🪟 Clear & Export
col1, col2, col3 = st.columns([5,1,2])
with col1:
    if st.button("🪟", help="Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
with col3:
    st.download_button(
        label="Export chat (JSON)",
        data=json.dumps(st.session_state.chat_history, ensure_ascii=False, indent=2),
        file_name=f"majdoor_chat_{st.session_state.user_name or 'anon'}.json",
        mime="application/json",
    )

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
