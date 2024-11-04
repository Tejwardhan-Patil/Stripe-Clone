import bcrypt
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
import re
import os
import sqlite3

class PasswordManager:
    def __init__(self, secret_key: str, salt: str = None):
        self.secret_key = secret_key
        self.salt = salt or os.urandom(16)
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.connection = sqlite3.connect("database.db")
        self.create_user_table()

    def create_user_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                password_last_set TIMESTAMP
            )
        ''')
        self.connection.commit()

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def generate_reset_token(self, user_email: str) -> str:
        return self.serializer.dumps(user_email, salt=self.salt)

    def verify_reset_token(self, token: str, expiration: int = 3600) -> str:
        try:
            email = self.serializer.loads(token, salt=self.salt, max_age=expiration)
        except Exception:
            return None
        return email

    def is_strong_password(self, password: str) -> bool:
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    def request_password_reset(self, user_email: str) -> str:
        reset_token = self.generate_reset_token(user_email)
        reset_url = f"https://website.com/reset-password?token={reset_token}"
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET password_last_set = ? WHERE email = ?", (datetime.now(), user_email))
        self.connection.commit()
        return reset_url

    def reset_password(self, token: str, new_password: str) -> bool:
        email = self.verify_reset_token(token)
        if email is None:
            return False
        if not self.is_strong_password(new_password):
            return False
        hashed_password = self.hash_password(new_password)
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET hashed_password = ?, password_last_set = ? WHERE email = ?", (hashed_password, datetime.now(), email))
        self.connection.commit()
        return True

    def update_password(self, email: str, current_password: str, new_password: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("SELECT hashed_password FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        if result is None:
            return False
        hashed_password_db = result[0]
        if not self.verify_password(current_password, hashed_password_db):
            return False
        if not self.is_strong_password(new_password):
            return False
        new_hashed_password = self.hash_password(new_password)
        cursor.execute("UPDATE users SET hashed_password = ?, password_last_set = ? WHERE email = ?", (new_hashed_password, datetime.now(), email))
        self.connection.commit()
        return True


class PasswordExpirationManager:
    def __init__(self, max_password_age: int = 90):
        self.max_password_age = max_password_age

    def is_password_expired(self, password_last_set: datetime) -> bool:
        return (datetime.now() - password_last_set).days > self.max_password_age

    def enforce_password_change(self, email: str) -> str:
        password_manager = PasswordManager(secret_key="secret-key")
        cursor = password_manager.connection.cursor()
        cursor.execute("SELECT password_last_set FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        if result is None:
            return None
        password_last_set = result[0]
        if self.is_password_expired(datetime.strptime(password_last_set, "%Y-%m-%d %H:%M:%S")):
            return password_manager.request_password_reset(email)
        return None


class PasswordHistoryManager:
    def __init__(self, history_limit: int = 5):
        self.history_limit = history_limit
        self.connection = sqlite3.connect("database.db")
        self.create_password_history_table()

    def create_password_history_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_history (
                user_id INTEGER,
                hashed_password TEXT NOT NULL,
                timestamp TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.connection.commit()

    def store_password_in_history(self, user_id: int, new_hashed_password: str):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO password_history (user_id, hashed_password, timestamp)
            VALUES (?, ?, ?)
        ''', (user_id, new_hashed_password, datetime.now()))
        self.connection.commit()

    def is_password_reused(self, user_id: int, new_password: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("SELECT hashed_password FROM password_history WHERE user_id = ?", (user_id,))
        history = cursor.fetchall()
        for past_password in history:
            if bcrypt.checkpw(new_password.encode('utf-8'), past_password[0].encode('utf-8')):
                return True
        return False


class PasswordResetRateLimiter:
    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        self.attempts = {}

    def can_attempt_reset(self, user_email: str) -> bool:
        now = datetime.now()
        attempts = self.attempts.get(user_email, [])
        attempts = [t for t in attempts if t > now - timedelta(minutes=self.window_minutes)]
        self.attempts[user_email] = attempts

        if len(attempts) >= self.max_attempts:
            return False

        self.attempts[user_email].append(now)
        return True

    def reset_attempts(self, user_email: str):
        if user_email in self.attempts:
            del self.attempts[user_email]