""" Raw SQL queries."""

# Можно ли оптимизировать запросы?
# Например как то объеденить запросы person_film_id и person_films

film = """
SELECT
   fw.id,
   fw.title,
   fw.description,
   fw.rating as imdb_rating,
   fw.created,
   fw.modified,
   COALESCE(ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
   FILTER (WHERE pfw.role = 'director' AND p.id is not null), '{}') AS director,
   ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
   FILTER (WHERE pfw.role = 'actor' AND p.id is not null) AS actors,
   ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
   FILTER (WHERE pfw.role = 'writer' AND p.id is not null) AS writers,
   ARRAY_AGG(DISTINCT p.full_name) 
   FILTER (WHERE pfw.role = 'actor' AND p.id is not null) AS actors_names,
   ARRAY_AGG(DISTINCT p.full_name) 
   FILTER (WHERE pfw.role = 'writer' AND p.id is not null) AS writers_names,
   ARRAY_AGG(DISTINCT jsonb_build_object('id', g.id, 'name', g.name))
   FILTER (WHERE g.id is not null) as genre
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.modified > %s
GROUP BY fw.id
ORDER BY fw.modified;
"""

person_id = """
SELECT id, modified
FROM content.person
WHERE modified > %s
ORDER BY modified;
"""

persons = """
SELECT p.id, 
       p.full_name,
       p.modified,
       ARRAY_AGG(DISTINCT pfw.role) as role,
       ARRAY_AGG(DISTINCT pfw.film_work_id)::text[] as film_ids
FROM content.person p
LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
WHERE modified > %s
GROUP BY p.id, role
ORDER BY modified;
"""

person_film_id = """
SELECT fw.id
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
WHERE pfw.person_id IN %s AND p.modified > fw.modified AND fw.modified > %s
ORDER BY fw.modified;
"""

person_films = """
SELECT DISTINCT fw.id as film_id, 
       fw.modified,
       COALESCE(ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
       FILTER (WHERE pfw.role = 'director' AND p.id is not null), '{}') AS director,
       ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
       FILTER (WHERE pfw.role = 'actor' AND p.id is not null) AS actors,
       ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
       FILTER (WHERE pfw.role = 'writer' AND p.id is not null) AS writers,
       ARRAY_AGG(DISTINCT p.full_name) 
       FILTER (WHERE pfw.role = 'actor' AND p.id is not null) AS actors_names,
       ARRAY_AGG(DISTINCT p.full_name) 
       FILTER (WHERE pfw.role = 'writer' AND p.id is not null) AS writers_names
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
WHERE fw.id IN %s
GROUP BY fw.id
ORDER BY fw.modified;
"""

genre_id = """
SELECT id, modified
FROM content.genre
WHERE modified > %s
ORDER BY modified;
"""

genres = """
SELECT id,
       name,
       description,
       modified
FROM content.genre
WHERE modified > %s
ORDER BY modified;
"""

genre_film_id = """
SELECT fw.id, fw.modified
FROM content.film_work fw
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE gfw.genre_id IN %s AND g.modified > fw.modified AND fw.modified > %s
ORDER BY fw.modified;
"""


genre_films = """
SELECT DISTINCT fw.id as film_id,
       fw.modified,
       ARRAY_AGG(DISTINCT jsonb_build_object('id', g.id, 'name', g.name))
       FILTER (WHERE g.id is not null) as genre
FROM content.film_work fw
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.id IN %s
GROUP BY fw.id
ORDER BY fw.modified;
"""
