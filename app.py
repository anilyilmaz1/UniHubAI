import streamlit as st
import os

# 1. Sayfa Yapısı
st.set_page_config(
    page_title="UniHub AI - Sakarya Üniversitesi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Tema ve Renk
st.markdown("""
<style>
    /* Sol Menü (Sidebar) Lacivert Tema */
    [data-testid="stSidebar"] {
        background-color: #0d1b2a;
        color: #ffffff;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Örnek Soru Buton Stilleri */
    div.stButton > button {
        width: 100%;
        background-color: #1b263b;
        color: #e0e1dd !important;
        border: 1px solid #415a77;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: left;
    }
    div.stButton > button:hover {
        background-color: #415a77;
        color: #ffffff !important;
        border-color: #778da9;
    }
</style>
""", unsafe_allow_html=True)

# 3. Session State
if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

# 4. Sidebar
with st.sidebar:
    st.title("🌐 UniHub AI")
    st.caption("Geliştirici: Senanur ADIGÜZEL - Anıl YILMAZ | Sürüm: 1.0")
    st.markdown("---")
    
    st.subheader("PROJE BİLGİLENDİRME")
    st.write("Proje Bilgilendirme: Kampüs Asistanı (Soru - Cevap ve Arıza Bildirimi) projesidir.")
    st.markdown("---")
    
    st.subheader("Örnek Sorular")
    
    sample_questions = [
        "Bugün yemekte ne var?",
        "Yemekte glütensiz seçenek var mi?",
        "Kütüphane çalışma saatleri?",
        "Kafeler ne zaman yoğun?"
    ]
    
    for q in sample_questions:
        if st.button(q, key=f"btn_{q}"):
            st.session_state.selected_question = q
            
    st.markdown("---")
    st.info("🛠️ Arıza/Takip sekmesi sağ alandaki üst sekmelerde yer almaktadır.")