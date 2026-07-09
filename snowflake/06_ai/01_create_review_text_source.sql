CREATE OR REPLACE TABLE AI.REVIEW_TEXT_SOURCE AS
SELECT
    review_id AS source_id,
    customer_id,
    product_id,
    product_category,
    product_sub_category,
    review_time AS source_time,
    rating,
    sentiment_hint,
    review_title,
    review_text,

    CONCAT(
        'Product Category: ', product_category, '\n',
        'Product Sub Category: ', product_sub_category, '\n',
        'Rating: ', rating, '\n',
        'Sentiment Hint: ', sentiment_hint, '\n',
        'Review Title: ', review_title, '\n',
        'Review Text: ', review_text
    ) AS document_text,

    'product_review' AS source_type,
    CURRENT_TIMESTAMP() AS ai_created_at

FROM SILVER.PRODUCT_REVIEW_EVENTS
WHERE review_text IS NOT NULL;

SELECT COUNT(*)
FROM AI.REVIEW_TEXT_SOURCE;

SELECT
    source_id,
    product_id,
    rating,
    sentiment_hint,
    document_text
FROM AI.REVIEW_TEXT_SOURCE
LIMIT 5;