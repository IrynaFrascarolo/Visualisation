import pandas as pd  # Data handling
import numpy as np   # Numerical operations
from datetime import datetime, timedelta  # Date and time handling

# Step 1: Set up data parameters
num_entries = 1000  # Total number of fake data rows
services = ['Auth Service', 'Payment Gateway', 'Data Sync', 'User Profile']
error_codes = [None, '500', '404', '503', '401']
satisfaction_scores = [1, 2, 3, 4, 5]

# Step 2: Generate timestamps starting from now, going backwards
timestamps = [datetime.now() - timedelta(minutes=i) for i in range(num_entries)]

# Step 3: Create random data
data = {
    'Timestamp': timestamps,
    'Service Name': np.random.choice(services, num_entries),  # Random service names
    'Response Time (ms)': np.random.randint(50, 1000, num_entries),  # Random response times
    'Error Code': np.random.choice(error_codes, num_entries, p=[0.8, 0.05, 0.05, 0.05, 0.05]),  # Random errors
    'User Satisfaction': np.random.choice(satisfaction_scores, num_entries)  # Random satisfaction
}

# Step 4: Convert data to a DataFrame
df = pd.DataFrame(data)

# Step 5: Save to a CSV file
df.to_csv('it_service_performance.csv', index=False)
print("✅ Data generated successfully! File saved as 'it_service_performance.csv'")
