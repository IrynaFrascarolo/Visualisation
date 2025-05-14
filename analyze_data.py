import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import glob
import os

base_folder = '/home/appuser/mount/src/'
cleaned_file_pattern = os.path.join(base_folder, 'Data_*', 'cleaned_it_service_performance_*.csv')
list_of_files = glob.glob(cleaned_file_pattern)

if not list_of_files:
    print("ANALYZE: No cleaned data files found.")
else:
    latest_file = max(list_of_files, key=os.path.getmtime)
    print(f"ANALYZE: Found cleaned data file: {latest_file}")
    cleaned_data_dir = os.path.dirname(latest_file)
    analysis_file_name = os.path.join(cleaned_data_dir, f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    print(f"ANALYZE: Saving summary to (explicit path): {analysis_file_name}")
    try:
        df = pd.read_csv(latest_file)
        print("ANALYZE: Data loaded successfully.")

        avg_response_time = df.groupby('Service Name')['Response Time (ms)'].mean()
        print("\nANALYZE: Average Response Time per Service:\n", avg_response_time)

        plt.figure(figsize=(8, 5))
        avg_response_time.sort_values().plot(kind='bar', color='skyblue')
        plt.title('Average Response Time per Service')
        plt.xlabel('Service Name')
        plt.ylabel('Response Time (ms)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        output_filename_avg_response = os.path.join(cleaned_data_dir, f'average_response_time_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(output_filename_avg_response)
        print(f"ANALYZE: Saved: {output_filename_avg_response}")
        plt.close()

        error_counts = df['Error Code'].value_counts()
        print("\nANALYZE: Error Code Frequencies:\n", error_counts)
        plt.figure(figsize=(6, 6))
        error_counts.plot(kind='pie', autopct='%1.1f%%', colors=['lightcoral', 'gold', 'lightblue', 'lightgreen', 'orange'])
        plt.title('Error Code Distribution')
        plt.ylabel('')
        plt.tight_layout()
        output_filename_error_dist = os.path.join(cleaned_data_dir, f'error_code_distribution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(output_filename_error_dist)
        print(f"ANALYZE: Saved: {output_filename_error_dist}")
        plt.close()

        plt.figure(figsize=(8, 5))
        sns.scatterplot(data=df, x='Response Time (ms)', y='User Satisfaction', hue='Service Name', alpha=0.7, palette='Set1')
        plt.title('Response Time vs User Satisfaction')
        plt.xlabel('Response Time (ms)')
        plt.ylabel('User Satisfaction')
        plt.tight_layout()
        output_filename_scatter = os.path.join(cleaned_data_dir, f'scatter_response_vs_satisfaction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(output_filename_scatter)
        print(f"ANALYZE: Saved: {output_filename_scatter}")
        plt.close()

        correlation = df['Response Time (ms)'].corr(df['User Satisfaction'])
        print("\nANALYZE: Correlation between Response Time and User Satisfaction:", correlation)

        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Hour'] = df['Timestamp'].dt.hour
        hourly_response = df.groupby('Hour')['Response Time (ms)'].mean()
        plt.figure(figsize=(8, 5))
        hourly_response.plot(kind='line', marker='o', color='purple')
        plt.title('Average Response Time Over Time')
        plt.xlabel('Hour of the Day')
        plt.ylabel('Average Response Time (ms)')
        plt.xticks(range(0, 24))
        plt.grid(True)
        plt.tight_layout()
        output_filename_hourly_response = os.path.join(cleaned_data_dir, f'average_response_time_hourly_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(output_filename_hourly_response)
        print(f"ANALYZE: Saved: {output_filename_hourly_response}")
        plt.close()

        plt.figure(figsize=(6, 4))
        sns.countplot(data=df, x='User Satisfaction', palette='viridis')
        plt.title('User Satisfaction Distribution')
        plt.xlabel('Satisfaction Level')
        plt.ylabel('Count')
        plt.tight_layout()
        output_filename_satisfaction = os.path.join(cleaned_data_dir, f'user_satisfaction_distribution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(output_filename_satisfaction)
        print(f"ANALYZE: Saved: {output_filename_satisfaction}")
        plt.close()

        print(f"ANALYZE: Saving summary content to: {analysis_file_name}")
        with open(analysis_file_name, 'w') as file:
            file.write("IT Service Performance Analysis Summary\n")
            #file.write(f"Data Source: {latest_file}\n")
            file.write(f"Analysis Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("\nAverage Response Times per Service:\n")
            file.write(avg_response_time.to_string() + "\n")
            file.write("\nError Code Frequencies:\n")
            file.write(error_counts.to_string() + "\n")
            file.write(f"\nCorrelation between Response Time and User Satisfaction: {correlation:.2f}\n")
            file.write("Analysis completed successfully!\n")
        print("ANALYZE: Summary saved successfully.")

    except FileNotFoundError:
        print(f"ANALYZE: Error: Cleaned data file not found at '{latest_file}'")
    except Exception as e:
        print(f"ANALYZE: An error occurred during analysis: {e}")
