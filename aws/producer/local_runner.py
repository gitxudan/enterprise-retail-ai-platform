from __future__ import annotations

import json
from pathlib import Path
import random

from simulator.master_data import generate_all_master_data
from simulator.event_generator import (
    generate_transaction,
    generate_inventory_event,
    generate_product_review,
    generate_support_ticket,
)


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(total_events: int = 1000) -> None:
    master = generate_all_master_data()
    stores = master["stores"]
    products = master["products"]
    customers = master["customers"]

    structured_events = []
    unstructured_events = []

    for _ in range(total_events):
        event_type = random.choices(
            ["transaction", "inventory", "review", "ticket"],
            weights=[55, 20, 15, 10],
        )[0]

        if event_type == "transaction":
            structured_events.append(generate_transaction(stores, products, customers))
        elif event_type == "inventory":
            structured_events.append(generate_inventory_event(stores, products))
        elif event_type == "review":
            unstructured_events.append(generate_product_review(products, customers))
        else:
            unstructured_events.append(generate_support_ticket(products, customers))

    write_jsonl(OUTPUT_DIR / "structured_events.jsonl", structured_events)
    write_jsonl(OUTPUT_DIR / "unstructured_events.jsonl", unstructured_events)

    with (OUTPUT_DIR / "master_data.json").open("w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(structured_events)} structured events")
    print(f"Generated {len(unstructured_events)} unstructured events")
    print("Files written to output/")


if __name__ == "__main__":
    main()
