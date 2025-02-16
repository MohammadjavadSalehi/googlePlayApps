import pandas as pd

# Load dataset
df = pd.read_csv("Google-Playstore.csv")

# Remove duplicates
df.drop_duplicates(inplace=True)

# Handle missing values
df.dropna(inplace=True)

# Handle missing values
df.dropna(subset=['Released'], inplace=True)  # Remove rows where 'released' is NULL

# Convert 'Last Updated' to datetime
df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors='coerce')

# Convert 'released' column to datetime
df['Released'] = pd.to_datetime(df['Released'], errors='coerce')

# Clean and standardize column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Save cleaned data
df.to_csv("cleaned_googleplaystore.csv", index=False)

print("✅ Data cleaned and saved successfully!")
