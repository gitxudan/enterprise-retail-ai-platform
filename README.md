# Enterprise Retail AI Platform

**An end-to-end retail data and AI engineering project built with AWS, Snowflake, Snowflake Cortex AI, and Model Context Protocol (MCP).**

This hands-on capstone explores how structured retail events and unstructured customer feedback can be ingested, transformed, modeled, and exposed to analytics and AI applications through a unified cloud data platform.

> **Project status:** Work in progress. The core data platform, analytical models, feature engineering, and MCP tool-discovery foundation have been implemented. Cortex Search integration, AI-agent workflows, and end-to-end testing are being finalized.

## Architecture

![alt text](my_plot.png)

---

```text
Retail Event Sources
  |-- POS Transactions
  |-- Inventory Movements
  |-- Product Reviews
  `-- Support Tickets
             |
             v
AWS Ingestion: Kinesis / Firehose / S3 / Lambda
             |
             v
Snowflake RAW (external stage, file format, Snowpipe)
             |
             v
BRONZE (raw JSON / VARIANT)
             |
             v
SILVER (typed events; Streams + Tasks)
             |
             +---------------------------+
             |                           |
             v                           v
GOLD (business marts)           AI text preparation
             |                           |
             v                           v
FEATURES (ML-ready data)       Cortex Search / semantic retrieval
             |                           |
             +-------------+-------------+
                           |
                           v
                  Python MCP Server
                           |
                           v
                  AI Client / Agent
```

**Cross-cutting controls:** data quality, pipeline audit, Snowflake governance, and compute-cost monitoring. The diagram describes the overall design; components still being integrated are identified in the status section below.

## Business Scenario

A retail organization receives data from multiple operational systems. Transaction and inventory events support revenue, customer, and stock analysis, while product reviews and support tickets contain valuable but less structured signals about product quality and customer experience.

The project addresses three related needs:

1. **Reliable analytics:** standardize incoming events into consistent business datasets.
2. **Reusable analytical features:** derive customer, product, and store-level features for downstream analytics and machine learning.
3. **AI-ready access:** prepare text for semantic retrieval and expose selected analytical capabilities through MCP tools.

## Technology Stack

| Area | Technologies |
| --- | --- |
| Event ingestion | Python, Amazon Kinesis, Amazon Data Firehose, Amazon S3, AWS Lambda |
| Warehouse ingestion | Snowflake external stages, file formats, Snowpipe |
| Data processing | Snowflake SQL, VARIANT, Streams, Tasks |
| Analytics | Bronze / Silver / Gold modeling, data quality checks |
| Feature engineering | Snowflake feature tables |
| AI and retrieval | Snowflake Cortex AI, Cortex Search (integration in progress) |
| AI interoperability | Python MCP SDK, FastMCP, MCP client |
| Development | VS Code, Python virtual environment, Git, GitHub |

## Data Engineering Implementation

### 1. AWS ingestion and RAW layer

The project simulates retail events and routes data through AWS services into S3. Snowflake external-stage objects in the `RAW` schema provide the ingestion interface to S3. Initial loading uses `COPY INTO`; the architecture also includes Snowpipe for automated ingestion.

### 2. Bronze and Silver layers

Four event domains are represented throughout the core pipeline: transactions, inventory, product reviews, and support tickets.

- **Bronze:** retains raw JSON events in `VARIANT` columns with source-file and load-time metadata.
- **Silver:** extracts typed attributes from event payloads and makes them available for analytical modeling.
- **Incremental processing:** Snowflake Streams track source-table changes and Tasks execute downstream processing when configured conditions are met.

### 3. Gold business marts

| Gold dataset | Business purpose |
| --- | --- |
| `GOLD.DAILY_SALES_SUMMARY` | Daily retail sales performance |
| `GOLD.PRODUCT_PERFORMANCE` | Product-level performance analysis |
| `GOLD.CUSTOMER_360` | Consolidated customer activity and value |
| `GOLD.INVENTORY_HEALTH` | Inventory and replenishment indicators |

### 4. Feature engineering

The `FEATURES` schema supports reusable analytical inputs, including customer behavior, product risk, store performance, and customer-support-related signals. Feature tables bridge reporting datasets and potential ML use cases; their existence does not imply that a predictive model has already been trained or deployed.

### 5. Data quality and monitoring

SQL checks cover important conditions such as missing identifiers, duplicate transactions, invalid review ratings, and negative values in selected datasets. Results are recorded in governance tables for review. Operational SQL also supports inspection of task execution, stream state, and Snowflake warehouse credit usage.

## AI and MCP Integration

### Unstructured text and Cortex Search

Product reviews and support tickets are prepared as text sources and chunks for semantic retrieval. The intended retrieval path is:

```text
Review / Support Text
    -> Document Preparation
    -> Chunking
    -> Cortex Search Index
    -> Semantic Retrieval
    -> Context for an LLM-powered application
