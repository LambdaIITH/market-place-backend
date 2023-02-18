-- name: post-item! 
-- Inserts a new item for selling into the database.
insert into items(name, description, price, seller_email)
values(:name, :description, :price, :seller_email);

-- name: post-bid!
-- Inserts a new bid into the database.
insert into bids (item_id, bidder_email, bid_amount) 
values (:item_id, :bidder_email, :bid_amount);


-- name: accept-bid!
-- Updates the status of the item to sold and the date of sale to the current time.
-- The item must be unsold.
update items set status = true, date_of_sale = CURRENT_TIMESTAMP where id = :item_id and status = false;

-- name: get-bids-for-item
-- Returns the bids for the given item_id
select * from bids where item_id = :item_id;