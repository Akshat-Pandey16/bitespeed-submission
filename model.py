from pydantic import BaseModel
from typing import Optional

class ContactInput(BaseModel):
  email: Optional[str] = None
  phoneNumber: Optional[str] = None