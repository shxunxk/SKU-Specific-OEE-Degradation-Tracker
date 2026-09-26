SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'OEE_COMMAND_CENTER.FACTORY_FLOOR.OEM_MANUAL_SEARCH',
    '{
        "query": "What is the critical temperature limit?",
        "columns": ["FILE_NAME", "CHUNK_INDEX", "CHUNK_TEXT"],
        "limit": 5
    }'
);