import streamlit as st

# Simplest possible app for iPhone 6s testing
st.set_page_config(page_title="Test", layout="centered")

st.title("📱 Mobile Test")
st.write("If you can see this, Streamlit works on your phone!")

st.success("✅ Connection successful!")

if st.button("Click me"):
    st.balloons()
    st.write("Button works!")

st.info("App: kingsford97-my-data-portal.streamlit.app")