```

Cortex Search service setup and end-to-end retrieval validation remain part of the ongoing integration work.

### MCP data interface

A Python MCP server exposes a focused set of business-oriented tools:

| Tool | Intended purpose |
| --- | --- |
| `get_customer_profile` | Customer purchase behavior and support context |
| `get_product_health` | Product performance, review, and inventory signals |
| `get_store_performance` | Store sales and operational indicators |
| `search_reviews_and_tickets` | Semantic retrieval across review and support text |

The MCP client has successfully initialized a session and discovered all four tools. Individual tool responses and agent-driven end-to-end execution require separate validation.

## Repository Structure

```text
enterprise-retail-ai-platform/
├── lambda/              # AWS Lambda processing code
├── producer/            # Event producer and local runner
├── simulator/           # Retail event simulation
├── schemas/             # Event schemas / contracts
├── mcp_server/          # MCP server, client, and Snowflake utilities
├── snowflake/           # SQL scripts organized by platform layer (being consolidated)
├── assets/              # Architecture diagram and screenshots (add as available)
├── output/              # Local generated outputs (not for version control)
└── README.md
```

The Snowflake SQL is organized by logical responsibilities, with related objects grouped into a manageable number of scripts rather than one file per table:

```text
snowflake/
├── 00_setup/
├── 01_raw/
├── 02_bronze/
├── 03_silver/
├── 04_gold/
├── 05_governance/
├── 06_features/
├── 07_ai/
└── 08_monitoring/
```

> The directory layout above is the target organization for the repository. Some SQL assets may still be stored in Snowflake worksheets until export is complete.

## Implementation Status

| Component | Status |
| --- | --- |
| AWS event simulation and ingestion pipeline | Implemented in project exercises |
| Snowflake RAW, Bronze, Silver | Implemented |
| Snowflake Streams and Tasks | Implemented |
| Gold business marts | Implemented and validated |
| SQL data quality checks | Implemented and validated |
| Feature engineering tables | Implemented; scope varies by feature domain |
| Review and support text preparation | Implemented in SQL exercises |
| Cortex Search service and retrieval | Integration / validation in progress |
| MCP server and tool discovery | Implemented; tool discovery verified |
| MCP tool execution against Snowflake | End-to-end validation in progress |
| Predictive ML training and model serving | Planned / not yet demonstrated |
| LLM agent orchestration | Planned / in progress |

## Local Development

The repository contains a Python-based event producer and an MCP implementation. Development requires the relevant AWS and Snowflake resources and credentials; cloning the repository alone does not provision cloud infrastructure.

Example commands from the repository root:

```powershell
# Run the MCP server as a Python module
python -m mcp_server.server.retail_mcp_server

# In a separate terminal, run the MCP console client
python -m mcp_server.client.console_client
```

The server uses MCP standard input/output transport, so it normally waits silently for a client rather than printing an interactive prompt. The console client can also be used to launch the server as a subprocess.

**Security:** keep `.env`, passwords, MFA codes, private keys, local virtual environments, and generated files out of version control. For future unattended deployment, use an appropriate non-interactive Snowflake authentication mechanism and a least-privilege service role rather than an administrator role.

## Engineering Decisions

- **RAW vs. Bronze:** RAW stores ingestion-facing Snowflake objects, while Bronze stores actual raw event records and ingestion metadata.
- **Structured and unstructured paths:** numeric event data supports business marts and feature tables; text data supports retrieval-oriented AI workflows.
- **Streams and Tasks:** incremental change processing is preferable to repeatedly rebuilding downstream tables when new event batches arrive.
- **MCP tools:** explicit business functions create a clearer interface for AI applications than unrestricted arbitrary SQL access.
- **Cost-aware development:** warehouses and scheduled compute should be monitored and suspended when exercises are not running; serverless services may have separate charges.

## Next Steps

- Validate Cortex Search results against newly ingested review and support records.
- Test all four MCP tools with actual Snowflake data and error cases.
- Connect the MCP interface to an LLM-driven retail assistant.
- Complete selected ML inference experiments if time and budget permit.
- Add architecture screenshots, execution evidence, and a short demonstration walkthrough.

## Project Context

This is an independent, hands-on learning and portfolio project based on a simulated retail scenario. It is designed to demonstrate practical data engineering and AI integration concepts rather than claim deployment into a live retail production environment.

