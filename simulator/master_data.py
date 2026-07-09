from __future__ import annotations

from dataclasses import dataclass, asdict
from faker import Faker
import random
from typing import List, Dict, Any


fake = Faker("en_US")
random.seed(42)
Faker.seed(42)


STORE_REGIONS = ["Central", "East", "West", "North", "North-East"]

STORE_FORMATS = [
    "CBD Flagship",
    "Mall Supermarket",
    "Neighborhood Store",
    "Convenience Store",
    "Online Fulfillment",
]

PERSONA_CONFIG = {
    "Student": {
        "weight": 18,
        "favorite_categories": ["Snacks", "Beverage", "Bakery"],
        "avg_basket_size": 2,
        "price_sensitivity": "High",
    },
    "Young Professional": {
        "weight": 32,
        "favorite_categories": ["Beverage", "Bakery", "Snacks"],
        "avg_basket_size": 3,
        "price_sensitivity": "Medium",
    },
    "Family": {
        "weight": 30,
        "favorite_categories": ["Fresh Produce", "Dairy", "Household", "Frozen"],
        "avg_basket_size": 8,
        "price_sensitivity": "Medium",
    },
    "Retiree": {
        "weight": 12,
        "favorite_categories": ["Fresh Produce", "Dairy", "Beverage"],
        "avg_basket_size": 4,
        "price_sensitivity": "Medium",
    },
    "Premium Shopper": {
        "weight": 8,
        "favorite_categories": ["Fresh Produce", "Dairy", "Beverage", "Bakery"],
        "avg_basket_size": 5,
        "price_sensitivity": "Low",
    },
}

LOYALTY_CONFIG = {
    "Bronze": {"weight": 45, "shopping_frequency_score": 1},
    "Silver": {"weight": 30, "shopping_frequency_score": 3},
    "Gold": {"weight": 18, "shopping_frequency_score": 6},
    "Platinum": {"weight": 7, "shopping_frequency_score": 10},
}

PRODUCT_CATEGORIES = {
    "Beverage": {
        "sub_categories": ["Coffee", "Tea", "Juice", "Sparkling Water", "Milk"],
        "base_popularity": 90,
        "shelf_life_days": 30,
    },
    "Bakery": {
        "sub_categories": ["Croissant", "Toast", "Cake", "Muffin", "Bun"],
        "base_popularity": 75,
        "shelf_life_days": 3,
    },
    "Dairy": {
        "sub_categories": ["Yogurt", "Cheese", "Butter", "Fresh Milk"],
        "base_popularity": 80,
        "shelf_life_days": 14,
    },
    "Frozen": {
        "sub_categories": ["Ice Cream", "Frozen Dumplings", "Frozen Pizza"],
        "base_popularity": 55,
        "shelf_life_days": 180,
    },
    "Household": {
        "sub_categories": ["Detergent", "Tissue", "Dish Soap", "Trash Bag"],
        "base_popularity": 50,
        "shelf_life_days": 365,
    },
    "Snacks": {
        "sub_categories": ["Chips", "Chocolate", "Biscuits", "Nuts"],
        "base_popularity": 85,
        "shelf_life_days": 120,
    },
    "Fresh Produce": {
        "sub_categories": ["Apple", "Banana", "Lettuce", "Tomato", "Avocado"],
        "base_popularity": 70,
        "shelf_life_days": 7,
    },
}


@dataclass
class Store:
    store_id: str
    store_name: str
    store_format: str
    region: str
    country: str
    city: str
    opening_date: str
    size_sqft: int
    daily_traffic_weight: int
    business_hours: str
    is_active: bool


@dataclass
class Product:
    product_id: str
    sku: str
    product_name: str
    category: str
    sub_category: str
    brand: str
    unit_price: float
    cost_price: float
    gross_margin_pct: float
    popularity_score: int
    shelf_life_days: int
    supplier_id: str
    is_active: bool


@dataclass
class Customer:
    customer_id: str
    customer_name: str
    gender: str
    age_group: str
    persona: str
    loyalty_tier: str
    shopping_frequency_score: int
    avg_basket_size: int
    price_sensitivity: str
    favorite_categories: List[str]
    preferred_store_id: str
    signup_date: str
    preferred_channel: str
    home_region: str
    is_active: bool


def weighted_choice(items: list, weights: list):
    return random.choices(items, weights=weights, k=1)[0]


def choose_persona() -> str:
    personas = list(PERSONA_CONFIG.keys())
    weights = [PERSONA_CONFIG[p]["weight"] for p in personas]
    return weighted_choice(personas, weights)


def choose_loyalty() -> str:
    tiers = list(LOYALTY_CONFIG.keys())
    weights = [LOYALTY_CONFIG[t]["weight"] for t in tiers]
    return weighted_choice(tiers, weights)


def traffic_weight_for_store(store_format: str, region: str) -> int:
    base = {
        "CBD Flagship": 100,
        "Mall Supermarket": 85,
        "Neighborhood Store": 50,
        "Convenience Store": 35,
        "Online Fulfillment": 70,
    }[store_format]

    region_multiplier = {
        "Central": 1.25,
        "East": 1.00,
        "West": 0.95,
        "North": 0.85,
        "North-East": 0.90,
    }[region]

    return max(10, int(base * region_multiplier + random.randint(-8, 8)))


