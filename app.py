import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI DAN INISIALISASI
# ==============================================================================

# Mengambil API key dari Streamlit Secrets atau environment variable
try:
    # Menggunakan Streamlit Secrets untuk deployment yang aman
    # Pastikan Anda telah mengaturnya di Streamlit Cloud
    API_KEY = st.secrets["gemini_api_key"]
    st.write("Mengambil API key dari Streamlit Secrets.")
except FileNotFoundError:
    # Fallback untuk local development, mengambil dari environment variable
    # Anda dapat mengatur ini dengan `export gemini_api_key='YOUR_API_KEY'`
    API_KEY = os.getenv("gemini_api_key")
    st.warning("Mengambil API key dari Environment Variable. Pastikan sudah diatur.")

if not API_KEY:
    st.error("API Key Gemini tidak ditemukan. Harap atur di Streamlit Secrets atau environment variable.")
    st.stop()

# Nama model Gemini
MODEL_NAME = 'gemini-1.5-flash'
genai.configure(api_key=API_KEY)

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

INITIAL_CHATBOT_CONTEXT = [
    {"role": "user", "parts": ["Kamu adalah seorang apoteker. Tuliskan obat apa yang diinginkan untuk menyembuhkan penyakit. Jawaban singkat dan faktual. Tolak pertanyaan non-apoteker."]},
    {"role": "model", "parts": ["Baik! Sebutkan nama penyakit atau gejala yang Anda alami, dan saya akan memberikan informasi singkat tentang obat yang relevan."]}
]

# ==============================================================================
# APLIKASI STREAMLIT
# ==============================================================================

st.title("💊 Asisten Apoteker Gemini")
st.markdown("Aplikasi chatbot ini menggunakan **Google Gemini** untuk memberikan informasi seputar obat-obatan. **Penting: Informasi ini bukan pengganti nasihat medis profesional.**")

# Menginisialisasi sesi chat di Streamlit, disimpan di session_state
if "chat" not in st.session_state:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        st.session_state.chat = model.start_chat(history=INITIAL_CHATBOT_CONTEXT)
        st.session_state.messages = INITIAL_CHATBOT_CONTEXT.copy()
    except Exception as e:
        st.error(f"Gagal menginisialisasi model: {e}")
        st.stop()

# Menampilkan riwayat chat dari session_state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# Menerima input dari pengguna
if prompt := st.chat_input("Tanyakan tentang obat..."):
    # Menambahkan input pengguna ke riwayat dan menampilkannya
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Mengirim prompt ke Gemini dan mendapatkan respons
    with st.spinner("Sedang mencari informasi..."):
        try:
            response = st.session_state.chat.send_message(prompt, request_options={"timeout": 60})
            if response and response.text:
                # Menambahkan respons Gemini ke riwayat
                st.session_state.messages.append({"role": "model", "parts": [response.text]})
                with st.chat_message("model"):
                    st.markdown(response.text)
            else:
                st.error("Maaf, terjadi kesalahan saat menerima respons.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
