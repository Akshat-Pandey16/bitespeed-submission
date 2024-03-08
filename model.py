from pydantic import BaseModel


class IdentifyInput(BaseModel):
    email: str
    phone_number: str
