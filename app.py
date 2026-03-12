import json
import random
import requests
import streamlit as st
from datetime import datetime
from rapidfuzz import fuzz
import os
from dotenv import load_dotenv
import threading
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Project ROMA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0a0f;
    color: #e8e8f0;
}

.stApp {
    background: #0a0a0f;
}

/* ── Animated background grid ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid rgba(99,102,241,0.2);
}

[data-testid="stSidebar"] * {
    color: #e8e8f0 !important;
}

/* ── Header ── */
.hero-header {
    text-align: center;
    padding: 2rem 0 1rem;
    position: relative;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 3rem;
    background: linear-gradient(135deg, #6366f1, #a78bfa, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin: 0;
}

.hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #6366f1;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
    50% { opacity: 0.8; box-shadow: 0 0 0 6px rgba(34,197,94,0); }
}

/* ── Chat container ── */
.chat-container {
    background: rgba(15, 15, 26, 0.8);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    min-height: 420px;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

/* ── Message bubbles ── */
.msg-bot {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 1rem;
    animation: fadeInLeft 0.3s ease;
}

.msg-user {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 1rem;
    flex-direction: row-reverse;
    animation: fadeInRight 0.3s ease;
}

@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-10px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes fadeInRight {
    from { opacity: 0; transform: translateX(10px); }
    to   { opacity: 1; transform: translateX(0); }
}

.avatar {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}

.avatar-bot { background: linear-gradient(135deg, #6366f1, #a78bfa); }
.avatar-user { background: linear-gradient(135deg, #06b6d4, #0891b2); }

.bubble {
    padding: 0.75rem 1rem;
    border-radius: 12px;
    max-width: 75%;
    font-size: 0.9rem;
    line-height: 1.5;
}

.bubble-bot {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    border-top-left-radius: 4px;
    color: #e8e8f0;
}

.bubble-user {
    background: rgba(6,182,212,0.12);
    border: 1px solid rgba(6,182,212,0.25);
    border-top-right-radius: 4px;
    color: #e8e8f0;
    text-align: right;
}

.timestamp {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #4b5563;
    margin-top: 4px;
}

/* ── Input area ── */
.stTextInput > div > div > input {
    background: rgba(15,15,26,0.9) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-family: 'Syne', sans-serif !important;
    padding: 0.75rem 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #a78bfa) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important;
}

/* ── Info cards ── */
.info-card {
    background: rgba(15,15,26,0.8);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.75rem;
}

.info-card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #6366f1;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Weather card ── */
.weather-card {
    background: linear-gradient(135deg, rgba(6,182,212,0.1), rgba(99,102,241,0.1));
    border: 1px solid rgba(6,182,212,0.3);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 0.75rem;
}

.weather-temp {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #06b6d4, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Note item ── */
.note-item {
    background: rgba(99,102,241,0.07);
    border-left: 3px solid #6366f1;
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 0.8rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
}

/* ── Reminder item ── */
.reminder-item {
    background: rgba(6,182,212,0.07);
    border-left: 3px solid #06b6d4;
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 0.8rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
}

/* ── Mood badge ── */
.mood-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'Space Mono', monospace;
}
.mood-happy  { background: rgba(34,197,94,0.15);  color: #22c55e;  border: 1px solid rgba(34,197,94,0.3);  }
.mood-sad    { background: rgba(239,68,68,0.15);   color: #ef4444;  border: 1px solid rgba(239,68,68,0.3);  }
.mood-neutral{ background: rgba(99,102,241,0.15);  color: #a78bfa;  border: 1px solid rgba(99,102,241,0.3); }

/* ── Divider ── */
hr { border-color: rgba(99,102,241,0.15) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 2px; }

/* ── Section labels ── */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #6366f1;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(99,102,241,0.2);
}
</style>
""", unsafe_allow_html=True)

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("API_KEY")

# ── JSON helpers ──────────────────────────────────────────────────────────────
def load_json(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# ── Session state init ────────────────────────────────────────────────────────
if "messages"  not in st.session_state: st.session_state.messages  = []
if "notes"     not in st.session_state: st.session_state.notes     = load_json("notes.json", [])
if "reminders" not in st.session_state: st.session_state.reminders = load_json("reminders.json", [])
if "user_data" not in st.session_state: st.session_state.user_data = load_json("user_data.json", {})
if "mood"      not in st.session_state: st.session_state.mood      = "neutral"
if "weather"   not in st.session_state: st.session_state.weather   = None
if "greeted"   not in st.session_state: st.session_state.greeted   = False

# ── Commands ──────────────────────────────────────────────────────────────────
commands_map = load_json("commands.json", {
    "add_note":      ["add note", "make note", "create note", "write note", "jot down note"],
    "list_notes":    ["list notes", "show notes", "display notes", "see notes"],
    "say_hi":        ["hi", "hello", "hey"],
    "search_notes":  ["search note", "find note", "look for note"],
    "delete_note":   ["delete note", "remove note", "erase note"],
    "add_reminder":  ["add reminder", "set reminder", "make reminder", "create reminder"],
    "tell_joke":     ["tell me a joke", "say a joke", "make me laugh"],
    "tell_fact":     ["tell me about you", "say something about yourself", "introduce yourself"],
    "get_time":      ["what time is it", "tell me the time", "current time"],
    "get_date":      ["what's the date", "tell me the date", "current date"],
    "get_day":       ["what day is it", "tell me the day", "current day"],
    "get_weather":   ["weather in", "tell me the weather", "what's the weather"],
    "remember_info": ["remember this", "save this info", "store this"],
    "recall_info":   ["do you remember", "recall info", "what do you remember"],
    "check_mood":    ["how are you", "your mood", "current mood"],
    "exit":          ["exit", "quit", "stop", "goodbye"]
})

def match_command(user_text):
    best_match, highest_score = None, 0
    for command, phrases in commands_map.items():
        for phrase in phrases:
            score = fuzz.token_set_ratio(user_text.lower(), phrase.lower())
            if score > highest_score:
                highest_score = score
                best_match = command
    return best_match if highest_score >= 60 else None

def update_mood(user_text):
    if any(w in user_text for w in ["thank", "good", "nice", "love"]):
        st.session_state.mood = "happy"
    elif any(w in user_text for w in ["bad", "hate", "angry", "stupid"]):
        st.session_state.mood = "sad"
    else:
        st.session_state.mood = "neutral"

def bot_reply(text):
    st.session_state.messages.append({
        "role": "bot", "text": text,
        "time": datetime.now().strftime("%H:%M")
    })

def user_msg(text):
    st.session_state.messages.append({
        "role": "user", "text": text,
        "time": datetime.now().strftime("%H:%M")
    })

# ── Bot logic ─────────────────────────────────────────────────────────────────
def process_command(user_text, extra={}):
    update_mood(user_text)
    command = match_command(user_text)

    if command == "say_hi":
        name = st.session_state.user_data.get("name", "there")
        bot_reply(f"Hey {name}! 👋 Great to see you.")

    elif command == "tell_joke":
        jokes = [
            "Why don't skeletons fight each other? They don't have the guts! 💀",
            "I told my computer I needed a break — it said 'No problem, going to sleep!' 💤",
            "Why was the math book sad? Too many problems. 📚"
        ]
        bot_reply(random.choice(jokes))

    elif command == "tell_fact":
        facts = [
            "I was built in Python by Harsh Raj Gupta — one of the friendliest languages around! 🐍",
            "I can remember details about you, set reminders, and even check the weather! 🌤️",
            "My mood changes based on how you talk to me. Be nice! 😊"
        ]
        bot_reply(random.choice(facts))

    elif command == "get_time":
        bot_reply(f"🕐 It's currently **{datetime.now().strftime('%H:%M:%S')}**")

    elif command == "get_date":
        bot_reply(f"📅 Today is **{datetime.now().strftime('%d %B %Y')}**")

    elif command == "get_day":
        bot_reply(f"📆 Today is **{datetime.now().strftime('%A')}**")

    elif command == "check_mood":
        mood_emoji = {"happy": "😄", "sad": "😔", "neutral": "😐"}
        bot_reply(f"My current mood is **{st.session_state.mood}** {mood_emoji.get(st.session_state.mood, '')}")

    elif command == "add_note":
        note = extra.get("note", "")
        if note:
            st.session_state.notes.append(note)
            save_json("notes.json", st.session_state.notes)
            bot_reply(f"📝 Note saved: *\"{note}\"*")
        else:
            bot_reply("📝 What should I note down? Use the **Add Note** panel on the left.")

    elif command == "list_notes":
        if st.session_state.notes:
            notes_list = "\n".join([f"{i+1}. {n}" for i, n in enumerate(st.session_state.notes)])
            bot_reply(f"📋 Your notes:\n{notes_list}")
        else:
            bot_reply("You have no notes yet!")

    elif command == "add_reminder":
        bot_reply("⏰ Use the **Add Reminder** panel on the left to set a reminder!")

    elif command == "get_weather":
        city = extra.get("city", "")
        if city:
            fetch_weather(city)
        else:
            bot_reply("🌤️ Enter a city in the **Weather** panel on the left!")

    elif command == "remember_info":
        key   = extra.get("key", "")
        value = extra.get("value", "")
        if key and value:
            st.session_state.user_data[key] = value
            save_json("user_data.json", st.session_state.user_data)
            bot_reply(f"🧠 Got it! I'll remember your **{key}** is **{value}**.")
        else:
            bot_reply("🧠 Tell me what to remember using the **Remember** panel!")

    elif command == "recall_info":
        key = extra.get("key", "")
        if key and key in st.session_state.user_data:
            bot_reply(f"🧠 Your **{key}** is **{st.session_state.user_data[key]}**.")
        elif key:
            bot_reply(f"Hmm, I don't have your **{key}** saved.")
        else:
            bot_reply("What detail would you like me to recall?")

    elif command == "exit":
        bot_reply("👋 Goodbye! See you soon.")

    else:
        bot_reply("Hmm, I'm not sure how to respond to that. Try asking me the time, weather, a joke, or managing your notes! 🤔")

def fetch_weather(city):
    if not API_KEY:
        bot_reply("⚠️ No API key found. Add `API_KEY` to your `.env` file.")
        return
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url).json()
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        humidity = response["main"]["humidity"]
        st.session_state.weather = {"city": city, "temp": temp, "desc": desc, "humidity": humidity}
        bot_reply(f"🌤️ **{city}**: {temp}°C, {desc}. Humidity: {humidity}%")
    except Exception as e:
        bot_reply(f"❌ Couldn't fetch weather for '{city}'.")

# ── Greeting ──────────────────────────────────────────────────────────────────
if not st.session_state.greeted:
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    name = st.session_state.user_data.get("name", None)
    if name:
        bot_reply(f"{greeting}, **{name}**! 👋 I'm Project ROMA, your AI assistant. How can I help you today?")
    else:
        bot_reply(f"{greeting}! 👋 I'm **Project ROMA**, your personal AI assistant. What's your name?")
    st.session_state.greeted = True

# ════════════════════════════════════════════════════════════════════════════
#  LAYOUT
# ════════════════════════════════════════════════════════════════════════════

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 1rem 0 0.5rem;'>
            <div style='font-size:2.5rem'>🤖</div>
            <div style='font-family:Syne,sans-serif; font-weight:800; font-size:1.3rem;
                        background:linear-gradient(135deg,#6366f1,#a78bfa);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
                Project ROMA
            </div>
            <div style='font-family:Space Mono,monospace; font-size:0.6rem;
                        color:#6366f1; letter-spacing:3px; margin-top:2px;'>
                PERSONAL AI ASSISTANT
            </div>
        </div>
        <hr style='border-color:rgba(99,102,241,0.2); margin: 0.75rem 0;'/>
    """, unsafe_allow_html=True)

    # ── User name ──
    st.markdown("<div class='section-label'>👤 Profile</div>", unsafe_allow_html=True)
    name_input = st.text_input("Your name", value=st.session_state.user_data.get("name", ""), placeholder="Enter your name...")
    if name_input and name_input != st.session_state.user_data.get("name"):
        st.session_state.user_data["name"] = name_input
        save_json("user_data.json", st.session_state.user_data)

    # ── Mood ──
    mood_class = f"mood-{st.session_state.mood}"
    mood_emoji = {"happy": "😄", "sad": "😔", "neutral": "😐"}
    st.markdown(f"""
        <div style='margin: 0.5rem 0 1rem;'>
            Mood: <span class='mood-badge {mood_class}'>
                {mood_emoji.get(st.session_state.mood,'')} {st.session_state.mood.upper()}
            </span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(99,102,241,0.15);'/>", unsafe_allow_html=True)

    # ── Weather ──
    st.markdown("<div class='section-label'>🌤️ Weather</div>", unsafe_allow_html=True)
    weather_city = st.text_input("City", placeholder="e.g. Mumbai", label_visibility="collapsed")
    if st.button("Get Weather", use_container_width=True):
        if weather_city:
            fetch_weather(weather_city)
            st.rerun()

    if st.session_state.weather:
        w = st.session_state.weather
        st.markdown(f"""
            <div class='weather-card'>
                <div style='font-size:0.75rem; color:#6366f1; letter-spacing:2px; font-family:Space Mono,monospace;'>
                    {w['city'].upper()}
                </div>
                <div class='weather-temp'>{w['temp']}°C</div>
                <div style='color:#a0aec0; font-size:0.85rem;'>{w['desc'].title()}</div>
                <div style='color:#4b5563; font-size:0.75rem; margin-top:4px;'>💧 {w['humidity']}% humidity</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(99,102,241,0.15);'/>", unsafe_allow_html=True)

    # ── Notes ──
    st.markdown("<div class='section-label'>📝 Notes</div>", unsafe_allow_html=True)
    new_note = st.text_area("New note", placeholder="Write something...", height=80, label_visibility="collapsed")
    if st.button("Add Note", use_container_width=True):
        if new_note.strip():
            st.session_state.notes.append(new_note.strip())
            save_json("notes.json", st.session_state.notes)
            bot_reply(f"📝 Note saved: *\"{new_note.strip()}\"*")
            st.rerun()

    if st.session_state.notes:
        for i, note in enumerate(st.session_state.notes):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"<div class='note-item'>{note}</div>", unsafe_allow_html=True)
            with col2:
                if st.button("✕", key=f"del_note_{i}"):
                    st.session_state.notes.pop(i)
                    save_json("notes.json", st.session_state.notes)
                    st.rerun()
    else:
        st.markdown("<div style='color:#4b5563; font-size:0.8rem; font-style:italic;'>No notes yet</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(99,102,241,0.15);'/>", unsafe_allow_html=True)

    # ── Reminders ──
    st.markdown("<div class='section-label'>⏰ Reminders</div>", unsafe_allow_html=True)
    rem_task = st.text_input("Task", placeholder="Reminder task...", key="rem_task")
    rem_date = st.date_input("Date", key="rem_date")
    rem_time = st.time_input("Time", key="rem_time")
    if st.button("Set Reminder", use_container_width=True):
        if rem_task:
            reminder = {
                "task": rem_task,
                "time": f"{rem_date.strftime('%d-%m-%Y')} {rem_time.strftime('%H:%M')}"
            }
            st.session_state.reminders.append(reminder)
            save_json("reminders.json", st.session_state.reminders)
            bot_reply(f"⏰ Reminder set: **{rem_task}** on {reminder['time']}")
            st.rerun()

    if st.session_state.reminders:
        for i, rem in enumerate(st.session_state.reminders):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                    <div class='reminder-item'>
                        <b>{rem['task']}</b><br>
                        <span style='color:#06b6d4; font-size:0.75rem;'>{rem['time']}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✕", key=f"del_rem_{i}"):
                    st.session_state.reminders.pop(i)
                    save_json("reminders.json", st.session_state.reminders)
                    st.rerun()
    else:
        st.markdown("<div style='color:#4b5563; font-size:0.8rem; font-style:italic;'>No reminders set</div>", unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
    <div class='hero-header'>
        <div class='hero-title'>Project ROMA AI</div>
        <div class='hero-sub'><span class='status-dot'></span>Online & Ready</div>
    </div>
""", unsafe_allow_html=True)

# ── DateTime strip ──
now = datetime.now()
col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    st.markdown(f"""<div class='info-card' style='text-align:center;'>
        <div class='info-card-title'>Time</div>
        <div style='font-size:1.4rem; font-weight:800; font-family:Space Mono,monospace;
                    color:#a78bfa;'>{now.strftime('%H:%M')}</div>
    </div>""", unsafe_allow_html=True)
with col_t2:
    st.markdown(f"""<div class='info-card' style='text-align:center;'>
        <div class='info-card-title'>Date</div>
        <div style='font-size:1rem; font-weight:700; color:#06b6d4;'>{now.strftime('%d %B %Y')}</div>
    </div>""", unsafe_allow_html=True)
with col_t3:
    st.markdown(f"""<div class='info-card' style='text-align:center;'>
        <div class='info-card-title'>Day</div>
        <div style='font-size:1rem; font-weight:700; color:#6366f1;'>{now.strftime('%A')}</div>
    </div>""", unsafe_allow_html=True)

# ── Chat window ──
chat_html = "<div class='chat-container'>"
for msg in st.session_state.messages:
    if msg["role"] == "bot":
        chat_html += f"""
        <div class='msg-bot'>
            <div class='avatar avatar-bot'>🤖</div>
            <div>
                <div class='bubble bubble-bot'>{msg['text']}</div>
                <div class='timestamp'>{msg['time']}</div>
            </div>
        </div>"""
    else:
        chat_html += f"""
        <div class='msg-user'>
            <div class='avatar avatar-user'>👤</div>
            <div>
                <div class='bubble bubble-user'>{msg['text']}</div>
                <div class='timestamp'>{msg['time']}</div>
            </div>
        </div>"""
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ── Input row ──
col_input, col_send = st.columns([6, 1])
with col_input:
    user_input = st.text_input(
        "message", placeholder="Type a message... (try: tell me a joke, what time is it, add note)",
        label_visibility="collapsed", key="chat_input"
    )
with col_send:
    send = st.button("Send ➤", use_container_width=True)

if send and user_input.strip():
    user_msg(user_input.strip())
    process_command(user_input.strip())
    st.rerun()

# ── Quick action chips ──
st.markdown("<div style='margin-top:0.5rem; display:flex; gap:0.5rem; flex-wrap:wrap;'>", unsafe_allow_html=True)
quick_cols = st.columns(5)
quick_actions = ["Tell me a joke 😂", "What time is it? 🕐", "How are you? 😊", "Introduce yourself 🤖", "What's today? 📅"]
for i, action in enumerate(quick_actions):
    with quick_cols[i]:
        if st.button(action, key=f"quick_{i}", use_container_width=True):
            user_msg(action)
            process_command(action)
            st.rerun()