import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime

# 1. Ma'lumotlar bazasini sozlash (Xabarlarni eslab qolish uchun)
def init_db():
    conn = sqlite3.connect('chat_history.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (username TEXT, role TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    return conn

def save_message(username, role, content):
    conn = sqlite3.connect('chat_history.db', check_same_thread=False)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO history VALUES (?, ?, ?, ?)", (username, role, content, timestamp))
    conn.commit()
    conn.close()

def load_messages(username):
    conn = sqlite3.connect('chat_history.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT role, content FROM history WHERE username=? ORDER BY timestamp", (username,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

# Bazani ishga tushiramiz
init_db()

# 2. Sahifa sozlamalari
st.set_page_config(page_title="AI Maktab Yordamchisi", page_icon="🤖")
st.title("🤖 Aqlli Maktab Yordamchisi")

# 3. Foydalanuvchini aniqlash (Login qismi)
if "username" not in st.session_state:
    st.info("Assalomu alaykum! Ilovadan foydalanish uchun ismingizni kiriting.")
    name_input = st.text_input("Ismingiz:")
    if st.button("Kirish"):
        if name_input:
            st.session_state.username = name_input
            st.session_state.messages = load_messages(name_input)
            st.rerun()
    st.stop()

username = st.session_state.username
st.sidebar.success(f"Xush kelibsiz, {username}!")
if st.sidebar.button("Chiqish (Log out)"):
    del st.session_state.username
    st.rerun()

# 4. API sozlamalari
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API kalit topilmadi!")
    st.stop()

# Modelni tanlash (2.5-flash bepul limit uchun eng yaxshisi)
model = genai.GenerativeModel('gemini-2.5-flash')

# 5. Chat tarixini ko'rsatish
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Savol yuborish va javob olish
if prompt := st.chat_input("Savolingizni yozing..."):
    # Foydalanuvchi xabarini ko'rsatish va saqlash
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    save_message(username, "user", prompt)

    # AI javobini olish
    try:
        response = model.generate_content(prompt)
        full_response = response.text
        
        with st.chat_message("assistant"):
            st.markdown(full_response)
        
        # Assistant javobini saqlash
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        save_message(username, "assistant", full_response)
        
    except Exception as e:
        st.error(f"Xatolik yuz berdi: {e}")