import pandas as pd
import psycopg2

# Database connection details
DB_NAME = "googleplay"
DB_USER = "user"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

# Connect to PostgreSQL
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()

# Load cleaned dataset
df = pd.read_csv("cleaned_googleplaystore.csv")

# Insert categories
categories = df["category"].unique()
for cat in categories:
    cursor.execute("INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (cat,))

# Insert developers (use developer_id instead of developer)
developers = df["developer_id"].unique()
for dev in developers:
    cursor.execute("INSERT INTO developers (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (dev,))

# Insert applications
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO applications (name, category_id, developer_id, rating, price, content_rating, released, last_updated)
        VALUES (
            %s, 
            (SELECT id FROM categories WHERE name=%s),
            (SELECT id FROM developers WHERE name=%s),
            %s, %s, %s, %s, %s
        );
    """, (row["app_name"], row["category"], row["developer_id"], row["rating"], row["price"], row["content_rating"],
          row["released"], row["last_updated"]))

# Commit and close connection
conn.commit()
cursor.close()
conn.close()
