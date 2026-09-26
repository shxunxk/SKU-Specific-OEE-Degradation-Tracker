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

# Perform the CoCo Semantic Model Deletion
print("Deleting the CoCo Semantic Model...")
yaml_filename = "factory_health_ontology.yaml"
model_name = "factory_health_ontology"
deleted = False

# Attempt 1: If CoCo CLI executable is installed and available in PATH
if shutil.which("coco"):
    try:
        print("Found CoCo CLI in PATH. Executing deletion...")
        result = subprocess.run(
            ["coco", "delete", "semantic-model", model_name],
            check=True,
            capture_output=True,
            text=True
        )
        print("Semantic Model Deletion Successful via CoCo CLI!")
        print(result.stdout)
        deleted = True
    except subprocess.CalledProcessError as e:
        print("Warning: CoCo CLI execution returned an error:")
        print(e.stderr or e.stdout)
    except Exception as e:
        print(f"Warning: CoCo CLI execution failed: {e}")

# Attempt 2: Direct Snowflake Native Stage Deletion
if not deleted:
    print("Deleting Semantic Model directly from Snowflake stage (@SEMANTIC_MODELS_STAGE)...")
    cs = conn.cursor()
    try:
        # Remove the YAML file from the Snowflake stage
        cs.execute(f"REMOVE @SEMANTIC_MODELS_STAGE/{yaml_filename}")
        
        # Verify staged file removal
        cs.execute("LIST @SEMANTIC_MODELS_STAGE")
        files = [row[0] for row in cs.fetchall()]
        
        print(f"Semantic Model '{yaml_filename}' successfully removed from Snowflake stage!")
        print(f"Remaining staged files: {files}")
        print("\nSemantic Model Deletion Complete!")
    except Exception as e:
        print(f"Error deleting Semantic Model in Snowflake: {e}")
    finally:
        cs.close()

conn.close()