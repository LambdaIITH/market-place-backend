--name: add_items
INSERT INTO items(name, description, price, seller_email, date_of_posting, date_of_sale, status) values(:name, :description, :price, :seller_email, :date_of_posting, :date_of_sale, :status) returning id;