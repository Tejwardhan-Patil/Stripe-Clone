from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app as app

Base = declarative_base()

# Database engine creation and session setup
engine = create_engine('sqlite:///website.db')
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    payments = relationship("Payment", back_populates="user", cascade="all, delete")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, expires_in=3600):
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def __repr__(self):
        return f'<User {self.username}>'


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="payments")

    def __repr__(self):
        return f'<Payment {self.id}, Status {self.status}, Amount {self.amount}>'


# UserManager class for handling user operations
class UserManager:

    @staticmethod
    def create_user(username, email, password):
        user = User(username=username, email=email, password=password)
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def authenticate(username_or_email, password):
        user = session.query(User).filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def reset_password(user_id, new_password):
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            session.commit()

    @staticmethod
    def deactivate_user(user_id):
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.is_active = False
            session.commit()

    @staticmethod
    def generate_password_reset_token(user_id):
        user = session.query(User).filter_by(id=user_id).first()
        return user.generate_token() if user else None

    @staticmethod
    def verify_password_reset_token(token):
        user_id = User.verify_token(token)
        if not user_id:
            return None
        user = session.query(User).filter_by(id=user_id).first()
        return user if user and user.is_active else None


# Query functions
def get_user_by_id(user_id):
    return session.query(User).filter_by(id=user_id).first()

def get_user_by_email(email):
    return session.query(User).filter_by(email=email).first()

def delete_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        session.delete(user)
        session.commit()
        return True
    return False


# JWT token management functions
def create_access_token(user):
    return user.generate_token()

def verify_access_token(token):
    user_id = User.verify_token(token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).first()
        return user if user and user.is_active else None
    return None


# Initialize database
def initialize_database():
    Base.metadata.create_all(engine)


# Entry point for testing and database initialization
if __name__ == '__main__':
    initialize_database()

    # Create a test user
    new_user = UserManager.create_user('Person1', 'person1@website.com', 'securepassword123')
    print(new_user)

    # Test password authentication
    authenticated_user = UserManager.authenticate('person1@website.com', 'securepassword123')
    print(authenticated_user)

    # Test token generation and verification
    token = create_access_token(new_user)
    print(f'Generated Token: {token}')

    verified_user = verify_access_token(token)
    print(f'User from Token: {verified_user}')