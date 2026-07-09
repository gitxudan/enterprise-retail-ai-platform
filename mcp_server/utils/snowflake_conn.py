import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv(override=True)

def get_snowflake_connection():
    return snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    passcode=os.getenv("SNOWFLAKE_MFA_PASSCODE"),
    role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    database=os.getenv("SNOWFLAKE_DATABASE", "RETAIL_AI_PLATFORM_DEV"),
)

def run_query(sql: str, params=None):
    conn = get_snowflake_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or {})
        columns = [col[0].lower() for col in cur.description]
        rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        result = run_query("SELECT CURRENT_USER(), CURRENT_DATABASE(), CURRENT_WAREHOUSE();")
        print("✅ Connected to Snowflake!")
        print(result)
    except Exception as e:
        print("❌ Connection failed:")
        print(e)