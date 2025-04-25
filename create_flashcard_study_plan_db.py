# create_tables.py
from app.models.models import Base, Flashcard, FlashcardReview
from app.models.db import engine
import sqlite3
import os

def create_tables():
    """
    Create the new tables for flashcards and progress tracking
    without using Alembic
    """
    print("Creating tables...")
    
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'codedspace.db')
    print(f"Database path: {db_path}")
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Flashcard table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flashcards (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        related_document_id TEXT,
        flashcard_content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (related_document_id) REFERENCES uploaded_documents(id)
    )
    ''')
    
    # Create FlashcardReview table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flashcard_reviews (
        id TEXT PRIMARY KEY,
        flashcard_id TEXT,
        user_id TEXT,
        confidence INTEGER,
        next_review_at TIMESTAMP,
        reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (flashcard_id) REFERENCES flashcards(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Create UserProfile table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_profiles (
        user_id TEXT PRIMARY KEY,
        exam_type TEXT,
        study_preferences TEXT,
        available_study_time TEXT,
        goals TEXT,
        initial_topics TEXT,
        learner_profile TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Create StudyPlan table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_plans (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        schedule TEXT,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()