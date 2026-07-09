from __future__ import annotations

import gzip
import json
import os
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List
from urllib.parse import unquote_plus

import boto3


s3 = boto3.client("s3")

PROCESSED_PREFIX = os.getenv("PROCESSED_PREFIX", "processed")
FAILED_PREFIX = os.getenv("FAILED_PREFIX", "failed/lambda")
AWS_REGION_VALUE = os.getenv("AWS_REGION_VALUE", "us-east-1")


SCHEMA_TO_PATH = {
    "transaction_event": "structured/transaction",
    "inventory_event": "structured/inventory",
    "product_review_event": "unstructured/review",
    "support_ticket_event": "unstructured/support_ticket",
}

REQUIRED_PAYLOAD_FIELDS = {
    "transaction_event": [
        "transaction_id", "event_time", "store_id", "customer_id", "product_id",
        "quantity", "unit_price", "gross_amount", "net_amount"
    ],
    "inventory_event": [
        "inventory_event_id", "event_time", "store_id", "product_id",
        "movement_type", "stock_before", "movement_qty", "stock_after"
    ],
    "product_review_event": [
        "review_id", "review_time", "customer_id", "product_id",
        "rating", "review_text", "language"
    ],
    "support_ticket_event": [
        "ticket_id", "created_time", "customer_id", "product_id",
        "category", "priority", "issue_text", "status"
    ],
}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def partition_path(dt: datetime) -> str:
    return f"year={dt:%Y}/month={dt:%m}/day={dt:%d}/hour={dt:%H}"


def read_s3_object(bucket: str, key: str) -> str:
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()

    if key.endswith(".gz"):
        body = gzip.decompress(body)

    return body.decode("utf-8")


def parse_json_records(text: str) -> Iterable[Dict[str, Any]]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        try:
            yield json.loads(line)
        except json.JSONDecodeError as exc:
            yield {
                "_invalid_json": True,
                "_line_number": line_number,
                "_raw_line": line,
                "_error": str(exc),
            }


def validate_event(record: Dict[str, Any]) -> List[str]:
    errors = []

    if record.get("_invalid_json"):
        return [f"INVALID_JSON: {record.get('_error')}"]

    metadata = record.get("metadata")
    payload = record.get("payload")

    if not isinstance(metadata, dict):
        errors.append("MISSING_OR_INVALID_METADATA")
        return errors

    if not isinstance(payload, dict):
        errors.append("MISSING_OR_INVALID_PAYLOAD")
        return errors

    schema = metadata.get("schema")
    version = metadata.get("version")

    if schema not in SCHEMA_TO_PATH:
        errors.append(f"UNSUPPORTED_SCHEMA: {schema}")

    if version != "1.0":
        errors.append(f"UNSUPPORTED_VERSION: {version}")

    if schema in REQUIRED_PAYLOAD_FIELDS:
        for field in REQUIRED_PAYLOAD_FIELDS[schema]:
            if field not in payload or payload[field] is None:
                errors.append(f"MISSING_REQUIRED_FIELD: payload.{field}")

    if schema == "transaction_event":
        if payload.get("quantity", 0) <= 0:
            errors.append("INVALID_QUANTITY")
        if payload.get("gross_amount", 0) < 0:
            errors.append("NEGATIVE_GROSS_AMOUNT")
        if payload.get("net_amount", 0) < 0:
            errors.append("NEGATIVE_NET_AMOUNT")
        if payload.get("discount_rate", 0) < 0 or payload.get("discount_rate", 0) > 1:
            errors.append("INVALID_DISCOUNT_RATE")

    if schema == "inventory_event":
        if payload.get("stock_after", 0) < 0:
            errors.append("NEGATIVE_STOCK_AFTER")

    if schema == "product_review_event":
        rating = payload.get("rating")
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            errors.append("INVALID_RATING")

    return errors


def standardize_event(record: Dict[str, Any], source_bucket: str, source_key: str) -> Dict[str, Any]:
    metadata = record["metadata"]
    payload = record["payload"]

    metadata["region"] = AWS_REGION_VALUE
    metadata["processed_time"] = now_utc().isoformat()
    metadata["source_s3_bucket"] = source_bucket
    metadata["source_s3_key"] = source_key
    metadata["quality_status"] = "valid"

    return {
        "metadata": metadata,
        "payload": payload,
    }


def build_output_key(schema: str, status_prefix: str, event_id: str) -> str:
    dt = now_utc()
    schema_path = SCHEMA_TO_PATH.get(schema, "unknown_schema")
    return (
        f"{status_prefix}/"
        f"{schema_path}/"
        f"{partition_path(dt)}/"
        f"{event_id}.json"
    )


def put_json(bucket: str, key: str, data: Dict[str, Any]) -> None:
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )


def process_object(bucket: str, key: str) -> Dict[str, int]:
    text = read_s3_object(bucket, key)
    valid_count = 0
    invalid_count = 0

    for idx, record in enumerate(parse_json_records(text), start=1):
        errors = validate_event(record)

        if errors:
            invalid_count += 1
            metadata = record.get("metadata", {}) if isinstance(record.get("metadata"), dict) else {}
            schema = metadata.get("schema", "unknown_schema")
            event_id = metadata.get("event_id", f"invalid-line-{idx}")

            failed_record = {
                "metadata": {
                    "event_id": event_id,
                    "schema": schema,
                    "quality_status": "invalid",
                    "processed_time": now_utc().isoformat(),
                    "source_s3_bucket": bucket,
                    "source_s3_key": key,
                    "line_number": idx,
                },
                "errors": errors,
                "original_record": record,
            }

            failed_key = build_output_key(schema, FAILED_PREFIX, event_id)
            put_json(bucket, failed_key, failed_record)
            continue

        valid_count += 1
        schema = record["metadata"]["schema"]
        event_id = record["metadata"]["event_id"]
        output = standardize_event(record, bucket, key)

        processed_key = build_output_key(schema, PROCESSED_PREFIX, event_id)
        put_json(bucket, processed_key, output)

    return {"valid": valid_count, "invalid": invalid_count}


def lambda_handler(event, context):
    total_valid = 0
    total_invalid = 0

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        try:
            if not key.startswith("raw/"):
                print(f"Skipping non-raw object: s3://{bucket}/{key}")
                continue

            result = process_object(bucket, key)
            total_valid += result["valid"]
            total_invalid += result["invalid"]

            print(json.dumps({
                "source": f"s3://{bucket}/{key}",
                "valid": result["valid"],
                "invalid": result["invalid"],
            }))

        except Exception as exc:
            error_key = (
                f"{FAILED_PREFIX}/lambda_runtime_error/"
                f"{partition_path(now_utc())}/"
                f"{context.aws_request_id}.json"
            )
            put_json(bucket, error_key, {
                "metadata": {
                    "quality_status": "lambda_runtime_error",
                    "source_s3_bucket": bucket,
                    "source_s3_key": key,
                    "processed_time": now_utc().isoformat(),
                    "request_id": context.aws_request_id,
                },
                "error": str(exc),
                "traceback": traceback.format_exc(),
            })
            raise

    return {
        "statusCode": 200,
        "valid_records": total_valid,
        "invalid_records": total_invalid,
    }
