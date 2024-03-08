from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = "sqlite:///./contact.db" 

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedId = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    linkPrecedence = Column(String, nullable=False)  # "primary" or "secondary"
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    deletedAt = Column(DateTime(timezone=True), nullable=True)

def create_tables():
    with engine.connect() as connection:
        if not connection.dialect.has_table(connection, "contacts"):
            Base.metadata.create_all(bind=engine)

