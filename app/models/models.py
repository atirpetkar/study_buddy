from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
   return str(uuid.uuid4())

class User(Base):
   __tablename__ = 'users'
   id = Column(String, primary_key=True, default=generate_uuid)
   email = Column(String, unique=True, nullable=False)
   hashed_password = Column(String, nullable=False)
   created_at = Column(DateTime, default=datetime.utcnow)

class UserProfile(Base):
   __tablename__ = 'user_profiles'
   user_id = Column(String, ForeignKey('users.id'), primary_key=True)
   exam_type = Column(String)
   study_preferences = Column(Text)
   available_study_time = Column(Text)
   goals = Column(String)
   initial_topics = Column(Text)
   learner_profile = Column(Text)
   created_at = Column(DateTime, default=datetime.utcnow)
   updated_at = Column(DateTime, default=datetime.utcnow)

class UploadedDocument(Base):
   __tablename__ = 'uploaded_documents'
   id = Column(String, primary_key=True, default=generate_uuid)
   user_id = Column(String, ForeignKey('users.id'))
   file_name = Column(String)
   file_path = Column(String)
   uploaded_at = Column(DateTime, default=datetime.utcnow)

class DocumentChunk(Base):
   __tablename__ = 'document_chunks'
   id = Column(String, primary_key=True, default=generate_uuid)
   document_id = Column(String, ForeignKey('uploaded_documents.id'))
   chunk_text = Column(Text)
   embedding = Column(String)  # Storing as stringified JSON or base64, ChromaDB stores embeddings separately
   chunk_index = Column(Integer)
   created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
   __tablename__ = 'conversations'
   id = Column(String, primary_key=True, default=generate_uuid)
   user_id = Column(String, ForeignKey('users.id'))
   message = Column(Text)
   response = Column(Text)
   source = Column(Text)
   created_at = Column(DateTime, default=datetime.utcnow)

class StudyPlan(Base):
   __tablename__ = 'study_plans'
   id = Column(String, primary_key=True, default=generate_uuid)
   user_id = Column(String, ForeignKey('users.id'))
   schedule = Column(Text)  # JSON stored as string
   generated_at = Column(DateTime, default=datetime.utcnow)

class Quiz(Base):
   __tablename__ = 'quizzes'
   id = Column(String, primary_key=True, default=generate_uuid)
   user_id = Column(String, ForeignKey('users.id'))
   related_document_id = Column(String, ForeignKey('uploaded_documents.id'))
   quiz_content = Column(Text)  # JSON stored as string
   created_at = Column(DateTime, default=datetime.utcnow)

class QuizAttempt(Base):
   __tablename__ = 'quiz_attempts'
   id = Column(String, primary_key=True, default=generate_uuid)
   quiz_id = Column(String, ForeignKey('quizzes.id'))
   user_id = Column(String, ForeignKey('users.id'))
   answers = Column(Text)  # JSON stored as string
   score = Column(Float)
   taken_at = Column(DateTime, default=datetime.utcnow)
   
class ProgressTracking(Base):
   __tablename__ = 'progress_tracking'
   id = Column(String, primary_key=True, default=generate_uuid)
   user_id = Column(String, ForeignKey('users.id'))
   topic = Column(String)
   proficiency = Column(Float, default=0.0)
   confidence = Column(Float, default=0.0)
   last_interaction = Column(DateTime, default=datetime.utcnow)
   interaction_type = Column(String)
