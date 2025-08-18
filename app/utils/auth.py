# Authentication utilities
import json
import hashlib

def load_users():
    with open('app/data/db.json') as f:
        return json.load(f)["users"]

def verify_login(email, password, role):
    users = load_users()
    for user in users:
        if user["email"] == email and user["role"] == role:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if user["password"] == hashed:
                if user.get("first_login", False):
                    return True, "first_login"
                return True, "success"
            else:
                return False, "Incorrect password"
    return False, "User not found"
