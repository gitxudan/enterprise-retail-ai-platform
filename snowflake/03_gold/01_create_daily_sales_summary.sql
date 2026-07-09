CREATE OR REPLACE TABLE GOLD.DAILY_SALES_SUMMARY AS
SELECT
    DATE(event_time) AS sales_date,
    country,
    city,
    store_region,
    store_format,
    channel,

    COUNT(DISTINCT transaction_id) AS total_transactions,
    COUNT(DISTINCT customer_id) AS active_customers,
    COUNT(DISTINCT product_id) AS products_sold,

    SUM(quantity) AS total_quantity,
    SUM(gross_amount) AS gross_revenue,
    SUM(discount_amount) AS total_discount,
    SUM(net_amount) AS net_revenue,

    ROUND(AVG(net_amount), 2) AS avg_transaction_value,
    ROUND(AVG(gross_margin_pct), 2) AS avg_gross_margin_pct,

    COUNT_IF(promotion_flag = TRUE) AS promotion_transactions,
    ROUND(
        COUNT_IF(promotion_flag = TRUE) / NULLIF(COUNT(*), 0),
        4
    ) AS promotion_transaction_ratio,

    CURRENT_TIMESTAMP() AS gold_updated_at

FROM SILVER.TRANSACTION_EVENTS
GROUP BY
    DATE(event_time),
    country,
    city,
    store_region,
    store_format,
    channel;