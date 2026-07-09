# Retail AI Platform - Data Simulator Starter

This starter generates realistic retail master data and event streams for an AWS + Snowflake Cortex AI capstone.

## Structure

- `simulator/master_data.py`: creates Store, Product, and Customer master data
- `simulator/event_generator.py`: generates transaction, inventory, review, and support-ticket events
- `producer/kinesis_producer.py`: optional Kinesis sender
- `producer/local_runner.py`: local JSONL generator for testing before AWS streaming
- `schemas/*.json`: example data contracts

## Local test

```bash
pip install faker boto3 python-dotenv
python -m producer.local_runner
```

## AWS streaming

Create a `.env` file locally:

```env
AWS_REGION=ap-southeast-1
KINESIS_STRUCTURED_STREAM=retail-dev-kds-pos
KINESIS_UNSTRUCTURED_STREAM=retail-dev-kds-review
```

Then run:

```bash
python -m producer.kinesis_producer
```

Never commit `.env` or AWS credentials.
