import streamlit as st
from config import ROLES, CATEGORIES


def render_sidebar():
    st.sidebar.title("🧠 RAG Knowledge Assistant")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📤 Upload Documents", "💬 Chat"]
    )

    st.sidebar.markdown("---")

    role = st.sidebar.selectbox(
        "👤 Professional Role",
        ROLES
    )

    category = st.sidebar.selectbox(
        "📂 Knowledge Category",
        CATEGORIES
    )

    return page, role, category
