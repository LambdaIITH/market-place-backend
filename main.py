from typing import Union

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from pydantic import BaseModel
import aiosql
import json

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
        res: int = queries.post_item(conn, name = item.name, description = item.description, price = item.price, seller_email = item.seller_email)
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail="Insert item failed")
    else: 
        raise HTTPException(status_code=200, detail="Insert item successful") 
    finally: 
        conn.commit()

# Pydantic model for bid which is used in the post request
class Bid(BaseModel):
    item_id: int | None
    bidder_email: str 
    bid_amount: float

# http://127.0.0.1:8000/bids/<item_id>
@app.post("/bids/{item_id}")
def create_bid(item_id: int, bid: Bid):
    try:
        # post_bid is a function in db/bids.sql
        res: int = queries.post_bid(conn, item_id = item_id, bidder_email = bid.bidder_email, bid_amount = bid.bid_amount)
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail="Insert bid failed")
    else: 
        raise HTTPException(status_code=200, detail="Insert bid successful") 
    finally: 
        conn.commit()


# currently: http://127.0.0.1:8000/bids/accept/<item_id>
# future: http://127.0.0.1:8000/bids/accept/<item_id>/<bid_id>
@app.post("/bids/accept/{item_id}/{id}")
def accept_bid(item_id: int):
    try:
        # accept_bid is a function in db/bids.sql
        res: int = queries.accept_bid(conn, item_id = item_id)
        # id is the id of the bid that was accepted, which could be a future addition to the code
    
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail="Accept bid failed")
    else: 
        raise HTTPException(status_code=200, detail="Accept bid successful")
    finally: 
        conn.commit() 


@app.get("/bids/{item_id}")
def get_item(item_id: int):
    try:
        # get_item is a function in db/items.sql
        res: dict = queries.get_bids_for_item(conn, item_id = item_id)
        res: str = json.dumps(res[0],default=str) # convert dict to json string, non-json serializable data types are converted to strings
        res_json = json.loads(res) # convert to json object

    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail="Get item failed")
    else: 
        return res_json
    finally: 
        conn.commit()