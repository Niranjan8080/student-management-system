
import streamlit as st
import requests

BASE_URL = "https://student-management-system-kfp1.onrender.com"

st.set_page_config(page_title="Student Management", layout="wide")

if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False

st.title("🎓 Student Management System")

if st.session_state.teacher_logged_in:
    st.sidebar.success("Teacher Logged In")
    if st.sidebar.button("Logout"):
        st.session_state.teacher_logged_in = False
        st.rerun()

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Student Login",
        "Teacher Login",
        "View Students",
        "Add Student",
        "Update Student",
        "Delete Student",
        "Search Student",
        "Change Password",
    ],
)

def require_teacher():
    if not st.session_state.teacher_logged_in:
        st.warning("Please login as Teacher first.")
        st.stop()

if menu == "Student Login":
    st.header("Student Login")
    roll = st.number_input("Roll No", min_value=1)
    name = st.text_input("Name")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        r = requests.post(f"{BASE_URL}/student",
                          json={"roll_no": int(roll), "name": name, "password": pwd})
        if r.ok:
            st.success("Login Successful")
            st.json(r.json())
        else:
            st.error(r.json().get("detail", "Login failed"))

elif menu == "Teacher Login":
    st.header("Teacher Login")
    pwd = st.text_input("Teacher Password", type="password")
    if st.button("Login"):
        r = requests.post(f"{BASE_URL}/teacher/login", json={"password": pwd})
        if r.ok:
            st.session_state.teacher_logged_in = True
            st.success("Login Successful")
            st.rerun()
        else:
            st.error(r.json().get("detail", "Wrong Password"))

elif menu == "View Students":
    require_teacher()
    st.header("Student List")
    if st.button("Load Students"):
        r = requests.get(f"{BASE_URL}/teacher/students")
        if r.ok:
            st.dataframe(r.json(), use_container_width=True)
        else:
            st.error(r.text)

elif menu == "Add Student":
    require_teacher()
    st.header("Add Student")
    name = st.text_input("Name")
    fees = st.number_input("Fees", min_value=0.0)
    pwd = st.text_input("Password", type="password")
    if st.button("Add Student"):
        r = requests.post(f"{BASE_URL}/teacher/add",
                          json={"name": name, "fees": fees, "password": pwd})
        if r.ok:
            st.success("Student Added")
            st.json(r.json())
        else:
            st.error(r.text)

elif menu == "Update Student":
    require_teacher()
    st.header("Update Student")
    roll = st.number_input("Roll No", min_value=1)
    name = st.text_input("New Name")
    fees = st.number_input("New Fees", min_value=0.0)
    pwd = st.text_input("New Password", type="password")
    if st.button("Update"):
        payload = {}
        if name: payload["name"] = name
        if fees > 0: payload["fees"] = fees
        if pwd: payload["password"] = pwd
        r = requests.put(f"{BASE_URL}/teacher/update/{int(roll)}", json=payload)
        if r.ok:
            st.success(r.json()["message"])
        else:
            st.error(r.text)

elif menu == "Delete Student":
    require_teacher()
    st.header("Delete Student")
    roll = st.number_input("Roll No", min_value=1)
    if st.button("Delete"):
        r = requests.delete(f"{BASE_URL}/teacher/delete/{int(roll)}")
        if r.ok:
            st.success(r.json()["message"])
        else:
            st.error(r.text)

elif menu == "Search Student":
    require_teacher()
    st.header("Search Student")
    roll = st.number_input("Roll No", min_value=1)
    if st.button("Search"):
        r = requests.get(f"{BASE_URL}/teacher/student/{int(roll)}")
        if r.ok:
            st.json(r.json())
        else:
            st.error(r.text)

elif menu == "Change Password":
    st.header("Change Password")
    roll = st.number_input("Roll No", min_value=1)
    old = st.text_input("Old Password", type="password")
    new = st.text_input("New Password", type="password")
    if st.button("Change Password"):
        r = requests.put(
            f"{BASE_URL}/student/change-password",
            json={"roll_no": int(roll), "old_password": old, "new_password": new},
        )
        if r.ok:
            st.success(r.json()["message"])
        else:
            st.error(r.text)
