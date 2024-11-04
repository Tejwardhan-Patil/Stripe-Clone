from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models.user import User 
from database.config.db_connections import get_database_url  

# Create a new database session
engine = create_engine(get_database_url())
Session = sessionmaker(bind=engine)
session = Session()

def seed_users():
    users = [
        {
            "first_name": "Person1",
            "last_name": "Lastname1",
            "email": "person1@website.com",
            "password": "hashedpassword1",  # Passwords are already hashed
            "phone_number": "1234567890",
            "address": "123 First Street, City, Country",
            "role": "admin",
            "is_active": True,
        },
        {
            "first_name": "Person2",
            "last_name": "Lastname2",
            "email": "person2@website.com",
            "password": "hashedpassword2",
            "phone_number": "0987654321",
            "address": "456 Second Street, City, Country",
            "role": "user",
            "is_active": True,
        },
        {
            "first_name": "Person3",
            "last_name": "Lastname3",
            "email": "person3@website.com",
            "password": "hashedpassword3",
            "phone_number": "1122334455",
            "address": "789 Third Street, City, Country",
            "role": "user",
            "is_active": True,
        },
        {
            "first_name": "Person4",
            "last_name": "Lastname4",
            "email": "person4@website.com",
            "password": "hashedpassword4",
            "phone_number": "5566778899",
            "address": "101 First Avenue, City, Country",
            "role": "user",
            "is_active": False,  # Inactive user
        },
        {
            "first_name": "Person5",
            "last_name": "Lastname5",
            "email": "person5@website.com",
            "password": "hashedpassword5",
            "phone_number": "1233211234",
            "address": "202 Second Avenue, City, Country",
            "role": "user",
            "is_active": True,
        },
    ]

    # Insert all users into the database
    for user_data in users:
        user = User(**user_data)
        session.add(user)

    session.commit()
    print("Users have been seeded successfully.")

if __name__ == "__main__":
    seed_users()