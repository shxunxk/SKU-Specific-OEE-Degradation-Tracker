--run this in snowflake worksheet after the files are uploaded as data--
COPY INTO RAW_IT_BATCHES FROM @FACTORY_DATA_STAGE/it_batch_schedule.csv;
COPY INTO RAW_OT_TELEMETRY FROM @FACTORY_DATA_STAGE/ot_telemetry_stream.csv;