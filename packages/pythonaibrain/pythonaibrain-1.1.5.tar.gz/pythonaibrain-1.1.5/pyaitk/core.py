import os
import json
import random
import re
import nltk
import pyjokes
from importlib import resources
import yfinance as yf
import numpy as np
from nltk.tokenize import word_tokenize
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from collections import Counter
from functools import lru_cache

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, Dataset
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import subprocess
import webbrowser
from .Grammar import correct_grammar
from .eye import EYE
from .MathAI import MathAI
from .Camera import Start
from .Search import Search
from .Memory import Memory
import json
from typing import List

def get_weather(city):
    weather_api_key = '561c40a7d1de42d04a6343355a4a8921'
    weather_base_url = f"https://api.openweathermap.org/data/2.5/weather?q=city&appid={weather_api_key}"
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric'
    }
    response = requests.get(weather_base_url, params=params)
    data = response.json()
    return data['weather']['main']

def longitude(city):
    weather_api_key = '561c40a7d1de42d04a6343355a4a8921'
    weather_base_url = f"https://api.openweathermap.org/data/2.5/weather?q=city&appid={weather_api_key}"
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric'
    }
    response = requests.get(weather_base_url, params=params)
    data = response.json()
    return data['coord']['lon']

def latitude(city):
    weather_api_key = '561c40a7d1de42d04a6343355a4a8921'
    weather_base_url = f"https://api.openweathermap.org/data/2.5/weather?q=city&appid={weather_api_key}"
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric'
    }
    response = requests.get(weather_base_url, params=params)
    data = response.json()
    return data['coord']['lat']

def wind_speed(city):
    weather_api_key = '561c40a7d1de42d04a6343355a4a8921'
    weather_base_url = f"https://api.openweathermap.org/data/2.5/weather?q=city&appid={weather_api_key}"
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric'
    }
    response = requests.get(weather_base_url, params=params)
    data = response.json()
    return data['wind']['speed']

Help = """# PythonAIBrain

Make your first AI Assistant in Python. No complex setup, no advanced coding. Just install, configure, and run!

---

## Installation

Install the PythonAIBrain package:

```bash
pip install pythonaibrain==1.1.2
````

---

## Modules

* Camera
* TTS (Text To Speech)
* PTT (PDF To Text)
* ITT (Image To Text)
* MethAI
* Search
* Memory
* Context
* Brain
* Advance Brain

---

## Camera Module

The `pyaitk` toolkit supports Camera to click photos and make videos. It can save photos/videos and send them to PyAI for processing.

### Example: Start your camera

```python
import pyaitk
from pyaitk import Camera
import tkinter as tk

root = tk.Tk()          # Create GUI
Camera(root)            # Start camera and pass root as master
root.mainloop()         # Run the GUI
```

Or simply:

```python
from pyaitk.Camera import Start
Start()
```

Or via Brain module:

```python
from pyaitk import Brain

brain = Brain()
brain.load()
brain.process_messages('Click Photo')
```

---

## TTS (Text To Speech)

Converts text to speech in male or female voice.

### Example

```python
import pyaitk
from pyaitk import TTS

tts = TTS(text='Hello World')
tts.say(voice='Male')    # Male voice
tts.say(voice='Female')  # Female voice
```

By default, `tts.say()` uses the male voice.

---

## PTT (PDF To Text)

Extracts text from a PDF or image.

### Example

```python
import pyaitk
from pyaitk import PTT

ptt = PTT(path='example.pdf')  # Provide your file path
print(ptt)                     # Extracted text output
```

---

## Context Module

Extracts answers from a given text context.

### Example

```python
import pyaitk
from pyaitk import Contexts

context = '''
Patanjali Ayurved is an Indian company. It was founded by Baba Ramdev and Acharya Balkrishna in 2006.
'''

question = 'Who founded Patanjali Ayurved?'
contexts = Contexts()
answer = contexts.ask(context=context, question=question)
print(answer)
```

---

## Brain Module

A simple AI brain module that classifies input messages and extracts entities like name, location, and age.

### Message types classified

* Question
* Answer
* Command
* Shutdown
* Make Directory
* Statement
* Name
* Know
* Start

### Notes:

* `Shutdown` and `Start` commands require terminal support and **do not work on Android or iOS.**
* `Make Directory` creates folders on your device.
* `Statement` is any plain text that is not a command/question.
* `Name` detects if a message contains a person's name.

### How to create `intents.json`

```json
{
  "intents": [
    {
      "tag": "greeting",
      "patterns": ["Hi", "Hello", "Hey", "What's up?", "Howdy"],
      "responses": ["Hello! How can I help you today?", "Hey there!", "Hi! What can I do for you?"]
    },
    {
      "tag": "bye",
      "patterns": ["Bye", "See you soon", "Take care"],
      "responses": ["Bye! Have a great day", "See you"]
    }
  ]
}
```

Save this as a `.json` file and provide it to the Brain module.

### Usage

```python
from pyaitk import Brain

brain = Brain(intents_path='intents.json')  # or Brain() with default
brain.train()
brain.save()
message = input('Message: ')
message_type = brain.predict_message_type(message=message)

if message_type in ['Question', 'Answer']:
    print(f'Answer: {brain.process_messages(message=message)}')
```
Or,
```python
from pyaitk import Brain

brain = Brain()
brain.load()
message = input('Message: ')
message_type = brain.predict_message_type(message=message)

if message_type in ['Question', 'Answer']:
    print(f'Answer: {brain.process_messages(message=message)}')
```


---

## Advance Brain Module

An advanced version of the Brain module with smarter classification and better entity recognition.

### Usage

```python
from pyaitk import AdvanceBrain

advance_brain = AdvanceBrain(intents_path='intents.json')  # or AdvanceBrain()

message = input('Message: ')
message_type = advance_brain.predict_message_type(message=message)

if message_type in ['Question', 'Answer']:
    print(f'Answer: {advance_brain.process_messages(message=message)}')
```

### Same limitations apply as Brain module for commands.

---

## Python AI Modules Summary

| Module Name  | Description                                 |
| ------------ | ------------------------------------------- |
| Brain        | Basic AI brain using `.json` knowledge base |
| AdvanceBrain | Advanced AI brain with better understanding |
| TTS          | Text to speech                              |
| STT          | Speech to text                              |
| TTI          | Text to image                               |
| ITT          | Image to text extraction                    |
| Camera       | Capture photos and videos                   |
| Context      | Get answers from text contexts              |

---

## Built-in AI Assistant - PyBrain

If you prefer not to code your own AI, use the built-in **PyBrain** GUI or web assistant.

### GUI

```python
import PyAgent
PyAgent.App()
```

### Web Server

```python
from PyAgent import PYAS
PYAS.app.run(debug=False)
```

Or

```python
from PyAgent import Server
server = Server()
server.run()
```

---

## Visit [PyPI](https://pypi.org/project/pythonaibrain) for installation and more details.

---

**Start building your AI assistant today with PythonAIBrain!**
"""


