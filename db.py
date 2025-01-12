from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Name of the database to be used
name = 'products'
db_path = f'database/{name}.db'

# Create the engine that allows SQLAlchemy to connect to the SQLite database
engine = create_engine(f'sqlite:///{db_path}',
                       connect_args={"check_same_thread": False}
                       )

# Create the session to interact with the database through transactions
Session = sessionmaker(bind=engine)
session = Session()

# Declarative base to map classes to database tables
Base = declarative_base()

