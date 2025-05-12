import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from io import BytesIO  # For download functionality

# --- 1. Load Data ---
# Use st.cache_data to cache the data loading for performance
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour
    return df

data_file = 'Scripts/cleaned_it_service_performance.csv'  # Store file path in variable
df = load_data(data_file)

# --- 2. Dashboard Title and Intro ---
st.title("IT Service Performance Dashboard")
st.markdown("This dashboard visualizes the performance and error analysis of IT services.")

# --- 3. Filters ---
st.sidebar.header("Filters")

# Date Range Filter
min_date = df['Timestamp'].min().date()  # Extract date part
max_date = df['Timestamp'].max().date()  # Extract date part
selected_dates = st.sidebar.date_input("Select Date Range", value=(min_date, max_date))

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
    df_filtered = df[(df['Timestamp'].dt.date >= start_date) & (df['Timestamp'].dt.date <= end_date)]
else:
    df_filtered = df.copy()

# Service Name Filter
selected_services = st.sidebar.multiselect("Select Services", df['Service Name'].unique(), default=list(df['Service Name'].unique()))
df_filtered = df_filtered[df_filtered['Service Name'].isin(selected_services)]


# 1. Average Response Time per Service
st.header("Average Response Time per Service")
avg_response_time = df.groupby('Service Name')['Response Time (ms)'].mean()

fig1, ax1 = plt.subplots()
avg_response_time.sort_values().plot(kind='bar', color='skyblue', ax=ax1)
plt.title('Average Response Time per Service')
plt.xlabel('Service Name')
plt.ylabel('Response Time (ms)')
st.pyplot(fig1)

# 2. Most Frequent Error Codes
st.header("Most Frequent Error Codes")
error_counts = df['Error Code'].value_counts()

fig2, ax2 = plt.subplots()
error_counts.plot(kind='pie', autopct='%1.1f%%', colors=['lightcoral', 'gold', 'lightblue', 'lightgreen', 'orange'], ax=ax2)
plt.title('Error Code Distribution')
plt.ylabel('')
st.pyplot(fig2)

# 3. Response Time vs User Satisfaction
st.header("Response Time vs User Satisfaction")
fig3, ax3 = plt.subplots()
sns.scatterplot(data=df, x='Response Time (ms)', y='User Satisfaction', hue='Service Name', alpha=0.7, ax=ax3)
plt.title('Response Time vs User Satisfaction')
st.pyplot(fig3)

# 4. Hourly Response Time Trend
st.header("Hourly Response Time Trend")
hourly_response = df.groupby('Hour')['Response Time (ms)'].mean()

fig4, ax4 = plt.subplots()
hourly_response.plot(kind='line', marker='o', color='purple', ax=ax4)
plt.title('Average Response Time Over Time')
plt.xlabel('Hour of the Day')
plt.ylabel('Average Response Time (ms)')
st.pyplot(fig4)

# 5. User Satisfaction Distribution
st.header("User Satisfaction Distribution")
fig5, ax5 = plt.subplots()
sns.countplot(data=df, x='User Satisfaction', palette='viridis', ax=ax5)
plt.title('User Satisfaction Levels')
plt.xlabel('Satisfaction Rating')
plt.ylabel('Count')
st.pyplot(fig5)

# Insights Summary
st.header("Insights Summary")
with open('Scripts/analysis_summary.txt', 'r') as file:
    summary = file.read()
st.text(summary)

st.success("Dashboard loaded successfully!")
