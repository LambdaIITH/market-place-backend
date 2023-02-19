from typing import Union
import aiosql
from fastapi import FastAPI
from pydantic import BaseModel
from src import databaseConfig, Item

conn = databaseConfig()

app = FastAPI()
queries = aiosql.from_path("db/queries.sql", "psycopg2")

@app.post("/items")
def add_items(item: Item) -> None:
    try:
        queries.add_items(conn, name=item.name, description=item.description, price=item.price, seller_email=item.seller_email,\
            date_of_posting=item.date_of_posting, date_of_sale=item.date_of_sale, status=item.status)
    except Exception as er:
        raise ("Exception occured", er)
    finally:
        conn.commit()
    return

