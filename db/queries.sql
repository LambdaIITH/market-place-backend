-- name: post_item! 
-- Inserts a new item for selling into the database.
insert into items(name, description, price, seller_email)
values(:name, :description, :price, :seller_email);

-- name: post_bid!
-- Inserts a new bid into the database.
insert into bids (item_id, bidder_email, bid_amount) 
values (:item_id, :bidder_email, :bid_amount);