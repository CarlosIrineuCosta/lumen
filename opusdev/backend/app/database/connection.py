"""
Database connection management for Lumen Photography Platform
Uses Cloud SQL PostgreSQL with connection pooling
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from google.cloud.sql.connector import Connector
import sqlalchemy

# Database configuration
DATABASE_USER = os.getenv("DB_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD", "")
DATABASE_NAME = os.getenv("DB_NAME", "lumen")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME", "lumen-photo-app-20250731:us-central1:lumen-db")

# Initialize Cloud SQL Connector
connector = Connector()

def getconn():
    """Create connection to Cloud SQL PostgreSQL instance"""
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        db=DATABASE_NAME,
    )
    return conn

# Create SQLAlchemy engine with Cloud SQL connector
engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
    poolclass=NullPool,  # Disable SQLAlchemy connection pooling (Cloud SQL handles this)
    echo=os.getenv("DEBUG", "false").lower() == "true"  # Enable SQL logging in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all tables in the database (for development only)"""
    Base.metadata.drop_all(bind=engine)