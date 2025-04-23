# create_db.py: Create SQLite DB for SQLAlchemy models
import os
from sqlalchemy import create_engine
from app.models.models import Base

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# SQLite DB path
DB_PATH = os.path.join('db', 'codedspace.db')
engine = create_engine(f'sqlite:///{DB_PATH}')

# Create all tables
Base.metadata.create_all(engine)

print(f"Database created at {DB_PATH}")
