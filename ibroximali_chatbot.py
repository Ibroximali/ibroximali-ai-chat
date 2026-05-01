import streamlit as st
import google.generativeai as genai

# Sahifa sarlavhasi
st.set_page_config(page_title="Mening Shaxsiy AI Yordamchim", page_icon="🤖")
st.title("🤖 Mening Shaxsiy AI Yordamchim")

# Secrets'dan API kalitni olish
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("API kalit topilmadi! Streamlit Secrets-ni tekshiring.")
    st.stop()

# Modelni sozlash
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# Chat tarixi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski xabarlarni chiqarish
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Foydalanuvchi kiritishi
if prompt := st.chat_input("Savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI javobi
    try:
        response = model.generate_content(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Xatolik yuz berdi: {e}")