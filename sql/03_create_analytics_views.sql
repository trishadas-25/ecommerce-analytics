-- ============================================================
-- OLIST E-COMMERCE ANALYTICS
-- FILE: 03_create_analytics_views.sql
-- PURPOSE: Create business-ready analytics views
-- ============================================================


-- ============================================================
-- 1. SALES OVERVIEW
-- ============================================================

CREATE OR REPLACE VIEW vw_sales_overview AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    o.delivery_days,
    o.estimated_delivery_days,
    o.delivered_late,

    oi.order_item_id,
    oi.product_id,
    oi.seller_id,

    oi.price,
    oi.freight_value,
    oi.item_total_value,

    p.product_category_name,

    COALESCE(
        ct.product_category_name_english,
        'Unknown'
    ) AS product_category_name_english,

    pay.payment_type,
    pay.payment_installments,
    pay.payment_value,

    r.review_score

FROM orders o

LEFT JOIN order_items oi
    ON o.order_id = oi.order_id

LEFT JOIN products p
    ON oi.product_id = p.product_id

LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name

LEFT JOIN payments pay
    ON o.order_id = pay.order_id

LEFT JOIN reviews r
    ON o.order_id = r.order_id;


-- ============================================================
-- 2. MONTHLY SALES
-- ============================================================

CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    DATE_TRUNC(
        'month',
        o.order_purchase_timestamp
    ) AS sales_month,

    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS total_items,

    ROUND(
        SUM(oi.price)::NUMERIC,
        2
    ) AS product_revenue,

    ROUND(
        SUM(oi.freight_value)::NUMERIC,
        2
    ) AS freight_revenue,

    ROUND(
        SUM(oi.item_total_value)::NUMERIC,
        2
    ) AS total_revenue,

    ROUND(
        (
            SUM(oi.item_total_value)
            / NULLIF(COUNT(DISTINCT o.order_id), 0)
        )::NUMERIC,
        2
    ) AS average_order_value

FROM orders o

INNER JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE o.order_status NOT IN (
    'canceled',
    'unavailable'
)

GROUP BY
    DATE_TRUNC(
        'month',
        o.order_purchase_timestamp
    )

ORDER BY sales_month;


-- ============================================================
-- 3. CATEGORY PERFORMANCE
-- ============================================================

CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS total_items,

    COUNT(DISTINCT o.customer_id) AS unique_customers,

    ROUND(
        SUM(oi.price)::NUMERIC,
        2
    ) AS product_revenue,

    ROUND(
        SUM(oi.freight_value)::NUMERIC,
        2
    ) AS freight_revenue,

    ROUND(
        SUM(oi.item_total_value)::NUMERIC,
        2
    ) AS total_revenue,

    ROUND(
        AVG(oi.price)::NUMERIC,
        2
    ) AS average_item_price

FROM order_items oi

INNER JOIN orders o
    ON oi.order_id = o.order_id

LEFT JOIN products p
    ON oi.product_id = p.product_id

LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name

WHERE o.order_status NOT IN (
    'canceled',
    'unavailable'
)

GROUP BY
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'Unknown'
    )

ORDER BY total_revenue DESC;


-- ============================================================
-- 4. PRODUCT PERFORMANCE
-- ============================================================

CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    oi.product_id,

    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS units_sold,

    ROUND(
        SUM(oi.price)::NUMERIC,
        2
    ) AS product_revenue,

    ROUND(
        SUM(oi.freight_value)::NUMERIC,
        2
    ) AS freight_revenue,

    ROUND(
        SUM(oi.item_total_value)::NUMERIC,
        2
    ) AS total_revenue,

    ROUND(
        AVG(oi.price)::NUMERIC,
        2
    ) AS average_price

FROM order_items oi

INNER JOIN orders o
    ON oi.order_id = o.order_id

LEFT JOIN products p
    ON oi.product_id = p.product_id

LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name

WHERE o.order_status NOT IN (
    'canceled',
    'unavailable'
)

GROUP BY
    oi.product_id,

    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'Unknown'
    )

ORDER BY total_revenue DESC;


-- ============================================================
-- 5. CUSTOMER PERFORMANCE
-- ============================================================

