import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
from PIL import Image
from pypdf import PdfReader
from streamlit_mic_recorder import mic_recorder
import streamlit.components.v1 as components

# 1. BAZA FUNKSIYALARI
def init_db():
    conn = sqlite3.connect('chat_history_pro.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (username TEXT, role TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    return conn

def save_message(username, role, content):
    conn = sqlite3.connect('chat_history_pro.db', check_same_thread=False)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO history VALUES (?, ?, ?, ?)", (username, role, content, timestamp))
    conn.commit()
    conn.close()

def load_messages(username):
    conn = sqlite3.connect('chat_history_pro.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT role, content FROM history WHERE username=? ORDER BY timestamp", (username,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

init_db()

# 2. SAHIFA SOZLAMALARI VA RADIKAL CSS (Yangilanishni to'xtatish uchun)
st.set_page_config(page_title="Ibroximali PRO AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    /* Sahifa yangilanishini (pull-to-refresh) butunlay bloklash */
    html, body, [data-testid="stAppViewContainer"], .main {
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
    }
    /* Mobil uchun chat maydonini optimallashtirish */
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ISMNI BRAUZERDA SAQLASH (JavaScript yordamida)
# Bu kod sahifa yangilansa ham ismni LocalStorage'dan qayta tiklaydi
if "username" not in st.session_state:
    st.session_state.username = None

# Login oynasi
if st.session_state.username is None:
    st.title("🚀 Ibroximali PRO AI")
    st.subheader("Soliyev Ibroximali yordamchisi")
    
    name_input = st.text_input("Ismingizni kiriting:", key="login_input")
    if st.button("Kirish"):
        if name_input:
            st.session_state.username = name_input
            st.session_state.messages = load_messages(name_input)
            st.rerun()
    st.stop()

username = st.session_state.username

# 4. API VA MODEL (Informatika o'qituvchisi instruktsiyasi bilan)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="Siz informatika fani o'qituvchisisiz. Sanoq sistemalari bo'yicha masalalarni yechishda raqamlarni rasmda juda aniq tahlil qiling va o'nlik sanoq sistemasiga o'tkazish orqali tekshiring."
)

# 5. SIDEBAR
st.sidebar.title(f"Salom, {username}!")
st.sidebar.info("Yaratuvchi: **Soliyev Ibroximali**")
uploaded_image = st.sidebar.file_uploader("🖼️ Rasm yuklang", type=['png', 'jpg', 'jpeg'])
uploaded_pdf = st.sidebar.file_uploader("📄 PDF yuklang", type=['pdf'])

if st.sidebar.button("🔴 Tizimdan chiqish"):
    st.session_state.username = None
    st.rerun()

# 6. CHAT TARIXI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. INPUTLAR
st.write("---")
audio = mic_recorder(start_prompt="🎤 Ovozli savol", stop_prompt="🛑 To'xtatish", key='recorder')
prompt = st.chat_input("Savolingizni yozing...")

if audio:
    prompt = "Ovozli savol yuborildi. Iltimos, ushbu audioni tahlil qil."

if prompt:
    inputs = [prompt]
    if uploaded_image:
        img = Image.open(uploaded_image)
        inputs.append(img)
    if uploaded_pdf:
        reader = PdfReader(uploaded_pdf)
        pdf_text = "".join([page.extract_text() for page in reader.pages[:3]])
        inputs.append(f"PDF matni: {pdf_text}")

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    save_message(username, "user", prompt)

    try:
        with st.spinner("Ibroximali AI tahlil qilmoqda..."):
            response = model.generate_content(inputs)
            full_response = response.text
        
        with st.chat_message("assistant"):
            st.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        save_message(username, "assistant", full_response)
    except Exception as e:
        st.error(f"Xatolik: {e}")