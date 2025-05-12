# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the cleaned data
df = pd.read_csv('cleaned_it_service_performance.csv')

# Display first few rows
print(df.head())

# Group by service name and calculate the average response time
avg_response_time = df.groupby('Service Name')['Response Time (ms)'].mean()

print("Average Response Time per Service:\n", avg_response_time)

# Visualize the results
plt.figure(figsize=(8, 5))
avg_response_time.sort_values().plot(kind='bar', color='skyblue')
plt.title('Average Response Time per Service')
plt.xlabel('Service Name')
plt.ylabel('Response Time (ms)')
plt.show()

# Count the occurrences of each error code
error_counts = df['Error Code'].value_counts()

print("Error Code Frequencies:\n", error_counts)

# Visualize as a pie chart
plt.figure(figsize=(6, 6))
error_counts.plot(kind='pie', autopct='%1.1f%%', colors=['lightcoral', 'gold', 'lightblue', 'lightgreen', 'orange'])
plt.title('Error Code Distribution')
plt.ylabel('')  # Hide the y-label
plt.show()

# Scatter plot to visualize the relationship
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x='Response Time (ms)', y='User Satisfaction', hue='Service Name', alpha=0.7)
plt.title('Response Time vs User Satisfaction')
plt.xlabel('Response Time (ms)')
plt.ylabel('User Satisfaction')
plt.show()

correlation = df['Response Time (ms)'].corr(df['User Satisfaction'])
print("Correlation between Response Time and User Satisfaction:", correlation)

# Convert Timestamp to datetime if not already done
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Extract hour from timestamp
df['Hour'] = df['Timestamp'].dt.hour

# Calculate average response time per hour
hourly_response = df.groupby('Hour')['Response Time (ms)'].mean()

# Plotting the trend
plt.figure(figsize=(8, 5))
hourly_response.plot(kind='line', marker='o', color='purple')
plt.title('Average Response Time Over Time')
plt.xlabel('Hour of the Day')
plt.ylabel('Average Response Time (ms)')
plt.show()

# Plotting satisfaction distribution
plt.figure(figsize=(6, 4))
sns.countplot(data=df, x='User Satisfaction', palette='viridis')
plt.title('User Satisfaction Distribution')
plt.xlabel('Satisfaction Level')
plt.ylabel('Count')
plt.show()

with open('analysis_summary.txt', 'w') as file:
    file.write("IT Service Performance Analysis Summary\n")
    file.write(f"Average Response Times per Service:\n{avg_response_time}\n")
    file.write(f"Error Code Frequencies:\n{error_counts}\n")
    file.write(f"Correlation between Response Time and User Satisfaction: {correlation}\n")
    file.write("Analysis completed successfully!")
print("✅ Analysis summary saved as 'analysis_summary.txt'")

