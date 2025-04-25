# app/models/create_tables.py
from sqlalchemy import create_engine
from .models import Base
from .db import SQLALCHEMY_DATABASE_URL
import os

def init_db():
    # Make sure the db directory exists
    db_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/db'
    os.makedirs(db_dir, exist_ok=True)
    
    # Create engine and all tables
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

if __name__ == "__main__":
    init_db()