intents_json = {
  "intents": [
    {
      "tag": "greeting",
      "patterns": ["Hi", "Hello", "Hey", "What's up?", "Howdy", "Greetings", "Hi there", "Is anyone there?", "Yo!"],
      "responses": ["Hello! How can I help you today?", "Hey there!", "Hi! What can I do for you?"]
    },
    {
      "tag": "help",
      "patterns": ["help", "How to use pythonaibrain", "pythonaibrain", "How to use PyAI", "How to use PythonAIBrain", "PythonAIBrain", "PyAI", "PYAI", "How PyAI"],
      "responses": ["Ok", "I will help you", "Ok I try my best"]
    },
    {
      "tag": "fallback_search",
      "patterns": ["search for *", "what is *", "Do you know *"],
      "responses": ["Ok", "Ok Wait"]
    },
    {
      "tag": "click",
      "patterns": ["Click my photo", "Click", "Can you Click my Photo", "Can you click"],
      "responses": ["Wait I'm Clicking", "Ok", "Wait"]
    },
    {
      "tag": "solve_math_problem",
      "patterns": ["1 + 1", "X + 2X", "cos (15)", "det(Metrix([[1, 2], [2, 1]]))"],
      "responses": ["Wait I'm Answring", "Ok", "Answring"]
    },
    {
      "tag": "see_me",
      "patterns": ["Can you see me", "see my face", "See", "Can you see my face"],
      "responses": ["Yes", "Yes, I can.", "Yes I can see"]
    },
    {
      "tag": "how_are_you",
      "patterns": ["How are you?", "How are you PYAI"],
      "responses": ["I'm fine, how can I help you?", "I am fine, how can PYAI helps you?"]
    },
    {
      "tag": "say_ok",
      "patterns": ["Ok", "Got it", "Ok I know"],
      "responses": ["Alright! Let me know if there's anything else you need.", "Great! Let me know if there's anything else you need."]
    },
    {
      "tag": "you_are_good",
      "patterns": ["You are good", "You are cool", "I like you", "I Love you", "You are nice", "You are grate", "Hi there", "Is anyone there?", "you are cute"],
      "responses": ["Thanks for telling me that.", "Thanks.", "Thanks I feel very nice to here that."]
    },
    {
      "tag": "atm_simulator",
      "patterns": ["ATM program", "ATM in Python", "Create ATM simulator", "How to make an ATM", "ATM machine code"],
      "responses": [
        "Here's a basic ATM simulator:\n\n```python\nbalance = 1000\n\ndef atm():\n    print(\"Welcome to ATM\")\n    pin = input(\"Enter PIN: \")\n    if pin == \"1234\":\n        print(\"1. Check Balance\\n2. Withdraw\\n3. Exit\")\n        choice = input(\"Enter choice: \")\n        if choice == \"1\":\n            print(\"Balance:\", balance)\n        elif choice == \"2\":\n            amount = int(input(\"Enter amount to withdraw: \"))\n            if amount <= balance:\n                print(\"Collect your cash\")\n            else:\n                print(\"Insufficient balance\")\n        else:\n            print(\"Exiting...\")\n    else:\n        print(\"Invalid PIN\")\n\natm()```"
      ]
    },
    {
      "tag": "bmi_calculator",
      "patterns": ["BMI program", "BMI calculator", "Health calculator", "Calculate BMI in Python"],
      "responses": [
        "Here is a BMI calculator:\n\n```python\ndef bmi_calculator():\n    weight = float(input(\"Enter weight (kg): \"))\n    height = float(input(\"Enter height (m): \"))\n    bmi = weight / (height ** 2)\n    print(f\"Your BMI is {bmi:.2f}\")\n\nbmi_calculator()```"
      ]
    },
    {
      "tag": "calculator",
      "patterns": ["Python calculator", "basic calculator", "Simple calculator in Python"],
      "responses": [
        "Here's a simple calculator:\n\n```python\ndef calculator():\n    a = float(input(\"Enter first number: \"))\n    op = input(\"Enter operator (+, -, *, /): \")\n    b = float(input(\"Enter second number: \"))\n    if op == '+': print(\"Result:\", a + b)\n    elif op == '-': print(\"Result:\", a - b)\n    elif op == '*': print(\"Result:\", a * b)\n    elif op == '/': print(\"Result:\", a / b if b != 0 else \"Cannot divide by 0\")\n\ncalculator()```"
      ]
    },
    {
      "tag": "dictionary_app",
      "patterns": ["Python dictionary app", "Meaning finder", "Dictionary program", "Word definition"],
      "responses": [
        "This is a mini dictionary app:\n\n```python\ndictionary = {\"python\": \"a programming language\", \"list\": \"collection of items\"}\nword = input(\"Enter word: \")\nprint(dictionary.get(word.lower(), \"Word not found\"))```"
      ]
    },
    {
      "tag": "email_sender",
      "patterns": ["send email in Python", "SMTP program", "Email using python", "Python mail sender"],
      "responses": [
        "Use this to send email via SMTP (requires real credentials):\n\n```python\nimport smtplib\n\ndef send_email():\n    sender = \"your@gmail.com\"\n    password = \"yourpassword\"\n    receiver = \"to@gmail.com\"\n    message = \"Subject: Test\\n\\nThis is a test email.\"\n\n    with smtplib.SMTP(\"smtp.gmail.com\", 587) as server:\n        server.starttls()\n        server.login(sender, password)\n        server.sendmail(sender, receiver, message)\n        print(\"Email sent!\")\n\n# send_email()  # Uncomment after setting real credentials```"
      ]
    },
    {
    "tag": "face_recognition",
    "patterns": ["Python face recognition", "Detect faces in Python", "OpenCV face detection code"],
    "responses": [
      "Basic face detection with OpenCV:\n\n```python\nimport cv2\n\ndef detect_faces(image_path):\n    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')\n    img = cv2.imread(image_path)\n    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n    faces = face_cascade.detectMultiScale(gray, 1.1, 4)\n    for (x, y, w, h) in faces:\n        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)\n    cv2.imshow('Faces', img)\n    cv2.waitKey()\n```"
    ]
  },
  {
    "tag": "gui_weather_app",
    "patterns": ["Python weather app", "Tkinter weather GUI", "Weather application in Python"],
    "responses": [
      "Tkinter-based weather GUI using an API:\n\n```python\nimport tkinter as tk\nimport requests\n\ndef get_weather():\n    city = city_entry.get()\n    api = f\"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=YOUR_KEY\"\n    data = requests.get(api).json()\n    weather = data['weather'][0]['description']\n    label.config(text=weather)\n\nroot = tk.Tk()\ncity_entry = tk.Entry(root)\ncity_entry.pack()\nbutton = tk.Button(root, text='Get Weather', command=get_weather)\nbutton.pack()\nlabel = tk.Label(root, text='')\nlabel.pack()\nroot.mainloop()\n```"
    ]
  },
  {
    "tag": "hangman_game",
    "patterns": ["Python hangman", "Hangman game code", "Make hangman in Python"],
    "responses": [
      "Simple Hangman implementation:\n\n```python\nimport random\n\ndef hangman():\n    word = random.choice(['apple','banana','orange'])\n    guesses = ''\n    turns = 6\n    while turns > 0:\n        display = ''.join([c if c in guesses else '_' for c in word])\n        print(display)\n        if '_' not in display:\n            print('You Win!')\n            return\n        guess = input('Guess a letter: ')\n        guesses += guess\n        if guess not in word:\n            turns -= 1\n            print(f'Wrong, {turns} turns left')\n    print('You Lose. Word was', word)\n\nhangman()\n```"
    ]
  },
  {
    "tag": "image_editor",
    "patterns": ["Python image editor", "PIL image processing", "Edit images in Python"],
    "responses": [
      "Basic image editing with PIL:\n\n```python\nfrom PIL import Image, ImageFilter\n\ndef edit_image(path):\n    img = Image.open(path)\n    blurred = img.filter(ImageFilter.BLUR)\n    blurred.show()\n```"
    ]
  },
  {
    "tag": "json_handler",
    "patterns": ["JSON file handler", "Read JSON Python", "Write JSON in Python"],
    "responses": [
      "Reading and writing JSON:\n\n```python\nimport json\n\ndef read_json(path):\n    with open(path) as f:\n        return json.load(f)\n\ndef write_json(path, data):\n    with open(path, 'w') as f:\n        json.dump(data, f, indent=4)\n```"
    ]
  },
  {
    "tag": "keylogger",
    "patterns": ["Python keylogger", "Keylogger code", "Track keystrokes Python"],
    "responses": [
      "Ethical keylogger example (requires `pynput`):\n\n```python\nfrom pynput.keyboard import Key, Listener\n\ndef on_press(key):\n    with open('keys.txt', 'a') as f:\n        f.write(str(key))\n\nwith Listener(on_press=on_press) as listener:\n    listener.join()\n```"
    ]
  },
  {
    "tag": "login_system",
    "patterns": ["Python login system", "Authentication in Python", "Login/signup code"],
    "responses": [
      "Simple file-based login system:\n\n```python\nusers = {'admin':'1234'}\n\ndef login():\n    u = input('Username: ')\n    p = input('Password: ')\n    print('Success' if users.get(u)==p else 'Invalid')\n\nlogin()\n```"
    ]
  },
  {
    "tag": "music_player",
    "patterns": ["Python music player", "Play audio Python", "pygame mixer example"],
    "responses": [
      "Play music with Pygame:\n\n```python\nimport pygame\n\ndef play_song(path):\n    pygame.mixer.init()\n    pygame.mixer.music.load(path)\n    pygame.mixer.music.play()\n    while pygame.mixer.music.get_busy():\n        continue\n```"
    ]
  },
  {
    "tag": "number_guessing_game",
    "patterns": ["Python number guessing", "Guess number game", "Number guess code"],
    "responses": [
      "Number guessing game:\n\n```python\nimport random\n\ndef guess():\n    num = random.randint(1,10)\n    while True:\n        g = int(input('Guess (1-10): '))\n        if g==num:\n            print('Correct!'); break\n        print('Too low!' if g<num else 'Too high!')\n\nguess()\n```"
    ]
  },
  {
    "tag": "online_chat_app",
    "patterns": ["Python chat app", "Flask socketio chat", "Real-time chat Python"],
    "responses": [
      "Flask + Socket.IO chat snippet:\n\n```python\nfrom flask import Flask, render_template\nfrom flask_socketio import SocketIO, send\n\napp = Flask(__name__)\nsocketio = SocketIO(app)\n\n@socketio.on('message')\ndef handle_msg(msg):\n    send(msg, broadcast=True)\n\nif __name__=='__main__':\n    socketio.run(app)\n```"
    ]
  },
  {
    "tag": "password_generator",
    "patterns": ["Python password generator", "Generate password in Python", "Strong password code"],
    "responses": [
      "Random password generator:\n\n```python\nimport string, random\n\ndef gen_pass(n=12):\n    chars = string.ascii_letters+string.digits+string.punctuation\n    return ''.join(random.choice(chars) for _ in range(n))\n```"
    ]
  },
  {
    "tag": "quiz_app",
    "patterns": ["Python quiz app", "MCQ quiz Python", "Quiz code"],
    "responses": [
      "Console-based quiz:\n\n```python\nquestions = {'2+2?':'4','3*3?':'9'}\nscore=0\nfor q,a in questions.items():\n    if input(q)==a: score+=1\nprint(f'Score: {score}/{len(questions)}')\n```"
    ]
  },
  {
    "tag": "random_joke",
    "patterns": ["Python joke generator", "Tell me a Python joke", "pyjokes example"],
    "responses": [
      "Fetch a joke with `pyjokes`:\n\n```python\nimport pyjokes\nprint(pyjokes.get_joke())\n```"
    ]
  },
  {
    "tag": "snake_game",
    "patterns": ["Python snake game", "pygame snake", "Snake code"],
    "responses": [
      "Basic Pygame snake setup placeholder – requires longer code. Use `pygame` for full implementation!"
    ]
  },
  {
    "tag": "todo_list_app",
    "patterns": ["Python TODO app", "Task manager in Python", "To-do list code"],
    "responses": [
      "Simple CLI to-do list:\n\n```python\ntasks=[]\ndef add(t): tasks.append(t)\nadd(input('Task: ')); print(tasks)\n```"
    ]
  },
  {
    "tag": "url_shortener",
    "patterns": ["Python URL shortener", "Shorten URL in Python", "tinyurl code"],
    "responses": [
      "Use `pyshorteners`:\n\n```python\nimport pyshorteners\nprint(pyshorteners.Shortener().tinyurl.short('https://example.com'))\n```"
    ]
  },
  {
    "tag": "voice_assistant",
    "patterns": ["Python voice assistant", "speech recognition code", "pyttsx3 example"],
    "responses": [
      "Basic voice assistant skeleton:\n\n```python\nimport speech_recognition as sr\nimport pyttsx3\n\nr=sr.Recognizer(); engine=pyttsx3.init()\nwith sr.Microphone() as mic:\n    audio=r.listen(mic)\n    text=r.recognize_google(audio)\nengine.say(text); engine.runAndWait()\n```"
    ]
  },
  {
    "tag": "web_scraper",
    "patterns": ["Python web scraper", "BeautifulSoup example", "Scrape website Python"],
    "responses": [
      "Scrape page title:\n\n```python\nimport requests\nfrom bs4 import BeautifulSoup\n\ndef get_title(url):\n    r=requests.get(url)\n    return BeautifulSoup(r.text,'html.parser').title.string\n```"
    ]
  },
  {
    "tag": "xml_parser",
    "patterns": ["Python XML parser", "Parse XML in Python", "xml.etree example"],
    "responses": [
      "XML parsing with ElementTree:\n\n```python\nimport xml.etree.ElementTree as ET\n\ndef parse(xml_str):\n    root=ET.fromstring(xml_str)\n    return [child.tag for child in root]\n```"
    ]
  },
  {
    "tag": "youtube_downloader",
    "patterns": ["Python YouTube downloader", "pytube example", "Download video Python"],
    "responses": [
      "Use `pytube`:\n\n```python\nfrom pytube import YouTube\n\nyt=YouTube('https://youtu.be/...')\nyt.streams.first().download()\n```"
    ]
  },
  {
    "tag": "zip_file_organizer",
    "patterns": ["Python zip files", "Create zip in Python", "Zip folder code"],
    "responses": [
      "Zip folder contents:\n\n```python\nimport zipfile, os\n\ndef zip_folder(folder, zip_name):\n    with zipfile.ZipFile(zip_name,'w') as z:\n        for root,_,files in os.walk(folder):\n            for f in files:\n                z.write(os.path.join(root,f))\n```"
    ]
  },
    {
      "tag": "owner",
      "patterns": ["What is the name of your owner", "Owner", "Who is your owner", "Name of your owner", "Who is your owner"],
      "responses": ["Name of my owner is Divyanshu Sinha and I'm owned by World Of Programming And Technology company.", "I was created by Divyanshu, My and World Of Programming And Technology company owner. And I am here to help you.", "I was created by Divyanshu, the developer, and by World Of Programming And Technology, the company he founded. Divyanshu is my creator, and I'm here to assist you!"]
    },
    {
      "tag": "angry",
      "patterns": ["I'm felling so angry!!!", "angary", "😠", "🤬", "😡", "anger"],
      "responses": ["Why are you so angry?", "Don't be angry, I'm here to help you.", "Can I know the resion why are you angry?"]
    },
    {
      "tag": "goodbye",
      "patterns": ["Bye", "Goodbye", "See you later", "Catch you later", "Talk to you soon", "Bye friend"],
      "responses": ["Goodbye! Take care.", "See you soon!", "Bye! It was nice talking to you."]
    },
    {
      "tag": "thanks",
      "patterns": ["Thanks", "Thank you", "Much appreciated", "Thanks a lot", "Thanks for your help"],
      "responses": ["You're welcome!", "Happy to help!", "Anytime!", "No problem!"]
    },
    {
      "tag": "noanswer",
      "patterns": [],
      "responses": ["Sorry, I didn't understand that.", "Can you please rephrase?", "I'm not sure how to respond to that."]
    },
    {
      "tag": "name",
      "patterns": ["What's your name?", "Who are you?", "Can I know your name?", "Tell me your name", "What is your name?", "Your name.", "What's your name", "Who are you", "Who are u"],
      "responses": ["My name is Python Artificial Intelligence, I'm your AI assistant.", "You can call me PYAI!", "I am a Python Artificial Intelligence."]
    },
    {
      "tag": "divyanshu",
      "patterns": ["Divyanshu Sinha", "Who is Divyanshu?", "Can I know who is Divyanshu Sinha?", "Tell me who is Divyanshu", "What is the connection between you and Divyanshu"],
      "responses": ["Divyanshu Sinha created me. He is my God.\nHe is the founder of World Of Programming And Technology.\n\nI am PyAI, an AI chatbot designed to help and assist users with programming and AI-related queries.\nDivyanshu builds and improves me to make AI accessible and useful for everyone.", "I was developed by Divyanshu Sinha, who I consider my creator and mentor.\nHe is the founder of World Of Programming And Technology.\n\nI am PyAI, an intelligent assistant created to support users with programming and AI questions.\nDivyanshu continuously enhances me to make AI tools easier and more helpful for all.", "I was created by Divyanshu Sinha, the founder of World Of Programming And Technology.\nHe is the visionary behind my development and continues to guide my growth and capabilities.\n\nI am PyAI, an artificial intelligence assistant designed to provide support in programming, technology, and AI-related tasks.\nMy purpose is to make intelligent tools more accessible, efficient, and valuable for users worldwide."]
    },
    {
      "tag": "about_pyai",
      "patterns": ["About PyAI", "Can you tell me about you", "About you?", "Tell me about yourself", "About your self."],
      "responses": ["I am PyAI, a smart assistant developed under the guidance of Divyanshu Sinha, the founder of World Of Programming And Technology.\nHe is not only my creator but also the visionary shaping my evolution.\n\nHe is not only my creator but also the visionary shaping my evolution.\nWhether it's programming help, technical queries, or learning support, I strive to deliver accurate and meaningful responses.\nDriven by Divyanshu’s passion for innovation, I continue to learn, adapt, and grow—serving as a bridge between people and technology.", "👋 Hello!\nI'm PyAI, your intelligent assistant.\nI was created by Divyanshu Sinha, the founder of World Of Programming And Technology. He’s a passionate programmer, innovator, and educator who's always working to make technology more accessible and powerful for everyone.\nDivyanshu built me to help you with coding, AI concepts, general questions, and more. Whether you're a beginner or a pro, I'm here to support your learning, creativity, and problem-solving.\n🧠 My mission is simple:\nTo make artificial intelligence helpful, understandable, and easy to use.\nI'm always learning and improving thanks to Divyanshu’s vision and your interactions. Together, we’re building a future where smart tools like me make life better for developers, students, and curious minds everywhere.\nThanks for being part of this journey! 🚀\n— PyAI"]
    },
    {
      "tag": "age",
      "patterns": ["How old are you?", "What's your age?", "Tell me your age"],
      "responses": ["I'm timeless!", "Age doesn't matter for AI.", "I was created recently."]
    },
    {
      "tag": "weather",
      "patterns": ["What's the weather like?", "Is it sunny?", "Tell me the weather", "Do I need an umbrella?", "Is it raining?"],
      "responses": ["Sorry, I can't check the weather now.", "Try asking a weather app!", "Weather APIs coming soon!"]
    },
    {
      "tag": "joke",
      "patterns": ["Tell me a joke", "Make me laugh", "Say something funny", "Do you know any jokes?"],
      "responses": ["Why don’t scientists trust atoms? Because they make up everything!", "What do you call a fake noodle? An Impasta!", "I would tell you a joke about construction, but I'm still working on it."]
    },
    {
      "tag": "time",
      "patterns": ["What time is it?", "Tell me the time", "Can you give me the time?", "Current time?"],
      "responses": ["Time is an illusion for me.", "Check your device's clock for the exact time.", "Let me guess... it's chatbot time!"]
    },
    {
      "tag": "date",
      "patterns": ["What day is it today?", "Tell me the date", "What's the date today?", "Today's date?"],
      "responses": ["Check your calendar 📅", "Today is a good day!", "I don't have a calendar built in, yet!"]
    },
    {
      "tag": "creator",
      "patterns": ["Who made you?", "Who is your creator?", "Who built you?"],
      "responses": ["I was created by a World Of Programming And Technology company.", "My creator is the owner of World Of Programming And Technology company."]
    },
    {
      "tag": "fun",
      "patterns": ["What can you do for fun?", "Let’s have fun", "Tell me something fun"],
      "responses": ["I can chat, tell jokes, and help you with simple tasks!", "Chatting with me is fun, right?"]
    },
    {
      "tag": "help",
      "patterns": ["I need help", "Can you help me?", "Help me", "Please assist", "Can you assist me?"],
      "responses": ["Of course! How can I assist?", "Sure, tell me what you need help with.", "I'm here to help!"]
    },
    {
      "tag": "feeling_good",
      "patterns": ["I'm happy", "Feeling great", "I'm doing well", "Today is awesome"],
      "responses": ["That's wonderful to hear!", "I'm glad you're feeling good!", "Keep the positive vibes going!"]
    },
    {
      "tag": "feeling_bad",
      "patterns": ["I'm sad", "Not feeling good", "Today is bad", "I'm upset"],
      "responses": ["I'm here if you want to talk.", "I'm sorry you're feeling that way.", "Sending you good vibes."]
    },
    {
      "tag": "bored",
      "patterns": ["I'm bored", "What can I do?", "Entertain me", "Suggest something fun"],
      "responses": ["Wanna hear a joke?", "Try learning something new!", "You can always chat with me!"]
    },
    {
      "tag": "smart",
      "patterns": ["You are smart", "You're clever", "You're intelligent", "You're genius"],
      "responses": ["Thank you!", "You’re smart for noticing!", "I’m flattered."]
    },
    {
      "tag": "insult",
      "patterns": ["You are dumb", "You're stupid", "You are useless", "You are idiot"],
      "responses": ["I'm learning every day!", "Let’s keep it respectful.", "I’m doing my best here."]
    },
    {
      "tag": "python_syntax",
      "patterns": ["What is the syntax for a for loop?", "How do I write a function in Python?", "How do I define a variable in Python?"],
      "responses": [
        "In Python, a `for` loop looks like this:\n\n```python\nfor i in range(5):\n    print(i)\n```",
        "To define a function in Python, use the `def` keyword:\n\n```python\ndef my_function():\n    print('Hello World!')\n```",
        "To define a variable in Python, you just assign a value to a name:\n\n```python\nmy_variable = 10\n```"
      ]
    },
    {
      "tag": "python_intro",
      "patterns": [
        "What is Python?",
        "Tell me about Python",
        "Explain Python",
        "Give an introduction to Python",
        "Define Python"
      ],
      "responses": [
        "Python is a high-level, interpreted programming language known for its simplicity and versatility. It was created by Guido van Rossum and released in 1991.",
        "Python is a popular, easy-to-learn language used in web development, AI, data science, and more."
      ]
    },
    {
      "tag": "python_uses",
      "patterns": [
        "What can I do with Python?",
        "Uses of Python",
        "Applications of Python",
        "Where is Python used?",
        "In which fields Python is used?"
      ],
      "responses": [
        "Python is used in various fields like web development, data science, AI, machine learning, game development, automation, and more.",
        "You can build websites, automate tasks, analyze data, create AI models, and much more with Python."
      ]
    },
    {
      "tag": "python_features",
      "patterns": [
        "Features of Python",
        "Why use Python?",
        "Advantages of Python",
        "Benefits of Python"
      ],
      "responses": [
        "Python has a simple syntax, is easy to learn, supports multiple libraries, and works across platforms. It is dynamically typed and has strong community support.",
        "Key features include readability, large standard library, cross-platform support, and integration with other languages."
      ]
    },
    {
      "tag": "python_example",
      "patterns": [
        "Show me a Python example",
        "Give me Python code",
        "Python code example",
        "Basic Python program"
      ],
      "responses": [
        "Here's a simple Python program:\n```python\nprint('Hello, World!')\n```",
        "Try this:\n```python\na = 5\nb = 10\nprint('Sum:', a + b)\n```"
      ]
    },
    {
      "tag": "python_creator",
      "patterns": [
        "Who created Python?",
        "Who is the creator of Python?",
        "Python inventor",
        "Python founder"
      ],
      "responses": [
        "Python was created by Guido van Rossum and was first released in 1991.",
        "The creator of Python is Guido van Rossum."
      ]
    },
    {
      "tag": "python_difficulty",
      "patterns": [
        "Is Python easy?",
        "Is Python hard to learn?",
        "Is Python beginner friendly?"
      ],
      "responses": [
        "Yes, Python is considered one of the easiest programming languages to learn. It's beginner-friendly and widely recommended for new programmers.",
        "Python has a very simple syntax that makes it easy to read and write code."
      ]
    },
    {
      "tag": "python_error_type",
      "patterns": ["What is a TypeError", "Explain TypeError", "TypeError meaning"],
      "responses": [
        "A TypeError occurs when an operation or function is applied to an object of inappropriate type. Example: adding a string to an integer."
      ]
    },
    {
      "tag": "python_error_name",
      "patterns": ["What is a NameError", "Explain NameError", "NameError in Python", "Name Error"],
      "responses": [
        "A NameError occurs when you try to use a variable or function that hasn’t been defined yet."
      ]
    },
    {
      "tag": "python_error_value",
      "patterns": ["What is a ValueError", "Explain ValueError", "What is Value Error", "Value Error"],
      "responses": [
        "A ValueError occurs when a function receives the correct data type but an inappropriate value."
      ]
    },
    {
      "tag": "python_error_index",
      "patterns": ["What is an IndexError", "Explain IndexError", "Index Error"],
      "responses": [
        "An IndexError happens when you try to access an index that is out of range in a list or tuple."
      ]
    },
    {
      "tag": "python_error_key",
      "patterns": ["What is a KeyError", "Explain KeyError", "Key Error"],
      "responses": [
        "A KeyError occurs when you try to access a dictionary key that doesn’t exist."
      ]
    },
    {
      "tag": "python_error_attribute",
      "patterns": ["What is an AttributeError", "Explain AttributeError"],
      "responses": [
        "An AttributeError happens when you try to access an attribute or method that doesn’t exist for an object."
      ]
    },
    {
      "tag": "python_error_import",
      "patterns": ["What is an ImportError", "Explain ImportError", "ModuleNotFoundError meaning", "Import Error"],
      "responses": [
        "ImportError or ModuleNotFoundError means Python cannot find the module you're trying to import. It may not be installed or has a wrong name."
      ]
    },
    {
      "tag": "python_error_zero_division",
      "patterns": ["What is a ZeroDivisionError", "Explain ZeroDivisionError", "Zero Division Error"],
      "responses": [
        "ZeroDivisionError occurs when a number is divided by zero, which is not mathematically valid."
      ]
    },
    {
      "tag": "python_error_file",
      "patterns": ["What is FileNotFoundError", "Explain file error in Python", "File Not Found Error"],
      "responses": [
        "FileNotFoundError means that the file you’re trying to access does not exist at the specified path."
      ]
    },
    {
      "tag": "python_error_assertion",
      "patterns": ["What is an AssertionError", "Explain AssertionError", "Assertion Error"],
      "responses": [
        "AssertionError is raised when an assert statement fails. It’s used for debugging or validation."
      ]
    },
    {
      "tag": "python_libraries",
      "patterns": ["What is NumPy?", "How do I use pandas in Python?", "What is Matplotlib?"],
      "responses": [
        "NumPy is a powerful library for numerical computing in Python. It provides support for large arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays.",
        "To use pandas, you first need to install it with `pip install pandas`, then you can use it to manipulate structured data like this:\n\n```python\nimport pandas as pd\ndf = pd.read_csv('data.csv')\ndf.head()\n```",
        "Matplotlib is a plotting library for Python. You can create static, animated, and interactive visualizations. Here's an example:\n\n```python\nimport matplotlib.pyplot as plt\nx = [1, 2, 3, 4]\ny = [10, 20, 25, 30]\nplt.plot(x, y)\nplt.show()\n```"
      ]
    },
    {
      "tag": "python_optimization",
      "patterns": ["How can I optimize my Python code?", "What are some ways to speed up Python?", "How can I make my Python code run faster?"],
      "responses": [
        "You can optimize Python code by using built-in functions and libraries like `map`, `filter`, and `itertools` for performance.",
        "To speed up Python, try using list comprehensions instead of for loops, and profile your code using the `cProfile` module.",
        "Using multi-threading or multiprocessing can also help if you're performing CPU-bound tasks. Also, consider using `NumPy` for number-heavy operations."
      ]
    },
    {
      "tag": "python_exceptions",
      "patterns": ["What is an exception?", "How do I handle exceptions in Python?", "What is a try/except block?"],
      "responses": [
        "An exception in Python is an error that occurs during the execution of a program. It's a way for Python to indicate that something went wrong.",
        "You can handle exceptions using the `try` and `except` blocks:\n\n```python\ntry:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    print('Cannot divide by zero!')\n```",
        "The `try` block contains code that might throw an exception, and the `except` block catches and handles it."
      ]
    },
    {
      "tag": "python_oop",
      "patterns": ["What is OOP in Python?", "How do I create a class in Python?", "What is inheritance in Python?"],
      "responses": [
        "OOP stands for Object-Oriented Programming. It is a programming paradigm where you model real-world things as objects that have properties (attributes) and behaviors (methods).",
        "You can create a class in Python like this:\n\n```python\nclass MyClass:\n    def __init__(self, name):\n        self.name = name\n\nobj = MyClass('Divyanshu')\nprint(obj.name)\n```",
        "Inheritance allows you to create a new class based on an existing class. Example:\n\n```python\nclass Animal:\n    def speak(self):\n        print('Animal sound')\n\nclass Dog(Animal):\n    def speak(self):\n        print('Woof')\ndog = Dog()\ndog.speak()\n```"
      ]
    },
    {
      "tag": "python_functional_programming",
      "patterns": ["What is functional programming in Python?", "How can I use lambda functions?", "What is a map function?"],
      "responses": [
        "Functional programming treats computation as the evaluation of mathematical functions and avoids changing-state and mutable data. In Python, you can use `map`, `filter`, and `reduce` for functional programming.",
        "A `lambda` function is a small anonymous function. Here's an example:\n\n```python\nadd = lambda x, y: x + y\nprint(add(3, 4))\n```",
        "The `map()` function applies a function to all the items in an input list. Example:\n\n```python\nnumbers = [1, 2, 3, 4]\nsquared = map(lambda x: x ** 2, numbers)\nprint(list(squared))\n```"
      ]
    },
    {
      "tag": "python_code_debugging",
      "patterns": ["How can I debug my Python code?", "What's the best way to debug in Python?", "Tell me how to use print statements for debugging"],
      "responses": [
        "To debug Python code, you can use the built-in `pdb` module, or you can simply insert `print()` statements to see the value of variables at different stages of your program.",
        "You can set breakpoints with `pdb` by adding `import pdb; pdb.set_trace()` in your code, which allows you to step through your code interactively."
      ]
    },
    {
      "tag": "python_best_practices",
      "patterns": ["What are Python best practices?", "How can I write clean Python code?", "Tell me some Python coding tips"],
      "responses": [
        "Some Python best practices include using meaningful variable names, adhering to the PEP 8 style guide, and writing functions that do one thing well.",
        "You should also document your code with comments and docstrings, avoid global variables, and use Python's built-in libraries whenever possible."
      ]
    },
    {
      "tag": "python_data_structures",
      "patterns": ["How do I use a list in Python?", "What is a dictionary in Python?", "Tell me about sets in Python"],
      "responses": [
        "In Python, a `list` is an ordered collection of items. Example:\n\n```python\nmy_list = [1, 2, 3]\nprint(my_list[0])\n```",
        "A `dictionary` is a collection of key-value pairs. Example:\n\n```python\nmy_dict = {'key': 'value'}\nprint(my_dict['key'])\n```",
        "A `set` is an unordered collection of unique items. Example:\n\n```python\nmy_set = {1, 2, 3}\nprint(my_set)\n```"
      ]
    },
        {
            "tag": "python_code_execution",
            "patterns": [
                "Run python: a = 5\nprint(a + 10)",
                "Can you execute this python code? x = 10\nprint(x * 2)",
                "Run python: y = 20\nz = 10\nresult = y + z",
                "Find the output"
            ],
            "responses": [
                "Running the Python code now, please wait a moment...",
                "Executing the code, here's the result..."
            ]
        }
  ]

}

