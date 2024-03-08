from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import create_tables, Contact, SessionLocal

app = FastAPI()

create_tables()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/identify", status_code=200)
async def identify(email: str, phone_number: str, db: Session = Depends(get_db)):
    email = email
    phone_number = phone_number

    if not email and not phone_number:
        raise HTTPException(
            status_code=400, detail="Either Email or Ph. Number must be provided."
        )

    existing_contact = (
        db.query(Contact)
        .filter((Contact.email == email) | (Contact.phoneNumber == phone_number))
        .first()
    )

    if existing_contact:
        if (
            existing_contact.email == email
            and existing_contact.phoneNumber == phone_number
        ):
            return {"message": "User already exists"}

        new_secondary_contact = Contact(
            email=email,
            phoneNumber=phone_number,
            linkPrecedence="secondary",
            linkedId=existing_contact.id,
        )
        db.add(new_secondary_contact)
        db.commit()

        secondary_contacts = (
            db.query(Contact)
            .filter(
                Contact.linkedId == existing_contact.id,
                Contact.linkPrecedence == "secondary",
            )
            .all()
        )

        unique_emails = list(
            set(
                [existing_contact.email]
                + [contact.email for contact in secondary_contacts]
            )
        )
        unique_phone_numbers = list(
            set(
                [existing_contact.phoneNumber]
                + [contact.phoneNumber for contact in secondary_contacts]
            )
        )

        updated_contact = {
            "primaryContactId": existing_contact.id,
            "emails": unique_emails,
            "phoneNumbers": unique_phone_numbers,
            "secondaryContactIds": [contact.id for contact in secondary_contacts],
        }

    else:
        new_contact = Contact(
            email=email, phoneNumber=phone_number, linkPrecedence="primary"
        )
        db.add(new_contact)
        db.commit()

        updated_contact = {
            "primaryContactId": new_contact.id,
            "emails": [new_contact.email],
            "phoneNumbers": [new_contact.phoneNumber],
            "secondaryContactIds": [],
        }

    return {"contact": updated_contact}


@app.get("/view-contacts")
async def view_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return {"contacts": contacts}


@app.post("/flush-database")
async def flush_database(db: Session = Depends(get_db)):
    db.query(Contact).delete()
    db.commit()
    return {"message": "Database flushed successfully"}


# @app.post("/create-database")
# async def create_database(db: Session = Depends(get_db)):
#     # Check if the "contacts" table already exists
#     if not db.dialect.has_table(db, "contacts"):
#         create_tables()
#         return {"message": "Database created successfully"}
#     else:
#         return {"message": "Database already exists"}
