import os
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, desc, sum, count, when, lower, unix_timestamp, round, dense_rank
import logging 
logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger(__name__)

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

spark = SparkSession.builder.appName("MoviesForRent").getOrCreate()

db_url = f"jdbc:postgresql://{db_host}:{db_port}/{db_name}"

db_properties = {
    "user": db_user,
    "password": db_password,
    "driver": "org.postgresql.Driver"
}

logger.info("--- READING DATA ---")
try:
    actor_df = spark.read.jdbc(url=db_url, table="actor", properties=db_properties)
    category_df = spark.read.jdbc(url=db_url, table="category", properties=db_properties)
    film_df = spark.read.jdbc(url=db_url, table="film", properties=db_properties)
    film_actor_df = spark.read.jdbc(url=db_url, table="film_actor", properties=db_properties)
    film_category_df = spark.read.jdbc(url=db_url, table="film_category", properties=db_properties)
    inventory_df = spark.read.jdbc(url=db_url, table="inventory", properties=db_properties)
    payment_df = spark.read.jdbc(url=db_url, table="payment", properties=db_properties)
    rental_df = spark.read.jdbc(url=db_url, table="rental", properties=db_properties)
    customer_df = spark.read.jdbc(url=db_url, table="customer", properties=db_properties)
    address_df = spark.read.jdbc(url=db_url, table="address", properties=db_properties)
    city_df = spark.read.jdbc(url=db_url, table="city", properties=db_properties)
    logger.info("--- SUCCESS ---")
except Exception as e:
    logger.error("!!! CONNECTION ERROR !!!")
    logger.error(str(e))

print("\n1. Output the number of movies in each category, sorted in descending order")

q1_result = category_df.join(film_category_df, "category_id") \
    .groupBy("name") \
    .agg(count("film_id").alias("film_count")) \
    .orderBy(desc("film_count"))

q1_result.show()


print("\n2. Output the 10 actors whose movies rented the most, sorted in descending order. ")

q2_result = actor_df.join(film_actor_df, "actor_id") \
    .join(inventory_df, "film_id") \
    .join(rental_df, "inventory_id") \
    .groupBy("actor_id", "first_name", "last_name") \
    .agg(count("rental_id").alias("total_rentals")) \
    .orderBy(desc("total_rentals")) \
    .limit(10)

q2_result.show()


print("\n3. Output the category of movies on which the most money was spent. ")

q3_result = category_df.join(film_category_df, "category_id") \
    .join(inventory_df, "film_id") \
    .join(rental_df, "inventory_id") \
    .join(payment_df, "rental_id") \
    .groupBy("name") \
    .agg(sum("amount").alias("total_sales")) \
    .orderBy(desc("total_sales")) \
    .limit(1)

q3_result.show()


print("\n4. Output the names of movies that are not in the inventory. ")

q4_result = film_df.join(inventory_df, "film_id", "left_anti") \
    .select("title")

q4_result.show()


print("\n5. Output the top 3 actors who have appeared most in movies in the “Children” category. " \
        "If several actors have the same number of movies, output all of them. ")

children_movies = category_df.filter(col("name") == "Children") \
    .join(film_category_df, "category_id") \
    .join(film_df, "film_id") \
    .join(film_actor_df, "film_id") \
    .join(actor_df, "actor_id")

actor_counts = children_movies.groupBy("actor_id", "first_name", "last_name") \
    .agg(count("film_id").alias("films_count"))

window_spec = Window.orderBy(desc("films_count"))

ranked_actors = actor_counts.withColumn("actor_rank", dense_rank().over(window_spec))

q5_result = ranked_actors.filter(col("actor_rank") <= 3) \
    .select("last_name", "first_name", "films_count")

q5_result.show()


print("\n6. Output cities with the number of active and inactive customers (active - customer.active = 1). " \
        "Sort by the number of inactive customers in descending order. ")

q6_result = city_df.join(address_df, "city_id") \
    .join(customer_df, "address_id") \
    .groupBy("city") \
    .agg(
        sum(when(col("active") == 1, 1).otherwise(0)).alias("active_customers"),
        sum(when(col("active") == 0, 1).otherwise(0)).alias("inactive_customers")
    ) \
    .orderBy(desc("inactive_customers"))

q6_result.show()


print("\n7. Output the category of movies that have the highest number of total rental hours in the cities (customer.address_id in this city), "
        "and that start with the letter “a”. Do the same for cities with a “-” symbol.")

full_data = city_df.join(address_df, "city_id") \
    .join(customer_df, "address_id") \
    .join(rental_df, "customer_id") \
    .join(inventory_df, "inventory_id") \
    .join(film_category_df, "film_id") \
    .join(category_df, "category_id") \
    .withColumn("rental_hours", (unix_timestamp("return_date") - unix_timestamp("rental_date")) / 3600)

print("   >>> Cities starting with 'a':")
res_a = full_data.filter(lower(col("city")).startswith("a")) \
    .groupBy("name") \
    .agg(round(sum("rental_hours"), 2).alias("total_hours")) \
    .orderBy(desc("total_hours")) \
    .limit(1)

res_a.show()

print("   >>> Cities with '-':")
res_dash = full_data.filter(col("city").contains("-")) \
    .groupBy("name") \
    .agg(round(sum("rental_hours"), 2).alias("total_hours")) \
    .orderBy(desc("total_hours")) \
    .limit(1)

res_dash.show()

spark.stop()