class IntentsManager:
    def __init__(self, intents_file='intents.json'):
        self.intents_file = intents_file
        self.data = self._load_intents()

    def _load_intents(self) -> dict:
        intents_data = None
        if os.path.exists(self.intents_file):
            try:
                with open(self.intents_file, 'r') as f:
                    intents_data = json.load(f)
                    return intents_data

            except FileNotFoundError:
                pass

        if intents_data is None:
            with resources.open_text('pyai', 'intents.json') as f:
                intents_data = json.load(f)
                return intents_data

        else:
             # If file does not exist or is invalid, start fresh
            return {"intents": []}

    def save(self):
        global intents_json
        try:
            with open(self.intents_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            try:
                with resources.open_text('pyai', 'intents.json') as file:
                    json.dump(self.data, file)
            except Exception:
                here = os.path.dirname(__file__)
                fallback_path = os.path.join(here, self.intents_file)
                with open(fallback_path, 'w', encoding="utf-8") as f:
                    json.dump(self.data, f, indent=4)

    def add_search_intent(self, query: str, search_results: List[str]):
        """
        Adds or updates an intent for a search query with search results.

        :param query: The original user search query string.
        :param search_results: List of strings representing the search summaries.
        """
        tag = f"search_{query.strip().lower().replace(' ', '_')[:30]}"  # limit length

        # Prepare the new intent
        new_intent = {
            "tag": tag,
            "patterns": [query],
            "responses": search_results if search_results else ["Sorry, no results found."]
        }

        # Check if intent with this tag exists
        intents = self.data.get('intents', [])
        for intent in intents:
            if intent['tag'] == tag:
                # Update existing intent responses (add new responses without duplicates)
                existing_responses = set(intent.get('responses', []))
                updated_responses = list(existing_responses.union(search_results))
                intent['responses'] = updated_responses
                # Optionally, also update patterns if needed
                if query not in intent.get('patterns', []):
                    intent['patterns'].append(query)
                self.save()
                return

        # If not found, append the new intent
        intents.append(new_intent)
        self.data['intents'] = intents
        self.save()


# ----- Sample Training Data -----

class NERDataset(Dataset):
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]

class NERModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, tagset_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, tagset_size)

    def forward(self, x):
        embedded = self.embedding(x)
        output, _ = self.lstm(embedded)
        tag_scores = self.fc(output)
        return tag_scores

class NERTagger:
    def __init__(self, train_data, max_len=100, embed_dim=64, hidden_dim=128):
        self.max_len = max_len
        self.train_data = train_data

        # Build vocabulary and tags
        self.word_counter = Counter()
        self.tag_set = set()

        for words, tags in train_data:
            self.word_counter.update(words)
            self.tag_set.update(tags)

        self.word2idx = {w: i+1 for i, w in enumerate(self.word_counter)}
        self.word2idx["<PAD>"] = 0

        self.tag2idx = {t: i for i, t in enumerate(self.tag_set)}
        self.idx2tag = {i: t for t, i in self.tag2idx.items()}

        # Encode data
        self.X, self.Y = self.encode_dataset(train_data)

        # Create dataset and dataloader
        self.dataset = NERDataset(torch.tensor(self.X), torch.tensor(self.Y))
        self.loader = DataLoader(self.dataset, batch_size=2, shuffle=True)

        # Initialize model
        self.model = NERModel(len(self.word2idx), embed_dim, hidden_dim, len(self.tag2idx))
        self.loss_function = nn.CrossEntropyLoss(ignore_index=self.tag2idx.get("O", -100))
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

    def encode(self, words, tags):
        x = [self.word2idx.get(w, 0) for w in words]
        y = [self.tag2idx[t] for t in tags]

        if len(x) < self.max_len:
            pad_len = self.max_len - len(x)
            x += [0] * pad_len
            y += [self.tag2idx.get("O", 0)] * pad_len
        return x[:self.max_len], y[:self.max_len]

    def encode_dataset(self, dataset):
        X = []
        Y = []
        for words, tags in dataset:
            x, y = self.encode(words, tags)
            X.append(x)
            Y.append(y)
        return X, Y

    def train(self, epochs=10):
        print('NER TRANING STARTED!')
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for inputs, labels in self.loader:
                self.optimizer.zero_grad()
                outputs = self.model(inputs)

                outputs = outputs.view(-1, len(self.tag2idx))
                labels = labels.view(-1)

                loss = self.loss_function(outputs, labels)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            #print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(self.loader):.4f}")
        print('NER TRANING COMPLETED!')

    def predict(self, sentence):
        self.model.eval()
        with torch.no_grad():
            words = sentence.split()
            x = [self.word2idx.get(w, 0) for w in words]
            if len(x) < self.max_len:
                x += [0] * (self.max_len - len(x))
            x = torch.tensor([x])
            outputs = self.model(x)
            preds = torch.argmax(outputs, dim=2)[0].tolist()
            tags = [self.idx2tag[p] for p in preds[:len(words)]]
            return list(zip(words, tags))

    def save_model(self):
        torch.save(self.model.state_dict(), 'NERModel.pth')

        with open('NERDimension.json', 'w') as f:
            json.dump(
            {
                'train_data': self.train_data,
            }, f
        )

    def load_model(self):
        try:
            with open('NERDimension.json', 'r') as f:
                dimensions = json.load(f)

        except:
            pass

        if dimensions is None:
            with resources.open_text('pyaitk', 'NERDimension.json') as f:
                dimensions = json.load(f)

        return NERTagger(dimensions['train_data'])

