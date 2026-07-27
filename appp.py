import streamlit as st
import requests
import pandas as pd

# The URL where your FastAPI backend is running
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Warehouse Logistics", layout="wide")
st.title("📦 Warehouse Logistics System")

# Role/Location Selection Menu
menu = st.sidebar.selectbox(
    "Select Role / Location",
    ["Warehouse A - Dispatch", "Transit Tracker", "Warehouse B - Receiving", "Master Inventory"]
)

# ---------------------------------------------------------
# Tab 1: Warehouse A - Dispatch
# ---------------------------------------------------------
if menu == "Warehouse A - Dispatch":
    st.header("📤 Dispatch Stock to Warehouse B")
    
    with st.form("dispatch_form"):
        product = st.text_input("Product Name")
        qty = st.number_input("Quantity", min_value=1, step=1)
        submit = st.form_submit_button("Dispatch")

        if submit:
            payload = {"product_name": product, "quantity": qty}
            # Sending a POST request to our FastAPI backend
            res = requests.post(f"{API_URL}/dispatch_stock", json=payload)
            
            if res.status_code == 201:
                st.success(f"Successfully dispatched {qty} units of {product}!")
            else:
                st.error("Failed to dispatch stock. Please check the backend.")

# ---------------------------------------------------------
# Tab 2: Transit Tracker
# ---------------------------------------------------------
elif menu == "Transit Tracker":
    st.header("🚚 In-Transit Shipments")
    
    # A handy toggle to use the query parameter we built in the backend!
    show_only_transit = st.checkbox("Show only 'In Transit'")
    url = f"{API_URL}/shipments"
    
    if show_only_transit:
        url += "?status_filter=In Transit"
        
    res = requests.get(url)
    
    if res.status_code == 200:
        data = res.json()
        if data:
            # Pandas makes the Streamlit table look incredibly clean
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("No shipments found.")
    else:
        st.error("Could not fetch the transit log.")

# ---------------------------------------------------------
# Tab 3: Warehouse B - Receiving
# ---------------------------------------------------------
elif menu == "Warehouse B - Receiving":
    st.header("📥 Receive Incoming Shipments")
    
    with st.form("receive_form"):
        shipment_id = st.number_input("Shipment ID", min_value=1, step=1)
        submit = st.form_submit_button("Mark as Received")

        if submit:
            # Sending a PUT request to trigger our backend logic
            res = requests.put(f"{API_URL}/receive_stock/{shipment_id}")
            
            if res.status_code == 200:
                st.success(res.json().get("message"))
            elif res.status_code == 404:
                st.error("Shipment ID not found.")
            elif res.status_code == 400:
                st.warning("This shipment has already been received.")
            else:
                st.error("Failed to process the shipment.")

# ---------------------------------------------------------
# Tab 4: Master Inventory
# ---------------------------------------------------------
elif menu == "Master Inventory":
    st.header("📊 Warehouse B Master Inventory")
    
    res = requests.get(f"{API_URL}/inventory")
    
    if res.status_code == 200:
        data = res.json()
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("Inventory is currently empty.")
    else:
        st.error("Could not fetch master inventory.")