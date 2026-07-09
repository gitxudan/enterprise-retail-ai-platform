from __future__ import annotations

import json
import os
import random
import time

import boto3
from dotenv import load_dotenv

from simulator.master_data import generate_all_master_data
from simulator.event_generator import (
    generate_transaction,
    generate_inventory_event,
    generate_product_review,
    generate_support_ticket,
)


load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
STRUCTURED_STREAM = os.getenv("KINESIS_STRUCTURED_STREAM", "retail-dev-kds-pos")
UNSTRUCTURED_STREAM = os.getenv("KINESIS_UNSTRUCTURED_STREAM", "retail-dev-kds-review")


def put_event(client, stream_name: str, event: dict, partition_key: str) -> None:
    client.put_record(
        StreamName=stream_name,
        Data=(json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8"),
        PartitionKey=partition_key,
    )


def main(sleep_seconds: float = 0.3) -> None:
    client = boto3.client("kinesis", region_name=AWS_REGION)
    master = generate_all_master_data()
    stores = master["stores"]
    products = master["products"]
    customers = master["customers"]

    print("Starting retail event stream. Press Ctrl+C to stop.")

    while True:
        event_type = random.choices(
            ["transaction", "inventory", "review", "ticket"],
            weights=[55, 20, 15, 10],
        )[0]

        if event_type == "transaction":
            event = generate_transaction(stores, products, customers)
            stream = STRUCTURED_STREAM
            partition_key = event["payload"]["store_id"]
        elif event_type == "inventory":
            event = generate_inventory_event(stores, products)
            stream = STRUCTURED_STREAM
            partition_key = event["payload"]["store_id"]
        elif event_type == "review":
            event = generate_product_review(products, customers)
            stream = UNSTRUCTURED_STREAM
            partition_key = event["payload"]["product_id"]
        else:
            event = generate_support_ticket(products, customers)
            stream = UNSTRUCTURED_STREAM
            partition_key = event["payload"]["customer_id"]

        put_event(client, stream, event, partition_key)
        print(f"Sent {event['metadata']['schema']} to {stream}")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()