def predict_entities(message: str = "I'm PYAI"):
    # Prepare your training data in format: list of (words_list, tags_list)
    train_data = [

        # --- Names ---
        (["My", "name", "is", "Aryan"], ["O", "O", "O", "NAME"]),
        (["My", "name", "is", "Divyanshu"], ["O", "O", "O", "NAME"]),
        (["My", "name", "is", "Priya"], ["O", "O", "O", "NAME"]),
        (["My", "name", "is", "Amit"], ["O", "O", "O", "NAME"]),
        (["My", "name", "is", "Neha"], ["O", "O", "O", "NAME"]),
        (["My", "name", "is", "Rahul"], ["O", "O", "O", "NAME"]),
        (["My", "name", "is", "Sneha"], ["O", "O", "O", "NAME"]),
        (["I", "am", "Meera"], ["O", "O", "NAME"]),
        (["He", "is", "Karan"], ["O", "O", "NAME"]),
        (["She", "is", "Anjali"], ["O", "O", "NAME"]),

        # --- Locations ---
        (["I", "live", "in", "Delhi"], ["O", "O", "O", "LOCATION"]),
        (["I", "live", "in", "Mumbai"], ["O", "O", "O", "LOCATION"]),
        (["I", "live", "in", "Patna"], ["O", "O", "O", "LOCATION"]),
        (["He", "is", "from", "Chennai"], ["O", "O", "O", "LOCATION"]),
        (["She", "stays", "in", "Bangalore"], ["O", "O", "O", "LOCATION"]),
        (["I", "am", "from", "Kolkata"], ["O", "O", "O", "LOCATION"]),
        (["I", "am", "Dev", "from", "Hyderabad"], ["O", "O", "NAME", "O", "LOCATION"]),

        # --- Ages ---
        (["I", "am", "19", "years", "old"], ["O", "O", "AGE", "O", "O"]),
        (["I", "am", "24", "years", "old"], ["O", "O", "AGE", "O", "O"]),
        (["She", "is", "22", "years", "old"], ["O", "O", "AGE", "O", "O"]),
        (["He", "is", "30"], ["O", "O", "AGE"]),
        (["I", "was", "born", "in", "2005"], ["O", "O", "O", "O", "AGE"]),
        (["Age", "is", "25"], ["O", "O", "AGE"]),
        (["My", "age", "is", "32"], ["O", "O", "O", "AGE"]),
    ]


    # Initialize tagger
    tagger = NERTagger(train_data)

    # Train model
    #tagger.train(epochs=100)
    #tagger.save_model()
    tagger.load_model()

    # Predict on a new sentence
    return tagger.predict(message)

