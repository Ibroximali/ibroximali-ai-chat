import streamlit as st
import google.generativeai as genai
import os

# Sahifa sarlavhasi
st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("🤖 Mening Shaxsiy AI Yordamchim")

# API kalitni sozlash
# DIQQAT: O'zingiz olgan kalitni shu yerga qo'ying
os.environ["GOOGLE_API_KEY"] = "AIzaSyCgcmVnTNgrve3sQEQNjBS51FdKrL8QD1s"
import streamlit as st
import google.generativeai as genai

# Streamlit Secrets-dan kalitni xavfsiz o'qib olish
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("API kalit topilmadi! Iltimos, Secrets bo'limini tekshiring.")
    st.stop()

genai.configure(api_key=api_key)
# Ro'yxatdagi eng yangi va kuchli modelni tanlaymiz
# Modelni sozlash va tizim yo'riqnomasini berish
# Modelni mavjud bo'lgan nom bilan sozlash (gemini-1.5-flash)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="Assalomu alaykum! Men Ibroximali Soliyev tomonidan yaratilgan maxsus sun'iy intellekt yordamchisiman. Foydalanuvchilarga informatika va texnologiyalar olamida yordam beraman."
)

# AI javobini olish qismini ham biroz o'zgartiramiz
if prompt := st.chat_input("Savol bering..."):
    # ... (oldingi kod qismlari)
    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        # Ba'zan natija response.text ichida bo'lmasligi mumkin, shuni tekshiramiz
        try:
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except:
            st.error("AI javob qaytara olmadi. API sozlamalarini tekshiring.")
# Xotira (Chat tarixi) yaratish
if "messages" not in st.session_state:
    st.session_state.messages = []

# Oldingi yozishmalarni ko'rsatish
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Foydalanuvchidan savol olish
if prompt := st.chat_input("Qanday yordam bera olaman?"):
    # Savolni ekranga chiqarish va xotiraga qo'shish
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI javobini olish
    with st.chat_message("assistant"):
        with st.spinner("O'ylayapman..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Xatolik yuz berdi: {e}")