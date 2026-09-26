import os
import subprocess
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

# Create a cursor and test a simple query
cs = conn.cursor()
try:
    cs.execute("SELECT current_version()")
    row = cs.fetchone()
    print(f"Snowflake version: {row[0]}")
finally:
    cs.close()
    conn.close()

print("Environment variables loaded and connection initiated successfully!\n")

# Perform the CoCo Semantic Model Deployment
print("Deploying the CoCo Semantic Model...")
yaml_path = "./semantic_models/factory_health_ontology.yaml"

if not os.path.exists(yaml_path):
    print(f"Error: YAML configuration file not found at '{yaml_path}'.")
    print("Please ensure the YAML file is saved in the correct directory before running this script.")
else:
    deployed = False
    import shutil

    # Attempt 1: If CoCo CLI executable is installed and available in PATH
    if shutil.which("coco"):
        try:
            print("Found CoCo CLI in PATH. Executing deployment...")
            result = subprocess.run(
                ["coco", "deploy", "semantic-model", yaml_path],
                check=True,
                capture_output=True,
                text=True
            )
            print("Semantic Model Deployment Successful via CoCo CLI!")
            print(result.stdout)
            deployed = True
        except subprocess.CalledProcessError as e:
            print("Warning: CoCo CLI execution returned an error:")
            print(e.stderr or e.stdout)
        except Exception as e:
            print(f"Warning: CoCo CLI execution failed: {e}")

    # Attempt 2: Direct Snowflake Native Stage Deployment
    if not deployed:
        print("Deploying Semantic Model directly into Snowflake stage (@SEMANTIC_MODELS_STAGE)...")
        conn = snowflake.connector.connect(
            account=db_account,
            user=db_user,
            password=db_password,
            warehouse="COMPUTE_WH",
            database="OEE_COMMAND_CENTER",
            schema="FACTORY_FLOOR"
        )
        cs = conn.cursor()
        try:
            # Create stage for semantic models if it doesn't already exist
            cs.execute("CREATE STAGE IF NOT EXISTS SEMANTIC_MODELS_STAGE DIRECTORY = (ENABLE = TRUE)")
            
            # Stage the YAML semantic model definition
            abs_yaml_path = os.path.abspath(yaml_path).replace("\\", "/")
            cs.execute(f"PUT 'file://{abs_yaml_path}' @SEMANTIC_MODELS_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
            
            # Verify staged file
            cs.execute("LIST @SEMANTIC_MODELS_STAGE")
            files = [row[0] for row in cs.fetchall()]
            
            print("Semantic Model successfully staged to Snowflake!")
            print(f"Stage Location: @SEMANTIC_MODELS_STAGE/{os.path.basename(yaml_path)}")
            print(f"Staged files: {files}")
            print("\nSemantic Model Deployment Complete!")
        except Exception as e:
            print(f"Error staging Semantic Model in Snowflake: {e}")
        finally:
            cs.close()
            conn.close()