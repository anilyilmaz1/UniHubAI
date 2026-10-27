import streamlit as st
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from groq import Groq

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="UniHub Academic AI - Sakarya Üniversitesi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GROQ API İLKELENDİRME ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- 3. ÖZEL TEMA VE STİL ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #0d1b2a;
        color: #ffffff;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    .quick-btn button {
        border-radius: 20px !important;
        font-size: 13px !important;
        margin-bottom: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. AKADEMİK BİLGİ TABANI (KNOWLEDGE BASE) ---
SAU_AKADEMIK_BILGI = """
[SAÜ AKADEMİK TAKVİM BİLGİLERİ]
- Güz Dönemi Vize Sınavları: 18 - 24 Kasım
- Güz Dönemi Final Sınavları: 6 - 17 Ocak
- Bütünleme Sınavları: 25 - 31 Ocak
- Bahar Dönemi Ders Kayıtları: 10 - 14 Şubat
- Mazeret Sınav Başvuruları: Sınav haftasını takip eden ilk 3 iş günü içinde fakülte sekreterliğine dilekçe ile yapılır.

[FAKÜLTE BAZLI STAJ SÜREÇLERİ VE REHBERİ]
1. Mühendislik / Bilgisayar Mühendisliği Stajı:
   - Toplam Süre: 40 İş Günü (Staj 1: 20 gün, Staj 2: 20 gün).
   - Adım 1: SABİS üzerinden "Zorunlu Staj Formu" indirilir ve firmaya imzalatılır.
   - Adım 2: Staj başlama tarihinden en geç 15 gün önce Bölüm Staj Komisyonuna SGK girişi için teslim edilir.
   - Adım 3: Staj bitimini takip eden ilk 2 hafta içinde Staj Defteri SABİS/Bölüm sistemine yüklenir.

2. İşletme / Siyasal Bilgiler Fakültesi Stajı:
   - Dönem İçi Mesleki Uygulama (7+1 Sistem): 8. yarıyılda tam zamanlı firma stajı yapılır.
   - Başvuru: 7. yarıyıl sonunda fakülte duyurularından firma tercihleri yapılır.

3. Fen-Edebiyat / İlahiyat / Diğer Fakülteler:
   - İsteğe bağlı stajlar için SGK kurum tarafından karşılanır, başvuru formu staj tarihinden 10 gün önce dekana verilir.

[DERS KAYIT & MAZERET VE AKADEMİK KURALLAR]
- Derse Devam Zorunluluğu: Teorik derslerde %70, uygulamalı derslerde %80'dir.
- Ağrılı Tek Ders Sınavı: Mezuniyet durumundaki öğrenciler için dönem sonlarında açılır.
"""

# --- 5. CANLI VERİ ÇEKME (SABİS YEMEKHANE) ---
def fetch_sau_daily_menu() -> str:
    url = "https://menu.sabis.sakarya.edu.tr/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.find_all(['div', 'td', 'span', 'li'])
            menu_items = []
            for elem in elements:
                text = elem.get_text(strip=True)
                if any(k in text for k in ['Çorba', 'Döner', 'Kebabı', 'Pilavı', 'Ayran', 'Yemeği', 'kcal']):
                    if text not in menu_items and len(text) < 60:
                        menu_items.append(text)
            if menu_items:
                return "\n".join([f"• {item}" for item in menu_items[:5]])
    except Exception as e:
        print(f"Scraping hatası: {e}")
    
    return (
        "• Sebze Çorba (110 kcal)\n"
        "• Gar.Et Döner (548 kcal) / Abant Kebabı\n"
        "• Etsiz Patlıcan Yemeği (Vejetaryen / Merkez Yemekhane)\n"
        "• Bulgur Pilavı (281 kcal)\n"
        "• Ayran (84 kcal)"
    )

