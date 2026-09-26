import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_factory_data():
    start_time = datetime.now() - timedelta(days=7)
    current_time = start_time
    equipment_id = "LINE-2-PACKAGING"
    skus = ["SKU-100", "SKU-500", "SKU-899"]
    
    it_records = []
    
    # 1. Generate IT Batch Schedule
    for i in range(50):
        duration = timedelta(hours=np.random.randint(2, 6))
        end_time = current_time + duration
        sku = np.random.choice(skus)
        
        it_records.append({
            "BATCH_ID": f"B-{1000+i}",
            "SKU_ID": sku,
            "EQUIPMENT_ID": equipment_id,
            "START_TIME": current_time,
            "END_TIME": end_time
        })
        current_time = end_time + timedelta(minutes=30) # Machine changeover time

    it_df = pd.DataFrame(it_records)

    # 2. Generate OT Telemetry Stream
    ot_records = []
    ot_time = start_time
    
    while ot_time < current_time:
        base_temp = 75.0
        base_vib = 2.0
        
        # Identify if current minute falls within an active batch
        active_batch = it_df[(it_df['START_TIME'] <= ot_time) & (it_df['END_TIME'] >= ot_time)]
        
        # Apply strict 15% thermal degradation exclusively for SKU-899
        if not active_batch.empty and active_batch.iloc[0]['SKU_ID'] == "SKU-899":
            temp = base_temp * 1.15 + np.random.normal(0, 1.0)
            vib = base_vib * 1.20 + np.random.normal(0, 0.15)
        else:
            temp = base_temp + np.random.normal(0, 1.0)
            vib = base_vib + np.random.normal(0, 0.15)

        ot_records.append({
            "TIMESTAMP": ot_time,
            "EQUIPMENT_ID": equipment_id,
            "TEMPERATURE_C": round(temp, 2),
            "VIBRATION_RMS": round(vib, 2)
        })
        ot_time += timedelta(minutes=1)

    ot_df = pd.DataFrame(ot_records)

    # 3. Export to CSV for Snowflake Staging
    it_df.to_csv("it_batch_schedule.csv", index=False)
    ot_df.to_csv("ot_telemetry_stream.csv", index=False)
    print(f"Generated {len(it_df)} IT records and {len(ot_df)} OT records.")

if __name__ == "__main__":
    generate_factory_data()