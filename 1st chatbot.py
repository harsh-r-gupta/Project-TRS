import json
import random
import requests
import pyttsx3
import speech_recognition as sr
from datetime import datetime
from colorama import Fore, Style, init
import threading
import time
from rapidfuzz import fuzz

# Initialize colorama & text-to-speech
init()
engine = pyttsx3.init()

# Load or create data files
def load_json(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

user_data = load_json("user_data.json", {})
reminders = load_json("reminders.json", [])
notes = load_json("notes.json", [])

# Bot settings
API_KEY = "f53b477b98b19f6e74a16fe518181ff9"  # API key for current weather 
mood = "neutral"

# ---------------- Command Phrases ----------------
commands_map = load_json("commands.json", { #stores command phrases
    "add_note": ["add note", "make note", "create note", "write note", "jot down note"],
    "list_notes": ["list notes", "show notes", "display notes", "see notes"],
    "say_hi":["hi","hello","hey"],
    "search_notes": ["search note", "find note", "look for note"],
    "delete_note": ["delete note", "remove note", "erase note"],
    "add_reminder": ["add reminder", "set reminder", "make reminder", "create reminder"],
    "tell_joke": ["tell me a joke", "say a joke", "make me laugh"],
    "tell_fact": ["tell me about you", "say something about yourself", "introduce yourself"],
    "get_time": ["what time is it", "tell me the time", "current time"],
    "get_date": ["what's the date", "tell me the date", "current date"],
    "get_day": ["what day is it", "tell me the day", "current day"],
    "get_weather": ["weather in", "tell me the weather", "what's the weather"],
    "remember_info": ["remember this", "save this info", "store this"],
    "recall_info": ["do you remember", "recall info", "what do you remember"],
    "check_mood": ["how are you", "your mood", "current mood"],
    "exit": ["exit", "quit", "stop", "goodbye"]
})



# ---------------- Utility Functions ----------------
def match_command(user_text):
    best_match = None
    highest_score = 0
    for command, phrases in commands_map.items():
        for phrase in phrases:
            score = fuzz.token_set_ratio(user_text.lower(), phrase.lower())
            if score > highest_score:
                highest_score = score
                best_match = command
    if highest_score >= 60:
        return best_match
    return None

def learn_new_command(user_text):
    speak("I don't know how to respond to that.")
    speak("Do you want me to learn this phrase for an existing command? (yes/no)")
    ans = input("Yes or No: ").strip().lower()
    if ans == "yes":
        speak("Here are my existing commands:")
        for cmd in commands_map.keys():
            print(Fore.YELLOW + cmd + Style.RESET_ALL)
        cmd_choice = input("Enter the command you want this phrase to map to: ").strip()
        if cmd_choice in commands_map:
            commands_map[cmd_choice].append(user_text)
            with open("commands.json", "w") as f:
                json.dump(commands_map, f, indent=4)
            speak(f"Got it! '{user_text}' will now trigger {cmd_choice}.")
        else:
            speak("Invalid command choice.")
    else:
        speak("Alright, I won't learn it.")


# ---------------- Speech Functions ----------------
def speak(text):
    print(Fore.CYAN + "Bot: " + text + Style.RESET_ALL)
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(Fore.YELLOW + "Listening..." + Style.RESET_ALL)
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        print(Fore.GREEN + "You: " + query + Style.RESET_ALL)
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Speech service is down.")
        return ""
    

# ---------------- Bot Abilities ----------------
def tell_joke():
    jokes = [
        "Why don’t skeletons fight each other? Because they don’t have the guts.",
        "I told my computer I needed a break, and it said 'No problem, I’ll go to sleep!'",
        "Why was the math book sad? Because it had too many problems."
    ]
    speak(random.choice(jokes))

def tell_fact():
    facts = [
        "I was created in Python, which is one of the friendliest programming languages.",
        "I can talk, listen, and even remember details about you.","I am the first python project made by Harsh Raj Gupta.","I can perform several tasks for you, just tell me to do something."
        "My mood changes based on how you treat me!"
    ]
    speak(random.choice(facts))

def get_time():
    now = datetime.now()
    speak("The current time is " + now.strftime("%H:%M:%S"))

def get_date():
    now = datetime.now()
    speak("Today's date is " + now.strftime("%d %B %Y"))

def get_day():
    now = datetime.now()
    speak("Today is " + now.strftime("%A"))

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        speak(f"The temperature in {city} is {temp}°C with {desc}.")
    except:
        speak("Sorry, I couldn't get the weather for that location.")

def remember_info(key, value):
    user_data[key] = value
    with open("user_data.json", "w") as f:
        json.dump(user_data, f)
    speak(f"I'll remember that your {key} is {value}.")

def recall_info(key):
    if key in user_data:
        speak(f"Your {key} is {user_data[key]}.")
    else:
        speak(f"Sorry, I don't remember your {key}.")

# ---------------- Notes Functions ----------------
def add_note(content):
    notes.append(content)
    with open("notes.json", "w") as f:
        json.dump(notes, f)
    speak("Note added successfully.")

def list_notes():
    if notes:
        speak(f"You have {len(notes)} notes.")
        for i, note in enumerate(notes, start=1):
            print(Fore.YELLOW + f"{i}. {note}" + Style.RESET_ALL)
    else:
        speak("You have no notes.")

def search_notes(keyword):
    found = [note for note in notes if keyword.lower() in note.lower()]
    if found:
        speak(f"I found {len(found)} notes containing '{keyword}'.")
        for note in found:
            print(Fore.CYAN + note + Style.RESET_ALL)
    else:
        speak(f"No notes found containing '{keyword}'.")

def delete_note(index):
    try:
        removed = notes.pop(index - 1)
        with open("notes.json", "w") as f:
            json.dump(notes, f)
        speak(f"Deleted note: {removed}")
    except IndexError:
        speak("Invalid note number.")

# ---------------- Reminder Functions ----------------
def add_reminder(task, date_str, time_str):
    try:
        reminder_time = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
        reminders.append({"task": task, "time": reminder_time.strftime("%d-%m-%Y %H:%M")})
        with open("reminders.json", "w") as f:
            json.dump(reminders, f)
        speak(f"Reminder set for {task} on {date_str} at {time_str}.")
    except ValueError:
        speak("Invalid date or time format. Please use DD-MM-YYYY for date and HH:MM for time.")

def check_reminders():
    while True:
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        for reminder in reminders[:]:
            if reminder["time"] == now:
                speak(f"Reminder: {reminder['task']}")
                reminders.remove(reminder)
                with open("reminders.json", "w") as f:
                    json.dump(reminders, f)
        time.sleep(30)

# ---------------- Mood Tracking ----------------
def update_mood(user_text):
    global mood
    if any(word in user_text for word in ["thank", "good", "nice", "love"]):
        mood = "happy"
    elif any(word in user_text for word in ["bad", "hate", "angry", "stupid"]):
        mood = "sad"

# ---------------- Greeting ----------------
def greet_user():
    now = datetime.now()
    hour = now.hour
    if hour < 12:
        time_greeting = "Good morning"
    elif 12 <= hour < 18:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"

    if "name" in user_data:
        speak(f"{time_greeting}, {user_data['name']}! Nice to see you again.")
    else:
        speak(f"{time_greeting}! I don't think we have met before. What's your name?")
        name = input("Enter your name: ")
        user_data["name"] = name
        with open("user_data.json", "w") as f:
            json.dump(user_data, f)
        speak(f"Nice to meet you, {name}! I'll remember your name for next time.")

# ---------------- Main Chat Loop ----------------
def chatbot():
    threading.Thread(target=check_reminders, daemon=True).start()
    greet_user()
    speak("You can talk to me by voice or text.")

    while True:
        choice = input(Fore.MAGENTA + "Type 'voice' for voice mode or 'text' for typing: " + Style.RESET_ALL).lower()
        if choice in ["voice", "text"]:
            break

    while True:
        if choice == "voice":
            user_text = listen()
        else:
            user_text = input(Fore.GREEN + "You: " + Style.RESET_ALL).lower()

        update_mood(user_text)
        command = match_command(user_text)

        if command == "add_note":
            content = input("Enter your note: ")
            add_note(content)
        elif command == "list_notes":
            list_notes()

        elif command == "say_hi":
            print("hello, nice to meet you")

        elif command == "search_notes":
            keyword = input("Enter keyword to search: ")
            search_notes(keyword)
        elif command == "delete_note":
            list_notes()
            try:
                num = int(input("Enter note number to delete: "))
                delete_note(num)
            except ValueError:
                speak("Please enter a valid number.")
        elif command == "add_reminder":
            task = input("Enter the task: ")
            date_str = input("Enter date (DD-MM-YYYY): ")
            time_str = input("Enter time (HH:MM in 24-hour format): ")
            add_reminder(task, date_str, time_str)
        elif command == "tell_joke":
            tell_joke()
        elif command == "tell_fact":
            tell_fact()
        elif command == "get_time":
            get_time()
        elif command == "get_date":
            get_date()
        elif command == "get_day":
            get_day()
        elif command == "get_weather":
            # city = user_text.replace("weather of", "").strip()
            # if not city:
            city = input("Enter city name: ")
            get_weather(city)
        elif command == "remember_info":
            key = input("Enter the detail type (e.g., father's name, hobby): ")
            value = input(f"Enter your {key}: ")
            remember_info(key, value)
        elif command == "recall_info":
            key = input("Enter the detail you want me to recall: ")
            recall_info(key)
        elif command == "check_mood":
            speak(f"My mood is currently {mood}.")
        elif command == "exit":
            speak("Goodbye! Have a nice day.")
            break
        else:
            learn_new_command(user_text)

if __name__ == "__main__":
    chatbot()
