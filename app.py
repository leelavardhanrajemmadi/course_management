import streamlit as st
import requests

BASE_URL = "https://course-management-vnu3.onrender.com"

st.title("📚 Course Management System")

menu = st.sidebar.selectbox(
    "Choose an Operation",
    ["View Courses", "Add Course", "Update Course", "Delete Course"]
)

# ------------------ View Courses ------------------
if menu == "View Courses":
    st.header("Available Courses")
    response = requests.get(f"{BASE_URL}/courses")

    if response.status_code == 200:
        data = response.json()
        st.table(data["courses"]) # Upgraded to a table for better visibility!
    else:
        st.error("Unable to fetch courses.")

# ------------------ Add Course ------------------
elif menu == "Add Course":
    st.header("Add a Course")
    
    with st.form("add_form"):
        course_id = st.number_input("Course ID", min_value=1, step=1)
        course_name = st.text_input("Course Name")
        course_price = st.number_input("Price", min_value=0, step=100)
        submitted = st.form_submit_button("Add")

        if submitted:
            # Package the data to match the Pydantic BaseModel exactly
            payload = {"id": course_id, "name": course_name, "price": course_price}
            
            # Send the payload as JSON
            response = requests.post(f"{BASE_URL}/add_course", json=payload)

            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error("Failed to add course.")

# ------------------ Update Course ------------------
elif menu == "Update Course":
    st.header("Update a Course")
    
    with st.form("update_form"):
        target_id = st.number_input("ID of Course to Update", min_value=1, step=1)
        st.write("Enter the new details below:")
        new_name = st.text_input("New Course Name")
        new_price = st.number_input("New Price", min_value=0, step=100)
        submitted = st.form_submit_button("Update")

        if submitted:
            payload = {"id": target_id, "name": new_name, "price": new_price}
            
            response = requests.put(f"{BASE_URL}/update_course/{target_id}", json=payload)

            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error("Failed to update course.")

# ------------------ Delete Course ------------------
elif menu == "Delete Course":
    st.header("Delete a Course")
    
    course_id = st.number_input("ID of Course to Delete", min_value=1, step=1)

    if st.button("Delete"):
        response = requests.delete(f"{BASE_URL}/delete_course/{course_id}")

        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error("Failed to delete course.")
