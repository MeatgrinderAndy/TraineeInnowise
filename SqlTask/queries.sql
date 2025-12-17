--	Output the number of movies in each category, sorted descending.

SELECT c.name AS category_name, COUNT (fc.film_id) AS film_count
FROM category c
INNER JOIN film_category fc ON c.category_id = fc.category_id
GROUP BY c.name
ORDER BY film_count DESC;


--	Output the 10 actors whose movies rented the most, sorted in descending order.

SELECT a.last_name, a.first_name, COUNT(r.rental_id) AS rental_count
FROM actor a
INNER JOIN film_actor fa ON a.actor_id = fa.actor_id
INNER JOIN inventory i ON fa.film_id = i.film_id
INNER JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY rental_count DESC
LIMIT 10;


--	Output the category of movies on which the most money was spent.

SELECT c.name AS category_name, SUM(p.amount) AS total_sales
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
JOIN inventory i ON fc.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
JOIN payment p ON r.rental_id = p.rental_id
GROUP BY c.name
ORDER BY total_sales DESC
LIMIT 1;


--	Print the names of movies that are not in the inventory. Write a query without using the IN operator.

SELECT f.title
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
WHERE i.film_id IS NULL;


--	Output the top 3 actors who have appeared the most in movies in the “Children” category. 
--	If several actors have the same number of movies, output all of them.

WITH ActorCounts AS (
    SELECT a.last_name, a.first_name, COUNT(f.film_id) AS films_count,
    	DENSE_RANK() OVER (ORDER BY COUNT(f.film_id) DESC) as actor_rank
    FROM actor a
    JOIN film_actor fa ON a.actor_id = fa.actor_id
    JOIN film f ON fa.film_id = f.film_id
    JOIN film_category fc ON f.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    WHERE c.name = 'Children'
    GROUP BY a.actor_id, a.first_name, a.last_name
)
SELECT last_name, first_name, films_count
FROM ActorCounts
WHERE actor_rank <= 3;


--	Output cities with the number of active and inactive customers (active - customer.active = 1). 
--	Sort by the number of inactive customers in descending order.

SELECT ci.city, SUM(CASE WHEN cu.active = 1 THEN 1 ELSE 0 END) AS active_customers, 
	SUM(CASE WHEN cu.active = 0 THEN 1 ELSE 0 END) AS inactive_customers
FROM city ci
JOIN address a ON ci.city_id = a.city_id
JOIN customer cu ON a.address_id = cu.address_id
GROUP BY ci.city_id, ci.city
ORDER BY inactive_customers DESC;


--	Output the category of movies that have the highest number of total rental hours in the city (customer.address_id in this city) 
--	and that start with the letter “a”. Do the same for cities that have a “-” in them. Write everything in one query.

WITH CityRentals AS (
    SELECT 
        cat.name AS category_name,
        ci.city,
        ROUND(EXTRACT(EPOCH FROM (r.return_date - r.rental_date))/3600, 2) AS hours
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film_category fc ON i.film_id = fc.film_id
    JOIN category cat ON fc.category_id = cat.category_id
    JOIN customer cu ON r.customer_id = cu.customer_id
    JOIN address a ON cu.address_id = a.address_id
    JOIN city ci ON a.city_id = ci.city_id
    WHERE r.return_date IS NOT NULL
),
GroupA AS (
    SELECT 'Cities starting with "a"' AS condition_group, category_name, SUM(hours) AS total_hours
    FROM CityRentals
    WHERE city ILIKE 'a%'
    GROUP BY category_name
),
GroupHyphen AS (
    SELECT 'Cities with "-"' AS condition_group, category_name, SUM(hours) AS total_hours
    FROM CityRentals
    WHERE city LIKE '%-%'
    GROUP BY category_name
)
SELECT * FROM (
    SELECT condition_group, category_name, total_hours
    FROM GroupA
    ORDER BY total_hours DESC
    LIMIT 1
) a_group
UNION ALL
SELECT * FROM (
    SELECT condition_group, category_name, total_hours
    FROM GroupHyphen
    ORDER BY total_hours DESC
    LIMIT 1
) hyphen_group;