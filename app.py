import streamlit as st

# 1. Sayfa Yapısı
st.set_page_config(
    page_title="UniHub AI - Sakarya Üniversitesi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Tema ve Renk Düzenlemesi
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
    
    /* Genel Buton Stilleri */
    div.stButton > button {
        border-radius: 8px;
    }
    
    /* Sol Menü Örnek Soru Butonları */
    [data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        background-color: #1b263b;
        color: #e0e1dd !important;
        border: 1px solid #415a77;
        text-align: left;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #415a77;
        color: #ffffff !important;
    }

    /* Karşılama Kartı Stili */
    .welcome-card {
        background-color: #eef4fb;
        border-left: 5px solid #1b263b;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #0d1b2a;
    }

    /* YUVARLAK ARIZA BİLDİRİM BUTONU STİLİ */
    .ariza-btn button {
        border-radius: 50% !important;
        width: 46px !important;
        height: 46px !important;
        font-size: 20px !important;
        padding: 0px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #e63946 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
    }
    .ariza-btn button:hover {
        background-color: #d62828 !important;
        transform: scale(1.08);
    }
</style>
""", unsafe_allow_html=True)

# 3. Session State
if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

# 4. Açılır Pencere Arıza Formu
@st.dialog("🛠️ Kampüs Sorun Bildirimi (Arıza / Takip)")
def open_issue_modal():
    st.caption("Kampüsteki arıza ve taleplerinizi bu form aracılığıyla doğrudan iletebilirsiniz.")
    
    name = st.text_input("Adınız Soyadınız", placeholder="Örn: Anıl Yılmaz")
    location = st.text_input("Konum", placeholder="Örn: Mühendislik Fakültesi, M4 Blok, Derslik 201")
    category = st.selectbox("Arıza Kategorisi", [
        "Elektrik / Bakım", 
        "Tesisat / Su", 
        "İnternet / Wi-Fi", 
        "Temizlik", 
        "Mobilya / Ekipman", 
        "Güvenlik", 
        "Diğer"
    ])
    priority = st.selectbox("Aciliyet Derecesi", ["Düşük", "Orta", "Yüksek"])
    description = st.text_area("Sorun Açıklaması", placeholder="Lütfen sorunu detaylı bir şekilde tarif ediniz...")
    
    if st.button("🚀 Başvuruyu Gönder", type="primary", use_container_width=True):
        if name and location and description:
            st.success("✅ Bildiriminiz başarıyla iletildi! Yapay zeka sistemimiz ilgili birime yönlendirme yaptı.")
        else:
            st.warning("Lütfen zorunlu alanları doldurunuz.")

# 5. Sidebar
with st.sidebar:
    st.title("🌐 UniHub AI")
    st.caption("Geliştirici: Sakarya University GDG | Sürüm: 1.0")
    st.markdown("---")
    
    st.subheader("PROJE BİLGİLENDİRME")
    st.write("Kampüs Asistanı (Soru - Cevap ve Arıza Bildirimi) projesidir.")
    st.markdown("---")
    
    st.subheader("Örnek Sorular")
    sample_questions = [
        "Bugün yemekte ne var?",
        "Yemekte glütensiz seçenek var mi?",
        "Kütüphane çalışma saatleri?",
        "Kafeler ne zaman yoğun?",
        "Söğüttü otobüs saatleri?"
    ]
    
    for q in sample_questions:
        if st.button(q, key=f"btn_{q}"):
            st.session_state.selected_question = q

# 6. Ana Ekran
st.markdown("""
<div class="welcome-card">
    <h3>UniHub Asistanı 🎓</h3>
    <p><strong>Merhaba Sayın Öğrencimiz!</strong> Sakarya Üniversitesi Kafeler, Yemekhane, Öğrenci İşleri & Çalışma Saatleri hakkında sorularınızı yanıtlayabilirim.</p>
</div>
""", unsafe_allow_html=True)

# Girdi Kutusu ve Yanındaki Yuvarlak Arıza Butonu
col_input, col_btn = st.columns([11, 1], vertical_alignment="bottom")

with col_input:
    query_val = st.session_state.selected_question if st.session_state.selected_question else ""
    user_input = st.text_input("Sorunuzu yazın...", value=query_val, placeholder="Örn: Bugün yemekte ne var?")

with col_btn:
    st.markdown('<div class="ariza-btn">', unsafe_allow_html=True)
    if st.button("🛠️", help="Arıza / Şikayet Bildir"):
        open_issue_modal()
    st.markdown('</div>', unsafe_allow_html=True)

# Hızlı Erişim Butonları
st.markdown("##### Hızlı Sorular")
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🍔 Yemek Menüsü (Bugün)", key="quick_yemek"):
        st.session_state.selected_question = "Bugün yemekte ne var?"
        st.rerun()
with c2:
    if st.button("🌾 Glütensiz Seçenek", key="quick_glutensiz"):
        st.session_state.selected_question = "Yemekte glütensiz seçenek var mı?"
        st.rerun()
with c3:
    if st.button("🚌 Otobüs Saatleri", key="quick_otobus"):
        st.session_state.selected_question = "Söğüttü otobüs saatleri?"
        st.rerun()
with c4:
    if st.button("📚 Kütüphane Saatleri", key="quick_kutup"):
        st.session_state.selected_question = "Kütüphane çalışma saatleri?"
        st.rerun()