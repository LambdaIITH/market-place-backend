from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime

class Bid(BaseModel):
    id: int | None = None
    item_id: int
    bidder_email: EmailStr
    bid_amount: float
    date_of_bid: date

    @validator("date_of_bid", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()