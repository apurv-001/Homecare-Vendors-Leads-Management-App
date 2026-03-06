import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="Hospital Data Management", layout="wide", initial_sidebar_state="expanded")

# File path for data storage
DATA_FILE = "hospital_data.csv"

# Initialize or load data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['Date', 'Time', 'Category', 'Type', 'Count', 'Notes', 'User'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Categories and Types configuration
CATEGORIES = ['Patient Admission', 'Patient Discharge', 'Emergency Cases', 'Surgery', 'Lab Tests', 'Pharmacy']
TYPES = ['General Ward', 'ICU', 'Emergency', 'OPD', 'Emergency Surgery', 'Diagnostic']

# Sidebar - Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page:", ["Data Entry", "Dashboard", "View Data"])

# Load data
df = load_data()

if page == "Data Entry":
    st.title("📋 Hospital Data Entry Form")
    st.write("Enter data that will automatically update the dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox("Select Category:", CATEGORIES)
    
    with col2:
        type_field = st.selectbox("Select Type:", TYPES)
    
    col3, col4 = st.columns(2)
    
    with col3:
        count = st.number_input("Enter Count:", min_value=1, step=1)
    
    with col4:
        user_name = st.text_input("Your Name:", placeholder="Enter your name")
    
    notes = st.text_area("Notes (Optional):", placeholder="Add any additional notes here...")
    
    if st.button("Submit Data", use_container_width=True):
        if user_name:
            new_entry = pd.DataFrame({
                'Date': [datetime.now().strftime("%Y-%m-%d")],
                'Time': [datetime.now().strftime("%H:%M:%S")],
                'Category': [category],
                'Type': [type_field],
                'Count': [count],
                'Notes': [notes],
                'User': [user_name]
            })
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.success(f"✅ Data submitted successfully by {user_name}!")
            st.balloons()
        else:
            st.error("Please enter your name!")

elif page == "Dashboard":
    st.title("📊 Hospital Dashboard")
    st.write("Real-time overview of hospital operations")
    
    if len(df) > 0:
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Entries", len(df))
        
        with col2:
            today_count = len(df[df['Date'] == datetime.now().strftime("%Y-%m-%d")])
            st.metric("Today's Entries", today_count)
        
        with col3:
            st.metric("Total Count", df['Count'].sum())
        
        with col4:
            unique_users = df['User'].nunique()
            st.metric("Active Users", unique_users)
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Entries by Category")
            category_data = df['Category'].value_counts()
            fig = px.pie(values=category_data.values, names=category_data.index, hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Count by Category")
            count_by_category = df.groupby('Category')['Count'].sum().sort_values(ascending=False)
            fig = px.bar(x=count_by_category.index, y=count_by_category.values, 
                        labels={'x': 'Category', 'y': 'Total Count'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Entries by Type")
            type_data = df['Type'].value_counts()
            fig = px.bar(x=type_data.index, y=type_data.values, 
                        labels={'x': 'Type', 'y': 'Number of Entries'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("User Activity")
            user_data = df['User'].value_counts().head(10)
            fig = px.bar(x=user_data.values, y=user_data.index, orientation='h',
                        labels={'x': 'Number of Entries', 'y': 'User'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet. Start entering data from the Data Entry section!")

elif page == "View Data":
    st.title("📑 View All Data")
    
    if len(df) > 0:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_category = st.multiselect("Filter by Category:", df['Category'].unique(), default=df['Category'].unique())
        
        with col2:
            filter_type = st.multiselect("Filter by Type:", df['Type'].unique(), default=df['Type'].unique())
        
        with col3:
            filter_user = st.multiselect("Filter by User:", df['User'].unique(), default=df['User'].unique())
        
        # Apply filters
        filtered_df = df[(df['Category'].isin(filter_category)) & 
                        (df['Type'].isin(filter_type)) & 
                        (df['User'].isin(filter_user))].copy()
        
        st.subheader(f"Total Records: {len(filtered_df)}")
        st.dataframe(filtered_df.sort_values('Date', ascending=False), use_container_width=True)
        
        # Download CSV
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"hospital_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available yet!")

st.sidebar.divider()
st.sidebar.info("💡 Tip: This app automatically saves all data. Multiple users can submit data simultaneously!")
