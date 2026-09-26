import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("SNOWFLAKE_USER")
db_password = os.getenv("SNOWFLAKE_PASSWORD")
db_account = os.getenv("SNOWFLAKE_ACCOUNT")

SEARCH_SERVICE = "OEE_COMMAND_CENTER.FACTORY_FLOOR.OEM_MANUAL_SEARCH"


def get_connection():
    print("Connecting to Snowflake...")

    return snowflake.connector.connect(
        account=db_account,
        user=db_user,
        password=db_password,
        warehouse="COMPUTE_WH",
        database="OEE_COMMAND_CENTER",
        schema="FACTORY_FLOOR"
    )


def retrieve_documents(conn, user_query):
    cursor = conn.cursor()

    try:
        sql = """
        SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            %s,
            PARSE_JSON(%s)
        ) AS SEARCH_RESULTS
        """

        search_payload = {
            "query": user_query,
            "columns": [
                "FILE_NAME",
                "CHUNK_INDEX",
                "CHUNK_TEXT"
            ],
            "limit": 5
        }

        import json

        cursor.execute(
            sql,
            (
                SEARCH_SERVICE,
                json.dumps(search_payload)
            )
        )

        result = cursor.fetchone()

        if result:
            return result[0]

        return None

    finally:
        cursor.close()


def main():

    user_query = input("\nEnter your OEM manual query: ").strip()

    if not user_query:
        print("Query cannot be empty.")
        return

    conn = None

    try:
        conn = get_connection()

        print(f"\nQuery: {user_query}")
        print("\nSearching OEM manual...")

        results = retrieve_documents(conn, user_query)

        print("\nRetrieved results:")
        print(results)

    except Exception as e:
        print("\nERROR:")
        print(e)

    finally:
        if conn:
            conn.close()
            print("\nSnowflake connection closed.")


if __name__ == "__main__":
    main()