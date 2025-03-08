import streamlit as st
from supabase import create_client
from data_processing import scan_qr, get_customer_balance, get_customer_saved, update_customer_balance, get_merchant_balance, update_merchant_balance

url="https://kcuzslepwnwfkkkomlfv.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjdXpzbGVwd253Zmtra29tbGZ2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA0NzM1NjksImV4cCI6MjA1NjA0OTU2OX0.GfnoOmNE0SDKQ0oUOhexOo7r2uD-FarmdYNUuEEdidU"
supabase = create_client(url, key)

# Initialize session state variables
if "merchant_id" not in st.session_state:
    st.session_state.merchant_id = None
if "merchant_balance" not in st.session_state:
    st.session_state.merchant_balance = 0
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "transaction_step" not in st.session_state:
    st.session_state.transaction_step = "price_entry"
if "entered_price" not in st.session_state:
    st.session_state.entered_price = 0
if "customer_id" not in st.session_state:
    st.session_state.customer_id = ""

# Title
st.title("Merchant Login")
st.write(f"Contact for any questions +41763091486 (WhatsApp) Alexander")

