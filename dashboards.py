import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from io import BytesIO
import glob
import os
from datetime import datetime, date
import subprocess
import sys
import time  # Import the time module

base_folder = '/home/appuser/'

def run_generation_cleaning():
    with st.spinner("Generating data..."):
        try:
            subprocess.run([sys.executable, 'generate_data.py'], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Error during data generation: {e}")
            return
    with st.spinner("Cleaning data..."):
        try:
            subprocess.run([sys.executable, 'clean_data.py'], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Error during data cleaning: {e}")
            return
    cleaned_file_pattern_check = os.path.join(base_folder, 'Data_*', 'cleaned_it_service_performance_*.csv')
    list_cleaned_files_check = glob.glob(cleaned_file_pattern_check)
    if list_cleaned_files_check:
        latest_cleaned_file_check = max(list_cleaned_files_check, key=os.path.getmtime)
        cleaned_dir_check = os.path.dirname(latest_cleaned_file_check)
        analysis_file_name_check = os.path.join(cleaned_dir_check, f"analysis_summary_*.txt")
        print(f"DASHBOARD (Pre-Analysis Check): Expected analysis file pattern: {analysis_file_name_check}")
    else:
        print("DASHBOARD (Pre-Analysis Check): No cleaned data found to determine analysis file location.")

    with st.spinner("Analyzing data..."):
        try:
            subprocess.run([sys.executable, 'analyze_data.py'], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Error during data analysis: {e}")
            return

    cleaned_file_pattern_post_analysis = os.path.join(base_folder, 'Data_*', 'cleaned_it_service_performance_*.csv')
    list_cleaned_files_post_analysis = glob.glob(cleaned_file_pattern_post_analysis)
    if list_cleaned_files_post_analysis:
        latest_cleaned_file_post_analysis = max(list_cleaned_files_post_analysis, key=os.path.getmtime)
        cleaned_dir_post_analysis = os.path.dirname(latest_cleaned_file_post_analysis)
        analysis_file_pattern_exists_check = os.path.join(cleaned_dir_post_analysis, "analysis_summary_*.txt")
        found_files = glob.glob(analysis_file_pattern_exists_check)
        print(f"DASHBOARD (Post-Analysis Check): Looking for analysis files in: {cleaned_dir_post_analysis}")
        print(f"DASHBOARD (Post-Analysis Check): Found analysis files: {found_files}")
        if found_files:
            print(f"DASHBOARD (Post-Analysis Check): Latest analysis file (if any): {max(found_files, key=os.path.getmtime)}")
        else:
            print("DASHBOARD (Post-Analysis Check): No analysis summary file found after analysis.")
    else:
        print("DASHBOARD (Post-Analysis Check): No cleaned data found to check for analysis file.")

    st.success("Data generation, cleaning, and analysis complete!")
    st.session_state['data_loaded'] = False
    time.sleep(1)  # Add a 1-second delay
    st.rerun()

@st.cache_data
def load_and_report_data(file_pattern):
    list_of_files = glob.glob(file_pattern)
    if not list_of_files:
        st.error("No cleaned data files found in the specified location.")
        return None, None, None
    latest_cleaned_file = max(list_of_files, key=os.path.getmtime)
    df_cleaned = pd.read_csv(latest_cleaned_file)
    df_cleaned['Timestamp'] = pd.to_datetime(df_cleaned['Timestamp'])
    df_cleaned['Hour'] = df_cleaned['Timestamp'].dt.hour

    cleaned_dir = os.path.dirname(latest_cleaned_file)
    original_file_path = os.path.join(cleaned_dir, 'generated_it_service_performance.csv')

    df_original = None
    cleaning_info = None
    if os.path.exists(original_file_path):
        df_original = pd.read_csv(original_file_path)

        initial_rows = len(df_original)
        final_rows = len(df_cleaned)
        rows_removed = initial_rows - final_rows
        percentage_removed = (rows_removed / initial_rows) * 100 if initial_rows > 0 else 0
        cleaning_info = {"initial_rows": initial_rows, "final_rows": final_rows, "rows_removed": rows_removed, "percentage_removed": percentage_removed}
    else:
        st.warning("Could not find the corresponding original generated data for cleaning info in the same directory.")

    # --- Find the analysis summary in the same directory as the cleaned data ---
    analysis_file_pattern_local = os.path.join(cleaned_dir, 'analysis_summary_*.txt')
    print(f"DASHBOARD: Looking for summary files with pattern: {analysis_file_pattern_local}")
    list_summary_files = glob.glob(analysis_file_pattern_local)
    print(f"DASHBOARD: Found summary files: {list_summary_files}")
    latest_summary_file = max(list_summary_files, key=os.path.getmtime) if list_summary_files else None
    if latest_summary_file:
        print(f"DASHBOARD: Latest summary file found: {latest_summary_file}")
    else:
        print("DASHBOARD: No analysis summary file found in the cleaned data directory.")

    return df_cleaned, cleaning_info, latest_summary_file

st.sidebar.button("Generate and Clean New Data", on_click=run_generation_cleaning)

if 'cleaned_file_pattern' not in st.session_state:
    cleaned_file_pattern = os.path.join(base_folder, 'Data_*', 'cleaned_it_service_performance_*.csv')
else:
    cleaned_file_pattern = st.session_state['cleaned_file_pattern']

if 'data_loaded' not in st.session_state or not st.session_state['data_loaded']:
    df_cleaned, cleaning_info, latest_summary_file = load_and_report_data(cleaned_file_pattern)
    st.session_state['data_loaded'] = True
    st.session_state['cleaning_info'] = cleaning_info
    st.session_state['latest_summary_file'] = latest_summary_file
else:
    df_cleaned = st.session_state.get('loaded_data', None)
    cleaning_info = st.session_state.get('cleaning_info', None)
    latest_summary_file = st.session_state.get('latest_summary_file', None)

if df_cleaned is not None:
    st.session_state['loaded_data'] = df_cleaned

    st.title("IT Service Performance Dashboard")
    st.markdown("Visualizing performance, error analysis, and satisfaction of IT services.")

    st.sidebar.header("Data Cleaning Summary")
    if cleaning_info:
        st.sidebar.markdown(f"**Initial Data Points:** {cleaning_info['initial_rows']}")
        st.sidebar.markdown(f"**Cleaned Data Points:** {cleaning_info['final_rows']}")
        st.sidebar.markdown(f"**Data Points Removed:** {cleaning_info['rows_removed']} ({cleaning_info['percentage_removed']:.2f}%)")
    else:
        st.sidebar.warning("Information on the amount of data cleaned is not available.")

    st.sidebar.header("Filters")
    min_date = df_cleaned['Timestamp'].min().date()
    max_date = df_cleaned['Timestamp'].max().date()
    selected_dates = st.sidebar.date_input("Select Date Range", value=(min_date, max_date))

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
        if start_date > end_date:
            st.warning("Start date must be earlier than or equal to the end date.")
            st.stop()

        df_filtered_date = df_cleaned[
            (df_cleaned['Timestamp'].dt.date >= start_date) &
            (df_cleaned['Timestamp'].dt.date <= end_date)
        ].copy()

        selected_services = st.sidebar.multiselect("Select Services", df_filtered_date['Service Name'].unique(), default=list(df_filtered_date['Service Name'].unique()))
        df_filtered = df_filtered_date[df_filtered_date['Service Name'].isin(selected_services)].copy()

        if not df_filtered.empty:
            # --- Hourly Response Time Trend ---
            st.header("Hourly Response Time Trend per Service")
            fig4, ax4 = plt.subplots(figsize=(10, 6))
            hourly_response = df_filtered.groupby(['Hour', 'Service Name'])['Response Time (ms)'].mean().unstack()
            hourly_response.plot(kind='line', marker='o', ax=ax4)
            plt.title('Hourly Average Response Time by Service')
            plt.xlabel('Hour of the Day')
            plt.ylabel('Average Response Time (ms)')
            plt.xticks(range(0, 24))
            plt.grid(True)
            plt.legend(title='Service Name')
            st.pyplot(fig4)

            # --- Average Response Time Trend ---
            st.header("Average Response Time per Service (Trend)")
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            for service in df_filtered['Service Name'].unique():
                service_data = df_filtered[df_filtered['Service Name'] == service].groupby('Timestamp')['Response Time (ms)'].agg(['mean', 'median']).reset_index()
                sns.lineplot(data=service_data, x='Timestamp', y='mean', label=f'{service} (Mean)', ax=ax1)
                sns.lineplot(data=service_data, x='Timestamp', y='median', label=f'{service} (Median)', linestyle='--', alpha=0.7, ax=ax1)
            plt.axhline(y=500, color='red', linestyle='--', label='Critical Threshold')
            plt.axhline(y=200, color='green', linestyle='--', label='Acceptable Threshold')
            plt.title('Trend of Average/Median Response Time per Service')
            plt.xlabel('Timestamp')
            plt.ylabel('Response Time (ms)')
            plt.legend()
            plt.grid(True)
            st.pyplot(fig1)

            # --- Most Frequent Error Codes ---
            st.header("Most Frequent Error Codes")
            error_counts = df_filtered['Error Code'].value_counts()
            if len(error_counts) > 10:
                top_errors = error_counts[:9]
                other_count = error_counts[9:].sum()
                error_counts_grouped = pd.concat([top_errors, pd.Series({'Other': other_count})])
            else:
                error_counts_grouped = error_counts

            fig2, ax2 = plt.subplots(figsize=(8, 6))
            error_counts_grouped.plot(kind='bar', color='skyblue', ax=ax2)
            plt.title('Error Code Frequency')
            plt.xlabel('Error Code')
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig2)

            # --- Response Time vs User Satisfaction ---
            st.header("Response Time vs User Satisfaction")
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            for service in df_filtered['Service Name'].unique():
                service_data = df_filtered[df_filtered['Service Name'] == service]
                sns.scatterplot(data=service_data, x='Response Time (ms)', y='User Satisfaction', label=service, alpha=0.6, ax=ax3)
                sns.regplot(data=service_data, x='Response Time (ms)', y='User Satisfaction', scatter=False, label=f'{service} Trend', ax=ax3)
            plt.title('Response Time vs User Satisfaction per Service')
            plt.xlabel('Response Time (ms)')
            plt.ylabel('User Satisfaction')
            plt.legend()
            plt.grid(True)
            st.pyplot(fig3)

            # --- User Satisfaction Distribution ---
            st.header("User Satisfaction Distribution")
            satisfaction_counts = df_filtered['User Satisfaction'].value_counts(normalize=True).sort_index() * 100
            fig5, ax5 = plt.subplots(figsize=(8, 5))
            satisfaction_counts.plot(kind='bar', color='orange', ax=ax5)
            plt.title('User Satisfaction Level Distribution (Percentage)')
            plt.xlabel('Satisfaction Level')
            plt.ylabel('Percentage (%)')
            plt.xticks(rotation=0)
            for i, v in satisfaction_counts.items():
                ax5.text(i, v + 0.5, f'{v:.1f}%', ha='center', va='bottom')
            st.pyplot(fig5)

            st.header("Insights Summary")
            if latest_summary_file:
                print(f"DASHBOARD: Trying to open summary file: {latest_summary_file}")
                try:
                    with open(latest_summary_file, 'r') as file:
                        summary = file.read()
                    st.text_area("Analysis Summary", summary, height=200)
                except FileNotFoundError:
                    st.warning("Analysis summary file not found (error during open).")
                except Exception as e:
                    st.error(f"Error reading summary file: {e}")
            else:
                st.warning("No analysis summary file found.")

            st.success("Dashboard loaded with updated visualizations and date range!")
        else:
            st.warning("No data available based on the selected date range and services.")
    else:
        st.warning("Please select a valid date range.")
else:
    st.warning("No cleaned data loaded. Please click 'Generate and Clean New Data'.")