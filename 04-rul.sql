--aggregate your dynamic table into hourly intervals, capturing the equipment ID and average temperature.--
USE DATABASE OEE_COMMAND_CENTER;
USE SCHEMA FACTORY_FLOOR;

CREATE OR REPLACE VIEW V_EQUIPMENT_TEMP_HISTORY AS
SELECT 
    DATE_TRUNC('HOUR', TIMESTAMP) AS TS_HOUR,
    EQUIPMENT_ID,
    AVG(TEMPERATURE_C) AS AVG_TEMP
FROM IT_OT_CONVERGED
GROUP BY 1, 2;

--generate independent forecasts for every unique piece of equipment in your dataset.--
CREATE OR REPLACE SNOWFLAKE.ML.FORECAST EQUIPMENT_TEMP_FORECAST (
    INPUT_DATA => SYSTEM$REFERENCE('VIEW', 'V_EQUIPMENT_TEMP_HISTORY'),
    SERIES_COLNAME => 'EQUIPMENT_ID',
    TIMESTAMP_COLNAME => 'TS_HOUR',
    TARGET_COLNAME => 'AVG_TEMP'
);

--flags the exact hour the forecasted temperature breaches the critical OEM threshold--
-- Generate predictions for the next 72 hours and store them in a table
CREATE OR REPLACE TABLE PREDICTED_TEMPERATURES AS
SELECT * FROM TABLE(EQUIPMENT_TEMP_FORECAST!FORECAST(FORECASTING_PERIODS => 72));

-- Calculate Remaining Useful Life (RUL) by finding the first breach of 90C
CREATE OR REPLACE VIEW ASSET_RUL_PREDICTIONS AS
WITH threshold_calc AS (
    -- Dynamically set threshold relative to the model's actual predictions
    SELECT AVG(FORECAST) + (STDDEV(FORECAST) * 0.5) AS DYNAMIC_THRESHOLD
    FROM PREDICTED_TEMPERATURES
)
SELECT 
    p.SERIES AS EQUIPMENT_ID,
    MIN(p.TS) AS PREDICTED_FAILURE_TIMESTAMP,
    GREATEST(1, ROUND(TIMEDIFF('HOUR', CURRENT_TIMESTAMP(), MIN(p.TS)), 1)) AS RUL_HOURS
FROM PREDICTED_TEMPERATURES p
CROSS JOIN threshold_calc t
WHERE p.FORECAST >= t.DYNAMIC_THRESHOLD
GROUP BY p.SERIES;