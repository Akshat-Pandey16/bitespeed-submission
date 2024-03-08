from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    MetaData,
)
from sqlalchemy.orm import declarative_base, Session

DATABASE_URL = "sqlite:///./contact.db"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

Base = declarative_base(metadata=metadata)


class Contact(Base):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedId = Column(Integer, ForeignKey("contact.id"), nullable=True)
    linkPrecedence = Column(Enum("primary", "secondary"), nullable=False)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    deletedAt = Column(DateTime, nullable=True)


Base.metadata.create_all(bind=engine)


def create_database():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
