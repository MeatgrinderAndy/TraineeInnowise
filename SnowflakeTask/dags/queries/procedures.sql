USE DATABASE SNOWFLAKE_LEARNING_DB;

CREATE OR REPLACE PROCEDURE STAGE1.load_raw_data()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
  rows_loaded INT DEFAULT 0;
BEGIN
  COPY INTO STAGE1.airline_raw 
  FROM @SNOWFLAKE_LEARNING_DB.STAGE1.csv_stage
  FILE_FORMAT = (
      TYPE = CSV 
      FIELD_DELIMITER = ',' 
      SKIP_HEADER = 1 
      FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  )
  FORCE = TRUE;
  
  rows_loaded := SQLROWCOUNT;
  
  COMMIT;
  
  RETURN 'Stage 1 Loaded: ' || :rows_loaded || ' rows';
END;
$$;

CREATE OR REPLACE PROCEDURE STAGE2.process_clean_data()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    row_count INT DEFAULT 0;
BEGIN
    INSERT INTO STAGE2.airline_clean (passenger_id, full_name, gender, age, country_name, flight_date, flight_status)
    SELECT 
        passenger_id, first_name || ' ' || last_name, gender, TRY_TO_NUMBER(age),
        country_name, TRY_TO_DATE(departure_date, 'MM/DD/YYYY'), flight_status
    FROM STAGE1.airline_raw_stream
    WHERE metadata$action = 'INSERT';
    
    row_count := SQLROWCOUNT;
    
    INSERT INTO AUDIT.etl_logs (step_name, rows_affected) VALUES ('Stage 1 -> Stage 2', :row_count);
    
    COMMIT;
    
    RETURN 'Stage 2 Processed: ' || :row_count || ' rows';
END;
$$;

CREATE OR REPLACE PROCEDURE STAGE3.aggregate_data()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    row_count INT DEFAULT 0;
BEGIN
    MERGE INTO STAGE3.flights_by_country AS target
    USING (
        SELECT country_name, COUNT(*) as cnt
        FROM STAGE2.airline_clean_stream
        WHERE metadata$action = 'INSERT'
        GROUP BY country_name
    ) AS source
    ON target.country_name = source.country_name
    WHEN MATCHED THEN UPDATE SET target.total_flights = target.total_flights + source.cnt, target.last_updated = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (country_name, total_flights, last_updated) VALUES (source.country_name, source.cnt, CURRENT_TIMESTAMP());

    row_count := SQLROWCOUNT;
    INSERT INTO AUDIT.etl_logs (step_name, rows_affected) VALUES ('Stage 2 -> Stage 3', :row_count);
    COMMIT;
    
    RETURN 'Stage 3 Aggregated: ' || :row_count || ' rows';
END;
$$;