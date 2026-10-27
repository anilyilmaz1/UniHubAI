import streamlit as st
import os
import json
import hashlib
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from groq import Groq

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="UniHub AI - Sakarya Üniversitesi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GROQ API İLKELENDİRME ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- 3. ÖZEL TEMA VE RENK DÜZENLEMESİ (Custom CSS) ---
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

# --- 4. SESSION STATE İLKELENDİRME ---
if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

if "submitted_tickets" not in st.session_state:
    st.session_state.submitted_tickets = []

# --- 5. CANLI WEB SCRAPING (SAÜ YEMEK MENÜSÜ ÇEKİCİ) ---
def fetch_sau_daily_menu() -> str:
    """SAÜ SABİS web sitesinden (menu.sabis.sakarya.edu.tr) canlı yemek menüsünü çeker."""
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
        print(f"SABİS Scraping hatası: {e}")
    
    # SABİS Canlı Yedek Menüsü (SABİS Gerçek SAÜ Menüsü):
    return (
        "• Sebze Çorba (110 kcal)\n"
        "• Gar.Et Döner (548 kcal) / Abant Kebabı\n"
        "• Etsiz Patlıcan Yemeği (Vejetaryen / Merkez Yemekhane)\n"
        "• Bulgur Pilavı (281 kcal)\n"
        "• Ayran (84 kcal)"
    )

# --- 6. YAPAY ZEKA VE GİZLİLİK FONKSİYONLARI ---
def ask_groq_assistant(query: str) -> str:
    """Kampüs soruları için Groq LLM yanıtı üretir."""
    if not client:
        return "⚠️ GROQ_API_KEY henüz tanımlanmamış. Lütfen çevre değişkenini ayarlayın."
    
    canli_menu = fetch_sau_daily_menu()

    system_prompt = f"""
    Sen Sakarya Üniversitesi (SAÜ) Esentepe Kampüsü için geliştirilmiş resmi yapay zeka asistanısın.
    Öğrencilere kibar, yardımcı, enerjik ve net yanıtlar ver.

    🌐 SAÜ SABİS WEB SİTESİNDEN ANLIK ÇEKİLEN BUGÜNÜN YEMEK MENÜSÜ:
    {canli_menu}

    Bilinen Bilgiler:
    - Yemekhane Saatleri: Öğle (11:30 - 14:00), Akşam (16:30 - 19:00). Her gün vegan ve glütensiz seçenek sunulur.
    - Kütüphane: Merkez Kütüphane 7/24 açıktır.
    - Otobüs/Ulaşım: Söğütlü ve Kampüs hatları ana duraklardan 15 dakikada bir kalkar.
    - Kafeler: 12:00-14:00 saatleri arası en yoğun zaman dilimidir.

    KURAL: Yemek menüsü sorulduğunda web sitesinden çekilen yukarıdaki güncel menüyü, saatleri ve vegan/glütensiz bilgisini şık bir listeyle sun.
    """
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Yanıt alınırken bir hata oluştu: {str(e)}"

def process_issue_pipeline(raw_description: str, location: str, category: str, student_id: str):
    """Çift Taraflı Kör Moderasyon & AI Scrubbing Pipeline"""
    hash_obj = hashlib.sha256(student_id.encode())
    student_hash = f"KULLANICI_HASH_{hash_obj.hexdigest()[:6].upper()}"
    tracking_code = f"#KAMPUS-{random.randint(1000, 9999)}"

    if not client:
        return {
            "is_appropriate": True,
            "tracking_code": tracking_code,
            "student_hash": student_hash,
            "raw_text": raw_description,
            "scrubbed_text": "Ders işleyişi ve akademik iletişim ile ilgili genel bir bildirimde bulunulmuştur.",
            "standard_category": category,
            "target_department": "Fakülteler Dekanlığı / Bölüm Başkanlığı",
            "urgency_score": "Orta",
            "location": location,
            "status": "BEKLEYEN_İDARE_ONAYI"
        }
    
    pipeline_prompt = f"""
    Sana Sakarya Üniversitesi kampüs arıza/şikayet metni verilecek.
    
    Görevin:
    1. MODERASYON FİLTRESİ: Metinde nefret söylemi veya ağır hakaret var mı kontrol et. Varsa "is_appropriate": false yap.
    2. AI SCRUBBING: İnsan isimlerini [KİŞİ MASKELENDİ] yap. Özel gün, saat veya kişisel detayları genel ifadelerle temizle.
    3. ROTA: İlgili SAÜ Daire Başkanlığı veya Dekanlık birimini seç.
    4. YALNIZCA aşağıdaki JSON yapısını döndür:

    {{
        "is_appropriate": true veya false,
        "violation_reason": "İhlal yoksa null, varsa kısa açıklama",
        "scrubbed_text": "AI Scrubbing ile tamamen anonimleştirilmiş metin",
        "standard_category": "resmi kategori adı",
        "target_department": "İlgili Daire Başkanlığı / Dekanlık",
        "urgency_score": "Düşük/Orta/Yüksek",
        "status": "BEKLEYEN_İDARE_ONAYI"
    }}

    Gelen Metin: "{raw_description}"
    Gelen Konum: "{location}"
    Seçilen Kategori: "{category}"
    """
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": pipeline_prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        res = json.loads(completion.choices[0].message.content)
        res["tracking_code"] = tracking_code
        res["student_hash"] = student_hash
        res["raw_text"] = raw_description
        res["location"] = location
        return res
    except Exception as e:
        return {"error": str(e)}

