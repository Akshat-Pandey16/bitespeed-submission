from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.sql import func

DATABASE_URL = "sqlite:///./contact.db"

engine = create_engine(DATABASE_URL)
Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedId = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    linkPrecedence = Column(String, nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    deletedAt = Column(DateTime(timezone=True), nullable=True)

    linked_contacts = relationship("Contact", remote_side=[id])


def create_database():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
