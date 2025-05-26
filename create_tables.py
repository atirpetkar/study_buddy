# Create missing tables script
import os
import sys

# Add the project root to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.models import Base
from app.models.db import engine

# Create all tables that don't exist yet
print("Creating missing tables...")
Base.metadata.create_all(bind=engine)
print("Done. All tables have been created.")
