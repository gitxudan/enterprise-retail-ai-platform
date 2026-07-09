from __future__ import annotations

import random
from typing import Any, Dict, List, Optional


def weighted_choice(items: List[Dict[str, Any]], weight_key: str) -> Dict[str, Any]:
    """
    Pick one dictionary item using a numeric weight column.

    Example:
        weighted_choice(stores, "daily_traffic_weight")
        weighted_choice(products, "popularity_score")
    """
    if not items:
        raise ValueError("weighted_choice received an empty item list")

    weights = [max(float(item.get(weight_key, 1)), 0.01) for item in items]
    return random.choices(items, weights=weights, k=1)[0]


def weighted_choice_by_score(items: List[Dict[str, Any]], score_key: str) -> Dict[str, Any]:
    """
    Alias for readability when the field is a score rather than a weight.
    """
    return weighted_choice(items, score_key)


def choose_customer(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    High-frequency customers should appear more often in transaction events.
    """
    return weighted_choice(customers, "shopping_frequency_score")


def choose_store(
    stores: List[Dict[str, Any]],
    customer: Optional[Dict[str, Any]] = None,
    preferred_store_probability: float = 0.75,
) -> Dict[str, Any]:
    """
    Most customers shop at their preferred store, but sometimes visit another store.
    """
    if customer and random.random() < preferred_store_probability:
        preferred_store_id = customer.get("preferred_store_id")
        matched = [s for s in stores if s["store_id"] == preferred_store_id]
        if matched:
            return matched[0]

    return weighted_choice(stores, "daily_traffic_weight")


def choose_product(
    products: List[Dict[str, Any]],
    customer: Optional[Dict[str, Any]] = None,
    favorite_category_probability: float = 0.80,
) -> Dict[str, Any]:
    """
    Customers mostly buy from their favorite categories.
    If no favorite-category product is available, fallback to popularity-weighted product choice.
    """
    candidate_products = products

    if customer and random.random() < favorite_category_probability:
        favorite_categories = set(customer.get("favorite_categories", []))
        filtered = [p for p in products if p.get("category") in favorite_categories]
        if filtered:
            candidate_products = filtered

    return weighted_choice(candidate_products, "popularity_score")


def choose_basket_products(
    products: List[Dict[str, Any]],
    customer: Dict[str, Any],
    max_distinct_items: int = 8,
) -> List[Dict[str, Any]]:
    """
    Generate a small realistic basket based on customer persona.
    This returns distinct products. Quantity is still handled by event_generator.
    """
    avg_basket_size = int(customer.get("avg_basket_size", 3))
    basket_size = max(1, min(max_distinct_items, int(random.gauss(avg_basket_size, 1.5))))

    selected = []
    seen_product_ids = set()

    attempts = 0
    while len(selected) < basket_size and attempts < basket_size * 5:
        product = choose_product(products, customer=customer)
        attempts += 1

        if product["product_id"] not in seen_product_ids:
            selected.append(product)
            seen_product_ids.add(product["product_id"])

    return selected


def choose_channel(customer: Dict[str, Any]) -> str:
    """
    Prefer the customer's preferred channel, but allow real-world variation.
    """
    preferred_channel = customer.get("preferred_channel", "POS")
    channels = ["POS", "Mobile App", "Web"]

    if preferred_channel not in channels:
        preferred_channel = "POS"

    weights = []
    for channel in channels:
        if channel == preferred_channel:
            weights.append(70)
        else:
            weights.append(15)

    return random.choices(channels, weights=weights, k=1)[0]


def choose_payment_method(channel: str) -> str:
    """
    Payment methods vary by channel.
    """
    if channel == "POS":
        methods = ["Visa", "Mastercard", "PayNow", "Cash", "GrabPay"]
        weights = [28, 24, 22, 16, 10]
    else:
        methods = ["Visa", "Mastercard", "PayNow", "GrabPay"]
        weights = [35, 30, 25, 10]

    return random.choices(methods, weights=weights, k=1)[0]


def choose_quantity(customer: Dict[str, Any], product: Dict[str, Any]) -> int:
    """
    Quantity depends on persona and product category.
    Family customers are more likely to buy larger quantities.
    """
    persona = customer.get("persona", "Young Professional")
    category = product.get("category", "")

    if persona == "Family":
        base_weights = [30, 35, 20, 10, 5]
    elif persona == "Student":
        base_weights = [65, 25, 7, 2, 1]
    elif persona == "Premium Shopper":
        base_weights = [45, 30, 15, 7, 3]
    else:
        base_weights = [55, 28, 12, 4, 1]

    # Household and dairy purchases often involve multiple units.
    if category in {"Household", "Dairy", "Frozen"}:
        base_weights = [35, 35, 18, 8, 4]

    return random.choices([1, 2, 3, 4, 5], weights=base_weights, k=1)[0]


def choose_promotion_flag(customer: Dict[str, Any]) -> bool:
    """
    Price-sensitive customers respond to promotions more often.
    """
    sensitivity = customer.get("price_sensitivity", "Medium")
    probability = {
        "High": 0.38,
        "Medium": 0.24,
        "Low": 0.12,
    }.get(sensitivity, 0.22)

    return random.random() < probability


def choose_discount_rate(promotion_flag: bool, customer: Dict[str, Any]) -> float:
    if not promotion_flag:
        return 0.0

    sensitivity = customer.get("price_sensitivity", "Medium")

    if sensitivity == "High":
        rates = [0.05, 0.10, 0.15, 0.20]
        weights = [20, 35, 30, 15]
    elif sensitivity == "Low":
        rates = [0.05, 0.10, 0.15]
        weights = [55, 30, 15]
    else:
        rates = [0.05, 0.10, 0.15]
        weights = [35, 45, 20]

    return random.choices(rates, weights=weights, k=1)[0]


def choose_review_rating(customer: Dict[str, Any]) -> int:
    """
    Premium and loyal customers tend to be slightly more positive;
    high price sensitivity leads to more neutral/negative feedback.
    """
    persona = customer.get("persona", "")
    sensitivity = customer.get("price_sensitivity", "Medium")

    if persona == "Premium Shopper" and sensitivity == "Low":
        weights = [3, 5, 12, 35, 45]
    elif sensitivity == "High":
        weights = [8, 12, 25, 35, 20]
    else:
        weights = [5, 8, 17, 35, 35]

    return random.choices([1, 2, 3, 4, 5], weights=weights, k=1)[0]


def choose_support_priority(customer: Dict[str, Any]) -> str:
    """
    Higher loyalty tiers are more likely to receive high-priority handling.
    """
    tier = customer.get("loyalty_tier", "Bronze")

    if tier in {"Gold", "Platinum"}:
        priorities = ["Low", "Medium", "High", "Critical"]
        weights = [25, 35, 30, 10]
    else:
        priorities = ["Low", "Medium", "High", "Critical"]
        weights = [50, 35, 12, 3]

    return random.choices(priorities, weights=weights, k=1)[0]
