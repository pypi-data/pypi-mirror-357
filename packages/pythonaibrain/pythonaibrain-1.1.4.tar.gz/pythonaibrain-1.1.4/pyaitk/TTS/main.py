import pyttsx3
import sys

# Voice name lists per platform
windows_voices = ['microsoft david desktop', 'microsoft zira desktop', 'microsoft mark desktop']
macos_voices = ['alex', 'samantha', 'victoria', 'fred', 'daniel', 'fiona']
linux_voices = ['english', 'english-us', 'english-uk', 'mb-en1', 'mb-fr1']

voice_name_help = {
    'windows': [
        'david',     # Microsoft David (Male, en-US)
        'zira',      # Microsoft Zira (Female, en-US)
        'mark'       # Microsoft Mark (Male, en-US)
    ],
    'macos': [
        'alex',      # Alex (Male, en-US)
        'samantha',  # Samantha (Female, en-US)
        'victoria',  # Victoria (Female, en-US)
        'fred',      # Fred (Male, robotic style)
        'daniel',    # Daniel (Male, en-GB)
        'fiona'      # Fiona (Female, en-GB)
    ],
    'linux': [
        'english',      # Default espeak voice
        'english-us',   # American English
        'english-uk',   # British English
        'mb-en1',       # MBROLA English 1
        'mb-fr1'        # MBROLA French 1
    ]
}

class TTS:
    def __init__(self, text: str = 'Hello from Py AI') -> None:
        self.text = text

    def OsType(self) -> str:
        platform = sys.platform
        if platform.startswith('win'):
            return 'windows'
        elif platform == 'darwin':
            return 'macos'
        elif platform.startswith('linux'):
            return 'linux'
        else:
            return 'unknown'

    def say(self, voice: str = 'david') -> None:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)

        # Get system voices
        voices = engine.getProperty('voices')
        system = self.OsType()

        # Pick appropriate list
        if system == 'windows':
            voice_list = windows_voices
        elif system == 'macos':
            voice_list = macos_voices
        elif system == 'linux':
            voice_list = linux_voices
        else:
            voice_list = []

        # Choose voice by name match
        selected_voice = None
        voice = voice.lower()

        for v in voices:
            vname = v.name.lower()
            if voice in vname or any(voice in n for n in voice_list if n in vname):
                selected_voice = v
                break

        # Fallback to first voice if none matched
        if not selected_voice:
            print(f"Warning: Voice '{voice}' not found. Using default.")
            self.help()
            selected_voice = voices[0]
            print(f'By default we take {selected_voice}')

        engine.setProperty('voice', selected_voice.id)
        engine.say(self.text)
        engine.runAndWait()

    def save(out_file_name: str = 'output.wav') -> None:
        self.engine.save_to_file(text, f'{out_file_name.split('.')[0]}.wav')

    def help(self, print_message: bool = True) -> list:
        voices = voice_name_help[self.OsType()]
        if print_message:
            print(f'You Can Select these voice: {voices}')

        return voices

def OSType() -> str:
        platform = sys.platform
        if platform.startswith('win'):
            return 'windows'
        elif platform == 'darwin':
            return 'macos'
        elif platform.startswith('linux'):
            return 'linux'
        else:
            return 'unknown'

def speak(text: str = 'Hi', voice: str = 'david') -> None:
    TTS(text).say(voice=voice)
