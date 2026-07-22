import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.title(" Course Management System")

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
        st.write(data["courses"])
    else:
        st.error("Unable to fetch courses.")

# ------------------ Add Course ------------------

elif menu == "Add Course":
    st.header("Add a Course")

    course = st.text_input("Course Name")

    if st.button("Add"):
        response = requests.post(f"{BASE_URL}/add_course/{course}")

        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error("Failed to add course.")

# ------------------ Update Course ------------------

elif menu == "Update Course":
    st.header("Update a Course")

    old_course = st.text_input("Old Course Name")
    new_course = st.text_input("New Course Name")

    if st.button("Update"):
        response = requests.put(
            f"{BASE_URL}/update_course/{old_course}/{new_course}"
        )

        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error("Failed to update course.")

# ------------------ Delete Course ------------------

elif menu == "Delete Course":
    st.header("Delete a Course")

    course = st.text_input("Course Name")

    if st.button("Delete"):
        response = requests.delete(
            f"{BASE_URL}/delete_course/{course}"
        )

        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error("Failed to delete course.")