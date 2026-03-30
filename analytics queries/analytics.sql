CREATE DATABASE coffee_shop ;


CREATE SCHEMA coffee_shop.raw;

    USE WAREHOUSE coffee_wh;
    USE DATABASE coffee_shop;
    USE SCHEMA raw;
    

CREATE STORAGE INTEGRATION s3_storage_integration 
TYPE = EXTERNAL_stage
STORAGE_provider = 'S3'
ENABLED = TRUE
storage_allowed_locations = ('S3 PATH')
storage_aws_role_arn = 'ARN OF THE ROLE WITH ACCESS TO S3 PATH'


DESC INTEGRATION s3_storage_integration;

CREATE STAGE coffee_stage 
URL = 'S3 PATH'
storage_integration = s3_storage_integration
FILE_FORMAT = (TYPE=  PARQUET)

list @coffee_stage

CREATE FILE FORMAT parquet_format
TYPE = PARQUET
SNAPPY_COMPRESSION = TRUE;

SELECT * FROM @coffee_stage (FILE_FORMAT => parquet_format, PATTERN => '.*[.]parquet') LIMIT 5;

SELECT 
    $1:order_id::STRING       AS order_id,
    $1:store_id::STRING       AS store_id,
    $1:system::STRING         AS system,
    $1:drink::STRING          AS drink,
    $1:quantity::INT          AS quantity,
    $1:price::FLOAT           AS price,
    $1:revenue::FLOAT         AS revenue,
    $1:customer_id::STRING    AS customer_id,
    $1:timestamp::TIMESTAMP   AS order_ts
FROM @coffee_stage
(FILE_FORMAT => parquet_format, PATTERN => '.*[.]parquet')
LIMIT 10;

CREATE TABLE coffee_shop.raw.orders AS

SELECT 
    $1:order_id::STRING AS order_id,
     $1:store_id::STRING       AS store_id,
     $1:system::STRING         AS system,
    $1:drink::STRING          AS drink,
     $1:quantity::INT          AS quantity,
     $1:price::FLOAT           AS price,
    $1:revenue::FLOAT         AS revenue,
    $1:customer_id::STRING    AS customer_id,
    $1:timestamp::TIMESTAMP   AS order_ts

    FROM @coffee_stage
    (FILE_FORMAT => parquet_format, PATTERN => '.*[.]parquet' )
    

SELECT COUNT(*) FROM coffee_shop.raw.orders;



// Total revenue by store 

SELECT 
    store_id,
    SUM(REVENUE) AS TOTAL_REVENUE
    FROM coffee_shop.raw.orders 
    GROUP BY store_id
    ORDER BY TOTAL_REVENUE DESC 


-- Most popular drink 

SELECT 
    Drink,
    COUNT(order_id) AS no_of_orders,
    SUM(price) AS total_price FROM coffee_shop.raw.orders
    GROUP BY Drink
    ORDER BY no_of_orders DESC

-- Most popular drink by store


SELECT 
    DRINK,
    store_id,
    COUNT(store_id) AS no_of_orders,
    SUM(REVENUE) AS Total_Revenue
    FROM coffee_shop.raw.orders
    GROUP BY Drink,store_id
    ORDER BY Total_Revenue DESC

-- How many orders came through POS,IOS,Android?

SELECT 
SYSTEM,
COUNT(order_id) AS no_of_orders,
SUM(Revenue) AS total_revenue
FROM coffee_shop.raw.orders
GROUP BY SYSTEM
ORDER BY total_revenue DESC

--How was the distribution of orders across hours of the day

SELECT 
HOUR(order_ts) AS hour_of_day,
COUNT(order_id) AS no_of_orders
FROM coffee_shop.raw.orders
GROUP BY hour_of_day
ORDER BY no_of_orders DESC
