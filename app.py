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

st.set_page_config(
    page_title="AgriSure - Market Intelligence",
    layout="wide",
    page_icon="🌾"
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

[data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 600 !important;
}

[data-testid="stMetricLabel"] {
    font-size: 16px !important;
    color: #666 !important;
}

.css-1q1n0ol {
    gap: 2rem;
}

.header {
    background: linear-gradient(135deg, #664343, #795757);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    margin-bottom: 2rem;
}

.card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
}

.footer {
    text-align: center;
    padding: 1.5rem;
    color: #666;
    font-size: 0.9rem;
    margin-top: 3rem;
}

.recommendation-card {
    border-left: 4px solid;
    padding-left: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Header
with st.container():
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.title("🌾 FarmConnect - Market Intelligence")
    st.markdown("**Real-time Agricultural Price Monitoring & Decision Support System**")
    st.markdown("</div>", unsafe_allow_html=True)

# Main Tabs
tab1, tab2, tab3 = st.tabs(["📊 Market Dashboard", "📈 Price Advisor", "🔒 Data Management"])

price_df = load_price_data()
latest = price_df.iloc[-1] if not price_df.empty else FALLBACK_PRICES
crops = ['Wheat', 'Rice', 'Potatoes', 'Tomatoes']

with tab1:
    # Current Prices Section
    st.subheader("Current Market Prices")
    cols = st.columns(4)
    crop_icons = {'Wheat': '🌾', 'Rice': '🍚', 'Potatoes': '🥔', 'Tomatoes': '🍅'}
    
    for idx, crop in enumerate(crops):
        with cols[idx]:
            delta = latest[crop] - price_df.iloc[-2][crop] if len(price_df) > 1 else 0
            delta_color = "inverse"
            if delta > 0:
                delta_color = "normal"
            st.metric(
                label=f"{crop_icons[crop]} {crop}",
                value=f"₹{latest[crop]:.0f}",
                delta=f"{delta:+.0f} ₹",
                delta_color=delta_color
            )
    
    # Date Range Selector
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        date_range = st.date_input(
            "Select Date Range",
            value=[price_df['Date'].min(), price_df['Date'].max()],
            format="DD/MM/YYYY"
        )
    
    # Price History Chart
    with col1:
        filtered_df = price_df[(price_df['Date'] >= pd.to_datetime(date_range[0])) & 
                              (price_df['Date'] <= pd.to_datetime(date_range[1]))]
        st.area_chart(
            filtered_df.set_index('Date')[crops],
            use_container_width=True,
            height=400
        )

with tab2:
    # Price Recommendation System
    st.subheader("Selling Recommendations")
    selected_crop = st.selectbox("Select Your Crop", crops, key='crop_select')
    
    current_price = latest[selected_crop]
    avg_price = price_df[selected_crop].mean()
    
    # Price Comparison
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"<div class='card'><h3 style='color: black;'>Current Price</h3><h2 style='color:#2c5f2d'>₹{current_price:,.0f}</h2></div>", 
                    unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='card'><h3 style='color: black;'>6-Month Average</h3><h2 style='color:#2c5f2d'>₹{avg_price:,.0f}</h2></div>", 
                    unsafe_allow_html=True)
    
    # Recommendation Logic
    with cols[2]:
        if current_price > avg_price * 1.15:
            st.markdown("""
            <div class='card recommendation-card' style='border-color: #2c5f2d'>
                <h3 style='color:#2c5f2d; margin:0'>🚜 Good to Sell</h3>
                <p style='color:#666; margin:0.5rem 0'>Current prices are 15% above average</p>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
        elif current_price < avg_price * 0.85:
            st.markdown("""
            <div class='card recommendation-card' style='border-color: #cc3300'>
                <h3 style='color:#cc3300; margin:0'>⏳ Hold Stock</h3>
                <p style='color:#666; margin:0.5rem 0'>Current prices are 15% below average</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card recommendation-card' style='border-color: #666'>
                <h3 style='color:#666; margin:0'>⚖️ Market Stable</h3>
                <p style='color:#666; margin:0.5rem 0'>Prices within normal fluctuation range</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Profit Calculator
    st.markdown("---")
    st.subheader("Profit Estimator")
    col1, col2 = st.columns(2)
    with col1:
        quantity = st.number_input("Stock Quantity (quintals)", min_value=1, value=100)
    with col2:
        st.markdown(f"""
        <div class='card'>
            <h3 style='margin-top:0; color: black;'>Estimated Value</h3>
            <h2 style='color:#2c5f2d'>₹{(current_price * quantity):,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    # Data Management System
    st.subheader("Data Management Portal")
    
    if st.toggle("Enable Admin Mode"):
        admin_pass = st.text_input("Enter Admin Password", type="password")
        
        if admin_pass == st.secrets.get("ADMIN_PASS", "farmconnect2024"):
            st.success("🔐 Administrator Access Granted")
            
            # Data Update Section
            with st.expander("📤 CSV Upload", expanded=True):
                st.markdown("### Official Data Sources")
                st.page_link("https://agmarknet.gov.in/", label="AGMARKNET Portal →")
                st.page_link("https://nhb.gov.in/", label="NHB Price Reports →")
                
                new_file = st.file_uploader("Upload Updated CSV", type="csv")
                if new_file:
                    try:
                        new_df = pd.read_csv(new_file)
                        if st.button("Preview Data"):
                            st.dataframe(new_df.head())
                        
                        if st.button("Commit Changes", type="primary"):
                            new_df.to_csv(PRICE_FILE, index=False)
                            st.success("Database updated successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
            
            # Manual Entry Form
            with st.expander("✍️ Manual Entry", expanded=True):
                with st.form("manual_entry_form"):
                    cols = st.columns(2)
                    with cols[0]:
                        entry_date = st.date_input("Entry Date", datetime.today())
                        wheat = st.number_input("Wheat Price", value=latest['Wheat'])
                        rice = st.number_input("Rice Price", value=latest['Rice'])
                    with cols[1]:
                        potatoes = st.number_input("Potatoes Price", value=latest['Potatoes'])
                        tomatoes = st.number_input("Tomatoes Price", value=latest['Tomatoes'])
                    
                    if st.form_submit_button("Submit Entry", type="primary"):
                        new_entry = {
                            'Date': entry_date,
                            'Wheat': wheat,
                            'Rice': rice,
                            'Potatoes': potatoes,
                            'Tomatoes': tomatoes
                        }
                        price_df.loc[len(price_df)] = new_entry
                        price_df.to_csv(PRICE_FILE, index=False)
                        st.success("Entry successfully added!")
                        st.rerun()
        
        elif admin_pass:
            st.error("Incorrect Admin Password")

# Footer
st.markdown("---")
st.markdown("""
<div class='footer'>
    <strong>FarmConnect</strong> - Ministry of Agriculture & Farmers Welfare Initiative<br>
    Data Updated Daily | Last Update: {date}<br>
    For support: contact@farmconnect.gov.in | ☎️ 1800-123-4567
</div>
""".format(date=datetime.today().strftime("%d %b %Y")), unsafe_allow_html=True)