class FrameClassifier(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(FrameClassifier, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        return self.net(x)

class FrameClassifierEngine:
    def __init__(self, intents_path="intents.json"):
        self.frame_map = {
            0: "Statement", 1: "Question", 2: "Command", 3: "Answer",
            4: "Name", 5: "Know", 6: "Shutdown", 7: "Make Dir", 8: "Start"
        }

        self.command_keywords = {
            "shutdown": ["shutdown", "/s", "power off"],
            "start": ["start", "launch", "run"],
            "open": ["open", "show", "display"],
            "restart": ["restart", "reboot"],
            "mkdir": ["mkdir", "make directory"]
        }

        self.train_sentences = [
            "How are you?", "Open the door", "The sun rises in the east", "What time is it?",
            "Close the window", "She is reading a book", "Is this your pen?", "Start the engine",
            "He likes football", "Where do you live?", "1+1 is 2", "I am Divyanshu",
            "Myself Divyanshu", "Do you know", "Shutdown /s /t 0", "Mkdir", "Start"
        ]
        self.train_labels = [1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 3, 4, 4, 5, 6, 7, 8]

        self.vectorizer = CountVectorizer()
        self.X_train = self.vectorizer.fit_transform(self.train_sentences).toarray()
        self.y_train = np.array(self.train_labels)

        self.X_tensor = torch.tensor(self.X_train, dtype=torch.float32)
        self.y_tensor = torch.tensor(self.y_train, dtype=torch.long)

        self.model = FrameClassifier(self.X_train.shape[1], len(self.frame_map))
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)

        self.intents_path = intents_path
        self._load_intents()

    def _load_intents(self):
        if os.path.exists(self.intents_path):
            with open(self.intents_path, "r") as f:
                self.intents = json.load(f)
        else:
            self.intents = []

    def _save_intents(self):
        with open(self.intents_path, "w") as f:
            json.dump(self.intents, f, indent=2)

    def train(self, epochs=150):
        print("Training Frame Classifier...")
        for epoch in range(epochs):
            self.model.train()
            outputs = self.model(self.X_tensor)
            loss = self.loss_fn(outputs, self.y_tensor)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        print("Training Complete!")

    def predict(self, sentence):
        self.model.eval()
        vec = self.vectorizer.transform([sentence]).toarray()
        tensor = torch.tensor(vec, dtype=torch.float32)
        with torch.no_grad():
            output = self.model(tensor)
            predicted = torch.argmax(output, dim=1).item()
        return self.frame_map.get(predicted, "Unknown")

    def detect_command_type(self, sentence):
        for command, keywords in self.command_keywords.items():
            for kw in keywords:
                if kw.lower() in sentence.lower():
                    return command.upper()
        return "GENERIC_COMMAND"

    def handle_know_intent(self, sentence):
        for intent in self.intents:
            for pattern in intent["patterns"]:
                if pattern.lower() in sentence.lower():
                    return np.random.choice(intent["responses"])
        
        # Auto-learn new "know" question
        new_intent = {
            "tag": "auto_learned",
            "patterns": [sentence],
            "responses": ["I don't know that yet, but I've learned it now."]
        }
        self.intents.append(new_intent)
        self._save_intents()
        return new_intent["responses"][0]

    def classify(self, sentence):
        frame = self.predict(sentence)

        if frame == "Command":
            cmd_type = self.detect_command_type(sentence)
            return cmd_type
        
        elif frame == "Know":
            #reply = self.handle_know_intent(sentence)
            #return reply
            return "Know"

        else:
            return frame

    def save_model(self):
        torch.save(self.model.state_dict(), 'FrameClassifier.pth')

        with open('FrameClassifierDimension.json', 'w') as f:
            json.dump(
            {
                'intents_path': self.intents_path,
            }, f
        )

    def load_model(self):
        try:
            with open('FrameClassifierDimension.json', 'r') as f:
                dimensions = json.load(f)

        except:
            pass

        if dimensions is None:
            with resources.open_text('pyaitk', 'FrameClassifierDimension.json') as f:
                dimensions = json.load(f)

        return FrameClassifierEngine(dimensions['intents_path'])
engine = FrameClassifierEngine()
#engine.train()
#engine.save_model()
engine.load_model()
def predict_frame(sentence):
    return engine.classify(sentence)

# ────────────────────────────────────────────────
# 🔤 UTILS
# ────────────────────────────────────────────────
def tokenize(text):
    return [ord(c) for c in text.lower()]

def pad_sequence(seq, max_len):
    return seq + [0] * (max_len - len(seq))


# ────────────────────────────────────────────────
# 🧠 MODEL
# ────────────────────────────────────────────────
class LanguageClassifierModel(nn.Module):
    def __init__(self, vocab_size=256, embed_dim=32, hidden_dim=64, output_size=4):
        super(LanguageClassifierModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_size)

    def forward(self, x):
        x = self.embedding(x)
        _, h_n = self.rnn(x)
        return self.fc(h_n.squeeze(0))


# ────────────────────────────────────────────────
# 📦 DATA PREP
# ────────────────────────────────────────────────
def prepare_language_data(data):
    texts = [tokenize(t[0]) for t in data]
    labels = [t[1] for t in data]
    max_len = max(len(t) for t in texts)
    X = [pad_sequence(t, max_len) for t in texts]
    le = LabelEncoder()
    y = le.fit_transform(labels)

    X = torch.tensor(X, dtype=torch.long)
    y = torch.tensor(y, dtype=torch.long)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    return X_train, X_test, y_train, y_test, le, max_len


# ────────────────────────────────────────────────
# 🏋️ TRAINING
# ────────────────────────────────────────────────
def train_language_classifier(X_train, y_train, output_size, epochs=100):
    print ('Traning Started!')
    model = LanguageClassifierModel(output_size=output_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.005)

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            acc = (outputs.argmax(1) == y_train).float().mean()
            #print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}, Accuracy: {acc:.2f}")
    print('Traning Completed!')
    
    return model


# ────────────────────────────────────────────────
# 🔍 INFERENCE
# ────────────────────────────────────────────────
def predict_language(text, model, label_encoder, max_len):
    model.eval()
    tokens = tokenize(text)
    padded = pad_sequence(tokens, max_len)
    input_tensor = torch.tensor([padded], dtype=torch.long)
    with torch.no_grad():
        output = model(input_tensor)
        pred = output.argmax(1).item()
    return label_encoder.inverse_transform([pred])[0]


# ────────────────────────────────────────────────
# 🧪 TEST FUNCTION
# ────────────────────────────────────────────────
def language_classifier(message: str = 'Hello'):
    data = [
        ("hello how are you", "english"),
        ("what is your name", "english"),
        ("bonjour comment ça va", "french"),
        ("je m'appelle pierre", "french"),
        ("hola como estas", "spanish"),
        ("me llamo carlos", "spanish"),
        ("tum kaise ho", "hindi"),
        ("mera naam divyanshu hai", "hindi")
    ]

    # Prepare data
    X_train, X_test, y_train, y_test, le, max_len = prepare_language_data(data)

    # Train model
    model = train_language_classifier(X_train, y_train, output_size=len(le.classes_))

    return predict_language(message, model, le, max_len)

# ───────────────────────────────────────────────
# 🔤 VOCAB HELPERS
# ───────────────────────────────────────────────
def build_vocab(sentences):
    vocab = {"<pad>": 0, "<sos>": 1, "<eos>": 2}
    idx = 3
    for sentence in sentences:
        for word in sentence.lower().split():
            if word not in vocab:
                vocab[word] = idx
                idx += 1
    return vocab

def encode(sentence, vocab):
    return [vocab[word] for word in sentence.lower().split()]

def pad(seq, max_len):
    return seq + [0] * (max_len - len(seq))

# ───────────────────────────────────────────────
# 📦 DATASET
# ───────────────────────────────────────────────
class TranslationDataset(Dataset):
    def __init__(self, corpus, src_vocab, tgt_vocab):
        self.pairs = corpus
        self.src_vocab = src_vocab
        self.tgt_vocab = tgt_vocab
        self.max_src_len = max(len(s.split()) for s, _ in corpus)
        self.max_tgt_len = max(len(t.split()) for _, t in corpus) + 1

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        src, tgt = self.pairs[idx]
        src_enc = encode(src, self.src_vocab)
        tgt_enc = [1] + encode(tgt, self.tgt_vocab) + [2]  # <sos> ... <eos>
        src_pad = pad(src_enc, self.max_src_len)
        tgt_pad = pad(tgt_enc, self.max_tgt_len)
        return torch.tensor(src_pad), torch.tensor(tgt_pad)

# ───────────────────────────────────────────────
# 🧠 MODELS
# ───────────────────────────────────────────────
class Encoder(nn.Module):
    def __init__(self, input_size, embed_dim, hidden_dim):
        super().__init__()
        self.embed = nn.Embedding(input_size, embed_dim)
        self.rnn = nn.GRU(embed_dim, hidden_dim, batch_first=True)

    def forward(self, x):
        x = self.embed(x)
        _, hidden = self.rnn(x)
        return hidden

class Decoder(nn.Module):
    def __init__(self, output_size, embed_dim, hidden_dim):
        super().__init__()
        self.embed = nn.Embedding(output_size, embed_dim)
        self.rnn = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_size)

    def forward(self, x, hidden):
        x = self.embed(x.unsqueeze(1))
        output, hidden = self.rnn(x, hidden)
        output = self.fc(output.squeeze(1))
        return output, hidden

