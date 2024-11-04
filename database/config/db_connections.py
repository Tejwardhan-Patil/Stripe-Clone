from sqlalchemy import (create_engine, Column, Integer, String, DateTime, ForeignKey, Numeric, datetime, relationship)
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
import logging

# Set up logging for database connection handling
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base model for ORM definitions
Base = declarative_base()

class DatabaseConfig:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'sqlite') 
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_user = os.getenv('DB_USER', 'user')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
        self.db_name = os.getenv('DB_NAME', 'stripe_clone')
        self.db_url = self._build_database_url()

    def _build_database_url(self):
        if self.db_type == 'postgresql':
            return f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
        elif self.db_type == 'mysql':
            return f'mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
        else:
            return f'sqlite:///{self.db_name}.db'

    def get_database_url(self):
        return self.db_url

class DatabaseConnection:
    def __init__(self):
        config = DatabaseConfig()
        self.database_url = config.get_database_url()
        self.engine = None
        self.session_factory = None
        self.session = None

    def setup_database(self):
        logger.info(f"Setting up database connection to {self.database_url}")
        self.engine = create_engine(
            self.database_url,
            pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800
        )
        self.session_factory = scoped_session(sessionmaker(bind=self.engine))
        self.session = self.session_factory()

    def create_tables(self):
        logger.info("Creating tables in the database...")
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        logger.info("Dropping all tables in the database...")
        Base.metadata.drop_all(self.engine)

    def get_session(self):
        logger.info("Getting database session...")
        return self.session_factory()

    def close_session(self):
        logger.info("Closing database session...")
        if self.session:
            self.session.close()

    def dispose_engine(self):
        logger.info("Disposing the engine...")
        if self.engine:
            self.engine.dispose()

    def test_connection(self):
        try:
            logger.info("Testing database connection...")
            conn = self.engine.connect()
            logger.info("Database connection successful.")
            conn.close()
        except Exception as e:
            logger.error(f"Database connection failed: {e}")

# SQLite-specific connection (for local development)
class SQLiteConnection(DatabaseConnection):
    def __init__(self):
        super().__init__()

# PostgreSQL-specific connection (for production)
class PostgreSQLConnection(DatabaseConnection):
    def __init__(self):
        super().__init__()

# MySQL-specific connection
class MySQLConnection(DatabaseConnection):
    def __init__(self):
        super().__init__()

# Utility function to get the correct database connection
def get_database_connection():
    db_type = os.getenv('DB_TYPE', 'sqlite')
    if db_type == 'postgresql':
        return PostgreSQLConnection()
    elif db_type == 'mysql':
        return MySQLConnection()
    else:
        return SQLiteConnection()

# Usage of DatabaseConnection
if __name__ == "__main__":
    connection = get_database_connection()
    connection.setup_database()
    connection.test_connection()

    # Operations: create and drop tables
    connection.create_tables()

    # Close and dispose the connection after use
    connection.close_session()
    connection.dispose_engine()

# ORM Model: User
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

# ORM Model: Payment
class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"

# Transaction management within a session
def manage_transaction():
    db_session = connection.get_session()
    try:
        # Adding a user
        new_user = User(username="Person", email="person@website.com", password_hash="hashed_password")
        db_session.add(new_user)
        db_session.commit()
        logger.info(f"User {new_user.username} added successfully.")
    except Exception as e:
        db_session.rollback()
        logger.error(f"Transaction failed: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    connection = get_database_connection()
    connection.setup_database()
    manage_transaction()
    connection.dispose_engine()