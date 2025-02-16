import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("Google Play Store Apps Dashboard")

# Fetch categories dynamically
category_response = requests.get("http://127.0.0.1:8000/categories")
categories = category_response.json()["categories"]
category = st.selectbox("Select Category", categories)

# Fetch content ratings dynamically
content_rating_response = requests.get("http://127.0.0.1:8000/content_ratings")
content_ratings = content_rating_response.json()["content_ratings"]
content_rating = st.selectbox("Select Content Rating", content_ratings)

# Filters
min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.0)
max_price = st.slider("Maximum Price ($)", 0.0, 50.0, 10.0)

# Fetch Data from FastAPI
response = requests.get(
    f"http://127.0.0.1:8000/apps?category={category}&min_rating={min_rating}&max_price={max_price}&content_rating={content_rating}"
)
data = response.json()["apps"]

if st.button("Show Free Social Apps"):
    response = requests.get("http://127.0.0.1:8000/free_social_apps")
    data = response.json()["apps"]

    # df = pd.DataFrame(data)
    # st.dataframe(df)

# Convert to DataFrame
df = pd.DataFrame(data)

# Display DataFrame
st.dataframe(df)

# 📌 Fetch & Display Finance Time Series Data
st.subheader("📊 Finance Apps - Release & Update Trends")

time_series_response = requests.get("http://127.0.0.1:8000/finance_time_series")
time_series_data = time_series_response.json()

# Convert to DataFrame
release_df = pd.DataFrame(time_series_data["release_data"])
update_df = pd.DataFrame(time_series_data["update_data"])

# 📌 Line Chart for Release & Update Trends
fig = px.line(release_df, x="release_year", y="release_count", title="Number of Finance Apps Released Per Year",
              markers=True)
st.plotly_chart(fig)

fig = px.line(update_df, x="update_year", y="update_count", title="Number of Finance Apps Updated Per Year",
              markers=True)
st.plotly_chart(fig)

# 📌 Fetch & Display Average Ratings by Category
st.subheader("⭐ Average Ratings by Category")

ratings_response = requests.get("http://127.0.0.1:8000/average_ratings")
ratings_data = ratings_response.json()

# Convert to DataFrame
ratings_df = pd.DataFrame(ratings_data["ratings"])

# 📌 Bar Chart for Average Ratings
fig = px.bar(ratings_df, x="category", y="avg_rating", title="Average Ratings per Category", color="avg_rating",
             height=500)
st.plotly_chart(fig)
