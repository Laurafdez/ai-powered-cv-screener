import streamlit as st
import requests
from config import UPLOAD_URL, ROLES

def render_upload():
    st.title("📤 Upload CV")
    st.markdown("Select the role (category) and upload the CV.")

    role = st.selectbox("Select Role", ROLES)

    uploaded_file = st.file_uploader("Choose a CV file", type=["pdf", "docx", "txt", "doc"])

    if uploaded_file and role:
        if st.button("🚀 Upload CV"):
            with st.spinner("Uploading CV..."):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)
                    }
                    data = {"category": role}  # role = category
                    response = requests.post(UPLOAD_URL, files=files, data=data)

                    if response.status_code == 200:
                        st.success("✅ CV uploaded successfully!")
                    else:
                        st.error("❌ Failed to upload CV")
                except Exception as e:
                    st.error("❌ Failed to upload CV")
