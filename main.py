from typing import Union

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from pydantic import BaseModel
import aiosql

load_dotenv()

DATABASE = os.getenv("DATABASE")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

conn = psycopg2.connect(
    database=DATABASE,
    user=POSTGRES_USER,
    password=POSTGRES_PASS,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    cursor_factory=RealDictCursor,
)

print("Opened database successfully!")

app = FastAPI()

# http://127.0.0.1:8000/
@app.get("/")
def read_root():
    return {"Hello": "World"}


# http://127.0.0.1:8000/items/5?q=somequery
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# item_queries is aiosql object which is used to call the functions in db/items.sql
queries = aiosql.from_path("db/queries.sql", "psycopg2") 

# Pydantic model for item which is used in the post request
class Item(BaseModel):
    name: str
    description: str 
    price: float
    seller_email: str

# http://127.0.0.1:8000/items
@app.post("/items")
def create_item(item: Item):
    try:
        # post_item is a function in db/items.sql
        a: int = queries.post_item(conn, name = item.name, description = item.description, price = item.price, seller_email = item.seller_email)
    except:
        raise HTTPException(status_code=400, detail="Insert item failed")
    else: 
        raise HTTPException(status_code=200, detail="Insert item successful") 
    finally: 
        conn.commit()


class Bid(BaseModel):
    item_id: int
    bidder_email: str 
    bid_amount: float

# http://127.0.0.1:8000/bids/<item_id>
@app.post("/bids/{item_id}")
def create_bid(item_id: int, bid: Bid):
    try:
        # post_bid is a function in db/bids.sql
        a: int = queries.post_bid(conn, item_id = bid.item_id, bidder_email = bid.bidder_email, bid_amount = bid.bid_amount)
    except:
        raise HTTPException(status_code=400, detail="Insert bid failed")
    else: 
        raise HTTPException(status_code=200, detail="Insert bid successful") 
    finally: 
        conn.commit()