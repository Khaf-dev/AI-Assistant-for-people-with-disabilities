"""Database ORM Models for Vision Assistant"""
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User preferences and profile"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    disability_type = Column(String, default="visually_impaired")
    language = Column(String, default="en")
    speech_rate = Column(Integer, default=150)
    preferences = Column(JSON)  # Store user preferences as JSON
    emergency_contacts = Column(JSON)  # Store emergency contacts as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Person(Base):
    """Registered people for face recognition"""
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Belongs to which app user
    person_name = Column(String, index=True)  # Name of the person to recognize
    relationship = Column(String, default="contact")  # friend, family, colleague, etc.
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    notes = Column(Text)  # Additional info about the person


class FaceEncoding(Base):
    """Face encodings for recognition"""
    __tablename__ = "face_encodings"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True)  # References Person.id
    person_name = Column(String, index=True)  # Denormalized for easier lookup
    encoding = Column(LargeBinary)  # Serialized face encoding vector
    encoding_metadata = Column(JSON)  # Metadata: shape, model_used, etc.
    source = Column(String, default="manual")  # manual, auto-detected, etc.
    confidence = Column(Float, default=1.0)  # Confidence of encoding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SceneMemory(Base):
    """Historical scene descriptions and memories"""
    __tablename__ = "scene_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    scene_description = Column(Text)
    objects_detected = Column(Text)  # JSON list
    timestamp = Column(DateTime, default=datetime.utcnow)
    location = Column(String)
    image_hash = Column(String, unique=True)


class ConversationHistory(Base):
    """Chat logs and conversation history"""
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    user_message = Column(Text)
    assistant_response = Column(Text)
    intent = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


class TextExtraction(Base):
    """OCR text extraction log"""
    __tablename__ = "text_extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    extracted_text = Column(Text)
    confidence = Column(Float)
    language = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ObjectDetection(Base):
    """Object detection log"""
    __tablename__ = "object_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    object_name = Column(String)
    confidence = Column(Float)
    bounding_box = Column(Text)  # JSON coordinates
    timestamp = Column(DateTime, default=datetime.utcnow)
