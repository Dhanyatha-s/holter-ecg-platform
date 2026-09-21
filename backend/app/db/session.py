"""
database_url
     ↓
create_engine()
     ↓
PostgreSQL connection pool
     ↓
SessionLocal
     ↓
individual database sessions
this module is responsible for creating a database engine and a session factory for interacting with the database. It uses the configuration settings defined in the config.py file to establish a connection to the PostgreSQL database. The sessionmaker is used to create new Session objects that can be used to interact with the database in a thread-safe manner.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker #sessionmaker is a factory for creating new Session objects

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping = True, #this is to check if the connection is alive before using it
)

sessionLocal = sessionmaker(
    bind = engine,
    autoflush = False, #this is to prevent the session from automatically flushing changes to the database
    autocommit = False, #this is to prevent the session from automatically committing changes to the database
)