from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime

class Item(BaseModel):
    id: int | None = None
    name: str
    description: str
    price: float
    seller_email: EmailStr
    date_of_posting: date
    date_of_sale: date | None = None
    status: bool

    @validator("date_of_posting", pre=True)
    def parse_birthdate(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()