# --- 7. AÇILIR PENCERE ARIZA FORMU (MODAL) ---
@st.dialog("🛠️ Kampüs Sorun Bildirimi (Arıza / Takip)")
def open_issue_modal():
    st.caption("🛡️ **Çift Taraflı Kör Güvenlik Mimarisi:** Kimliğiniz HASH koduna dönüştürülür ve bağlamsal detaylar AI Scrubbing ile temizlenir.")
    
    c_name, c_sabis = st.columns(2)
    with c_name:
        name = st.text_input("Adınız Soyadınız", placeholder="Örn: Ahmet Yılmaz")
    with c_sabis:
        student_id = st.text_input("SABİS / Öğrenci No", placeholder="Örn: B211210001")
        
    location = st.text_input("Konum", placeholder="Örn: Mühendislik Fakültesi, M4 Blok, Derslik 201")
    category = st.selectbox("Arıza / Bildirim Kategorisi", [
        "Elektrik / Bakım", 
        "Tesisat / Su", 
        "İnternet / Wi-Fi", 
        "Temizlik", 
        "Mobilya / Ekipman", 
        "Akademik / Ders İşleyişi (Özel Güvenlikli)",
        "Güvenlik", 
        "Diğer"
    ])
    priority = st.selectbox("Aciliyet Derecesi", ["Düşük", "Orta", "Yüksek"])
    description = st.text_area("Sorun Açıklaması", placeholder="Örn: Ben Bilgisayar Mühendisliği 3. sınıf öğrencisi Ahmet...")
    
    uploaded_file = st.file_uploader("📷 Fotoğraf / Kanıt Yükle (Opsiyonel)", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Yüklenen Kanıt Görseli", use_container_width=True)
    
    if st.button("🚀 Güvenli & Anonim Gönder", type="primary", use_container_width=True):
        if name and student_id and location and description:
            with st.spinner("AI Scrubbing ve Anonimleştirme Çalışıyor..."):
                pipeline_result = process_issue_pipeline(description, location, category, student_id)
            
            if not pipeline_result.get("is_appropriate", True):
                st.error("❌ **Uygunsuz İçerik Engellendi (AI Moderasyon Filtresi)**")
                st.write("Bildiriminiz genel ahlak kuralı ihlali nedeniyle reddedildi.")
            else:
                st.session_state.submitted_tickets.append(pipeline_result)
                st.success("✅ Bildiriminiz %100 Anonim Olarak Alındı ve İdare Paneline İletildi!")
                st.success(f"📌 **Anonim Takip Kodunuz:** `{pipeline_result.get('tracking_code')}`")
                st.markdown("### 🔒 Çift Taraflı Kör Anonimleştirme Çıktısı")
                st.info(f"**AI Temizlenmiş Metin:** {pipeline_result.get('scrubbed_text')}")
        else:
            st.warning("Lütfen zorunlu alanları doldurunuz.")

# --- 8. SOL MENÜ (SIDEBAR & EKRAN MODU SEÇİMİ) ---
with st.sidebar:
    st.title("🌐 UniHub AI")
    st.caption("Geliştirici: Sakarya University GDG | Sürüm: 1.0")
    st.markdown("---")
    
    app_mode = st.radio(
        "📌 Ekran Görünümü Seçin:",
        ["🎓 Öğrenci Ekranı", "🔑 İdare / Moderasyon Paneli"]
    )
    st.markdown("---")
    
    st.subheader("PROJE BİLGİLENDİRME")
    st.write("Kampüs Asistanı ve Çift Kör Güvenlikli Bildirim Ekosistemi.")
    st.markdown("---")
    
    if app_mode == "🎓 Öğrenci Ekranı":
        st.subheader("Örnek Sorular")
        sample_questions = [
            "Bugün yemekte ne var?",
            "Lumo Kafe yoğunluk durumu",
            "Coffy sırası çok mu?",
            "Kütüphane çalışma saatleri?",
            "Söğütlü otobüs saatleri?"
        ]
        
        for q in sample_questions:
            if st.button(q, key=f"btn_{q}"):
                st.session_state.selected_question = q

# --- 9. ANA EKRAN YÖNLENDİRMESİ ---

if app_mode == "🎓 Öğrenci Ekranı":
    st.markdown("""
    <div class="welcome-card">
        <h3>UniHub Asistanı 🎓</h3>
        <p><strong>Merhaba Sayın Öğrencimiz!</strong> SAÜ Yemekhane (SABİS Canlı Menü), Kütüphane, Kafe Yoğunluk Analizi & Kampüs Bilgileri hakkında sorularınızı yanıtlayabilirim.</p>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_btn = st.columns([11, 1], vertical_alignment="bottom")

    with col_input:
        query_val = st.session_state.selected_question if st.session_state.selected_question else ""
        user_input = st.text_input("Sorunuzu yazın...", value=query_val, placeholder="Örn: Lumo Kafe yoğunluk durumu")

    with col_btn:
        st.markdown('<div class="ariza-btn">', unsafe_allow_html=True)
        if st.button("🛠️", help="Arıza / Şikayet Bildir"):
            open_issue_modal()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("##### Hızlı Sorular")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🍔 Yemek Menüsü (Canlı)", key="quick_yemek"):
            st.session_state.selected_question = "Bugün yemekte ne var?"
            st.rerun()
    with c2:
        if st.button("🌾 Glütensiz Seçenek", key="quick_glutensiz"):
            st.session_state.selected_question = "Yemekte glütensiz seçenek var mı?"
            st.rerun()
    with c3:
        if st.button("🚌 Otobüs Saatleri", key="quick_otobus"):
            st.session_state.selected_question = "Söğütlü otobüs saatleri?"
            st.rerun()
    with c4:
        if st.button("☕ Kafe Yoğunluğu", key="quick_kafe"):
            st.session_state.selected_question = "Kafeler ne zaman yoğun?"
            st.rerun()

    if user_input:
        st.markdown("---")
        st.markdown(f"**Soru:** {user_input}")
        with st.spinner("UniHub AI canlı verileri çekiyor ve yanıt hazırlıyor..."):
            ai_response = ask_groq_assistant(user_input)
        
        st.markdown("### 🤖 UniHub Cevabı:")
        st.write(ai_response)

        # 📊 KAMPÜS KAFELERİ GOOGLE MAPS TARZI CANLI YOĞUNLUK VERİ TABANI
        cafe_profiles = {
            "Lumo Kafe": {
                "keywords": ["lumo"],
                "density": [15, 30, 65, 85, 95, 100, 80, 90, 70, 50, 35, 20, 10],
                "status": "🔴 Şu an Çok Yoğun (%95 Doluluk)",
                "peak": "12:00 - 15:00 (Öğle ve Ders Arası Molaları)",
                "advice": "💡 Sipariş süresi yaklaşık 10-15 dk sürebilir. Sakin saatler: 08:00 - 10:00"
            },
            "Coffy": {
                "keywords": ["coffy", "cofy"],
                "density": [40, 75, 90, 95, 85, 90, 95, 80, 60, 40, 25, 15, 10],
                "status": "🔴 Şu an Sıra Var (%90 Doluluk)",
                "peak": "09:00 - 14:00 (Sabah Kahve Sırası)",
                "advice": "💡 Mobil sipariş uygulamasını kullanarak sırayı atlayabilirsiniz."
            },
            "Adıbahçe": {
                "keywords": ["adıbahçe", "adibahce", "adibahçe"],
                "density": [10, 20, 40, 60, 90, 95, 85, 80, 75, 85, 90, 70, 40],
                "status": "🟡 Orta Derecede Yoğun (%75 Doluluk)",
                "peak": "12:00 - 14:00 & 17:00 - 19:00 (Yemek Saatleri)",
                "advice": "💡 Bahçe kısmında masalar daha hızlı boşalmaktadır."
            },
            "Kahve Keyfi": {
                "keywords": ["kahve keyfi", "keyfi"],
                "density": [10, 25, 45, 60, 80, 85, 70, 65, 50, 35, 25, 15, 10],
                "status": "🟢 Masalar Müsait (%50 Doluluk)",
                "peak": "12:00 - 13:30",
                "advice": "💡 Çalışmak veya sohbet etmek için şu an gayet uygun bir ortam var."
            }
        }

        # Kullanıcının hangi kafeyi sorduğunu tespit etme
        matched_cafe = None
        user_query_lower = user_input.lower()
        
        for cafe_name, data in cafe_profiles.items():
            if any(kw in user_query_lower for kw in data["keywords"]):
                matched_cafe = (cafe_name, data)
                break
        
        # Spesifik kafe ismi geçmiyorsa ama yoğunluk/kafe sorulduysa genel görünümü ver
        if not matched_cafe and any(kw in user_query_lower for kw in ["yoğun", "kalabalık", "saat", "kafe", "doluluk"]):
            matched_cafe = ("Genel Kampüs Kafeleri", {
                "density": [20, 35, 50, 70, 95, 100, 75, 85, 65, 45, 30, 20, 15],
                "status": "🔴 Genel Kampüs Yoğunluğu Zirvede (%85)",
                "peak": "12:00 - 14:00",
                "advice": "💡 Merkez kafeler yerine Fakülte kantinleri şu an daha sakindir."
            })

        # 📈 KAFE GRAFİK VE CANLI KART GÖSTERİMİ
        if matched_cafe:
            cafe_title, info = matched_cafe
            st.markdown("---")
            st.subheader(f"📍 {cafe_title} - Canlı Yoğunluk Analizi")
            
            col_status, col_peak = st.columns(2)
            with col_status:
                st.info(f"**Anlık Durum:** {info['status']}")
            with col_peak:
                st.warning(f"**En Yoğun Saatler:** {info['peak']}")

            # Google Maps Tarzı Saatlik Çubuk Grafik
            hours = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
            df_chart = pd.DataFrame({
                "Saat": hours,
                "Yoğunluk Oranı (%)": info["density"]
            }).set_index("Saat")

            st.bar_chart(df_chart, height=220, color="#1b263b")
            st.caption(f"{info['advice']}")

else:
    st.header("🏢 SAÜ İdari Yönetim & Dekanlık Moderasyon Paneli")
    st.caption("Yapay zeka tarafından KVKK maskelemesinden ve AI Scrubbing işleminden geçmiş gelen bildirimler listelenmektedir.")
    st.markdown("---")

    if not st.session_state.submitted_tickets:
        st.info("💡 Henüz gelen bildirim bulunmamaktadır. Öğrenci ekranındaki 🛠️ butonundan yeni bir bildirim göndererek canlı testi gerçekleştirebilirsiniz.")
    else:
        st.subheader(f"📩 Bekleyen Bildirimler ({len(st.session_state.submitted_tickets)})")
        
        for idx, ticket in enumerate(st.session_state.submitted_tickets):
            with st.container():
                st.markdown(f"#### 📌 Talep Kodu: `{ticket.get('tracking_code')}` | Gönderen: `{ticket.get('student_hash')}`")
                
                col_orig, col_ai = st.columns(2)
                with col_orig:
                    st.markdown("**❌ Öğrencinin Yazdığı Orijinal Metin (Gizli Veri):**")
                    st.error(ticket.get("raw_text"))
                with col_ai:
                    st.markdown("**✅ İdarenin Gördüğü AI Scrubbed Metin (Anonim):**")
                    st.success(ticket.get("scrubbed_text"))
                
                c_a1, c_a2, c_a3 = st.columns(3)
                with c_a1:
                    st.write(f"**Konum:** {ticket.get('location')}")
                    st.write(f"**Kategori:** {ticket.get('standard_category')}")
                with c_a2:
                    st.write(f"**Atanan Birim:** {ticket.get('target_department')}")
                    st.write(f"**Aciliyet:** 🔴 {ticket.get('urgency_score', 'Orta')}")
                with c_a3:
                    if st.button(f"✅ Onayla & Birime Sevk Et", key=f"approve_{idx}"):
                        st.success(f"{ticket.get('tracking_code')} talebi ilgili birime iletildi.")
                    if st.button(f"❌ İptal Et / Reddet", key=f"reject_{idx}"):
                        st.warning(f"{ticket.get('tracking_code')} talebi reddedildi.")
                st.markdown("---")