USE DATABASE RETAIL_AI_PLATFORM_DEV;
USE WAREHOUSE COMPUTE_WH;

CREATE SCHEMA IF NOT EXISTS FEATURES;

CREATE OR REPLACE TABLE FEATURES.CUSTOMER_BEHAVIOR_FEATURES AS
SELECT
    customer_id,
    customer_persona,
    loyalty_tier,

    COUNT(DISTINCT transaction_id) AS lifetime_transaction_count,
    SUM(net_amount) AS lifetime_spend,
    ROUND(AVG(net_amount), 2) AS avg_order_value,

    COUNT_IF(event_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())) AS txn_count_7d,
    COUNT_IF(event_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())) AS txn_count_30d,

    SUM(CASE WHEN event_time >= DATEADD(day, -7, CURRENT_TIMESTAMP()) THEN net_amount ELSE 0 END) AS spend_7d,
    SUM(CASE WHEN event_time >= DATEADD(day, -30, CURRENT_TIMESTAMP()) THEN net_amount ELSE 0 END) AS spend_30d,

    COUNT_IF(promotion_flag = TRUE) AS promotion_txn_count,
    ROUND(COUNT_IF(promotion_flag = TRUE) / NULLIF(COUNT(*), 0), 4) AS promotion_usage_ratio,

    MIN(event_time) AS first_purchase_time,
    MAX(event_time) AS last_purchase_time,
    DATEDIFF(day, MAX(event_time), CURRENT_DATE()) AS days_since_last_purchase,

    CASE
        WHEN SUM(net_amount) >= 1000 THEN 'HIGH_VALUE'
        WHEN SUM(net_amount) >= 300 THEN 'MEDIUM_VALUE'
        ELSE 'LOW_VALUE'
    END AS customer_value_segment,

    CASE
        WHEN DATEDIFF(day, MAX(event_time), CURRENT_DATE()) > 30 THEN 'CHURN_RISK'
        WHEN COUNT_IF(event_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())) = 0 THEN 'INACTIVE'
        ELSE 'ACTIVE'
    END AS customer_activity_signal,

    CURRENT_TIMESTAMP() AS feature_updated_at

FROM SILVER.TRANSACTION_EVENTS
GROUP BY
    customer_id,
    customer_persona,
    loyalty_tier;

SELECT COUNT(*)
FROM FEATURES.CUSTOMER_BEHAVIOR_FEATURES;

SELECT *
FROM FEATURES.CUSTOMER_BEHAVIOR_FEATURES
ORDER BY lifetime_spend DESC
LIMIT 10;