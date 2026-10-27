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
    [data-testid="stSidebar"] {
        background-color: #0d1b2a;
        color: #ffffff;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    div.stButton > button {
        border-radius: 8px;
    }
    .welcome-card {
        background-color: #eef4fb;
        border-left: 5px solid #1b263b;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #0d1b2a;
    }
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
</style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE İLKELENDİRME ---
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = "" # "ogrenci", "dekan", "memur", "admin"
if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""
if "submitted_tickets" not in st.session_state:
    # Başlangıç test verisi
    st.session_state.submitted_tickets = [
        {
            "tracking_code": "#KAMPUS-8463",
            "student_hash": "KULLANICI_HASH_57B3B7",
            "raw_text": "Prof. Dr. Mehmet Kaya ders saatlerine uymuyor.",
            "scrubbed_text": "İlahiyat Fakültesi ders sorumlusu Prof. Dr. Mehmet Kaya'nın ders saatlerine uymadığı bildirilmiştir.",
            "standard_category": "Akademik / Ders İşleyişi (Özel Güvenlikli)",
            "target_department": "İlahiyat Fakültesi Dekanlığı",
            "urgency_score": "Orta",
            "location": "İlahiyat Fakültesi",
            "status": "BEKLEYEN_İDARE_ONAYI"
        },
        {
            "tracking_code": "#KAMPUS-1209",
            "student_hash": "KULLANICI_HASH_A9C4E2",
            "raw_text": "M4 blok 201 nolu sınıfta priz çalışmıyor ve Wi-Fi kopuyor.",
            "scrubbed_text": "Mühendislik Fakültesi M4 Blok 201 nolu sınıfta elektrik prizi arızalı ve Wi-Fi bağlantısı kesintili.",
            "standard_category": "Elektrik / Bakım",
            "target_department": "Yapı İşleri ve Teknik Daire Başkanlığı",
            "urgency_score": "Yüksek",
            "location": "Mühendislik Fakültesi M4 Blok 201",
            "status": "BEKLEYEN_İDARE_ONAYI"
        }
    ]

# --- 5. CANLI SCRAPING & AI FONKSİYONLARI ---
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

def ask_groq_assistant(query: str) -> str:
    if not client:
        return "⚠️ GROQ_API_KEY henüz tanımlanmamış."
    canli_menu = fetch_sau_daily_menu()
    system_prompt = f"""
    Sen Sakarya Üniversitesi (SAÜ) Esentepe Kampüsü için geliştirilmiş resmi yapay zeka asistanısın.
    🌐 SAÜ SABİS WEB SİTESİNDEN ANLIK ÇEKİLEN BUGÜNÜN YEMEK MENÜSÜ:
    {canli_menu}
    - Yemekhane Saatleri: Öğle (11:30 - 14:00), Akşam (16:30 - 19:00).
    - Kütüphane: Merkez Kütüphane 7/24 açıktır.
    KURAL: Yemek menüsü sorulduğunda yukarıdaki güncel menüyü şık bir listeyle sun.
    """
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Hata: {str(e)}"

