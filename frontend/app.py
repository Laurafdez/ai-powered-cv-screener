import streamlit as st
from ui.home import render_home
from ui.upload import render_upload
from ui.chat import render_chat
from config import ROLES

st.set_page_config(page_title="CV Knowledge Assistant", page_icon="🧠", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Upload CV", "Chat"])

# Initialize selected_role for Chat page
selected_role = None

if page == "Chat":
    # Chat page specific role selection
    st.sidebar.markdown("### Select Category to Ask About:")
    if ROLES:
        selected_role = st.sidebar.selectbox("Select Category to Ask About", ROLES)
    else:
        st.sidebar.warning("No roles available for selection. Please check configuration.")

# Render content based on the selected page
st.markdown("---")
if page == "Home":
    render_home()
elif page == "Upload CV":
    render_upload()
elif page == "Chat":
    if selected_role:
        render_chat(selected_role)
    else:
        st.warning("Please select a role to continue with the Chat.")
