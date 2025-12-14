import streamlit as st

def render_home():
    st.title("🧠 CV Knowledge Assistant")
    st.markdown("""
    Welcome to the CV Knowledge Assistant!

    This system allows you to:

    - 📤 Upload CVs by role (category)
    - 💬 Ask questions about CVs by category
    - Manage knowledge based on professional roles

    **How to use:**

    1. Select "Upload CV" in the left menu to upload CVs.
    2. Select "Chat" to ask questions about CVs by category.

    """)