CREATE OR REPLACE VIEW vw_customer_performance AS
SELECT
    c.customer_unique_id,

    c.customer_state,

    c.customer_city,

    COUNT(DISTINCT o.order_id) AS total_orders,

    ROUND(
        SUM(oi.item_total_value)::NUMERIC,
        2
    ) AS total_spend,

    ROUND(
        (
            SUM(oi.item_total_value)
            / NULLIF(COUNT(DISTINCT o.order_id), 0)
        )::NUMERIC,
        2
    ) AS average_order_value,

    MIN(
        o.order_purchase_timestamp
    ) AS first_order_date,

    MAX(
        o.order_purchase_timestamp
    ) AS latest_order_date

FROM customers c

INNER JOIN orders o
    ON c.customer_id = o.customer_id

INNER JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE o.order_status NOT IN (
    'canceled',
    'unavailable'
)

GROUP BY
    c.customer_unique_id,
    c.customer_state,
    c.customer_city;


-- ============================================================
-- 6. SELLER PERFORMANCE
-- ============================================================

CREATE OR REPLACE VIEW vw_seller_performance AS
SELECT
    s.seller_id,

    s.seller_state,

    s.seller_city,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS units_sold,

    COUNT(DISTINCT oi.product_id) AS unique_products,

    ROUND(
        SUM(oi.price)::NUMERIC,
        2
    ) AS product_revenue,

    ROUND(
        SUM(oi.freight_value)::NUMERIC,
        2
    ) AS freight_revenue,

    ROUND(
        SUM(oi.item_total_value)::NUMERIC,
        2
    ) AS total_revenue,

    ROUND(
        AVG(oi.price)::NUMERIC,
        2
    ) AS average_item_price

FROM sellers s

INNER JOIN order_items oi
    ON s.seller_id = oi.seller_id

INNER JOIN orders o
    ON oi.order_id = o.order_id

WHERE o.order_status NOT IN (
    'canceled',
    'unavailable'
)

GROUP BY
    s.seller_id,
    s.seller_state,
    s.seller_city

ORDER BY total_revenue DESC;


-- ============================================================
-- 7. DELIVERY PERFORMANCE
-- ============================================================

CREATE OR REPLACE VIEW vw_delivery_performance AS
SELECT
    DATE_TRUNC(
        'month',
        order_purchase_timestamp
    ) AS order_month,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(
        CASE
            WHEN order_delivered_customer_date IS NOT NULL
            THEN order_id
        END
    ) AS delivered_orders,

    ROUND(
        AVG(delivery_days)::NUMERIC,
        2
    ) AS average_delivery_days,

    ROUND(
        AVG(estimated_delivery_days)::NUMERIC,
        2
    ) AS average_estimated_delivery_days,

    COUNT(
        CASE
            WHEN delivered_late = TRUE
            THEN order_id
        END
    ) AS late_orders,

    ROUND(
        (
            COUNT(
                CASE
                    WHEN delivered_late = TRUE
                    THEN order_id
                END
            )::NUMERIC
            /
            NULLIF(
                COUNT(
                    CASE
                        WHEN delivered_late IS NOT NULL
                        THEN order_id
                    END
                ),
                0
            )
        ) * 100,
        2
    ) AS late_delivery_percentage

FROM orders

GROUP BY
    DATE_TRUNC(
        'month',
        order_purchase_timestamp
    )

ORDER BY order_month;


-- ============================================================
-- 8. REVIEW PERFORMANCE
-- ============================================================

CREATE OR REPLACE VIEW vw_review_performance AS
SELECT
    r.review_score,

    COUNT(*) AS review_count,

    ROUND(
        (
            COUNT(*)::NUMERIC
            /
            SUM(COUNT(*)) OVER ()
        ) * 100,
        2
    ) AS percentage_of_reviews

FROM reviews r

GROUP BY
    r.review_score

ORDER BY
    r.review_score;


-- ============================================================
-- 9. PAYMENT PERFORMANCE
-- ============================================================

CREATE OR REPLACE VIEW vw_payment_performance AS
SELECT
    payment_type,

    COUNT(*) AS payment_count,

    COUNT(DISTINCT order_id) AS unique_orders,

    ROUND(
        SUM(payment_value)::NUMERIC,
        2
    ) AS total_payment_value,

    ROUND(
        AVG(payment_value)::NUMERIC,
        2
    ) AS average_payment_value,

    ROUND(
        AVG(payment_installments)::NUMERIC,
        2
    ) AS average_installments

FROM payments

GROUP BY
    payment_type

ORDER BY
    total_payment_value DESC;


-- ============================================================
-- END
-- ============================================================

SELECT 'Analytics views created successfully.' AS status;
