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

# Show login form only if the user is not authenticated
if not st.session_state.authenticated:
    password = st.text_input("Enter your password:", type="password")

    if st.button("Login"):
        result = supabase.table("merchants").select("*").eq("password", password).execute().data
        if result:
            st.session_state.merchant_id = result[0]["id"]
            st.session_state.merchant_balance = result[0]["balance"]
            st.session_state.merchant_payback = result[0]["payback"]
            st.session_state.merchant_discount = result[0]["discount"]
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.rerun()  # Refresh to hide login form
        else:
            st.error("You are not registered. Please contact the admin.")

# If authenticated, proceed with transaction logic
if st.session_state.authenticated:
    st.subheader("Welcome!")
    st.write(f"Your ID: {st.session_state.merchant_id}")
    st.write(f"Current Balance: {st.session_state.merchant_balance:.2f} CHF")
    st.write(f"Payback: {st.session_state.merchant_payback}% &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Discount: {st.session_state.merchant_discount}%")
    
    st.markdown("<hr style='border: 3px solid black;'>", unsafe_allow_html=True)

    if st.session_state.transaction_step == "price_entry":
        # Step 1: Merchant enters the price
        st.session_state.entered_price = st.number_input("Enter PRICE (CHF)", min_value=0.0, format="%.2f")

        if st.session_state.entered_price > 0:
            potential_discount = st.session_state.entered_price * (st.session_state.merchant_discount / 100)
            merchant_balance_sufficient = st.session_state.merchant_balance >= potential_discount

            st.write(f"Potential Discount: {potential_discount:.2f} CHF")
            st.write("Merchant has enough balance for discount." if merchant_balance_sufficient else "Merchant does NOT have enough balance for discount. Payback will be applied")

            if st.button("Continue"):
                st.session_state.transaction_step = "customer_entry"
                st.rerun()

    elif st.session_state.transaction_step == "customer_entry":
        # Step 2: Customer ID
        if st.button("Scan QR Code"):
            scanned_code = scan_qr()  # Call the function
            if scanned_code:
                st.session_state.customer_id = scanned_code
            else:
                st.error("No QR code detected. Try again.")
        
        if st.session_state.customer_id:
            customer_balance = get_customer_balance(st.session_state.customer_id)
            
            if customer_balance is not None:
                st.write(f"Customer's Current Balance: {customer_balance:.2f} CHF")

                potential_discount = st.session_state.entered_price * (st.session_state.merchant_discount / 100)
                potential_payback = st.session_state.entered_price * (st.session_state.merchant_payback / 100)

                discount_applied = 0
                payback_applied = 0
                final_price = st.session_state.entered_price

                if st.session_state.merchant_balance >= potential_discount:
                    if customer_balance >= potential_discount:
                        discount_applied = potential_discount
                        final_price -= discount_applied
                    else:
                        payback_applied = potential_payback
                else:
                    payback_applied = potential_payback

                st.write(f"Final Price: {final_price:.2f} CHF")
                if payback_applied > 0:
                    st.write(f"Payback will be applied: {payback_applied:.2f} CHF")

                if st.button("Continue"):
                    # Step 3: Finalize transaction
                    merchant_balance = st.session_state.merchant_balance
                    customer_balance = get_customer_balance(st.session_state.customer_id)
                    customer_saved = get_customer_saved(st.session_state.customer_id)
                    if discount_applied > 0:
                        customer_balance -= discount_applied
                        merchant_balance -= discount_applied
                        customer_saved += discount_applied
                    else:
                        customer_balance += payback_applied
                        merchant_balance += payback_applied

                    # Update balances in Supabase
                    update_customer_balance(st.session_state.customer_id, customer_balance, customer_saved)
                    update_merchant_balance(st.session_state.merchant_id, merchant_balance)

                    # **Fetch the updated balance from Supabase**
                    st.session_state.merchant_balance = get_merchant_balance(st.session_state.merchant_id)

                    # Reset transaction state for the next purchase
                    st.session_state.transaction_step = "price_entry"
                    st.session_state.customer_id = ""
                    st.session_state.entered_price = 0

                    st.success("Transaction completed!")
                    st.rerun()
            else:
                st.error("There is no customer with such ID")
                if st.button("Cancel"):
                    # Reset transaction and allow new price entry
                    st.session_state.transaction_step = "price_entry"
                    st.session_state.customer_id = ""
                    st.session_state.entered_price = 0
                    st.rerun()

    elif st.button("Cancel"):
        # Reset transaction and allow new price entry
        st.session_state.transaction_step = "price_entry"
        st.session_state.customer_id = ""
        st.session_state.entered_price = 0
        st.rerun()