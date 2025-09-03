import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL (PENTING! UBAH SESUAI KEBUTUHAN ANDA)
# ==============================================================================

# Ambil API Key dari Streamlit Secrets untuk keamanan
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key Gemini tidak ditemukan. Harap tambahkan 'GEMINI_API_KEY' ke Streamlit Secrets Anda.")
    st.stop()  # Menghentikan eksekusi jika API Key tidak ada

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash' 

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
# Ini adalah "instruksi sistem" yang akan membuat chatbot berperilaku sesuai keinginan Anda.
# Buatlah singkat, jelas, dan langsung pada intinya untuk menghemat token.
INITIAL_CHATBOT_CONTEXT = [
    {"role": "user", 
     "parts": ["Kamu adalah seorang apoteker. Tuliskan obat apa yang diinginkan untuk menyembuhkan penyakit Anda. Jawaban singkat dan faktual. Tolak pertanyaan non-apoteker."]
    },
    {"role": "model", 
     "parts": ["Baik! Sampaikan gejala atau penyakit yang Anda rasakan untuk saya bantu rekomendasikan obat."]
    }
]

# ==============================================================================
# FUNGSI UTAMA CHATBOT (HINDARI MENGUBAH BAGIAN INI JIKA TIDAK YAKIN)
# ==============================================================================

# Konfigurasi API
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Kesalahan saat mengkonfigurasi API Key: {e}")
    st.stop()

# Inisialisasi model
try:
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat inisialisasi model '{MODEL_NAME}': {e}")
    st.stop()

# ==============================================================================
# APLIKASI STREAMLIT
# ==============================================================================

st.set_page_config(page_title="Chatbot Apoteker 💊")

# Judul dan deskripsi aplikasi
st.title("👨‍⚕️ Chatbot Apoteker")
st.caption("🤖 Model Gemini akan merekomendasikan obat berdasarkan gejala yang Anda berikan. ")
st.divider()

# Inisialisasi riwayat chat di session state jika belum ada
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

# Tampilkan riwayat chat yang ada
for message in st.session_state.messages:
    # Hanya tampilkan pesan dari pengguna dan model, bukan instruksi sistem awal
    if message["role"] in ["user", "model"]:
        with st.chat_message(message["role"]):
            st.markdown(message["parts"][0])

# Terima input dari pengguna
user_input = st.chat_input("Tuliskan gejala atau pertanyaan Anda di sini...")

if user_input:
    # Tambahkan input pengguna ke riwayat chat
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Kirim riwayat chat lengkap ke model dan dapatkan respons
    try:
        # Kirim riwayat chat ke model
        response = model.generate_content(
            contents=st.session_state.messages,
            request_options={"timeout": 60}
        )
        
        # Tambahkan respons model ke riwayat chat
        full_response = response.text
        st.session_state.messages.append({"role": "model", "parts": [full_response]})
        with st.chat_message("model"):
            st.markdown(full_response)

    except Exception as e:
        st.error(f"Maaf, terjadi kesalahan: {e}")
        st.error("Kemungkinan penyebab: masalah koneksi, API key tidak valid, atau melebihi kuota.")
