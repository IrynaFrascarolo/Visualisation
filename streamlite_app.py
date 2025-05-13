import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from io import BytesIO
import glob
import os
from datetime import datetime
import subprocess  # To run external scripts

base_folder = os.path.expanduser('~/Qimproject/')

def run_generation_cleaning():
    with st.spinner("Generating data..."):
        subprocess.run(['python', 'generate_data.py'], check=True)
    with st.spinner("Cleaning data..."):
        # Assuming clean_data.py can find the latest generated file
        subprocess.run(['python', 'clean_data.py'], check=True)
    st.success("Data generation and cleaning complete!")
    st.session_state['data_loaded'] = False # Force reload
    st.rerun()

# --- 1. Load Data ---
@st.cache_data
def load_and_report_data(file_pattern):
    # ... (rest of your load_and_report_data function remains the same)

# Button to Run Generation and Cleaning
if st.sidebar.button("Generate and Clean New Data"):
    run_generation_cleaning()

if 'cleaned_file_pattern' not in st.session_state:
    cleaned_file_pattern = os.path.join(base_folder, 'Data_*', 'cleaned_it_service_performance_*.csv')
else:
    cleaned_file_pattern = st.session_state['cleaned_file_pattern']

if 'data_loaded' not in st.session_state or not st.session_state['data_loaded']:
    df_cleaned, df_original = load_and_report_data(cleaned_file_pattern)
    st.session_state['data_loaded'] = True
else:
    df_cleaned, df_original = st.session_state.get('loaded_data', (None, None))

# --- (Rest of your Streamlit dashboard code remains largely the same) ---
if df_cleaned is not None:
    # ... (your dashboard visualizations and information)
    pass
else:
    st.warning("No cleaned data available.")