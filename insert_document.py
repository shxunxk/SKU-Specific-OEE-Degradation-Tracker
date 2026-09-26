import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db_user = os.getenv("SNOWFLAKE_USER")
db_password = os.getenv("SNOWFLAKE_PASSWORD")
db_account = os.getenv("SNOWFLAKE_ACCOUNT")

# Local PDF
PDF_FILE = "LINE-2-PACKAGING OEM Maintenance Manual.pdf"

# Snowflake stage
STAGE = "@OEE_COMMAND_CENTER.FACTORY_FLOOR.OEM_MANUALS_STAGE"


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


def upload_pdf(conn):
    print("\nUploading OEM manual...")

    cursor = conn.cursor()

    try:
        # Upload PDF to Snowflake internal stage
        sql = f"""
        PUT 'file://{os.path.abspath(PDF_FILE)}'
        {STAGE}
        AUTO_COMPRESS=FALSE
        OVERWRITE=TRUE
        """

        cursor.execute(sql)

        for row in cursor.fetchall():
            print(row)

        print("PDF uploaded successfully.")

    finally:
        cursor.close()


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

        # 1. Upload PDF
        upload_pdf(conn)

        # 2. Execute parsing/chunking SQL
        execute_sql_file(
            conn,
            "04-oem.sql"
        )

        print("\nOEM document pipeline completed.")

    except Exception as e:
        print("\nERROR:")
        print(e)

    finally:
        if conn:
            conn.close()
            print("\nSnowflake connection closed.")


if __name__ == "__main__":
    main()