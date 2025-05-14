import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

base_folder = '/mount/src/'
folder_name = datetime.now().strftime('Data_%Y%m%d_%H%M%S')
full_path = os.path.join(base_folder, folder_name)
os.makedirs(full_path, exist_ok=True)

num_entries = 5000
services = ['Auth Service', 'Payment Gateway', 'Data Sync', 'User Profile']
error_codes = [None, '500', '404', '503', '401']
satisfaction_scores = [1, 2, 3, 4, 5]
timestamps = [datetime.now() - timedelta(minutes=i) for i in range(num_entries)]
data = {
    'Timestamp': timestamps,
    'Service Name': np.random.choice(services, num_entries),
    'Response Time (ms)': np.random.randint(50, 1000, num_entries),
    'Error Code': np.random.choice(error_codes, num_entries, p=[0.8, 0.05, 0.05, 0.05, 0.05]),
    'User Satisfaction': np.random.choice(satisfaction_scores, num_entries)
}
df = pd.DataFrame(data)
generated_file_name = os.path.join(full_path, 'generated_it_service_performance.csv')
df.to_csv(generated_file_name, index=False)
print(f"✅ Generated data saved at: {generated_file_name}")
