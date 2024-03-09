from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from db import create_database, Contact, get_db
from model import ContactInput
from collections import OrderedDict

app = FastAPI()

create_database()


@app.post("/identify")
def identify_contact(data: ContactInput, db: Session = Depends(get_db)):
    email = data.email
    phoneNumber = data.phoneNumber
    if email is None and phoneNumber is None:
        raise HTTPException(
            status_code=400, detail="Either email or phoneNumber is required"
        )

    contact_email = db.query(Contact).filter(Contact.email == email).first()
    contact_phone = db.query(Contact).filter(Contact.phoneNumber == phoneNumber).first()

    if contact_email or contact_phone:
        existing_contact = contact_email or contact_phone
        if existing_contact.linkPrecedence == "secondary":
            secondary_contact = Contact(
                phoneNumber=phoneNumber,
                email=email,
                linkedId=existing_contact.linkedId,
                linkPrecedence="secondary",
            )
            linkedid = existing_contact.linkedId
        else:
            secondary_contact = Contact(
                phoneNumber=phoneNumber,
                email=email,
                linkedId=existing_contact.id,
                linkPrecedence="secondary",
            )
            linkedid = existing_contact.id

        db.add(secondary_contact)
        db.commit()
        db.refresh(secondary_contact)

        primary_contact = db.query(Contact).filter(Contact.id == linkedid).first()
        secondary_contacts = (
            db.query(Contact)
            .filter(Contact.linkedId == linkedid, Contact.linkPrecedence == "secondary")
            .all()
        )

        email_list = [primary_contact.email] + [
            contact.email for contact in secondary_contacts if contact.email
        ]
        phone_list = [primary_contact.phoneNumber] + [
            contact.phoneNumber for contact in secondary_contacts if contact.phoneNumber
        ]

        response_data = OrderedDict(
            {
                "primaryContatctId": primary_contact.id,
                "emails": list(OrderedDict.fromkeys(email_list)),
                "phoneNumbers": list(OrderedDict.fromkeys(phone_list)),
                "secondaryContactIds": [contact.id for contact in secondary_contacts],
            }
        )

        return {"contact": response_data}

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

        email_list = [primary_contact.email] if primary_contact.email else []
        phone_list = (
            [primary_contact.phoneNumber] if primary_contact.phoneNumber else []
        )

        response_data = {
            "primaryContatctId": primary_contact.id,
            "emails": email_list,
            "phoneNumbers": phone_list,
            "secondaryContactIds": [],
        }

        return {"contact": response_data}


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
    return {"message": "Hello, FastAPI!"}


# @app.post("/create-contact")
# def create_contact(
#     phoneNumber: str = None,
#     email: str = None,
#     linkedId: int = None,
#     linkPrecedence: str = None,
#     db: Session = Depends(get_db),
# ):
#     if phoneNumber is None and email is None:
#         raise HTTPException(
#             status_code=400, detail="Either email or phoneNumber is required"
#         )
#     else:
#         new_contact = Contact(
#             phoneNumber=phoneNumber,
#             email=email,
#             linkedId=linkedId,
#             linkPrecedence=linkPrecedence,
#         )
#         db.add(new_contact)
#         db.commit()
#         db.refresh(new_contact)
#         return {"message": "Contact created successfully"}
