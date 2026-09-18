-- OLIST E-COMMERCE ANALYTICS
-- DATABASE INDEXES


-- Orders

CREATE INDEX IF NOT EXISTS idx_orders_customer_id
ON orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp
ON orders(order_purchase_timestamp);

CREATE INDEX IF NOT EXISTS idx_orders_status
ON orders(order_status);


-- Order Items

CREATE INDEX IF NOT EXISTS idx_order_items_product_id
ON order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_order_items_seller_id
ON order_items(seller_id);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id
ON order_items(order_id);


-- Payments

CREATE INDEX IF NOT EXISTS idx_payments_order_id
ON payments(order_id);

CREATE INDEX IF NOT EXISTS idx_payments_payment_type
ON payments(payment_type);


-- Reviews

CREATE INDEX IF NOT EXISTS idx_reviews_order_id
ON reviews(order_id);

CREATE INDEX IF NOT EXISTS idx_reviews_score
ON reviews(review_score);


-- Products

CREATE INDEX IF NOT EXISTS idx_products_category
ON products(product_category_name);


-- Customers

CREATE INDEX IF NOT EXISTS idx_customers_state
ON customers(customer_state);

CREATE INDEX IF NOT EXISTS idx_customers_city
ON customers(customer_city);


-- Sellers

CREATE INDEX IF NOT EXISTS idx_sellers_state
ON sellers(seller_state);

CREATE INDEX IF NOT EXISTS idx_sellers_city
ON sellers(seller_city);


-- Geolocation

CREATE INDEX IF NOT EXISTS idx_geolocation_zip
ON geolocation(geolocation_zip_code_prefix);

CREATE INDEX IF NOT EXISTS idx_geolocation_state
ON geolocation(geolocation_state);


-- Category Translation

CREATE INDEX IF NOT EXISTS idx_category_translation_english
ON category_translation(product_category_name_english);