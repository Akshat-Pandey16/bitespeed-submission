from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from db import create_database, Contact, get_db
from model import ContactInput

app = FastAPI()

create_database()


def get_contact(db: Session, email: str = None, phoneNumber: str = None):
    if email:
        return db.query(Contact).filter(Contact.email == email).first()
    elif phoneNumber:
        return db.query(Contact).filter(Contact.phoneNumber == phoneNumber).first()


def update_field(db: Session, contact, linked_id, precedence):
    contact.linkedId = linked_id
    contact.linkPrecedence = precedence
    db.commit()
    db.refresh(contact)

def get_info(primary_contact, secondary_contacts):
    primary_email = primary_contact.email
    secondary_emails = {contact.email for contact in secondary_contacts if contact.email}
    all_emails = list(secondary_emails)
    if primary_email:
        all_emails.insert(0, primary_email)

    primary_phone = primary_contact.phoneNumber
    secondary_phones = {contact.phoneNumber for contact in secondary_contacts if contact.phoneNumber}
    all_phones = list(secondary_phones)
    if primary_phone:
        all_phones.insert(0, primary_phone)

    all_emails = list(set(all_emails))
    all_phones = list(set(all_phones))

    return {
        "primaryContatctId": primary_contact.id,
        "emails": all_emails,
        "phoneNumbers": all_phones,
        "secondaryContactIds": [contact.id for contact in secondary_contacts],
    }


@app.post("/identify")
def identify_contact(data: ContactInput, db: Session = Depends(get_db)):
    email = data.email
    phoneNumber = data.phoneNumber
    if email is None and phoneNumber is None:
        raise HTTPException(
            status_code=400, detail="Either email or phoneNumber is required"
        )

    contact_email = get_contact(db, email=email)
    contact_phone = get_contact(db, phoneNumber=phoneNumber)

    if contact_email and contact_phone:
        if contact_email.linkPrecedence == "primary" and contact_phone.linkPrecedence == "primary":
            if contact_email.id > contact_phone.id:
                update_field(db, contact_email, contact_phone.id, "secondary")
                primary_contact = contact_phone
            else:
                update_field(db, contact_phone, contact_email.id, "secondary")
                primary_contact = contact_email

            secondary_contacts = db.query(Contact).filter(Contact.linkedId == primary_contact.id, Contact.linkPrecedence == "secondary").all()

            return {"contact": get_info(primary_contact, secondary_contacts)}

    elif contact_email or contact_phone:
        existing_contact = contact_email or contact_phone
        if existing_contact.linkPrecedence == "secondary":
            linked_id = existing_contact.linkedId
        else:
            linked_id = existing_contact.id

        secondary_contact = Contact(
            phoneNumber=phoneNumber,
            email=email,
            linkedId=linked_id,
            linkPrecedence="secondary",
        )
        db.add(secondary_contact)
        db.commit()
        db.refresh(secondary_contact)

        primary_contact = db.query(Contact).filter(Contact.id == linked_id).first()
        secondary_contacts = db.query(Contact).filter(Contact.linkedId == linked_id, Contact.linkPrecedence == "secondary").all()

        return {"contact": get_info(primary_contact, secondary_contacts)}

    else:
        primary_contact = Contact(
            phoneNumber=phoneNumber,
            email=email,
            linkedId=None,
            linkPrecedence="primary",
        )
        db.add(primary_contact)
        db.commit()
        db.refresh(primary_contact)

        return {"contact": {
            "primaryContatctId": primary_contact.id,
            "emails": [primary_contact.email] if primary_contact.email else [],
            "phoneNumbers": [primary_contact.phoneNumber] if primary_contact.phoneNumber else [],
            "secondaryContactIds": [],
        }}


@app.post("/flush-database")
def flush_database(db: Session = Depends(get_db)):
    try:
        db.query(Contact).delete()
        db.commit()
        return {"message": "Database flushed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error flushing database: {str(e)}"
        )


@app.get("/view-database")
def view_database(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return {"contacts": contacts}


@app.get("/")
def read_root():
    return {"message": "Go to /docs to view the API documentation."}
