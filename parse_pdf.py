import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db_user = os.getenv("SNOWFLAKE_USER")
db_password = os.getenv("SNOWFLAKE_PASSWORD")
db_account = os.getenv("SNOWFLAKE_ACCOUNT")


def get_connection():
    print("Testing Snowflake connection...")

    return snowflake.connector.connect(
        account=db_account,
        user=db_user,
        password=db_password,
        warehouse="COMPUTE_WH",
        database="OEE_COMMAND_CENTER",
        schema="FACTORY_FLOOR"
    )


def execute_sql_file(conn, sql_file):
    print(f"\nExecuting {sql_file}...")

    cursor = conn.cursor()

    try:
        with open(sql_file, "r", encoding="utf-8") as f:
            sql = f.read()

        statements = [
            statement.strip()
            for statement in sql.split(";")
            if statement.strip()
        ]

        for i, statement in enumerate(statements, start=1):

            print(f"\n[{i}/{len(statements)}]")
            print(statement[:200])

            cursor.execute(statement)

            if cursor.description:
                rows = cursor.fetchall()

                for row in rows:
                    print(row)

        print(f"\nSuccessfully executed: {sql_file}")

    finally:
        cursor.close()


def main():

    conn = None

    try:
        conn = get_connection()

        # 1. Parse PDF and create chunks
        execute_sql_file(
            conn,
            "05-parse.sql"
        )

        # 2. Create/update Cortex Search Service
        execute_sql_file(
            conn,
            "06-cortex.sql"
        )

        print("\nDocument processing + Cortex Search setup completed.")

    except Exception as e:
        print("\nERROR:")
        print(e)

    finally:
        if conn:
            conn.close()

        print("\nSnowflake connection closed.")


if __name__ == "__main__":
    main()