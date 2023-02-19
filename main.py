from typing import Union
from fastapi import FastAPI, Request
from authlib.integrations.starlette_client import OAuth, OAuthError
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, HTMLResponse
import aiosql
from functools import wraps
load_dotenv(".env")
DATABASE = os.getenv("DATABASE")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
SECRET_KEY = os.getenv("SECRET_KEY")

conn = psycopg2.connect(
    database=DATABASE,
    user=POSTGRES_USER,
    password=POSTGRES_PASS,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    cursor_factory=RealDictCursor,
)
print("Opened database successfully!")
queries = aiosql.from_path("db/init.sql", "psycopg2")

#decorator to check if user is the owner of the item
def user_check(func):
    @wraps(func)
    async def innerfunction(*args, **kwargs):
        user = kwargs['request'].session.get('user')
        seller_email = queries.get_seller_email(conn, bid_id=kwargs['bid_id'])
        if user is not None:
            user_email = user['email']
            if user_email == seller_email[0]['seller_email']:
                return await func(*args, **kwargs)
        return {"error": "You are not the seller"}
    return innerfunction
        
#decorator to check if user is logged in
def is_authenticated(func):
    @wraps(func)
    async def innerfunction(*args, **kwargs):
        user = kwargs['request'].session.get('user')
        if user is not None:
            return await func(*args, **kwargs)
        return {"error": "You are not logged in"}
    return innerfunction

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid email profile'
    }
)

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float

class Bid(BaseModel):
    item_id: int
    bid_amount: float

# http://127.0.0.1:8000/
@app.get("/")
def read_root(request: Request):
    user = request.session.get('user')
    if user:
        return user['name']
    else:
        return {'error': 'You are not logged in'}


# http://127.0.0.1:8000/items/5?q=somequery
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

#route to create a new item for selling
@app.post("/new_item")
@is_authenticated
async def new_item(item: Item, request: Request):
    queries.create_item(conn, name=item.name, description=item.description, price=item.price, seller_email=request.session.get('user')['email'])
    conn.commit()
    
#route to insert bids of a user on a particular item
@app.post("/new_bid")
@is_authenticated
async def new_bid( bid: Bid, request: Request):
    queries.create_bid(conn, item_id=bid.item_id, bidder_email=request.session.get('user')['email'] , bid_amount=bid.bid_amount)
    conn.commit()

#route to get/view all bids for an item   
@app.get("/get_bids")
async def get_bids(item_id: int):
    return queries.get_bids(conn, item_id=item_id)

# Route to accept a bid for an item
@app.post("/accept_bid/{bid_id}}")
@user_check
async def accept_bid(request:Request,bid_id):
    queries.accept_bid(conn, bid_id=bid_id)
    queries.add_sales(conn, bid_id=bid_id)
    conn.commit()

#route for login using google
@app.route('/login')
async def login(request: Request):
    # absolute url for callback
    # we will define it below
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

#route for callback after login
@app.route('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = await oauth.google.parse_id_token(request, token)
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/')

# Route to add a new user with their phone number
@app.post('/add_user/{phone_number}}')
@is_authenticated
async def add_user(phone_number, request: Request):
    queries.add_user(conn, name=request.session.get('user')['name'], email=request.session.get('user')['name'], phone_number=phone_number)
    conn.commit()
    
# Route to get all items
@app.get('/get_items')
async def get_items():
    return queries.get_items(conn)