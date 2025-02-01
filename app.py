# app.py - Complete Indian Market Price Solution
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

# ======================
# DATA MANAGEMENT SYSTEM
# ======================

PRICE_FILE = "indian_prices.csv"
FALLBACK_PRICES = {
    'Wheat': 2250,  # ₹ per quintal
    'Rice': 3150,
    'Potatoes': 850,
    'Tomatoes': 1250
}

def load_price_data():
    """Load prices with improved error handling"""
    try:
        df = pd.read_csv("indian_prices.csv")

        # Trim spaces from column names
        df.columns = df.columns.str.strip()

        # Ensure "Date" column exists
        if "Date" not in df.columns:
            st.error("CSV file is missing the 'Date' column! Please check your data.")
            return pd.DataFrame()

        # Convert "Date" column to datetime format safely
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Drop rows where Date conversion failed
        df = df.dropna(subset=['Date'])

        return df

    except FileNotFoundError:
        st.warning("Price database missing! Using fallback values")
        return pd.DataFrame({
            'Date': [datetime.today()],
            **FALLBACK_PRICES
        })
    except Exception as e:
        st.error(f"Error loading price data: {str(e)}")
        return pd.DataFrame()

# =================
# STREAMLIT INTERFACE
# =================

st.set_page_config(page_title="FarmConnect - Indian Market Prices", layout="wide")

# Header
st.title("🇮🇳 Indian Crop Price Monitor")
st.markdown("""
**Data Sources:**
- [AGMARKNET](https://agmarknet.gov.in/) (Government of India)
- [National Horticulture Board](https://nhb.gov.in/)
- Manual State Agriculture Department Reports
""")

# Main Layout
col1, col2 = st.columns([3, 2])

with col1:
    # ======================
    # PRICE VISUALIZATION
    # ======================
    st.subheader("Current Market Rates (₹/Quintal)")
    
    price_df = load_price_data()
    
    # Show latest prices
    latest = price_df.iloc[-1]
    crops = ['Wheat', 'Rice', 'Potatoes', 'Tomatoes']
    
    cols = st.columns(len(crops))
    for idx, crop in enumerate(crops):
        with cols[idx]:
            delta = latest[crop] - price_df.iloc[-2][crop] if len(price_df) > 1 else 0
            st.metric(
                label=crop,
                value=f"₹{latest[crop]:.0f}",
                delta=f"{delta:+.0f} ₹" if delta != 0 else None
            )
    
    # Price History Chart
    st.line_chart(
        price_df.set_index('Date')[crops],
        use_container_width=True
    )

with col2:
    # ======================
    # MANUAL UPDATE SYSTEM
    # ======================
    st.subheader("Data Management")
    
    # Password-protected updates
    if st.toggle("Admin Mode"):
        admin_pass = st.text_input("Enter Admin Password", type="password")
        
        if admin_pass == st.secrets.get("ADMIN_PASS", "farmconnect2024"):
            st.success("Admin Access Granted")
            
            # Download Latest Prices
            st.markdown("**1. Get Official Data**")
            st.page_link("https://agmarknet.gov.in/", label="AGMARKNET Prices →")
            st.page_link("https://nhb.gov.in/", label="NHB Horticulture Prices →")
            
            # CSV Upload
            st.markdown("**2. Update Price Database**")
            new_file = st.file_uploader("Upload Updated CSV", type="csv")
            
            if new_file:
                try:
                    new_df = pd.read_csv(new_file)
                    required_cols = ['Date', 'Wheat', 'Rice', 'Potatoes', 'Tomatoes']
                    
                    if all(col in new_df.columns for col in required_cols):
                        new_df.to_csv(PRICE_FILE, index=False)
                        st.success("Database updated successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid file format! Required columns: Date, Wheat, Rice, Potatoes, Tomatoes")
                
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
            
            # Manual Entry
            st.markdown("**3. Or Enter Manually**")
            with st.form("manual_entry"):
                entry_date = st.date_input("Date", datetime.today())
                wheat = st.number_input("Wheat Price", value=latest['Wheat'])
                rice = st.number_input("Rice Price", value=latest['Rice'])
                potatoes = st.number_input("Potatoes Price", value=latest['Potatoes'])
                tomatoes = st.number_input("Tomatoes Price", value=latest['Tomatoes'])
                
                if st.form_submit_button("Add Entry"):
                    new_entry = {
                        'Date': entry_date,
                        'Wheat': wheat,
                        'Rice': rice,
                        'Potatoes': potatoes,
                        'Tomatoes': tomatoes
                    }
                    price_df.loc[len(price_df)] = new_entry
                    updated_df = price_df
                    updated_df.to_csv(PRICE_FILE, index=False)
                    st.success("Manual entry added!")
                    st.rerun()
        
        elif admin_pass:
            st.error("Incorrect Admin Password")

# ======================
# PRICE ALERT SYSTEM
# ======================
st.subheader("💡 Selling Recommendations")
selected_crop = st.selectbox("Select Your Stored Crop", crops)

current_price = latest[selected_crop]
avg_price = price_df[selected_crop].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Price", f"₹{current_price:.0f}")
with col2:
    st.metric("6-Month Average", f"₹{avg_price:.0f}")
with col3:
    if current_price > avg_price * 1.15:
        st.success("🚨 Good Time to Sell!")
        st.balloons()
    elif current_price < avg_price * 0.85:
        st.error("⚠️ Consider Holding Stock")
    else:
        st.info("🕒 Normal Market Conditions")

# ======================
# DATA SOURCE INSTRUCTIONS
# ======================
st.divider()
st.markdown("""
**How to Update Prices:**
1. Visit [AGMARKNET](https://agmarknet.gov.in/)
2. Select your state and crop
3. Download weekly/monthly reports
4. Convert to CSV format (Excel → Save As CSV)
5. Upload using Admin Mode

**Recommended Update Frequency:**
- Weekly for perishables (Tomatoes, Potatoes)
- Monthly for grains (Wheat, Rice)
""")