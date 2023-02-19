from typing import Union
import aiosql
from fastapi import FastAPI
from pydantic import BaseModel
from src import databaseConfig, Item, Bid

conn = databaseConfig()

app = FastAPI()
queries = aiosql.from_path("db/queries.sql", "psycopg2")

#post a new item for selling
@app.post("/items")
async def add_items(item: Item) -> None:
    try:
        await queries.add_items(conn, name=item.name, description=item.description, price=item.price, seller_email=item.seller_email,\
            date_of_posting=item.date_of_posting, date_of_sale=item.date_of_sale, status=item.status)
    except Exception as er:
        raise ("Exception occured", er)
    finally:
        conn.commit()
    return

#insert bids of a user on a particular item
@app.post("/bids")
async def add_bids(bid: Bid):
    try:
        await queries.add_bids(conn, item_id=bid.item_id, bidder_email=bid.bidder_email,\
        bid_amount=bid.bid_amount, date_of_bid=bid.date_of_bid)
    except Exception as er:
        raise ("Exception occured", er)
    finally:
        conn.commit()
    return

#get the current bids on a particular item
@app.get("/items/{item_id}")
async def get_bids(item_id: int):
    try:
        bid_list = await queries.get_bids(conn, item_id)
    except Exception as er:
        raise ("Exception occured", er)
    return bid_list.json()

#accept the bid of a user on a particular item
@app.post("/sales")
async def add_sales(bid_id: int):
    try:
        await queries.add_sales(conn, bid_id)
    except Exception as er:
        raise ("Exception occured", er)
    return 