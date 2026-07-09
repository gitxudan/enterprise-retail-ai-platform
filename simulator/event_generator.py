from __future__ import annotations

from datetime import datetime, timezone
from faker import Faker
import random
import uuid
from typing import Dict, Any, List

from simulator.sampling import (
    choose_customer,
    choose_store,
    choose_product,
    choose_quantity,
    choose_channel,
    choose_payment_method,
    choose_promotion_flag,
    choose_discount_rate,
    choose_review_rating,
    choose_support_priority,
    weighted_choice,
)


fake = Faker("en_US")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def envelope(schema: str, source_system: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "metadata": {
            "event_id": f"EVT-{uuid.uuid4()}",
            "schema": schema,
            "version": "1.0",
            "producer": "retail-simulator-v2a",
            "source_system": source_system,
            "region": "aus-east-1",
            "ingestion_time": utc_now(),
        },
        "payload": payload,
    }


def generate_transaction(
    stores: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    customers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate one POS / online transaction event.

    Business-aware logic:
    - High-frequency customers appear more often.
    - Customers usually shop at their preferred store.
    - Customers mostly buy from their favorite categories.
    - Product popularity affects product selection.
    - Price-sensitive customers are more promotion-responsive.
    """
    customer = choose_customer(customers)
    store = choose_store(stores, customer=customer)
    product = choose_product(products, customer=customer)

    quantity = choose_quantity(customer, product)
    channel = choose_channel(customer)
    promotion_flag = choose_promotion_flag(customer)
    discount_rate = choose_discount_rate(promotion_flag, customer)

    gross_amount = round(quantity * product["unit_price"], 2)
    discount_amount = round(gross_amount * discount_rate, 2)
    net_amount = round(gross_amount - discount_amount, 2)

    payload = {
        "transaction_id": f"TXN-{uuid.uuid4()}",
        "event_time": utc_now(),

        # business keys
        "store_id": store["store_id"],
        "customer_id": customer["customer_id"],
        "product_id": product["product_id"],

        # denormalized attributes for stream debugging
        "store_region": store["region"],
        "store_format": store["store_format"],
        "customer_persona": customer["persona"],
        "loyalty_tier": customer["loyalty_tier"],
        "product_category": product["category"],
        "product_sub_category": product["sub_category"],

        # transaction measures
        "quantity": quantity,
        "unit_price": product["unit_price"],
        "gross_amount": gross_amount,
        "discount_rate": discount_rate,
        "discount_amount": discount_amount,
        "net_amount": net_amount,
        "gross_margin_pct": product["gross_margin_pct"],

        # channel/payment
        "payment_method": choose_payment_method(channel),
        "channel": channel,
        "promotion_flag": promotion_flag,

        # geography
        "country": store["country"],
        "city": store["city"],
    }
    return envelope("transaction_event", "POS", payload)


def generate_inventory_event(
    stores: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate one inventory movement event.

    Business-aware logic:
    - High-traffic stores create more inventory events.
    - Popular products create more inventory movement.
    """
    store = weighted_choice(stores, "daily_traffic_weight")
    product = weighted_choice(products, "popularity_score")

    movement_type = random.choices(
        ["SALE", "RESTOCK", "ADJUSTMENT", "RETURN"],
        weights=[55, 25, 10, 10],
        k=1,
    )[0]

    stock_before = random.randint(0, 300)

    if movement_type == "SALE":
        movement_qty = -random.randint(1, 8)
    elif movement_type == "RESTOCK":
        movement_qty = random.randint(20, 150)
    elif movement_type == "RETURN":
        movement_qty = random.randint(1, 5)
    else:
        movement_qty = random.randint(-10, 10)

    stock_after = max(stock_before + movement_qty, 0)

    payload = {
        "inventory_event_id": f"INV-{uuid.uuid4()}",
        "event_time": utc_now(),

        "store_id": store["store_id"],
        "store_region": store["region"],
        "product_id": product["product_id"],
        "product_category": product["category"],
        "product_sub_category": product["sub_category"],
        "warehouse_id": f"WH-{random.randint(1, 5):03d}",

        "movement_type": movement_type,
        "stock_before": stock_before,
        "movement_qty": movement_qty,
        "stock_after": stock_after,
        "reorder_flag": stock_after < 25,
        "supplier_id": product["supplier_id"],
        "shelf_life_days": product["shelf_life_days"],
    }
    return envelope("inventory_event", "INVENTORY_SYSTEM", payload)


def generate_product_review(
    products: List[Dict[str, Any]],
    customers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate one product review event.

    Business-aware logic:
    - More active customers write more reviews.
    - Reviews usually relate to preferred categories.
    - Rating distribution depends on persona and price sensitivity.
    """
    customer = choose_customer(customers)
    product = choose_product(products, customer=customer)
    rating = choose_review_rating(customer)

    positive_reviews = [
        "Good quality and consistent value for money.",
        "Fresh product and easy to find in store.",
        "My family buys this often and we are satisfied.",
        "Packaging is convenient and the taste is nice.",
        "The product is reliable and I would purchase again.",
    ]

    neutral_reviews = [
        "The product is acceptable but nothing special.",
        "Average quality for the price paid.",
        "It meets basic expectations but could be improved.",
    ]

    negative_reviews = [
        "The item was not fresh when I received it.",
        "The price increased and the quality feels lower.",
        "Stock is often unavailable at my nearby store.",
        "Packaging was damaged and support was slow.",
        "I expected better quality based on previous purchases.",
    ]

    if rating >= 4:
        review_text = random.choice(positive_reviews)
        sentiment_hint = "positive"
    elif rating == 3:
        review_text = random.choice(neutral_reviews)
        sentiment_hint = "neutral"
    else:
        review_text = random.choice(negative_reviews)
        sentiment_hint = "negative"

    payload = {
        "review_id": f"REV-{uuid.uuid4()}",
        "review_time": utc_now(),

        "customer_id": customer["customer_id"],
        "customer_persona": customer["persona"],
        "loyalty_tier": customer["loyalty_tier"],

        "product_id": product["product_id"],
        "product_category": product["category"],
        "product_sub_category": product["sub_category"],

        "rating": rating,
        "review_title": fake.sentence(nb_words=6),
        "review_text": review_text,
        "language": "en",
        "sentiment_hint": sentiment_hint,
    }
    return envelope("product_review_event", "MOBILE_APP", payload)


def generate_support_ticket(
    products: List[Dict[str, Any]],
    customers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate one customer support ticket.

    Business-aware logic:
    - More active customers contact support more often.
    - Issue priority depends partly on loyalty tier.
    - Issue category determines ticket text.
    """
    customer = choose_customer(customers)
    product = choose_product(products, customer=customer)

    issue_category = random.choices(
        ["Refund", "Product Quality", "Delivery", "Payment", "Loyalty Points", "Stock Availability"],
        weights=[20, 24, 16, 12, 10, 18],
        k=1,
    )[0]

    issue_templates = {
        "Refund": "Customer requested refund because the purchased item did not meet expectations.",
        "Product Quality": "Customer reported quality issue related to freshness, packaging, or product condition.",
        "Delivery": "Customer complained about delayed or incomplete delivery.",
        "Payment": "Customer reported a failed or duplicated payment transaction.",
        "Loyalty Points": "Customer said loyalty points were missing after purchase.",
        "Stock Availability": "Customer could not find the product in nearby stores.",
    }

    status = random.choices(
        ["Open", "In Progress", "Resolved"],
        weights=[35, 30, 35],
        k=1,
    )[0]

    resolution_by_status = {
        "Open": ["Pending investigation."],
        "In Progress": [
            "Customer contacted by support team.",
            "Case escalated for further review.",
            "Store operations team is checking the issue.",
        ],
        "Resolved": [
            "Refund approved.",
            "Replacement arranged.",
            "Case closed after explanation.",
            "Loyalty points adjusted.",
        ],
    }

    payload = {
        "ticket_id": f"TCK-{uuid.uuid4()}",
        "created_time": utc_now(),

        "customer_id": customer["customer_id"],
        "customer_persona": customer["persona"],
        "loyalty_tier": customer["loyalty_tier"],

        "product_id": product["product_id"],
        "product_category": product["category"],
        "product_sub_category": product["sub_category"],

        "category": issue_category,
        "priority": choose_support_priority(customer),
        "issue_text": issue_templates[issue_category],
        "status": status,
        "resolution_text": random.choice(resolution_by_status[status]),
    }
    return envelope("support_ticket_event", "CUSTOMER_SUPPORT", payload)
