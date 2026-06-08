import os
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    new_user = User(email="test@test.com", password_hash=generate_password_hash("password123"))
    db.session.add(new_user)
    try:
        db.session.commit()
        print("User added successfully.")
    except Exception as e:
        print(f"Error adding user: {e}")
        db.session.rollback()

    users = User.query.all()
    print(f"Total users in db: {len(users)}")
    for u in users:
        print(u.email)
