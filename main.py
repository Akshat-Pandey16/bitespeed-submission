from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from db import create_database, get_db, Contact
from datetime import datetime

app = FastAPI()

create_database()


@app.post("/identify", status_code=200)
def identify(email: str = None, phoneNumber: str = None, db: Session = Depends(get_db)):
    if email is None and phoneNumber is None:
        raise HTTPException(
            status_code=400, detail="Either email or phoneNumber must be provided."
        )

    primary_contact = None

    if email:
        primary_contact = (
            db.query(Contact)
            .filter((Contact.email == email) | (Contact.linkPrecedence == "primary"))
            .first()
        )
    elif phoneNumber:
        primary_contact = (
            db.query(Contact)
            .filter(
                (Contact.phoneNumber == phoneNumber)
                | (Contact.linkPrecedence == "primary")
            )
            .first()
        )

    if primary_contact:
        secondary_contact = Contact(
            phoneNumber=phoneNumber,
            email=email,
            linkedId=primary_contact.id,
            linkPrecedence="secondary",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        db.add(secondary_contact)
        db.commit()
        db.refresh(secondary_contact)

        return {"message": "Secondary contact created successfully."}

    new_contact = Contact(
        phoneNumber=phoneNumber,
        email=email,
        linkedId=None,
        linkPrecedence="primary",
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return {"message": "Primary contact created successfully."}


@app.get("/view-contacts")
async def view_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return {"contacts": contacts}


@app.post("/flush-database")
async def flush_database(db: Session = Depends(get_db)):
    db.query(Contact).delete()
    db.commit()
    return {"message": "Database flushed successfully"}


@app.get("/")
def read_root():
    return {"Hello": "World"}
