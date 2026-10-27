import os
import streamlit as st
from dotenv import load_dotenv

# .env dosyasındaki API key'leri yükler
load_dotenv()

# Sayfa Ayarları
st.set_page_config(page_title="Hackathon Projesi", page_icon="🚀", layout="wide")

st.title("🚀 Hackathon Proje Başlığı")
st.write("Yarınki proje için hazır Streamlit şablonu.")

# Yan Menü (Sidebar)
st.sidebar.header("Ayarlar")
st.sidebar.info("API Key veya parametreleri buradan yönetebilirsin.")

# Basit Sohbet Arayüzü
user_input = st.chat_input("Bir şeyler yazın...")
if user_input:
    st.write(f"**Gelen Mesaj:** {user_input}")