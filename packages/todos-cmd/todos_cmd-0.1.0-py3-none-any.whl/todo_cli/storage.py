import os
import json

FILE_PATH = os.path.expanduser("~/.todo_cli.json")

def load_data():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f, indent=2)
