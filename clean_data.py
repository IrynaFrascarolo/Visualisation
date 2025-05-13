import pandas as pd
from datetime import datetime
import os
import glob

base_folder = os.path.expanduser('~/Qimproject/')
def clean_data(df):
    # Ensure the 'Error Code' column is treated as string to accommodate 'No Error'
    df['Error Code'] = df['Error Code'].astype(str).fillna('No Error')
    return df

list_of_folders = [os.path.join(base_folder, d) for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d)) and d.startswith('Data_')]
if not list_of_folders:
    print("❌ No 'Data_' folders found in the base directory.")
else:
    latest_folder = max(list_of_folders, key=os.path.getctime)
    generated_file_path = os.path.join(latest_folder, 'generated_it_service_performance.csv')

    if os.path.exists(generated_file_path):
        df = pd.read_csv(generated_file_path)
        initial_rows = df.shape[0]
        df['Error Code'].fillna('No Error', inplace=True)
        df.drop_duplicates(inplace=True)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        threshold = df['Response Time (ms)'].quantile(0.95)
        df = df[df['Response Time (ms)'] <= threshold]
        final_rows = df.shape[0]
        cleaned_file_name = os.path.join(latest_folder, f"cleaned_it_service_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(cleaned_file_name, index=False)
        print(f"✅ Cleaned data saved as '{cleaned_file_name}' in '{latest_folder}'")
    else:
        print(f"❌ Error: Generated data file not found at '{generated_file_path}'")
