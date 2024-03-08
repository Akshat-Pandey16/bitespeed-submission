from pydantic import BaseModel
from typing import Optional

class ContactModel(BaseModel):
  email: Optional[str] = None
  phoneNumber: Optional[str] = None