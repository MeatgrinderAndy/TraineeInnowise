USE DATABASE SNOWFLAKE_LEARNING_DB;
CREATE SCHEMA IF NOT EXISTS STAGE1;
CREATE SCHEMA IF NOT EXISTS STAGE2;
CREATE SCHEMA IF NOT EXISTS STAGE3;
CREATE SCHEMA IF NOT EXISTS AUDIT;

CREATE OR REPLACE STAGE STAGE1.csv_stage FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1);

CREATE TABLE IF NOT EXISTS STAGE1.airline_raw (
    row_index VARCHAR, passenger_id VARCHAR, first_name VARCHAR, last_name VARCHAR,
    gender VARCHAR, age VARCHAR, nationality VARCHAR, airport_name VARCHAR,
    airport_country_code VARCHAR, country_name VARCHAR, airport_continent VARCHAR,
    continents VARCHAR, departure_date VARCHAR, arrival_airport VARCHAR,
    pilot_name VARCHAR, flight_status VARCHAR, ticket_type VARCHAR, passenger_status VARCHAR
);

CREATE STREAM IF NOT EXISTS STAGE1.airline_raw_stream ON TABLE STAGE1.airline_raw;

CREATE TABLE IF NOT EXISTS STAGE2.airline_clean (
    passenger_id VARCHAR,
    full_name VARCHAR,
    gender VARCHAR,
    age NUMBER,
    country_name VARCHAR,
    flight_date DATE,
    flight_status VARCHAR
);

CREATE STREAM IF NOT EXISTS STAGE2.airline_clean_stream ON TABLE STAGE2.airline_clean;

CREATE TABLE IF NOT EXISTS STAGE3.flights_by_country (
    country_name VARCHAR,
    total_flights NUMBER,
    last_updated TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS AUDIT.etl_logs (
    log_id INT IDENTITY(1,1),
    step_name VARCHAR,
    rows_affected INT,
    log_time TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);