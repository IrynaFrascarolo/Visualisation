# Import libraries
import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('it_service_performance.csv')

# Display the first few rows to inspect
print(df.head())

# Check for missing values in each column
print("Missing values:\n", df.isnull().sum())

# Replace missing error codes with "No Error"
df['Error Code'].fillna('No Error', inplace=True)

# Confirm the change
print("Missing values after cleaning:\n", df.isnull().sum())

# Check for duplicates
print("Number of duplicate rows:", df.duplicated().sum())

# Drop duplicates
df.drop_duplicates(inplace=True)

# Confirm removal
print("Number of duplicate rows after cleaning:", df.duplicated().sum())

# Check data types
print("Data types before correction:\n", df.dtypes)

# Convert Timestamp to datetime format
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Confirm the change
print("Data types after correction:\n", df.dtypes)

# Basic statistics to spot outliers
print(df['Response Time (ms)'].describe())

# Set threshold for outliers
threshold = df['Response Time (ms)'].quantile(0.95)

# Remove rows with unusually high response times
df = df[df['Response Time (ms)'] <= threshold]

print("Shape after removing outliers:", df.shape)

# Save the cleaned data to a new CSV file
df.to_csv('cleaned_it_service_performance.csv', index=False)
print("✅ Cleaned data saved as 'cleaned_it_service_performance.csv'")

# Preview the cleaned data
print(df.head())


