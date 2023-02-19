-- name: create_schema#
CREATE TABLE users (
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) PRIMARY KEY,
  phone_number NUMERIC(10) NOT NULL,
);

CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description VARCHAR(255) NOT NULL,
  price NUMERIC(10,2) NOT NULL,
  seller_email VARCHAR(255) NOT NULL,
  date_of_posting TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  date_of_sale TIMESTAMP,
  status BOOLEAN NOT NULL DEFAULT FALSE, -- false = not sold, true = sold
  FOREIGN KEY (seller_email) REFERENCES users(email),
);

CREATE TABLE bids (
  id SERIAL PRIMARY KEY,
  item_id INTEGER NOT NULL,
  bidder_email VARCHAR(255) NOT NULL,
  bid_amount NUMERIC(10,2) NOT NULL,
  date_of_bid TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (item_id) REFERENCES items(id),
  FOREIGN KEY (bidder_email) REFERENCES users(email),
  PRIMARY KEY (item_id, bidder_email),
);

CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  bid_id INTEGER NOT NULL,
  FOREIGN KEY (bid_id) REFERENCES bids(id),
);

-- name: create_item!
insert into items(name, description, price, seller_email) values(:name, :description, :price, :seller_email)

--name: create_bid!
insert into bids(item_id,bidder_email,bid_amount) values(:item_id, :bidder_email, :bid_amount)

--name: get_bids
select * from bids where item_id = :item_id;

--name: accept_bid!
update items set status = true, date_of_sale = CURRENT_TIMESTAMP where id = (select item_id from bids where id = :bid_id);

--name: get_seller_email
select seller_email from items where id = (select item_id from bids where id = :bid_id);

--name: add_sales!
insert into sales(bid_id) values(:bid_id);

--name: add_user!
-- add a new user to the users table
INSERT INTO users (name, email, phone_number) VALUES (:name, :email, :phone_number);

--name: get_items
-- get all items from the items table
SELECT * FROM items where STATUS = false;