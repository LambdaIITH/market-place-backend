-- name: post_item! 
-- Inserts a new item for selling into the database.
insert into items(name, description, price, seller_email)
values(:name, :description, :price, :seller_email);