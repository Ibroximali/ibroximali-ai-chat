import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
from PIL import Image
from pypdf import PdfReader
from streamlit_mic_recorder import mic_recorder

# 1. MA'LUMOTLAR BAZASI
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

# 2. SAHIFA VA DIZAYN
st.set_page_config(page_title="Ibroximali PRO AI", page_icon="🚀", layout="wide")

# 3. LOGIN VA MUALLIFLIK
if "username" not in st.session_state:
    st.title("🚀 Ibroximali PRO AI Assistant")
    st.subheader("Men Soliyev Ibroximali tomonidan yaratilgan ko'p funksiyali shaxsiy botman.")
    st.markdown("""
    **Imkoniyatlarim:**
    * 🖼️ Rasmlarni ko'rib tahlil qilish (Vision)
    * 🎤 Ovozli buyruqlarni tushunish
    * 📄 PDF darsliklar bilan ishlash
    * 💾 Har bir foydalanuvchini eslab qolish
    """)
    
    name = st.text_input("Davom etish uchun ismingizni kiriting:")
    if st.button("Tizimga kirish") and name:
        st.session_state.username = name
        st.session_state.messages = load_messages(name)
        st.rerun()
    st.stop()

username = st.session_state.username

# 4. API VA MODELLAR
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 5. SIDEBAR - MULTIMEDIA FUNKSIYALARI
st.sidebar.title(f"Xush kelibsiz, {username}!")
st.sidebar.info("Yaratuvchi: **Soliyev Ibroximali**")

st.sidebar.divider()
st.sidebar.subheader("🎥 Multimedia")

# Rasm yuklash (Vision)
uploaded_image = st.sidebar.file_uploader("Rasm yuklang (Masala yechish)", type=['png', 'jpg', 'jpeg'])

# PDF yuklash
uploaded_pdf = st.sidebar.file_uploader("PDF darslik yuklang", type=['pdf'])

# Ovozli buyruq
st.sidebar.write("🎤 Ovozli xabar:")
audio = mic_recorder(start_prompt="Yozishni boshlash", stop_prompt="To'xtatish", key='recorder')

if st.sidebar.button("Tarixni tozalash"):
    st.session_state.messages = []
    st.rerun()

# 6. CHAT OYNASI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. ASOSIY MANTIQ (INPUTLAR)
prompt = st.chat_input("Savolingizni yozing...")

# Ovozni matnga aylantirish (Oddiyroq variant - matn sifatida qabul qilish)
if audio:
    prompt = "Ovozli xabar yuborildi (Hozircha matnli rejimda savol yozing)" # Kelajakda Whisper API ulanadi

if prompt:
    context_text = prompt
    inputs = [prompt]

    # PDF tahlili
    if uploaded_pdf:
        reader = PdfReader(uploaded_pdf)
        pdf_text = ""
        for page in reader.pages[:5]: # Birinchi 5 betni o'qiydi
            pdf_text += page.extract_text()
        inputs.append(f"\nPDF mazmuni: {pdf_text}")

    # Rasm tahlili
    if uploaded_image:
        img = Image.open(uploaded_image)
        inputs.append(img)
        st.image(img, caption="Yuklangan rasm", width=300)

    # Ko'rsatish va saqlash
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    save_message(username, "user", prompt)

    # AI JAVOBI
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

if st.sidebar.button("Chiqish"):
    del st.session_state.username
    st.rerun()