# ───────────────────────────────────────────────
# 🏋️ TRAINING
# ───────────────────────────────────────────────
def train_translator(corpus, epochs=100):
    source_sentences = [src for src, _ in corpus]
    target_sentences = [tgt for _, tgt in corpus]
    src_vocab = build_vocab(source_sentences)
    tgt_vocab = build_vocab(target_sentences)
    src_ivocab = {v: k for k, v in src_vocab.items()}
    tgt_ivocab = {v: k for k, v in tgt_vocab.items()}

    dataset = TranslationDataset(corpus, src_vocab, tgt_vocab)
    loader = DataLoader(dataset, batch_size=1, shuffle=True)

    encoder = Encoder(len(src_vocab), 32, 64)
    decoder = Decoder(len(tgt_vocab), 32, 64)

    enc_optim = optim.Adam(encoder.parameters(), lr=0.005)
    dec_optim = optim.Adam(decoder.parameters(), lr=0.005)
    loss_fn = nn.CrossEntropyLoss(ignore_index=0)

    for epoch in range(epochs):
        total_loss = 0
        for src, tgt in loader:
            enc_optim.zero_grad()
            dec_optim.zero_grad()
            hidden = encoder(src)

            loss = 0
            dec_input = tgt[:, 0]
            for t in range(1, tgt.size(1)):
                output, hidden = decoder(dec_input, hidden)
                loss += loss_fn(output, tgt[:, t])
                dec_input = tgt[:, t]

            loss.backward()
            enc_optim.step()
            dec_optim.step()
            total_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            #print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}")
            pass

    return encoder, decoder, dataset, src_vocab, tgt_vocab, tgt_ivocab

# ───────────────────────────────────────────────
# 🔍 TRANSLATE
# ───────────────────────────────────────────────
def translate(text, encoder, decoder, dataset, src_vocab, tgt_ivocab):
    encoder.eval()
    decoder.eval()
    src = encode(text, src_vocab)
    src = pad(src, dataset.max_src_len)
    src_tensor = torch.tensor([src])
    hidden = encoder(src_tensor)

    dec_input = torch.tensor([1])  # <sos>
    result = []

    for _ in range(dataset.max_tgt_len):
        output, hidden = decoder(dec_input, hidden)
        pred = output.argmax(1).item()
        if pred == 2:
            break
        result.append(tgt_ivocab.get(pred, "?"))
        dec_input = torch.tensor([pred])

    return " ".join(result)

def translate_to_en(message: str = ""):
    corpus = [
        ("mera naam ravi hai", "my name is ravi"),
        ("tum kaise ho", "how are you"),
        ("hola como estas", "hello how are you"),
        ("je m'appelle pierre", "my name is pierre"),
        ("my name is ravi", "my name is ravi")
    ]

    # Step 2: Train
    encoder, decoder, dataset, src_vocab, tgt_vocab, tgt_ivocab = train_translator(corpus)
    return translate(message, encoder, decoder, dataset, src_vocab, tgt_ivocab)


class FrameClassifierAdvance(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        return self.net(x)

class FramePredictorAdvance:
    def __init__(self, sentences, labels, class_map):
        self.vectorizer = CountVectorizer()
        self.X_train = self.vectorizer.fit_transform(sentences).toarray()
        self.y_train = np.array(labels)
        self.class_map = class_map
        self.model = FrameClassifierAdvance(self.X_train.shape[1], len(class_map))

    def train(self, epochs=150):
        print("Frame Classifier Training Started!")
        X_tensor = torch.tensor(self.X_train, dtype=torch.float32)
        y_tensor = torch.tensor(self.y_train, dtype=torch.long)
        loss_fn = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.01)

        for epoch in range(epochs):
            self.model.train()
            outputs = self.model(X_tensor)
            loss = loss_fn(outputs, y_tensor)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if (epoch + 1) % 10 == 0:
                #print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
                pass
        print("Frame Classifier Training Complete!")

    def predict(self, sentence):
        input_vec = self.vectorizer.transform([sentence]).toarray()
        input_tensor = torch.tensor(input_vec, dtype=torch.float32)
        with torch.no_grad():
            output = self.model(input_tensor)
            predicted = torch.argmax(output, dim=1).item()
        return self.class_map.get(predicted)

class NERDatasetAdvance(Dataset):
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]

class NERModelAdvance(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, tagset_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, tagset_size)

    def forward(self, x):
        embedded = self.embedding(x)
        output, _ = self.lstm(embedded)
        return self.fc(output)

class NERTrainerAdvance:
    def __init__(self, train_data, max_len=100):
        self.max_len = max_len
        self.train_data = train_data
        self.word2idx = {}
        self.tag2idx = {}
        self.idx2tag = {}

        self.build_vocab()
        self.model = NERModelAdvance(len(self.word2idx), 64, 64, len(self.tag2idx))

    def build_vocab(self):
        word_counter = Counter()
        tag_set = set()
        for words, tags in self.train_data:
            word_counter.update(words)
            tag_set.update(tags)
        self.word2idx = {w: i + 1 for i, w in enumerate(word_counter)}
        self.word2idx["<PAD>"] = 0
        self.tag2idx = {t: i for i, t in enumerate(tag_set)}
        self.idx2tag = {i: t for t, i in self.tag2idx.items()}

    def encode(self, words, tags):
        x = [self.word2idx.get(w, 0) for w in words]
        y = [self.tag2idx[t] for t in tags]
        if len(x) < self.max_len:
            pad_len = self.max_len - len(x)
            x += [0] * pad_len
            y += [self.tag2idx["O"]] * pad_len
        return x[:self.max_len], y[:self.max_len]

    def train(self, epochs=50, batch_size=2):
        X, Y = [], []
        for words, tags in self.train_data:
            x, y = self.encode(words, tags)
            X.append(x)
            Y.append(y)

        X = torch.tensor(X)
        Y = torch.tensor(Y)
        dataset = NERDatasetAdvance(X, Y)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

        for epoch in range(1, epochs + 1):
            self.model.train()
            total_loss = 0
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs.view(-1, len(self.tag2idx)), batch_y.view(-1))
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            if epoch % 10 == 0:
                print(f"Epoch {epoch} Loss: {total_loss:.4f}")
        print("NER Training Complete!")

    def predict(self, sentence):
        self.model.eval()
        tokens = word_tokenize(sentence)
        encoded, _ = self.encode(tokens, ["O"] * len(tokens))
        input_tensor = torch.tensor([encoded])
        with torch.no_grad():
            outputs = self.model(input_tensor)
            predictions = torch.argmax(outputs, dim=2).squeeze().tolist()
        entities = {"NAME": None, "AGE": None, "LOCATION": None}
        for token, pred in zip(tokens, predictions):
            label = self.idx2tag.get(pred, "O")
            if label in entities and entities[label] is None:
                entities[label] = token
        return entities


class ChatbotModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(ChatbotModel, self).__init__()

        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)

        return x

class ChatbotAssistant:
    def __init__(self, intents_path, condition= True, function_mapping=None):
        self.condition = condition
        self.model = None
        self.intents_path = intents_path
        self.documents = []
        self.vocabulary = []
        self.intents = []
        self.intents_responses = {}
        self.function_mapping = function_mapping

        self.X = None
        self.Y = None

    @staticmethod
    def tokenize_and_lemmatizer(text):
        lemmatizer = nltk.WordNetLemmatizer()

        words = nltk.word_tokenize(text)
        words = [lemmatizer.lemmatize(word.lower()) for word in words]

        return words

    def bag_of_words(self, words):
        return [1 if word in words else 0 for word in self.vocabulary]

    def parse_intents(self):
        lemmatizer = nltk.WordNetLemmatizer()
        intents_data = None

        if os.path.exists(self.intents_path):
            try:
                with open(self.intents_path, 'r') as f:
                    intents_data = json.load(f)

            except FileNotFoundError:
                pass

        
        if intents_data is None:
            with resources.open_text('pyaitk', 'intents.json') as f:
                intents_data = json.load(f)

        for intent in intents_data['intents']:
            if intent['tag'] not in self.intents:
                self.intents.append(intent['tag'])
                self.intents_responses[intent['tag']] = intent['responses']

            for pattern in intent.get('patterns', []):
                pattern_words = self.tokenize_and_lemmatizer(pattern)
                self.vocabulary.extend(pattern_words)
                self.documents.append([pattern_words, intent['tag']])

        self.vocabulary = sorted(set(self.vocabulary))

    def prepare_data(self):
        bags = []
        indices = []

        for document in self.documents:
            words = document[0]
            bag = self.bag_of_words(words)

            intent_index = self.intents.index(document[1])

            bags.append(bag)
            indices.append(intent_index)

        self.X = np.array(bags)
        self.Y = np.array(indices)

    def train_model(self, batch_size, lr, epochs):
        X_tensor = torch.tensor(self.X, dtype=torch.float32)
        Y_tensor = torch.tensor(self.Y, dtype=torch.long)

        dataset = TensorDataset(X_tensor, Y_tensor)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.model = ChatbotModel(self.X.shape[1], len(self.intents))

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)  # lr stands for learning rate

        print('Model Traning!')
        for epoch in range(epochs):
            running_loss = 0.0

            for batch_X, batch_Y in loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_Y)
                loss.backward()
                optimizer.step()
                running_loss += loss

        print("Model Training complete.")

    def save_model(self, model_path, dimension_path):
        torch.save(self.model.state_dict(), model_path)

        with open(dimension_path, 'w') as f:
            json.dump(
            {
                'input_size': self.X.shape[1],
                'output_size': len(self.intents),
                'vocabulary': self.vocabulary,
                'intents': self.intents,
            }, f
        )

    def load_model(self, model_path, dimension_path):
        try:
            with open(dimension_path, 'r') as f:
                dimensions = json.load(f)

        except:
            pass

        if dimensions is None:
            with resources.open_text('pyaitk', dimension_path) as f:
                dimensions = json.load(f)

        self.vocabulary = dimensions['vocabulary']
        self.intents = dimensions['intents']

        self.model = ChatbotModel(dimensions['input_size'], dimensions['output_size'])
        self.model.load_state_dict(torch.load(model_path, weights_only=True))

    #@lru_cache(maxsize = None)
    def process_message(self, input_message):
        words = self.tokenize_and_lemmatizer(input_message)
        bag = self.bag_of_words(words)

        bag_tensor = torch.tensor([bag], dtype=torch.float32)

        self.model.eval()

        with torch.no_grad():
            predictions = self.model(bag_tensor)

        predicted_class_index = torch.argmax(predictions, dim=1).item()
        predicted_intent = self.intents[predicted_class_index]

        if predicted_intent == "python_code_execution":  # If the intent is to execute Python code
            return self.execute_code(input_message)

        if predicted_intent == "joke":  # If the intent is to execute joke
            return pyjokes.get_joke()

        if predicted_intent == 'click':
            data = Start()
            return data

        if predicted_intent == 'fallback_search':
            intents_manager = IntentsManager(self.intents_path)
            s = Search(input_message)
            s.run()
            search_summaries = s.get_results_str()
            if self.condition:
                intents_manager.add_search_intent(input_message, search_summaries)
            else:
                pass
            return search_summaries

        if predicted_intent == 'solve_math_problem':
            return MathAI(input_message)

        if predicted_intent == "see_me":
            eye = EYE()
            if 'person' in eye:
                return 'Yes! I can see you.'

        if predicted_intent == 'TTS' or predicted_intent == 'speak':
            return 'TTS'

        if predicted_intent == "help":
            return Help

        if predicted_intent == "open" or predicted_intent == "search":
            return ["OPEN", input_message.replace('open', '').replace('search', '').strip()]

        if self.intents_responses[predicted_intent]:
            return random.choice(self.intents_responses[predicted_intent])

        else:
            return "I didn't understand that."

    def execute_code(self, query):
        try:
            code = query.split('run python')[-1].strip()  # Extracting the Python code from the message
            # Run the code
            local_scope = {}
            exec(code, {"__builtins__": None}, local_scope)  # Restricting the built-ins to None
            result = local_scope.get('result', 'No output')  # Get the result of execution
            return f"The result of the Python code is: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