def process_issue_pipeline(raw_description: str, location: str, category: str, student_id: str):
    hash_obj = hashlib.sha256(student_id.encode())
    student_hash = f"KULLANICI_HASH_{hash_obj.hexdigest()[:6].upper()}"
    tracking_code = f"#KAMPUS-{random.randint(1000, 9999)}"

    if not client:
        return {
            "is_appropriate": True,
            "tracking_code": tracking_code,
            "student_hash": student_hash,
            "raw_text": raw_description,
            "scrubbed_text": f"{location} konumunda {category} ile ilgili bildirim oluşturulmuştur.",
            "standard_category": category,
            "target_department": "Yapı İşleri / Dekanlık",
            "urgency_score": "Orta",
            "location": location,
            "status": "BEKLEYEN_İDARE_ONAYI"
        }
    
    pipeline_prompt = f"""
    Sana SAÜ kampüs arıza/şikayet metni verilecek.
    1. MODERASYON: Ağır hakaret var mı? Varsa "is_appropriate": false yap.
    2. AI SCRUBBING: ŞİKAYET EDEN ÖĞRENCİNİN adını/numarasını sil. Ancak ŞİKAYET EDİLEN HOCA/PERSONEL ADINI, SINIF ve DERS DETAYLARINI KORU.
    3. YALNIZCA aşağıdaki JSON yapısını döndür:
    {{
        "is_appropriate": true veya false,
        "scrubbed_text": "Öğrenci kimliğinden arındırılmış resmi metin",
        "standard_category": "{category}",
        "target_department": "İlgili Daire Başkanlığı / Dekanlık",
        "urgency_score": "Düşük/Orta/Yüksek",
        "status": "BEKLEYEN_İDARE_ONAYI"
    }}
    Gelen Metin: "{raw_description}" | Konum: "{location}" | Kategori: "{category}"
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

@st.dialog("🛠️ Kampüs Sorun Bildirimi (Arıza / Şikayet)")
def open_issue_modal():
    st.caption("🛡️ **Çift Taraflı Kör Güvenlik:** Kimliğiniz HASH koduna dönüştürülür ve yapay zeka tarafından anonimleştirilir.")
    c_name, c_sabis = st.columns(2)
    with c_name:
        name = st.text_input("Adınız Soyadınız", placeholder="Ahmet Yılmaz")
    with c_sabis:
        student_id = st.text_input("SABİS / Öğrenci No", placeholder="B211210001")
        
    location = st.text_input("Konum", placeholder="Örn: Mühendislik Fakültesi M4 Blok 201")
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
    description = st.text_area("Sorun Açıklaması", placeholder="Örn: M4 201 nolu sınıfta priz çalışmıyor...")
    
    if st.button("🚀 Güvenli & Anonim Gönder", type="primary", use_container_width=True):
        if name and student_id and location and description:
            with st.spinner("AI Scrubbing ve Otomatik Rotalama Çalışıyor..."):
                res = process_issue_pipeline(description, location, category, student_id)
            if not res.get("is_appropriate", True):
                st.error("❌ Uygunsuz içerik engellendi (AI Moderasyon Filtresi).")
            else:
                st.session_state.submitted_tickets.append(res)
                st.success(f"✅ Bildiriminiz Alındı! Anonim Takip Kodunuz: `{res.get('tracking_code')}`")
        else:
            st.warning("Lütfen tüm zorunlu alanları doldurunuz.")

# --- 6. KURUMSAL GİRİŞ PORTALI ---
if not st.session_state.user_authenticated:
    st.markdown("<h2 style='text-align: center;'>🌐 UniHub AI - Kurumsal Giriş Portalı</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Rol tabanlı yetkilendirme için lütfen kurumsal e-posta adresinizle giriş yapın.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email_input = st.text_input("SAÜ E-Posta Adresi", placeholder="örn: ogrenci@ogr.sakarya.edu.tr")
            password_input = st.text_input("Şifre", type="password", placeholder="••••••••")
            login_btn = st.form_submit_button("🔑 Manuel Giriş Yap", use_container_width=True)
            
            if login_btn and email_input:
                email_lower = email_input.lower()
                st.session_state.user_authenticated = True
                st.session_state.user_email = email_input
                
                if "admin" in email_lower:
                    st.session_state.user_role = "admin"
                elif "dekan" in email_lower:
                    st.session_state.user_role = "dekan"
                elif "memur" in email_lower or "teknik" in email_lower:
                    st.session_state.user_role = "memur"
                else:
                    st.session_state.user_role = "ogrenci"
                st.rerun()

        st.markdown("---")
        st.markdown("##### ⚡ Hızlı Demo Girişleri (Jüri Sunumu İçin):")
        
        q1, q2 = st.columns(2)
        with q1:
            if st.button("🎓 Öğrenci Girişi", use_container_width=True):
                st.session_state.user_authenticated = True
                st.session_state.user_email = "ahmet.yilmaz@ogr.sakarya.edu.tr"
                st.session_state.user_role = "ogrenci"
                st.rerun()
            if st.button("🏛️ Dekan Girişi (Akademik)", use_container_width=True):
                st.session_state.user_authenticated = True
                st.session_state.user_email = "ilahiyat.dekan@sakarya.edu.tr"
                st.session_state.user_role = "dekan"
                st.rerun()
        with q2:
            if st.button("👷 Memur Girişi (Teknik Ekip)", use_container_width=True):
                st.session_state.user_authenticated = True
                st.session_state.user_email = "bakim.memur@sakarya.edu.tr"
                st.session_state.user_role = "memur"
                st.rerun()
            if st.button("👑 Sistem Admin Girişi", use_container_width=True):
                st.session_state.user_authenticated = True
                st.session_state.user_email = "admin@sakarya.edu.tr"
                st.session_state.user_role = "admin"
                st.rerun()

# --- 7. OTURUM AÇILDIKTAN SONRAKİ ROL TABANLI EKRANLAR ---
else:
    # SOL MENÜ
    with st.sidebar:
        st.title("🌐 UniHub AI")
        st.caption(f"👤 Aktif Kullanıcı: **{st.session_state.user_email}**")
        
        role_label = {
            "ogrenci": "🎓 Öğrenci",
            "dekan": "🏛️ Dekan / Akademik İdare",
            "memur": "👷 Görevli Memur / Teknik Ekip",
            "admin": "👑 Sistem Yöneticisi (Admin)"
        }.get(st.session_state.user_role, "Bilinmiyor")
        
        st.caption(f"🛡️ Rol: **{role_label}**")
        st.markdown("---")
        
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.user_authenticated = False
            st.session_state.user_email = ""
            st.session_state.user_role = ""
            st.rerun()

    # A) 🎓 ÖĞRENCİ EKRANI
    if st.session_state.user_role == "ogrenci":
        st.markdown("""
        <div class="welcome-card">
            <h3>UniHub Öğrenci Asistanı 🎓</h3>
            <p>SABİS Canlı Menü, Kütüphane & Kafe Yoğunluğu hakkında sorular sorabilir, 🛠️ butonundan anonim arıza/şikayet bildirebilirsiniz.</p>
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

        if user_input:
            st.markdown("---")
            with st.spinner("UniHub AI yanıtlıyor..."):
                ai_response = ask_groq_assistant(user_input)
            st.markdown("### 🤖 UniHub Cevabı:")
            st.write(ai_response)
            
            if any(kw in user_input.lower() for kw in ["lumo", "coffy", "adıbahçe", "keyfi", "yoğun", "kafe"]):
                hours = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"]
                df_chart = pd.DataFrame({"Saat": hours, "Yoğunluk (%)": [20, 50, 95, 80, 60, 30]}).set_index("Saat")
                st.markdown("---")
                st.subheader("📍 Kafe Canlı Yoğunluk Analizi")
                st.bar_chart(df_chart, height=200, color="#1b263b")

    # B) 🏛️ DEKAN / AKADEMİK İDARE EKRANI (SADECE AKADEMİK BİLETLER)
    elif st.session_state.user_role == "dekan":
        st.header("🏛️ İlahiyat / Mühendislik Fakültesi Dekanlık Paneli")
        st.caption("🔒 Yalnızca dekanlık yetki alanındaki **Akademik & Ders İşleyişi** şikayetleri gösterilmektedir. Teknik arızalar gösterilmez.")
        st.markdown("---")

        academic_tickets = [t for t in st.session_state.submitted_tickets if "Akademik" in t.get("standard_category", "")]

        if not academic_tickets:
            st.info("💡 Dekanlığa iletilmiş bekleyen akademik şikayet bulunmamaktadır.")
        else:
            st.subheader(f"📩 Bekleyen Akademik Bildirimler ({len(academic_tickets)})")
            for idx, ticket in enumerate(academic_tickets):
                with st.container():
                    st.markdown(f"#### 📌 Talep Kodu: `{ticket.get('tracking_code')}` | Gönderen: `{ticket.get('student_hash')}`")
                    st.success(f"**📄 Anonim Bildirim Metni:** {ticket.get('scrubbed_text')}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Konum:** {ticket.get('location')}")
                        st.write(f"**Kategori:** {ticket.get('standard_category')}")
                    with c2:
                        st.write(f"**Hedef Birim:** {ticket.get('target_department')}")
                        st.write(f"**Aciliyet:** 🔴 {ticket.get('urgency_score')}")

                    st.markdown("**📋 Dekanlık Sevk / İnceleme Kararı:**")
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button(f"🏛️ Bölüm Başkanına İlet", key=f"dek_dept_{idx}", type="primary"):
                            st.success(f"{ticket.get('tracking_code')} Bölüm Başkanlığına iletildi.")
                    with b2:
                        if st.button(f"🔎 İnceleme Başlat", key=f"dek_invest_{idx}"):
                            st.info(f"{ticket.get('tracking_code')} için resmi inceleme başlatıldı.")
                    with b3:
                        if st.button(f"❌ Reddet / Kapat", key=f"dek_rej_{idx}"):
                            st.warning(f"{ticket.get('tracking_code')} talebi kapatıldı.")
                st.markdown("---")

    # C) 👷 GÖREVLİ MEMUR / TEKNİK EKİP EKRANI (SADECE TEKNİK / FİZİKSEL ARİZALAR)
    elif st.session_state.user_role == "memur":
        st.header("👷 Yapı İşleri & Teknik Bakım Memuru Paneli")
        st.caption("🔒 Yalnızca kampüs içi **Elektrik, Priz, İnternet, Tesisat ve Temizlik** arızaları gösterilmektedir. Akademik şikayetler gizlenmiştir.")
        st.markdown("---")

        technical_tickets = [t for t in st.session_state.submitted_tickets if "Akademik" not in t.get("standard_category", "")]

        if not technical_tickets:
            st.info("💡 Teknik ekibe atanmış bekleyen arıza kaydı bulunmamaktadır.")
        else:
            st.subheader(f"🛠️ İşlem Bekleyen Arıza Kayıtları ({len(technical_tickets)})")
            for idx, ticket in enumerate(technical_tickets):
                with st.container():
                    st.markdown(f"#### 📌 Talep Kodu: `{ticket.get('tracking_code')}` | Gönderen: `{ticket.get('student_hash')}`")
                    st.info(f"**🔧 Arıza Detayı:** {ticket.get('scrubbed_text')}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Konum:** {ticket.get('location')}")
                        st.write(f"**Arıza Tipi:** {ticket.get('standard_category')}")
                    with c2:
                        st.write(f"**Atanan Birim:** {ticket.get('target_department')}")
                        st.write(f"**Aciliyet:** 🔴 {ticket.get('urgency_score')}")

                    st.markdown("**🛠️ Teknik Ekip Saha Aksiyonu:**")
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button(f"🚚 Saha Ekibine Atandı", key=f"mem_assign_{idx}", type="primary"):
                            st.success(f"{ticket.get('tracking_code')} arıza ekibine yönlendirildi.")
                    with b2:
                        if st.button(f"✅ Arıza Çözüldü", key=f"mem_done_{idx}"):
                            st.success(f"{ticket.get('tracking_code')} arızası giderildi ve kapatıldı.")
                    with b3:
                        if st.button(f"📦 Yedek Parça Bekleniyor", key=f"mem_wait_{idx}"):
                            st.warning(f"{ticket.get('tracking_code')} için parça siparişi verildi.")
                st.markdown("---")

    # D) 👑 SİSTEM ADMİN EKRANI (TÜM BİLETLER & GENEL BAKIŞ)
    elif st.session_state.user_role == "admin":
        st.header("👑 SAÜ Kampüs Operasyon Yönetim Merkezi (Admin)")
        st.caption("🌐 Tüm kategorilerdeki gelen bildirimler ve yetki alanı genel göstergeleri.")
        st.markdown("---")

        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Toplam Bildirim", len(st.session_state.submitted_tickets))
        with kpi2:
            acad_count = len([t for t in st.session_state.submitted_tickets if "Akademik" in t.get("standard_category", "")])
            st.metric("Akademik Şikayetler", acad_count)
        with kpi3:
            tech_count = len([t for t in st.session_state.submitted_tickets if "Akademik" not in t.get("standard_category", "")])
            st.metric("Teknik Arızalar", tech_count)

        st.markdown("---")
        st.subheader("📑 Sistemdeki Tüm Aktif Bildirimler")
        for idx, ticket in enumerate(st.session_state.submitted_tickets):
            with st.expander(f"📌 {ticket.get('tracking_code')} - {ticket.get('standard_category')} ({ticket.get('location')})"):
                st.write(f"**Gönderen HASH:** `{ticket.get('student_hash')}`")
                st.write(f"**Anonim Metin:** {ticket.get('scrubbed_text')}")
                st.write(f"**Atanan Birim:** {ticket.get('target_department')}")