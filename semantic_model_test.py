import os
import shutil
import subprocess
import snowflake.connector
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Access the variables
db_user = os.getenv('SNOWFLAKE_USER')
db_password = os.getenv('SNOWFLAKE_PASSWORD')
db_account = os.getenv('SNOWFLAKE_ACCOUNT')

def run_tests():
    print("Initiating Semantic Model Testing Suite...\n")
    
    # Establish the connection
    conn = snowflake.connector.connect(
        account=db_account,
        user=db_user,
        password=db_password,
        warehouse="COMPUTE_WH",
        database="OEE_COMMAND_CENTER",
        schema="FACTORY_FLOOR"
    )
    cs = conn.cursor()

    # ---------------------------------------------------------
    # TEST 1: Physical Data Integrity Check
    # ---------------------------------------------------------
    print("--- TEST 1: Underlying Data Integrity ---")
    try:
        cs.execute("SELECT COUNT(*) FROM IT_OT_CONVERGED")
        count = cs.fetchone()[0]
        if count > 0:
            print(f"SUCCESS: IT_OT_CONVERGED dynamic table contains {count} rows.")
        else:
            print("WARNING: IT_OT_CONVERGED is empty. Semantic queries will return no results.")

        # Fetch a sample row to verify join logic
        cs.execute("SELECT * FROM IT_OT_CONVERGED LIMIT 1")
        sample_row = cs.fetchone()
        print(f"Sample Data Row: {sample_row}\n")

    except Exception as e:
        print(f"Data Integrity Test Failed: {e}\n")
    finally:
        cs.close()
        conn.close()

    # ---------------------------------------------------------
    # TEST 2: Natural Language Semantic Translation
    # ---------------------------------------------------------
    print("--- TEST 2: Natural Language Query Translation ---")
    
    test_query = "What is the average temperature for SKU-899 compared to SKU-100 on LINE-2-PACKAGING?"
    ontology_name = "factory_health_ontology" 
    
    # Mirroring the fallback logic from semantic_model_deployment.py
    if shutil.which("coco"):
        try:
            print(f"CoCo CLI found. Executing NLP test query: '{test_query}'")
            result = subprocess.run(
                ["coco", "test", "semantic-model", ontology_name, "--query", test_query],
                check=True,
                capture_output=True,
                text=True
            )
            print("\nSUCCESS: Semantic Translation Passed!")
            print("Generated SQL & Results:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("\nERROR: NLP Test Failed via CoCo CLI:")
            print(e.stderr or e.stdout)
    else:
        print("WARNING: CoCo CLI not found in PATH.")
        print("Because your semantic_model_deployment.py script staged the YAML file directly, ")
        print("you must execute the Cortex Analyst natural language tests directly inside the ")
        print("Snowsight UI (Data -> Databases -> Cortex Analyst) to verify translation.")

if __name__ == "__main__":
    run_tests()