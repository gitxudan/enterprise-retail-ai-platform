
from mcp.server.fastmcp import FastMCP
from mcp_server.utils.snowflake_conn import run_query

mcp = FastMCP("Retail AI Intelligence Engine", json_response=True)


@mcp.tool()
async def get_customer_profile(customer_id: str) -> dict:
    """
    Get a customer's business profile, purchase behavior, and support risk.

    Args:
        customer_id (str): Customer ID, for example CUST_001.

    Returns:
        dict: Customer profile from Gold and Feature layers.
    """
    sql = """
        SELECT
            c.customer_id,
            c.customer_persona,
            c.loyalty_tier,
            c.lifetime_value,
            c.total_transactions,
            c.customer_value_segment,
            c.customer_activity_status,
            f.avg_order_value,
            f.spend_30d,
            f.promotion_usage_ratio,
            s.customer_support_risk_score,
            s.support_risk_segment
        FROM GOLD.CUSTOMER_360 c
        LEFT JOIN FEATURES.CUSTOMER_BEHAVIOR_FEATURES f
            ON c.customer_id = f.customer_id
        LEFT JOIN FEATURES.CUSTOMER_SUPPORT_FEATURES s
            ON c.customer_id = s.customer_id
        WHERE c.customer_id = %(customer_id)s
        LIMIT 1;
    """

    result = run_query(sql, {"customer_id": customer_id})

    if not result:
        return {"error": f"No customer found for customer_id={customer_id}"}

    return result[0]


@mcp.tool()
async def get_product_health(product_id: str) -> dict:
    """
    Get product performance, review health, support risk, and inventory signals.

    Args:
        product_id (str): Product ID.

    Returns:
        dict: Product health profile.
    """
    sql = """
        SELECT
            p.product_id,
            p.product_category,
            p.product_sub_category,
            p.total_net_revenue,
            p.avg_rating,
            p.total_reviews,
            p.total_support_tickets,
            p.product_health_status,
            r.product_risk_score,
            r.product_risk_segment,
            r.negative_review_ratio,
            r.open_ticket_ratio,
            r.min_stock_after
        FROM GOLD.PRODUCT_PERFORMANCE p
        LEFT JOIN FEATURES.PRODUCT_RISK_FEATURES r
            ON p.product_id = r.product_id
        WHERE p.product_id = %(product_id)s
        LIMIT 1;
    """

    result = run_query(sql, {"product_id": product_id})

    if not result:
        return {"error": f"No product found for product_id={product_id}"}

    return result[0]


@mcp.tool()
async def get_store_performance(store_id: str) -> dict:
    """
    Get store-level sales, margin, promotion, and inventory risk signals.

    Args:
        store_id (str): Store ID.

    Returns:
        dict: Store performance summary.
    """
    sql = """
        SELECT
            store_id,
            store_region,
            store_format,
            country,
            city,
            transaction_count,
            unique_customer_count,
            net_revenue,
            avg_transaction_value,
            avg_margin_pct,
            promotion_ratio,
            inventory_turnover_signal,
            store_performance_segment,
            store_inventory_signal
        FROM FEATURES.STORE_PERFORMANCE_FEATURES
        WHERE store_id = %(store_id)s
        LIMIT 1;
    """

    result = run_query(sql, {"store_id": store_id})

    if not result:
        return {"error": f"No store found for store_id={store_id}"}

    return result[0]


@mcp.tool()
async def search_reviews_and_tickets(query: str) -> dict:
    """
    Search customer reviews and support tickets using Snowflake Cortex Search.

    Args:
        query (str): Natural language search query, for example
                     "delivery delay complaints" or "poor product quality".

    Returns:
        dict: Search results from Cortex Search.
    """
    sql = """
        SELECT PARSE_JSON(
            SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                'AI.RETAIL_TEXT_SEARCH_SERVICE',
                OBJECT_CONSTRUCT(
                    'query', %(query)s,
                    'columns', ARRAY_CONSTRUCT(
                        'chunk_id',
                        'source_type',
                        'product_id',
                        'product_category',
                        'chunk_text'
                    ),
                    'limit', 5
                )::STRING
            )
        ) AS search_results;
    """

    result = run_query(sql, {"query": query})

    if not result:
        return {"error": "No search results returned."}

    return result[0]


if __name__ == "__main__":
    mcp.run(transport="stdio")