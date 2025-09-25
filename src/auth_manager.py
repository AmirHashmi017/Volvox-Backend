import json
import hashlib
import os
from datetime import datetime

USER_FILE = "../data/user_data.json"

# -------------------------------
# Load & Save Functions
# -------------------------------
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as file:
        return json.load(file)

def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

# -------------------------------
# Password Hashing
# -------------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------------
# Create New User
# -------------------------------
def create_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False

    users[username] = {
        "password": hash_password(password),
        "theme": "dark",
        "history": []
    }
    save_users(users)
    return True

# -------------------------------
# Authenticate User
# -------------------------------
def authenticate_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

# -------------------------------
# Save User History
# -------------------------------
def save_user_history(username: str, message: str):
    users = load_users()
    if username in users:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users[username]["history"].append(f"____________________________________________________________________________________________________________________________________\n[{timestamp}] {message}\n")
        save_users(users)

# -------------------------------
# Change Theme
# -------------------------------
def change_theme(username: str, theme: str):
    users = load_users()
    if username in users:
        users[username]["theme"] = theme
        save_users(users)

# -------------------------------
# Get User Info
# -------------------------------
def get_user_info(username: str):
    users = load_users()
    return users.get(username, None)