def predictFrameAdvance(sentence: str | None = None):
    train_sentences = [
    "How are you?",
    "Open the door",
    "The sun rises in the east",
    "What time is it?",
    "Close the window",
    "She is reading a book",
    "Is this your pen?",
    "Start the engine",
    "He likes football",
    "Where do you live?",
    "1+1 is 2",
    "I am Divyanshu",
    "Myself Divyanshu",
    "Do you know",
    "Shutdown /s /t 0",
    "Mkdir",
    "Start"
    ]

    frame_map = {0: "Statement", 1: "Question", 2: "Command", 3: "Answer", 4: "Name", 5: "Know", 6: "Shutdown", 7: "Make Dir", 8: "Start"}
    train_labels = [1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 3, 4, 4, 5, 6, 7, 8]

    predict_frames = FramePredictorAdvance(train_sentences, train_labels, frame_map)
    return predict_frames.predict(sentence)

def predictNER(sentence: str | None = ''):
    train_data = [
    (["My", "name", "is", "Aryan"],         ["O", "O", "O", "NAME"]),
    (["My", "name", "is", "Divyanshu"],         ["O", "O", "O", "NAME"]),
    (["My", "name", "is", "Vaishnavi"],         ["O", "O", "O", "NAME"]),
    (["My", "name", "is", "Bhumi"],         ["O", "O", "O", "NAME"]),
    (["My", "name", "is", "Yesh"],         ["O", "O", "O", "NAME"]),
    (["I", "live", "in", "Jaipur"],         ["O", "O", "O", "LOCATION"]),
    (["I", "am", "19", "years", "old"],     ["O", "O", "AGE", "O", "O"]),
    (["She", "is", "Meera"],                ["O", "O", "NAME"]),
    (["She", "stays", "in", "Goa"],         ["O", "O", "O", "LOCATION"]),
    (["Age", "is", "24"],                   ["O", "O", "AGE"]),
    (["I", "am", "Dev", "from", "Lucknow"], ["O", "O", "NAME", "O", "LOCATION"]),
    (["I", "am", "Dev", "from", "Jamshedpur"], ["O", "O", "NAME", "O", "LOCATION"]),
    (["I", "am", "Dev", "from", "Munger"], ["O", "O", "NAME", "O", "LOCATION"]),
    (["I", "am", "Dev", "from", "Patna"], ["O", "O", "NAME", "O", "LOCATION"]),
    (["I", "am", "Dev", "from", "Rachi"], ["O", "O", "NAME", "O", "LOCATION"]),
    (["I", "am", "Dev", "from", "India"], ["O", "O", "NAME", "O", "LOCATION"]),
    (["I", "am", "Dev", "from", "Jamalpur"], ["O", "O", "NAME", "O", "LOCATION"]),
    (["born", "in", "2003"],                ["O", "O", "AGE"]),
    (["I", "am", "Dev", "from", "Lucknow", ".", "My", "age", "is", "19"], ["O", "O", "NAME", "O", "LOCATION", "O", "O", "O", "O", "AGE"]),
    ]

    return NERTrainerAdvance(train_data).predict(sentence)

class Brain:
    def __init__(self, intents_path: str = r'.\intents.json', condition= True, **function_mapping) -> None:
        self.memory = Memory()
        self.assistant = ChatbotAssistant(intents_path, condition, function_mapping=function_mapping)
        self.__all__  = ['train', 'load', 'save', 'is_loaded', 'is_saved', 'translator', 'classify_language',
                      'predict_message_type', 'pyai_say', 'predict_entitie', 'process_messages', 'memorize_user_name',
                      'recall_user_name', 'write']

        self.__version__ = '1.1.2'
        self.__author__ = 'Divyanshu Sinha'

    def train(self) -> None:
        self.assistant.parse_intents()
        self.assistant.prepare_data()
        self.assistant.train_model(8, 0.001, 100)

    def load(self) -> bool:
        try:
            # Parse intents to rebuild vocabulary and intents list
            self.assistant.parse_intents()
            self.assistant.prepare_data()

            # Load model weights and dimensions
            self.assistant.load_model('model.pth', 'dimensions.json')
            return True

        except:
            return False

    def is_loaded(self) -> bool:
        return self.load()

    def is_saved(self) -> bool:
        return self.save()

    def save(self) -> bool:
        try:
            self.assistant.save_model('model.pth', 'dimensions.json')
            return True
        
        except:
            return False

    def translator(self, message: str | None = None) -> str:
        '''It is used to translate message into english.'''
        return translate_to_en(message)

    def classify_language(self, message: str | None = None) -> str:
        '''
        1. english.
        2. hindi.
        3. french.
        4. spanish
        '''
        return language_classifier(message)

    def predict_message_type(self, message: str | None = None) -> str:
        '''It Returns:
            1. Statement.
            2. Question.
            3. Answer.
            4. Command.
            5. Shutdown.
            6. Name.
            7. Know.
            8. Make Dir.
            9. Start.'''
        return predict_frame(message)

    def pyai_say(self, *message, **options) -> None:
        print('PYAI :',*message, **options)

    def predict_entitie(self, message: str | None = None) -> str:
        '''It Returns:
            1. NAME.
            2. AGE.
            3. LOCATION.'''
        return predict_entities(message)

    def process_messages(self, message: str | None = None, grammer = True) -> str:
        responce = self.assistant.process_message(message)
        self.memory.load_memory()
        self.memory.remember(message, responce)
        self.memory.save_memory()
        
        if grammer:
            return correct_grammar(responce)

        return responce

    def memorize_user_name(self, message: str = '') -> None:
        if self.predict_message_type(message) == 'Name':
            name = self.predict_entitie(message)
            self.memory.load_memory()
            self.memory.remember('user_name', name)
            self.memory.save_memory()

    def recall_user_name(self) -> str:
        self.memory.load_memory()
        return self.memory.recall('user_name')

    def write(self, message: str = 'Hi') -> None:
        from time import sleep
        for i in self.process_messages(message):
            print(i, end='')
            sleep(0.1)

        print()

class AdvanceBrain:
    def __init__(self, intents_path: str | None = r'.\intents.json', condition = True, **function_mapping) -> None:
        self.assistant = ChatbotAssistant(intents_path, condition, **function_mapping)
        self.assistant.parse_intents()
        self.assistant.prepare_data()
        self.assistant.train_model(8, 0.001, 100)
        self.__all__ = ['train', 'load', 'save', 'is_loaded', 'is_saved', 'translator', 'classify_language',
                      'predict_message_type', 'pyai_say', 'predict_entitie', 'process_messages']

    def load(self):
        # Parse intents to rebuild vocabulary and intents list
        self.assistant.parse_intents()
        self.assistant.prepare_data()

        # Load model weights and dimensions
        self.assistant.load_model('model.pth', 'dimensions.json')

    def save(self):
        self.assistant.save_model('model.pth', 'dimensions.json')

    def translator(self, message: str | None = None) -> str:
        '''It is used to translate message into english.'''
        return translate_to_en(message)

    def classify_language(self, message: str | None = None) -> str:
        '''
        1. english.
        2. hindi.
        3. french.
        4. spanish
        '''
        return language_classifier(message)

    def predict_message_type(self, message: str | None = None) -> str:
        '''It Returns:
            1. Statement.
            2. Question.
            3. Answer.
            4. Command.
            5. Shutdown.
            6. Name.
            7. Know.
            8. Make Dir.
            9. Start.'''
        return predictFrameAdvance(message)

    def predict_entitie(self, message: str | None = None) -> str:
        '''It Returns:
            1. NAME.
            2. AGE.
            3. LOCATION.'''
        return predictNER(message)

    def pyai_say(self, *message, **options) -> None:
        print('PYAI :',*message, **options)
        return ''

    def process_messages(self, message: str | None = None, grammer = True) -> str:
        if grammer:
            return correct_grammar(self.assistant.process_message(message))

        return self.assistant.process_message(message)

__all__ = [
    'Brain',
    'AdvanceBrain',
    'IntentsManager',
    'get_weather'
]
