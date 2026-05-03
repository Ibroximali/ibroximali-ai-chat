import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
from PIL import Image
from pypdf import PdfReader
from streamlit_mic_recorder import mic_recorder

# 1. BAZA VA SAQLASH FUNKSIYALARI
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

# 2. SAHIFA SOZLAMALARI (MUAMMO TUZATILDI)
st.set_page_config(page_title="DIAMOND AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    /* MOBILDA YANGILANIB KETISHNI TO'XTATISH */
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain;
    }
    /* Chat konteyneri balandligi */
    .stChatMessage {
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN TIZIMI
if "username" not in st.session_state:
    st.title("🚀 DIAMOND AI")
    st.subheader("Soliyev Ibroximali tomonidan yaratilgan shaxsiy yordamchi")
    
    name = st.text_input("Ismingizni kiriting:", key="login_name")
    if st.button("Kirish") and name:
        st.session_state.username = name
        st.session_state.messages = load_messages(name)
        st.rerun()
    st.stop()

username = st.session_state.username

# 4. API VA SYSTEM INSTRUCTION (SANOQ SISTEMASI XATOSINI TUZATISH UCHUN)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
# AI ga o'qituvchi rolini beramiz
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="Siz tajribali informatika o'qituvchisisiz. Sanoq sistemalari (2, 8, 10, 16) ustidagi amallarni matematik aniqlikda, bosqichma-bosqich yechib berasiz. Rasmda raqamlarni juda diqqat bilan o'qing."
)

# 5. SIDEBAR
st.sidebar.title(f"Assalomu alaykum, {username}!")
uploaded_image = st.sidebar.file_uploader("🖼️ Masalani rasmga olib yuklang", type=['png', 'jpg', 'jpeg'])
uploaded_pdf = st.sidebar.file_uploader("📄 PDF darslik yuklang", type=['pdf'])

if st.sidebar.button("🔴 Tizimdan chiqish"):
    del st.session_state.username
    st.rerun()

# 6. CHAT TARIXI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. OVOZLI VA MATNLI INPUT
st.write("---")
audio = mic_recorder(start_prompt="🎤 Ovozli savol", stop_prompt="🛑 To'xtatish", key='recorder')
prompt = st.chat_input("Savolingizni yozing...")

if audio:
    prompt = "Ovozli xabar qabul qilindi. Iltimos, ushbu audioni tahlil qiling."

if prompt:
    inputs = [prompt]
    
    if uploaded_image:
        img = Image.open(uploaded_image)
        inputs.append(img)
    
    if uploaded_pdf:
        reader = PdfReader(uploaded_pdf)
        pdf_text = "".join([page.extract_text() for page in reader.pages[:3]])
        inputs.append(f"Hujjat mazmuni: {pdf_text}")

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