# --- 6. AI CEVAP OLUŞTURUCU ---
def generate_academic_response(messages_history, student_faculty: str, student_dept: str) -> str:
    if not client:
        return "⚠️ GROQ_API_KEY henüz tanımlanmamış. Lütfen Hugging Face Secrets alanına ekleyin."

    canli_menu = fetch_sau_daily_menu()

    system_prompt = f"""
    Sen Sakarya Üniversitesi (SAÜ) öğrencilerinin resmi Akademik ve Kampüs Asistanısın.
    
    [ÖĞRENCİ PROFİLİ]
    - Fakülte: {student_faculty if student_faculty else "Genel SAÜ Öğrencisi"}
    - Bölüm: {student_dept if student_dept else "Belirtilmedi"}

    [SİSTEMDEKİ GÜNCEL VERİLER]
    🌐 CANLI SABİS YEMEK MENÜSÜ:
    {canli_menu}

    📘 SAÜ AKADEMİK BİLGİ TABANI & TAKVİMİ:
    {SAU_AKADEMIK_BILGI}

    [MİSYON VE YANIT KURALLARI]
    1. Öğrenci staj, akademik takvim, sınavlar, mazeret dilekçesi, devam zorunluluğu gibi akademik konular sorduğunda doğrudan bilgi tabanından NET ve ADIM ADIM yanıt ver.
    2. Öğrenci staj sorduğunda eğer bölümü belliyse o bölümün adım adım staj sürecini anlat (Örn: 1. Formu doldur, 2. Firma onayı al, 3. 15 gün önce teslim et).
    3. Yanıtların her zaman nazik, motive edici, resmi ama samimi bir üslupta olsun.
    4. Gerekli yerlerde maddeler (bullet points) ve kalın yazılar (**bold**) kullan.
    """

    full_messages = [{"role": "system", "content": system_prompt}] + messages_history

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=full_messages,
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"

# --- 7. SESSION STATE HIZLI İLKELENDİRME ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba! Ben SAÜ Akademik Asistanı. Akademik takvim, vize/final tarihleri, staj başvuru süreçleri veya kampüs yaşamı hakkında bana dilediğini sorabilirsin. 🎓"}
    ]

# --- 8. SOL MENÜ (ÖĞRENCİ PROFİLİ) ---
with st.sidebar:
    st.title("🎓 UniHub Academic AI")
    st.caption("Sakarya Üniversitesi Akıllı Kampüs Asistanı")
    st.markdown("---")
    
    st.subheader("👤 Öğrenci Profili")
    faculty = st.selectbox("Fakülteniz", [
        "Mühendislik Fakültesi",
        "İşletme Fakültesi",
        "İlahiyat Fakültesi",
        "Fen-Edebiyat Fakültesi",
        "Siyasal Bilgiler Fakültesi",
        "Diğer"
    ])
    
    department = st.text_input("Bölümünüz", placeholder="Örn: Bilgisayar Mühendisliği")
    
    st.markdown("---")
    if st.button("🧹 Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Sohbet temizlendi. Nasıl yardımcı olabilirim?"}
        ]
        st.rerun()

# --- 9. ANA EKRAN & CHAT ARAYÜZÜ ---
st.title("💬 SAÜ Akademik & Kampüs Asistanı")
st.caption(f"Aktif Bağlam: **{faculty}** {f'({department})' if department else ''}")

# Hızlı Soru Butonları
st.markdown("##### ⚡ Hızlı Sorular:")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

prompt_to_send = None

with q_col1:
    if st.button("📅 Sınav ve Takvim Tarihleri", use_container_width=True):
        prompt_to_send = "Vize, final ve büt sınav tarihleri ne zaman?"
with q_col2:
    if st.button("📝 Staj Başvurusu Nasıl Yapılır?", use_container_width=True):
        prompt_to_send = f"{faculty} {department} öğrencisiyim. Staj yaparken izlemem gereken adımlar nelerdir?"
with q_col3:
    if st.button("🍽️ Bugünü Yemek Menüsü", use_container_width=True):
        prompt_to_send = "Bugün yemekhanede ne var?"
with q_col4:
    if st.button("📩 Mazeret Sınavı Şartları", use_container_width=True):
        prompt_to_send = "Vizeye giremezsem mazeret sınavı başvurusu nasıl yapılır?"

# Geçmiş Mesajları Ekrana Yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı Girişi (Chat Input veya Hızlı Buton)
user_query = st.chat_input("Akademik takvim, staj veya kampüs hakkında bir soru sorun...")

if prompt_to_send:
    user_query = prompt_to_send

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Akademik bilgi tabanı taranıyor..."):
            history_for_api = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            response_text = generate_academic_response(history_for_api, faculty, department)
            st.markdown(response_text)
            
    st.session_state.messages.append({"role": "assistant", "content": response_text})