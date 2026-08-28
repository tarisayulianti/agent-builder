"""Simpan state ke file JSON."""
import json, os
from datetime import datetime

class State:
    def __init__(self, path="hermes_state.json"):
        self.path = path
        self.data = self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get(self, key, default=None):
        return self.data.get(key, default)
