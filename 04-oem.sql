USE ROLE ACCOUNTADMIN;

USE DATABASE OEE_COMMAND_CENTER;
USE SCHEMA FACTORY_FLOOR;

-- 1. Create the internal stage
CREATE STAGE IF NOT EXISTS OEM_MANUALS_STAGE
    DIRECTORY = (ENABLE = TRUE);

-- 2. Upload the OEM PDF into the stage
PUT 'file:///C:/Users/Shaunak/Documents/snowflake cococli/SKU-Specific-OEE-Degradation-Tracker/data/OEM_LINE-2-PACKAGING_Equipment_Manual.pdf'
    @OEM_MANUALS_STAGE
    AUTO_COMPRESS = FALSE
    OVERWRITE = TRUE;

-- 3. Refresh stage directory metadata
ALTER STAGE OEM_MANUALS_STAGE REFRESH;

-- 4. Verify the uploaded file
SELECT *
FROM DIRECTORY(@OEM_MANUALS_STAGE);