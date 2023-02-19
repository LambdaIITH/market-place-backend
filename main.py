from typing import Union

from fastapi import FastAPI, HTTPException, Request, Depends, Response
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from pydantic import BaseModel
import aiosql
import json
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as req
load_dotenv()

DATABASE = os.getenv("DATABASE")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET_ID = os.getenv("CLIENT_SECRET_ID")
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

oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth", tokenUrl="http://localhost:8000/auth/callback",scopes={"openid": "OpenID Connect",
        "email": "Email address",
        "profile": "User profile information",})

def get_access_token(request: Request, token: str = Depends(oauth2_scheme)) -> str:
    # Verify and decode the access token from the cookie
    try:
        # Verify the ID token and get the user's email address
        id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        email : str = id_info["email"]
    except Exception as error:
        print(error)
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    return email
# http://127.0.0.1:8000/
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path == "/login" or request.url.path == "/" or request.url.path == "/auth/callback":
        response = await call_next(request)
        return response
    
    try:
        # Try to get the access token from the cookie
        # was using curl requests to test eveything so didn't have a cookie
        access_token = request.cookies["access_token"] 
    except KeyError:
        # If the access token is not present, redirect the user to the login page
        return RedirectResponse(url="/login")

    # Authenticate the user using the access token
    request.state.user = get_access_token(request, token=access_token)

    # Call the next middleware or route handler in the chain
    response = await call_next(request)

    return response

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    # Redirect the user to Google's authentication page
    auth_uri : str = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={CLIENT_ID}&response_type=code&scope=email&redirect_uri=http://localhost:8000/auth/callback"
    return RedirectResponse(auth_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request, response: Response):

    # Exchange the authorization code for an access token
    authorization_code : str = request.query_params["code"]
    
    token_url : str = "https://oauth2.googleapis.com/token"
    
    # token_payload is the data that is sent to the token_url
    token_payload : dict = {
        "code": authorization_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET_ID,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:8000/auth/callback"
    }
    token_response = req.post(token_url, data=token_payload)
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    
    # Set a cookie with the access token and redirect the user to the home page
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return RedirectResponse("/")


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
def create_item(request : Request,item: Item, email: str = Depends(get_access_token)):
    try:
        if email != item.seller_email:
            raise HTTPException(status_code=403, detail="Access denied")
        # post_item is a function in db/items.sql
        res: int = queries.post_item(conn, name = item.name, description = item.description, price = item.price, seller_email = item.seller_email)
    except HTTPException as error:
        raise error
    except Exception as error:
        print(error)
        raise HTTPException(status_code=409, detail="Insert item failed")
    else: 
        raise HTTPException(status_code=201, detail="Insert item successful") 
    finally: 
        conn.commit()

# Pydantic model for bid which is used in the post request
class Bid(BaseModel):
    item_id: int | None
    bidder_email: str 
    bid_amount: float

# http://127.0.0.1:8000/bids/<item_id>
@app.post("/bids/{item_id}")
def create_bid(request: Request,item_id: int, bid: Bid, email: str = Depends(get_access_token)):
    try:
        if email != bid.bidder_email:
            raise HTTPException(status_code=403, detail="Access denied")

        # post_bid is a function in db/bids.sql
        res: int = queries.post_bid(conn, item_id = item_id, bidder_email = bid.bidder_email, bid_amount = bid.bid_amount)
    except HTTPException as error:
        raise error
    except Exception as error:
        print(error)
        raise HTTPException(status_code=409, detail="Insert bid failed")
    else: 
        raise HTTPException(status_code=201, detail="Insert bid successful") 
    finally: 
        conn.commit()


# currently: http://127.0.0.1:8000/bids/accept/<item_id>
# future: http://127.0.0.1:8000/bids/accept/<item_id>/<bid_id>

''' The route is decorated with a Depends function that verifies and decodes the access token
 from the cookie, and checks that the user is the owner of the item before allowing them to view 
 the bids.'''
@app.post("/bids/accept/{item_id}")
async def accept_bid(request: Request, item_id: int,email: str = Depends(get_access_token)):
    try:
        # check if the user is the seller of the item
        cur = conn.cursor()
        cur.execute(f"select seller_email from items where id={item_id};")

        # extracting seller_email from the query result
        res = [json.dumps(dict(record)) for record in cur] # it calls .fetchone() in loop
        res = eval(res[0])
        if email != res["seller_email"]:
            raise HTTPException(status_code=403, detail="Access denied")

        # accept_bid is a function in db/bids.sql
        res: int = queries.accept_bid(conn, item_id = item_id)
        # id is the id of the bid that was accepted, which could be a future addition to the code
        cur.close()

    except HTTPException as error:
        raise error
    except Exception as error:
        print(error)
        raise HTTPException(status_code=409, detail="Accept bid failed")
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