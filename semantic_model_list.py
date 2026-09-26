import os
import subprocess
import shutil
import snowflake.connector
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Access the variables
db_user = os.getenv('SNOWFLAKE_USER')
db_password = os.getenv('SNOWFLAKE_PASSWORD')
db_account = os.getenv('SNOWFLAKE_ACCOUNT')

# Establish the connection
print("Testing Snowflake connection...")
conn = snowflake.connector.connect(
    account = db_account,
    user = db_user,
    password = db_password,
    warehouse = "COMPUTE_WH",
    database = "OEE_COMMAND_CENTER",
    schema = "FACTORY_FLOOR" 
)

cs = conn.cursor()
try:
    cs.execute("SELECT current_version()")
    row = cs.fetchone()
    print(f"Snowflake version: {row[0]}")
finally:
    cs.close()

print("Environment variables loaded and connection initiated successfully!\n")

# Perform the CoCo Semantic Model Listing
print("Retrieving existing CoCo Semantic Models...")
listed = False

# Attempt 1: If CoCo CLI executable is installed and available in PATH
if shutil.which("coco"):
    try:
        print("Found CoCo CLI in PATH. Fetching list...")
        result = subprocess.run(
            ["coco", "list", "semantic-models"],
            check=True,
            capture_output=True,
            text=True
        )
        print("\n--- Semantic Models (via CoCo CLI) ---")
        print(result.stdout)
        listed = True
    except subprocess.CalledProcessError as e:
        print("Warning: CoCo CLI execution returned an error:")
        print(e.stderr or e.stdout)
    except Exception as e:
        print(f"Warning: CoCo CLI execution failed: {e}")

# Attempt 2: Direct Snowflake Native Stage Listing
if not listed:
    print("Listing Semantic Models directly from Snowflake stage (@SEMANTIC_MODELS_STAGE)...")
    cs = conn.cursor()
    try:
        # Query the stage for semantic model files
        cs.execute("LIST @SEMANTIC_MODELS_STAGE")
        files = cs.fetchall()
        
        print("\n--- Semantic Models (via Snowflake Stage) ---")
        if files:
            for file_row in files:
                # file_row[0] contains the relative path/filename
                # file_row[1] contains the file size
                # file_row[3] contains the last modified timestamp
                file_name = os.path.basename(file_row[0])
                file_size = file_row[1]
                last_modified = file_row[3]
                print(f"- {file_name} (Size: {file_size} bytes | Last Modified: {last_modified})")
        else:
            print("No semantic models found. The @SEMANTIC_MODELS_STAGE is currently empty.")
            
    except snowflake.connector.errors.ProgrammingError as e:
        if "does not exist" in str(e).lower():
            print("\nThe stage @SEMANTIC_MODELS_STAGE does not exist yet. No models have been deployed.")
        else:
            print(f"\nError listing Semantic Models in Snowflake: {e}")
    except Exception as e:
        print(f"\nError listing Semantic Models in Snowflake: {e}")
    finally:
        cs.close()

conn.close()