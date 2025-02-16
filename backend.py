from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

app = FastAPI()

# Database Connection
DB_NAME = "googleplay"
DB_USER = "user"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cursor = conn.cursor(cursor_factory=RealDictCursor)


@app.get("/")
def home():
    return {"message": "Google Play API is running!"}


@app.get("/apps")
def get_apps(category: str, min_rating: float = 0.0, max_price: float = 100.0, content_rating: str = "Everyone"):
    query = """
        SELECT name, rating, price, content_rating FROM applications
        WHERE category_id = (SELECT id FROM categories WHERE name = %s)
        AND rating >= %s AND price <= %s
        AND content_rating = %s
    """
    cursor.execute(query, (category, min_rating, max_price, content_rating))
    results = cursor.fetchall()
    return {"apps": results}


@app.get("/categories")
def get_categories():
    query = "SELECT DISTINCT name FROM categories"
    cursor.execute(query)
    results = cursor.fetchall()
    return {"categories": [row["name"] for row in results]}


@app.get("/content_ratings")
def get_content_ratings():
    query = "SELECT DISTINCT content_rating FROM applications"
    cursor.execute(query)
    results = cursor.fetchall()
    return {"content_ratings": [row["content_rating"] for row in results]}


@app.get("/free_social_apps")
def get_free_social_apps():
    query = """
        SELECT name, rating, price FROM applications
        WHERE category_id = (SELECT id FROM categories WHERE name = 'Social')
        AND price = 0.0
    """
    cursor.execute(query)
    results = cursor.fetchall()
    return {"apps": results}


@app.get("/finance_time_series")
def get_finance_time_series():
    query = """
        SELECT EXTRACT(YEAR FROM released) AS release_year,
               COUNT(*) AS release_count
        FROM applications
        WHERE category_id = (SELECT id FROM categories WHERE name = 'Finance')
        GROUP BY release_year
        ORDER BY release_year;
    """
    cursor.execute(query)
    release_data = cursor.fetchall()

    query = """
        SELECT EXTRACT(YEAR FROM last_updated) AS update_year,
               COUNT(*) AS update_count
        FROM applications
        WHERE category_id = (SELECT id FROM categories WHERE name = 'Finance')
        GROUP BY update_year
        ORDER BY update_year;
    """
    cursor.execute(query)
    update_data = cursor.fetchall()

    return {"release_data": release_data, "update_data": update_data}


@app.get("/average_ratings")
def get_average_ratings():
    query = """
        SELECT c.name AS category, (AVG(a.rating), 2) AS avg_rating
        FROM applications a
        JOIN categories c ON a.category_id = c.id
        GROUP BY c.name
        ORDER BY avg_rating DESC;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    return {"ratings": results}


# Define a Pydantic model for validation
class AppCreate(BaseModel):
    name: str
    category: str
    developer_id: str
    rating: float
    price: float
    content_rating: str
    released: str
    last_updated: str


@app.post("/apps")
def create_app(app: AppCreate):
    query = """
        INSERT INTO applications (name, category_id, developer_id, rating, price, content_rating, released, last_updated)
        VALUES (
            %s,
            (SELECT id FROM categories WHERE name=%s),
            (SELECT id FROM developers WHERE name=%s),
            %s, %s, %s, %s, %s
        ) RETURNING id;
    """
    cursor.execute(query, (
        app.name, app.category, app.developer_id, app.rating, app.price, app.content_rating, app.released,
        app.last_updated))
    conn.commit()
    return {"message": "Application created successfully!"}


class AppUpdate(BaseModel):
    rating: float
    price: float


@app.put("/apps/{app_id}")
def update_app(app_id: int, app: AppUpdate):
    query = """
        UPDATE applications
        SET rating = %s, price = %s
        WHERE id = %s
    """
    cursor.execute(query, (app.rating, app.price, app_id))
    conn.commit()
    return {"message": "Application updated successfully!"}


@app.delete("/apps/{app_id}")
def delete_app(app_id: int):
    query = "DELETE FROM applications WHERE id = %s"
    cursor.execute(query, (app_id,))
    conn.commit()
    return {"message": "Application deleted successfully!"}
