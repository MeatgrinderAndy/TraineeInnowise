USE DATABASE SNOWFLAKE_LEARNING_DB;

//DDL
CREATE table STAGE2.airline_clean_backup clone STAGE2.airline_clean at (OFFSET => -60*5)

DROP TABLE STAGE2.airline_clean_backup;
UNDROP TABLE STAGE2.airline_clean_backup;

//DML
SELECT * FROM STAGE2.airline_clean BEFORE (STATEMENT => '01c24df4-0005-07c5-0001-3526000602c6');

INSERT INTO STAGE2.airline_clean_backup SELECT * FROM STAGE2.airline_clean_backup AT (OFFSET => -1200) WHERE passenger_id = 'ABVWIg';

//Secure View + Row level security
CREATE OR REPLACE ROW ACCESS POLICY admin_policy AS (country VARCHAR) RETURNS BOOLEAN -> 
    CURRENT_ROLE() = 'ACCOUNTADMIN' OR country = 'United States';

ALTER TABLE STAGE3.flights_by_country ADD ROW ACCESS POLICY admin_policy ON (country_name);

CREATE OR REPLACE SECURE VIEW STAGE3.secure_flights_view AS SELECT * FROM STAGE3.flights_by_country;
