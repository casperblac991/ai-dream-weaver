import hashlib
from models import create_user, get_user_by_email

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    hashed = hash_password(password)
    return create_user(username, email, hashed)

def login_user(email, password):
    user = get_user_by_email(email)
    if user and user["password"] == hash_password(password):
        return user
    return None
