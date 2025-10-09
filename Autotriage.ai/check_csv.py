import pandas as pd

# Read the CSV file
csv_path = "[Usecase 7] AI-Driven Customer Support Enhancing Efficiency Through Multiagents/Historical_ticket_data.csv"
df = pd.read_csv(csv_path)

# Print column names to see what we're working with
print("Column names in CSV:")
print(df.columns.tolist())

# Print first few rows
print("\nFirst few rows of data:")
print(df.head())