--name: add_items
INSERT INTO items(name, description, price, seller_email, date_of_posting, date_of_sale, status) values(:name, :description, :price, :seller_email, :date_of_posting, :date_of_sale, :status) returning id;

--name: add_bids
INSERT INTO bids(item_id, bidder_email, bid_amount, date_of_bid) values(:item_id, :bidder_email, :bid_amount, :date_of_bid) returning id;

--name: get_bids
SELECT * from bids where item_id = :item_id;

--name: add_sales
INSERT INTO sales(bid_id) values(:bid_id) returning id;