def price_for_category(category: str) -> float:
    ranges = {
        "Beverage": (1.8, 12.0),
        "Bakery": (1.5, 18.0),
        "Dairy": (2.0, 25.0),
        "Frozen": (4.0, 35.0),
        "Household": (3.0, 55.0),
        "Snacks": (1.5, 20.0),
        "Fresh Produce": (1.2, 30.0),
    }
    low, high = ranges[category]
    return round(random.uniform(low, high), 2)


def popularity_for_category(category: str) -> int:
    base = PRODUCT_CATEGORIES[category]["base_popularity"]
    return max(1, min(100, int(base + random.randint(-20, 15))))


def generate_stores(n: int = 20) -> List[Dict[str, Any]]:
    stores = []

    predefined = [
        ("Central", "CBD Flagship", "CBD Flagship Store"),
        ("Central", "Mall Supermarket", "Orchard Mall Supermarket"),
        ("East", "Online Fulfillment", "Changi Fulfillment Hub"),
        ("West", "Neighborhood Store", "Jurong Neighborhood Store"),
        ("North-East", "Convenience Store", "Serangoon Convenience Store"),
    ]

    for i in range(1, n + 1):
        if i <= len(predefined):
            region, store_format, store_name = predefined[i - 1]
        else:
            region = random.choice(STORE_REGIONS)
            store_format = random.choice(STORE_FORMATS)
            store_name = f"{region} {store_format} {i:03d}"

        stores.append(asdict(Store(
            store_id=f"SG{i:03d}",
            store_name=store_name,
            store_format=store_format,
            region=region,
            country="Singapore",
            city="Singapore",
            opening_date=str(fake.date_between(start_date="-8y", end_date="-6m")),
            size_sqft=random.randint(1200, 30000),
            daily_traffic_weight=traffic_weight_for_store(store_format, region),
            business_hours="08:00-22:00" if store_format != "Online Fulfillment" else "00:00-23:59",
            is_active=True,
        )))
    return stores


def generate_products(n: int = 200) -> List[Dict[str, Any]]:
    products = []
    categories = list(PRODUCT_CATEGORIES.keys())
    category_weights = [90, 75, 80, 55, 50, 85, 70]

    for i in range(1, n + 1):
        category = weighted_choice(categories, category_weights)
        config = PRODUCT_CATEGORIES[category]
        sub_category = random.choice(config["sub_categories"])
        unit_price = price_for_category(category)
        margin_pct = round(random.uniform(0.22, 0.55), 2)
        cost_price = round(unit_price * (1 - margin_pct), 2)

        products.append(asdict(Product(
            product_id=f"PROD{i:04d}",
            sku=f"SKU-{category[:3].upper()}-{i:05d}",
            product_name=f"{fake.company().split()[0]} {sub_category}",
            category=category,
            sub_category=sub_category,
            brand=fake.company().split()[0],
            unit_price=unit_price,
            cost_price=cost_price,
            gross_margin_pct=margin_pct,
            popularity_score=popularity_for_category(category),
            shelf_life_days=config["shelf_life_days"],
            supplier_id=f"SUP{random.randint(1, 30):03d}",
            is_active=True,
        )))
    return products


def generate_customers(
    n: int = 500,
    stores: List[Dict[str, Any]] | None = None
) -> List[Dict[str, Any]]:
    if stores is None:
        stores = generate_stores()

    customers = []
    store_weights = [s["daily_traffic_weight"] for s in stores]

    for i in range(1, n + 1):
        persona = choose_persona()
        loyalty_tier = choose_loyalty()
        persona_config = PERSONA_CONFIG[persona]
        loyalty_config = LOYALTY_CONFIG[loyalty_tier]
        preferred_store = weighted_choice(stores, store_weights)

        customers.append(asdict(Customer(
            customer_id=f"CUS{i:05d}",
            customer_name=fake.name(),
            gender=random.choice(["Female", "Male", "Unknown"]),
            age_group=random.choice(["18-24", "25-34", "35-44", "45-54", "55+"]),
            persona=persona,
            loyalty_tier=loyalty_tier,
            shopping_frequency_score=loyalty_config["shopping_frequency_score"],
            avg_basket_size=persona_config["avg_basket_size"],
            price_sensitivity=persona_config["price_sensitivity"],
            favorite_categories=persona_config["favorite_categories"],
            preferred_store_id=preferred_store["store_id"],
            signup_date=str(fake.date_between(start_date="-5y", end_date="-7d")),
            preferred_channel=random.choice(["POS", "Mobile App", "Web"]),
            home_region=preferred_store["region"],
            is_active=True,
        )))
    return customers


def generate_all_master_data() -> Dict[str, List[Dict[str, Any]]]:
    stores = generate_stores()
    products = generate_products()
    customers = generate_customers(stores=stores)
    return {
        "stores": stores,
        "products": products,
        "customers": customers,
    }
