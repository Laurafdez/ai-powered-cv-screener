import streamlit as st
import requests
from config import CHAT_URL

def render_chat(selected_role):
    st.title("💬 Chat Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


    # Render chat history
    for msg in st.session_state.chat_history:
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question...")

    if user_input and selected_role:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        payload = {"message": user_input, "category": selected_role}

        with st.spinner("Thinking..."):
            response = requests.post(CHAT_URL, json=payload)

        if response.status_code == 200:
            answer = response.json().get("response", "")
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)
        else:
            st.error("❌ Error contacting backend")
