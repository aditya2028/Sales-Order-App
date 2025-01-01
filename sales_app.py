import streamlit as st
from datetime import datetime, timedelta
import urllib.parse
import pandas as pd

# Sample product data
products = {
    "divine pipe 15mm": 525,
    "divine pipe 19mm": 655,
    "divine pipe 23mm": 872,
    "divine pipe 25mm": 1070,
    "ultra pipe 19mm": 786,
    "ultra pipe 23mm": 1017,
    "ultra pipe 25mm": 1248,
    "ultra pipe 28 (50)mm": 720,
    "ultra pipe 28(100)mm": 1404,
    "unique super pipe 19mm": 867,
    "unique super pipe 23mm": 1123,
    "unique super pipe 25mm": 1377,
    "unique deluxe 20mm": 1058,
    "unique deluxe 24mm": 1305,
    "unique super deluxe 20mm": 1235,
    "unique super deluxe 24mm": 1780,
}

# Streamlit app
st.set_page_config(page_title="Sales Order App", layout="wide")
st.title("Sales Order App")

# Initialize session state variables
if 'final_price' not in st.session_state:
    st.session_state.final_price = 0.0
if 'invoice_generated' not in st.session_state:
    st.session_state.invoice_generated = False
if 'invoice_details' not in st.session_state:
    st.session_state.invoice_details = ""
if 'production_plan' not in st.session_state:
    st.session_state.production_plan = pd.DataFrame(columns=['Product', 'Delivery Date', 'Priority'])

# Customer details
st.header("Customer Details")
customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
customer_phone = st.text_input("Customer Phone Number", placeholder="Enter customer phone number")

# Delivery date input
delivery_date = st.date_input("Delivery Date", value=(datetime.now() + timedelta(days=7)).date())

# Product selection
st.header("Order Details")
product_options = list(products.keys())
selected_product = st.selectbox("Select Product", product_options)

# Quantity input
quantity = st.number_input("Quantity", min_value=1, step=1, value=1)

# Discount input
discount_percentage = st.number_input("Discount Percentage", min_value=0, max_value=100, step=1, value=0)

# Calculate total price
def calculate_total_price():
    price_per_unit = products[selected_product]
    total_price = price_per_unit * quantity
    discount_amount = (discount_percentage / 100) * total_price
    st.session_state.final_price = total_price - discount_amount
    return st.session_state.final_price

if st.button("Calculate Total Price"):
    final_price = calculate_total_price()
    st.success(f"Total Price after {discount_percentage}% discount: ₹{final_price:.2f}")
    st.session_state.invoice_generated = False  # Reset invoice status if recalculated

# Generate Invoice
def generate_invoice():
    if not customer_name or not customer_phone:
        st.error("Please fill in all customer details.")
        return False
    if st.session_state.final_price <= 0:
        st.error("Please calculate the total price before generating the invoice.")
        return False

    invoice_details = (
        f"Invoice Details:\n"
        f"Customer Name: {customer_name}\n"
        f"Customer Phone: {customer_phone}\n"
        f"Delivery Date: {delivery_date}\n"
        f"Product: {selected_product}\n"
        f"Quantity: {quantity}\n"
        f"Total Price: ₹{st.session_state.final_price:.2f}"
    )
    st.session_state.invoice_details = invoice_details

    # Add to production plan
    new_entry = pd.DataFrame([{
        'Product': selected_product,
        'Delivery Date': datetime.combine(delivery_date, datetime.min.time()),
        'Priority': "High" if datetime.combine(delivery_date, datetime.min.time()) <= datetime.now() + timedelta(days=7) else "Medium"
    }])
    st.session_state.production_plan = pd.concat([st.session_state.production_plan, new_entry], ignore_index=True)

    return invoice_details

if st.button("Generate Invoice"):
    invoice_details = generate_invoice()
    if invoice_details:
        st.session_state.invoice_generated = True
        st.text_area("Invoice Details", invoice_details, height=200)

        # WhatsApp sharing section
        st.header("Share Invoice on WhatsApp")
        pre_filled_message = f"Hello, here are your invoice details:\n\n{st.session_state.invoice_details}"
        custom_message = st.text_area("Customize your message", pre_filled_message)
        full_message = urllib.parse.quote(custom_message)

        # Default WhatsApp numbers
        default_numbers = ["1234567890", "0987654321"]
        st.write("Invoice will be shared to the following default numbers and customer number:")
        for number in default_numbers:
            st.write(f"- {number}")

        # Enhanced WhatsApp sharing functionality
        st.subheader("Sharing Options")
        col1, col2, col3 = st.columns(3)

        # Customer WhatsApp link
        customer_whatsapp_link = f"https://wa.me/{customer_phone}?text={full_message}"
        col1.markdown(f"[Share with Customer on WhatsApp]({customer_whatsapp_link})", unsafe_allow_html=True)

        # Default numbers WhatsApp links
        for idx, number in enumerate(default_numbers):
            default_whatsapp_link = f"https://wa.me/{number}?text={full_message}"
            col2.markdown(f"[Share with Default {idx+1} on WhatsApp]({default_whatsapp_link})", unsafe_allow_html=True)

        st.success("Invoice generated and enhanced sharing options are ready!")

# Production Planning
st.header("Production Planning")
if not st.session_state.production_plan.empty:
    st.write("### Production Plan for the Week")
    current_week = datetime.now().isocalendar()[1]
    production_plan = st.session_state.production_plan.copy()
    production_plan['Week Number'] = production_plan['Delivery Date'].apply(lambda x: x.isocalendar()[1])
    production_plan['Priority'] = production_plan['Priority'].apply(lambda x: "High" if x == "High" else "Medium")
    weekly_plan = production_plan[production_plan['Week Number'] == current_week]

    if not weekly_plan.empty:
        st.table(weekly_plan[['Product', 'Delivery Date', 'Priority']])
    else:
        st.info("No high-priority products for the current week.")
else:
    st.info("No production data available yet.")
