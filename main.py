from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from db import create_database, get_db, Contact
from datetime import datetime
from collections import OrderedDict
from model import ContactModel

app = FastAPI()

create_database()


def get_exist_contact(db: Session, email: str = None, phoneNumber: str = None):
    if email:
        return (
            db.query(Contact)
            .filter((Contact.email == email) | (Contact.linkPrecedence == "primary"))
            .first()
        )
    elif phoneNumber:
        return (
            db.query(Contact)
            .filter(
                (Contact.phoneNumber == phoneNumber)
                | (Contact.linkPrecedence == "primary")
            )
            .first()
        )


def get_linked_info(db: Session, primary_contact_id: int, link_precedence: str):
    contacts = (
        db.query(Contact)
        .filter(
            Contact.linkedId == primary_contact_id,
            Contact.linkPrecedence == link_precedence,
        )
        .all()
    )

    result = {
        "emails": [contact.email for contact in contacts if contact.email is not None],
        "phoneNumbers": [
            contact.phoneNumber
            for contact in contacts
            if contact.phoneNumber is not None
        ],
        "contactIds": [contact.id for contact in contacts],
    }

    return result


@app.post("/identify", status_code=200)
def identify(data: ContactModel, db: Session = Depends(get_db)):
    email = data.email
    phoneNumber = data.phoneNumber
    if email is None and phoneNumber is None:
        raise HTTPException(
            status_code=400, detail="Either email or phoneNumber must be provided."
        )

    exist_contact = get_exist_contact(db, email=email, phoneNumber=phoneNumber)

    if exist_contact:
        secondary_contact = Contact(
            phoneNumber=phoneNumber,
            email=email,
            linkedId=exist_contact.id,
            linkPrecedence="secondary",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        db.add(secondary_contact)
        db.commit()
        db.refresh(secondary_contact)

        secondary_info = get_linked_info(db, exist_contact.id, "secondary")

        return OrderedDict(
            {
                "contact": {
                    "primaryContactId": exist_contact.id,
                    "emails": list(
                        set([exist_contact.email] + secondary_info["emails"])
                    ),
                    "phoneNumbers": list(
                        set(
                            [exist_contact.phoneNumber] + secondary_info["phoneNumbers"]
                        )
                    ),
                    "secondaryContactIds": secondary_info["contactIds"],
                }
            }
        )

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

    return OrderedDict(
        {
            "contact": {
                "primaryContactId": new_contact.id,
                "emails": [new_contact.email],
                "phoneNumbers": [new_contact.phoneNumber],
                "secondaryContactId": None,
            }
        }
    )


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
