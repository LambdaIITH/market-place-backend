CREATE TABLE users(
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) PRIMARY KEY,
  phone_number NUMERIC(10) NOT NULL
);

CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description VARCHAR(255) NOT NULL,
  price NUMERIC(10,2) NOT NULL,
  seller_email VARCHAR(255) NOT NULL,
  date_of_posting TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  date_of_sale TIMESTAMP,
  status BOOLEAN NOT NULL DEFAULT FALSE -- false = not sold, true = sold
);

CREATE TABLE bids (
  id SERIAL PRIMARY KEY,
  item_id INTEGER NOT NULL,
  bidder_email VARCHAR(255) NOT NULL,
  bid_amount NUMERIC(10,2) NOT NULL,
  date_of_bid TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (item_id) REFERENCES items(id),
  FOREIGN KEY (bidder_email) REFERENCES users(email)
);

CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  bid_id INTEGER NOT NULL,
  FOREIGN KEY (bid_id) REFERENCES bids(id)
);
