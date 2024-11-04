import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Define the Base class for models
Base = declarative_base()

class Config:
    """Base configuration class for the database."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

class DevelopmentConfig(Config):
    """Development environment specific configuration."""
    DATABASE_URL = os.getenv("DEV_DATABASE_URL", "postgresql://dev_user:dev_password@localhost/dev_db")
    SQLALCHEMY_ECHO = True  # Enable SQL echo for debugging

class TestingConfig(Config):
    """Testing environment specific configuration."""
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://test_user:test_password@localhost/test_db")
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    """Production environment specific configuration."""
    DATABASE_URL = os.getenv("PROD_DATABASE_URL", "postgresql://prod_user:prod_password@localhost/prod_db")
    SQLALCHEMY_ECHO = False

# Configuration mapping
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}

# Set default environment configuration
env = os.getenv("FLASK_ENV", "development")
current_config = config_by_name.get(env, DevelopmentConfig)

# Create engine and session factory
engine = create_engine(current_config.DATABASE_URL, echo=current_config.SQLALCHEMY_ECHO)
SessionFactory = scoped_session(sessionmaker(bind=engine))

# Utility function to get the current session
def get_session():
    """Returns a new database session."""
    return SessionFactory()

def close_session(session):
    """Closes the provided session."""
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Function to initialize the database
def init_db():
    """Initializes the database by creating all tables."""
    import backend.src.models.user_model as user_model
    import backend.src.models.payment_model as payment_model
    Base.metadata.create_all(bind=engine)

# Custom error handling for database connection
class DatabaseConnectionError(Exception):
    """Custom exception class for database connection errors."""
    def __init__(self, message="Failed to connect to the database"):
        self.message = message
        super().__init__(self.message)

# Function to test database connection
def test_db_connection():
    """Test the database connection by attempting to connect and run a basic query."""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            for row in result:
                print(f"Test query result: {row[0]}")
    except Exception as e:
        raise DatabaseConnectionError(str(e))

# Class for handling database migrations
class DatabaseMigrations:
    """Handles database migrations."""
    
    @staticmethod
    def run_migration():
        """Runs the migration script."""
        import subprocess
        try:
            result = subprocess.run(["alembic", "upgrade", "head"], check=True)
            print("Migration completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Migration failed: {e}")

    @staticmethod
    def create_migration(message: str):
        """Creates a new migration with the provided message."""
        import subprocess
        try:
            result = subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)
            print(f"Migration '{message}' created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Migration creation failed: {e}")

# Function to seed the database with initial data
def seed_data():
    """Seeds the database with initial data."""
    session = get_session()
    try:
        from backend.src.models.user_model import User
        from backend.src.models.payment_model import Payment
        
        # Seed data for users
        user1 = User(username="Person1", email="person1@website.com")
        user2 = User(username="Person2", email="person2@website.com")
        session.add_all([user1, user2])

        # Seed data for payments
        payment1 = Payment(user_id=user1.id, amount=100.0, status="completed")
        payment2 = Payment(user_id=user2.id, amount=250.0, status="pending")
        session.add_all([payment1, payment2])

        session.commit()
        print("Database seeded successfully.")
    except Exception as e:
        session.rollback()
        print(f"Seeding failed: {e}")
    finally:
        close_session(session)

# Function to rollback transactions
def rollback_transaction(session):
    """Rolls back the current transaction."""
    session.rollback()

# Custom logging for database operations
import logging

logger = logging.getLogger("database_logger")
logger.setLevel(logging.DEBUG)

# Logging handler to log into a file
file_handler = logging.FileHandler("database_operations.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Log any database errors
def log_db_error(error_message):
    """Logs database errors."""
    logger.error(f"Database Error: {error_message}")

# Exception handling for database session management
class SessionManager:
    """Context manager to handle sessions."""
    
    def __enter__(self):
        self.session = get_session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            rollback_transaction(self.session)
            log_db_error(f"Exception: {exc_value}")
        close_session(self.session)

# Use of the session manager
def process_data():
    """Process data using session manager."""
    with SessionManager() as session:
        from backend.src.models.user_model import User
        from backend.src.models.payment_model import Payment

        # Create a new user
        new_user = User(username="NewPerson", email="newperson@website.com")
        session.add(new_user)
        session.commit()

        # Query the database for users
        users = session.query(User).all()
        for user in users:
            print(f"User: {user.username}, Email: {user.email}")

        # Create a new payment for the new user
        new_payment = Payment(user_id=new_user.id, amount=150.0, status="completed")
        session.add(new_payment)
        session.commit()

        # Query the database for payments
        payments = session.query(Payment).filter_by(user_id=new_user.id).all()
        for payment in payments:
            print(f"Payment: {payment.amount}, Status: {payment.status}")

# Clean up resources when shutting down
def shutdown():
    """Closes the database connection and resources when shutting down."""
    engine.dispose()
    print("Database engine disposed.")