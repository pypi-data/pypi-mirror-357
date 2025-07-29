# Memory
import json
import os

class Memory:
    def __init__(self, filename=r"memory.json"):
        self.filename = filename
        self.data = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        else:
            return {}

    def save_memory(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def remember(self, key, value):
        self.data[key] = value
        self.save_memory()

    def recall(self, key):
        return self.data.get(key, None)

    def clear_memory(self):
        self.data = {}
        self.save_memory()

memory = Memory()
