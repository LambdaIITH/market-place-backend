from pydantic import BaseModel, EmailStr, PositiveInt, validator


class Item(BaseModel):
    name: str
    email: EmailStr
    phone_number: PositiveInt

    @validator("phone_number")

    def phone_length(cls, v):
        if len(str(v)) != 10:
            raise ValueError("Phone number must be of ten digits")
        return v