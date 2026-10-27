import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime, date
from bs4 import BeautifulSoup
from groq import Groq
import plotly.graph_objects as go
import re

# ==========================================
# 1. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="UniHub Academic AI - SAÜ Akıllı Asistan",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. GROQ API İLKELENDİRME
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ==========================================
# 3. ÖZEL SAÜ TEMA VE GELİŞMİŞ CSS
# ==========================================
st.markdown("""
<style>
    /* Ana Sayfa Arka Planı */
    .stApp {
        background-color: #f3f7f8 !important;
    }

    /* Sidebar SAÜ Kurumsal Lacivert (#002855) */
    [data-testid="stSidebar"] {
        background-color: #002855 !important;
    }

    /* Sidebar Metinleri ve Başlıkları (Beyaz) */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stCaption {
        color: #ffffff !important;
    }

    /* Girdi Kutuları Siyah Font ve Beyaz Arka Plan */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] div[role="combobox"],
    [data-testid="stSidebar"] select {
        color: #000000 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* Selectbox açılır menü iç metin rengi (Siyah) */
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #000000 !important;
    }

    /* Placeholder metin rengi */
    [data-testid="stSidebar"] input::placeholder {
        color: #64748b !important;
    }

    /* Özel Kart Tasarımları */
    .info-card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #002855;
        margin-bottom: 12px;
    }
    .gmaps-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    .tag-badge {
        background-color: #e2e8f0;
        color: #0f172a;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
        display: inline-block;
        margin-top: 6px;
    }
    .recommend-card {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 6px solid #16a34a;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 18px;
    }
    .bus-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. KAFE YOĞUNLUK VERİ TABANI & DİNAMİK GRAFİK MOTORU
# ==========================================
CAFE_DATABASE = {
    "Taş Kafe": {
        "tags": ["🔌 Bol Priz", "📶 SAÜ Wifi", "☕ Demleme Çay", "🌳 Açık Bahçe"],
        "weekday": [0, 5, 15, 35, 65, 85, 95, 90, 80, 70, 55, 30, 15, 5, 0, 0, 0, 0],
        "friday":  [0, 5, 20, 45, 75, 90, 85, 95, 85, 75, 60, 40, 20, 5, 0, 0, 0, 0],
        "weekend": [0, 0, 5, 10, 25, 40, 55, 60, 50, 40, 30, 15, 5, 0, 0, 0, 0, 0]
    },
    "Lumo Coffee": {
        "tags": ["☕ Nitelikli Kahve", "🔌 Çalışma Masaları", "❄️ Klima", "🎵 Hafif Müzik"],
        "weekday": [0, 10, 25, 50, 80, 95, 90, 85, 75, 85, 90, 60, 30, 10, 0, 0, 0, 0],
        "friday":  [0, 15, 30, 60, 85, 98, 95, 90, 80, 90, 85, 50, 25, 10, 0, 0, 0, 0],
        "weekend": [0, 5, 15, 30, 50, 65, 75, 70, 65, 60, 45, 25, 10, 0, 0, 0, 0, 0]
    },
    "Coffy SAÜ": {
        "tags": ["⚡ Hızlı Sipariş", "💳 Sabit Fiyat", "🔌 Priz Alanı", "🚶‍♂️ Al-Git Pratik"],
        "weekday": [0, 15, 35, 60, 85, 90, 80, 75, 85, 90, 70, 45, 20, 5, 0, 0, 0, 0],
        "friday":  [0, 20, 40, 70, 90, 95, 85, 80, 90, 95, 75, 50, 25, 5, 0, 0, 0, 0],
        "weekend": [0, 5, 20, 35, 55, 70, 65, 60, 55, 50, 35, 15, 5, 0, 0, 0, 0, 0]
    },
    "Adıbahçe": {
        "tags": ["🍔 Geniş Menü", "🛋️ Konforlu Koltuklar", "🗣️ Grup Çalışması", "📺 Maç Yayınları"],
        "weekday": [0, 0, 10, 20, 45, 70, 80, 85, 90, 95, 85, 65, 35, 10, 0, 0, 0, 0],
        "friday":  [0, 0, 15, 30, 55, 80, 90, 95, 98, 95, 90, 70, 40, 15, 0, 0, 0, 0],
        "weekend": [0, 0, 10, 25, 40, 60, 75, 85, 90, 85, 70, 45, 20, 5, 0, 0, 0, 0]
    },
    "Espressolab SAÜ": {
        "tags": ["☕ Özel Harman Kahve", "🔌 Bol Priz & USB", "🤫 Sessiz Çalışma Katı", "🥐 Taze Pastane"],
        "weekday": [0, 10, 30, 65, 90, 98, 95, 90, 85, 95, 90, 75, 40, 15, 0, 0, 0, 0],
        "friday":  [0, 15, 35, 70, 95, 100, 95, 90, 90, 98, 92, 70, 35, 10, 0, 0, 0, 0],
        "weekend": [0, 5, 20, 40, 65, 80, 85, 80, 75, 70, 55, 30, 10, 0, 0, 0, 0, 0]
    },
    "Merkez Kütüphane Kafe": {
        "tags": ["🤫 Tam Sessiz Alan", "📚 Ders Çalışma Odaları", "🔌 Her Masada Priz", "🌙 24 Saat Açık"],
        "weekday": [20, 15, 25, 45, 70, 85, 95, 100, 95, 90, 85, 75, 60, 50, 40, 35, 30, 25],
        "friday":  [15, 10, 20, 40, 65, 80, 90, 90, 85, 80, 75, 65, 50, 40, 35, 30, 25, 20],
        "weekend": [10, 10, 15, 30, 50, 65, 75, 80, 75, 70, 60, 50, 40, 30, 25, 20, 15, 10]
    }
}

HOURS_LABELS = [f"{h:02d}" for h in range(6, 24)]

def get_hourly_profile_by_day(cafe_name: str, day_name: str) -> list:
    data = CAFE_DATABASE.get(cafe_name, {})
    if "Cuma" in day_name:
        return data.get("friday", [30]*18)
    elif any(d in day_name for d in ["Cumartesi", "Pazar"]):
        return data.get("weekend", [20]*18)
    else:
        return data.get("weekday", [30]*18)

def get_cafe_density_info(cafe_name: str, day_name: str, target_hour: int) -> tuple:
    profile = get_hourly_profile_by_day(cafe_name, day_name)
    
    if target_hour < 6 or target_hour >= 24:
        if cafe_name == "Merkez Kütüphane Kafe":
            return profile[target_hour if target_hour < 6 else 17], "🟡 Gece Çalışması Müsait", "Kütüphane Kafe 24 saat açıktır."
        return 0, "🟢 Kapalı", "Şu an mekan kapalıdır."
    
    idx = target_hour - 6
    density = profile[idx]
    
    if density >= 80:
        return density, "🔴 Çok Yoğun (Pik Saat)", "Masa bulmak zor olabilir, sıra bekleyebilirsiniz."
    elif density >= 50:
        return density, "🟡 Orta Yoğunluk", "Masa bulunabilir, çalışma ortamı makul."
    else:
        return density, "🟢 Sakin & Müsait", "Rahatça ders çalışabilir veya oturabilirsiniz."

def render_google_maps_populer_saatler(cafe_name: str, day_name: str, highlight_hour: int):
    raw_data = get_hourly_profile_by_day(cafe_name, day_name)
    
    bar_colors = []
    for h in range(6, 24):
        if h == highlight_hour:
            bar_colors.append('#1d5d63')
        else:
            bar_colors.append('#528f95')

    fig = go.Figure(data=[
        go.Bar(
            x=HOURS_LABELS,
            y=raw_data,
            marker_color=bar_colors,
            marker_line_width=0,
            hovertemplate="Saat: %{x}:00<br>Yoğunluk: %{y}%<extra></extra>",
            width=0.75
        )
    ])

    fig.update_layout(
        title=dict(
            text=f"<b>Popüler saatler</b> &nbsp;&nbsp;<span style='font-size:13px; color:#5f6368;'>({day_name})</span>",
            font=dict(size=18, color="#202124", family="Arial")
        ),
        xaxis=dict(
            type='category',
            showgrid=False,
            showline=True,
            linecolor='#dadce0',
            tickvals=['06', '09', '12', '15', '18', '21'],
            ticktext=['06', '09', '12', '15', '18', '21'],
            tickfont=dict(size=12, color="#5f6368")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f1f3f4',
            showticklabels=False,
            range=[0, 100]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=220,
        margin=dict(l=10, r=10, t=40, b=30),
        bargap=0.2
    )
    return fig

# ==========================================
# 5. ULAŞIM & OTOBÜS DETAYLI VERİTABANI
# ==========================================
BUS_LINES_DATA = {
    "4 Nolu Hat (Kampüs - Gar - Çark Cad.)": {
        "freq": "3 - 5 Dakikada Bir",
        "first_bus": "06:15",
        "last_bus": "23:45",
        "route": "Esentepe Kampüsü ➔ Kampüs Yolu ➔ Mavi Durak ➔ Serdivan ➔ Çark Caddesi ➔ Sakarya Garı",
        "desc": "Kampüsten merkeze ve gar bölgesine ulaşım için en sık çalışan ana hattır."
    },
    "15 Nolu Hat (Kampüs - Serdivan AVM - Ring)": {
        "freq": "7 - 10 Dakikada Bir",
        "first_bus": "06:30",
        "last_bus": "23:30",
        "route": "Esentepe Kampüsü ➔ Üniversite Cad. ➔ Serdivan AVM ➔ Cadde54 ➔ Ağız ve Diş Sağlığı ➔ Kampüs Ring",
        "desc": "Alışveriş merkezleri (Serdivan AVM / Cadde54) ve kafeler bölgesine direkt ulaşım sağlar."
    },
    "24 Nolu Hat (Kampüs - Kent Park - Ofis Park)": {
        "freq": "10 - 12 Dakikada Bir",
        "first_bus": "06:45",
        "last_bus": "23:15",
        "route": "Esentepe Kampüsü ➔ Mavi Durak ➔ Çark Cad. ➔ Ofis Park ➔ Kent Park ➔ Donatım",
        "desc": "Kent Park ve Ofis Park istikametine gidecek öğrenciler için ideal hattır."
    },
    "54 Nolu Hat (Kampüs - Otogar)": {
        "freq": "15 - 20 Dakikada Bir",
        "first_bus": "06:00",
        "last_bus": "00:15",
        "route": "Esentepe Kampüsü ➔ Serdivan ➔ D-100 Karayolu ➔ Sakarya Şehirlerarası Otobüs Terminali",
        "desc": "Şehir dışına seyahat edecek öğrencilerin otogara aktarmasız gitmesini sağlar."
    },
    "3 Nolu Hat (Kampüs - Kampüs Ring & Çevre)": {
        "freq": "15 Dakikada Bir",
        "first_bus": "07:00",
        "last_bus": "22:00",
        "route": "Merkez Kütüphane ➔ Mühendislik Fak. ➔ Fen-Edebiyat ➔ İlahiyat ➔ Helikopter Pist Yolu",
        "desc": "Kampüs içi fakülteler arası ring ve çevre yerleşke hattıdır."
    },
    "21B Nolu Hat (Kampüs - Hendek / Dış İlçeler)": {
        "freq": "20 - 30 Dakikada Bir",
        "first_bus": "06:30",
        "last_bus": "21:30",
        "route": "Kampüs ➔ Otoban Bağlantı Yolu ➔ Hendek / Erenler İstikameti",
        "desc": "Kampüsten dış ilçelere geçiş yapacak öğrenciler için ekspres hattır."
    }
}

# SAÜ Harf Notları Standart Alt Sınır Tablosu
SAU_LETTER_GRADES = {
    "AA (90 - Pekiyi)": 90.0,
    "BA (85 - İyi-Pekiyi)": 85.0,
    "BB (75 - İyi)": 75.0,
    "CB (65 - Orta-İyi)": 65.0,
    "CC (50 - Standart Geçer)": 50.0,
    "DC (45 - Şartlı Geçer)": 45.0,
    "DD (40 - Şartlı Geçer)": 40.0
}

# ==========================================
# 6. CHATBOT İÇİN YEMEK BİLGİSİ
# ==========================================
def fetch_today_menu_summary():
    today_dt = date.today()
    if today_dt.weekday() in (5, 6):
        return "Hafta sonu nedeniyle yemekhanede yemek servisi yapılmamaktadır."
    if today_dt.month == 10 and today_dt.day in [28, 29]:
        return "28-29 Ekim Arefe ve Cumhuriyet Bayramı resmi tatili nedeniyle yemekhane kapalıdır."
    
    try:
        url = "https://menu.sabis.sakarya.edu.tr/"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=3)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            items = []
            for elem in soup.find_all(['p', 'span', 'td', 'div']):
                t = elem.get_text(strip=True)
                if any(w in t.lower() for w in ['çorba', 'döner', 'kebap', 'pilav', 'köfte', 'nohut', 'sote']):
                    if t not in items and len(t) < 50:
                        items.append(t)
            if items:
                return "\n".join([f"• {item}" for item in items[:5]])
    except Exception:
        pass
    return "SABİS canlı menüsü için Yemekhane sekmesini ziyaret edebilirsiniz."

# ==========================================
# 7. AKADEMİK BİLGİ TABANI (KNOWLEDGE BASE)
# ==========================================
SAU_AKADEMIK_BILGI = """
[SAÜ AKADEMİK TAKVİM BİLGİLERİ]
- Güz Dönemi Vize Sınavları: 18 - 24 Kasım
- Güz Dönemi Final Sınavları: 6 - 17 Ocak
- Bütünleme Sınavları: 25 - 31 Ocak
- Bahar Dönemi Ders Kayıtları: 10 - 14 Şubat
- Mazeret Sınav Başvuruları: Sınav haftasını takip eden ilk 3 iş günü içinde fakülte sekreterliğine dilekçe ile yapılır.

[SAÜ NOT SİSTEMİ VE BARAJ DERS KURALLARI]
- Standart Oranlar: Vize %40, Final %60.
- FİNAL BARAJI KURALI: Öğrencinin dersten geçebilmesi için Final veya Bütünleme sınavından EN AZ 50 ALMASI ZORUNLUDUR! (Yıl içi ortalaması 90 bile olsa final 49 ise dersten FF ile kalır).
- Harf Notu Sınırları: AA (90-100), BA (85-89), BB (75-84), CB (65-74), CC (50-64 Standart Geçer), DC (45-49 Şartlı), DD (40-44 Şartlı), FF (0-39 Kaldı).

[FAKÜLTE VE BÖLÜM BAZLI STAJ YÖNERGELERİ]
1. Mühendislik Fakültesi (Bilgisayar, Elektrik-Elektronik, Endüstri vb.):
   - Zorunlu Staj: Toplam 40 İş Günü (Staj-1: 20 gün, Staj-2: 20 gün).
   - Başvuru: SABİS Zorunlu Staj Formu doldurulup firmaya imzalatılır. Başlangıçtan en geç 15 gün önce Bölüm Staj Komisyonuna teslim edilir.
2. İşletme / Siyasal Bilgiler Fakültesi:
   - 7+1 Uygulamalı Eğitim: 8. yarıyılda tam zamanlı firma stajı yapılır. Başvurular 7. yarıyıl sonunda fakülte sisteminden alınır.
3. Fen-Edebiyat / İlahiyat / Diğer Fakülteler:
   - İsteğe bağlı ve zorunlu stajlar için SGK kurum tarafından karşılanır. Formlar stajdan 10 gün önce teslim edilir.

[ULAŞIM & SAKUS REHBERİ]
- 4 Nolu Hat: Kampüs - Mavi Durak - Çark Cad. - Gar (Her 5 dk bir)
- 15 Nolu Hat: Kampüs - Serdivan AVM - Kampüs (Her 7 dk bir)
- 24 Nolu Hat: Kampüs - Mavi Durak - Kent Park
- 54 Nolu Hat: Kampüs - Şehirlerarası Otogar
"""

# ==========================================
# 8. GROQ AI CEVAP ENTEGRASYONU
# ==========================================
def generate_academic_response(messages_history, student_faculty: str, student_dept: str) -> str:
    if not client:
        return "⚠️ GROQ_API_KEY bulunamadı. Lütfen Hugging Face Secrets alanına GROQ_API_KEY ekleyin."

    menu_summary = fetch_today_menu_summary()

    system_prompt = f"""
    Sen Sakarya Üniversitesi (SAÜ) öğrencilerinin resmi Akıllı Kampüs Asistanısın. Öğrencilerin zaman kaybetmeden doğru bilgiye ulaşmalarını sağlamak senin ana görevindir.
    
    [ÖĞRENCİ PROFİLİ]
    - Fakülte: {student_faculty if student_faculty else "Genel SAÜ Öğrencisi"}
    - Bölüm: {student_dept if student_dept else "Belirtilmedi"}

    [GÜNCEL SİSTEM VERİLERİ]
    🌐 BUGÜNKÜ SABİS YEMEK MENÜSÜ:
    {menu_summary}

    📘 SAÜ AKADEMİK BİLGİ TABANI & REHBERİ:
    {SAU_AKADEMIK_BILGI}

    [MİSYON VE YANIT KURALLARI]
    1. Not hesaplama sorularında matematiği yap: (Vize*%40) + (Final*%60) = 50 formülünü kullan. SAÜ'nün **FİNALDEN EN AZ 50 ALMA BARAJI** kuralını belirt!
    2. Staj sorularında öğrencinin seçtiği fakülte/bölüm yönergesine sadık kal.
    3. Kafe yoğunluğu sorulursa saatlik doluluk durumunu özetle.
    4. Yanıtların net, sevimli, motive edici, maddeler (**bold**) halinde ve %100 doğru olsun.
    """

    full_messages = [{"role": "system", "content": system_prompt}] + messages_history

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_messages,
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception:
        try:
            completion = client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=full_messages,
                temperature=0.3
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Yanıt üretilirken bir hata oluştu: {str(e)}"

# ==========================================
# 9. SESSION STATE İLKELENDİRME
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba! Ben SAÜ Akıllı Kampüs Asistanı. Akademik takvim, bölümüne özel staj rehberi, not hesabı, canlı kafe yoğunluğu ve günün yemek menüsü hakkında kafana takılan her şeyi sorabilirsin. 🎓"}
    ]

# ==========================================
# 10. SOL MENÜ (ÖĞRENCİ PROFİLİ & QUICK LINKS)
# ==========================================
with st.sidebar:
    st.title("🎓 UniHub Academic AI")
    st.caption("Sakarya Üniversitesi Akıllı Kampüs Portalı")
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
    st.subheader("🔗 Hızlı Kısayollar")
    st.markdown("- [🔗 SABİS Öğrenci Sistemi](https://sabis.sakarya.edu.tr)")
    st.markdown("- [🍽️ SABİS Yemek Menüsü](https://menu.sabis.sakarya.edu.tr)")
    st.markdown("- [🚌 SAKUS Canlı Otobüs Takip](https://sakus.sakarya.bel.tr)")
    st.markdown("- [📚 SAÜ Merkez Kütüphane](https://kutuphane.sakarya.edu.tr)")

    st.markdown("---")
    if st.button("🧹 Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Sohbet temizlendi. Nasıl yardımcı olabilirim?"}
        ]
        st.rerun()

# ==========================================
# 11. ANA EKRAN SEKMELİ YAPI
# ==========================================
st.title("💬 SAÜ Akıllı Kampüs & Akademik Asistanı")
st.caption(f"Aktif Öğrenci Bağlamı: **{faculty}** {f'({department})' if department else ''}")

tab_chat, tab_food, tab_cafe, tab_bus, tab_calc = st.tabs([
    "💬 Akıllı AI Asistan", 
    "🍱 SABİS Canlı Yemek Menüsü", 
    "☕ Kafe Yoğunluk Analizi", 
    "🚌 Ulaşım & SAKUS Canlı Takip", 
    "🧮 Gelişmiş Not & Baraj Hesapla"
])

# ------------------------------------------
# SEKME 1: AKILLI CHATBOT
# ------------------------------------------
with tab_chat:
    st.markdown("##### ⚡ Hızlı Sorular:")
    q1, q2, q3, q4 = st.columns(4)

    prompt_to_send = None
    with q1:
        if st.button("📅 Vize & Final Tarihleri", use_container_width=True):
            prompt_to_send = "Vize ve final sınav tarihleri ne zaman?"
    with q2:
        if st.button("📝 Staj Yönergesi", use_container_width=True):
            prompt_to_send = f"{faculty} {department} öğrencisiyim. Staj yaparken izlemem gereken adımlar nelerdir?"
    with q3:
        if st.button("☕ Lumo Yoğun mu?", use_container_width=True):
            prompt_to_send = "Lumo Coffee ve Coffy şu an kalabalık mı?"
    with q4:
        if st.button("🧮 Vize 45 Aldım Geçer miyim?", use_container_width=True):
            prompt_to_send = "Vizeden 45 aldım, dersten CC ile geçmek için finalden kaç almam lazım?"

    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "cafe_chart" in message:
                fig_chat = render_google_maps_populer_saatler(message["cafe_chart"], "Salı günleri", datetime.now().hour)
                st.plotly_chart(fig_chat, use_container_width=True, config={'displayModeBar': False}, key=f"chat_hist_chart_{idx}")

    user_query = st.chat_input("Akademik takvim, staj, not hesabı veya kampüs hakkında sorun...")
    if prompt_to_send:
        user_query = prompt_to_send

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("SAÜ bilgi tabanı ve veri kaynakları taranıyor..."):
                history_for_api = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if "content" in m]
                response_text = generate_academic_response(history_for_api, faculty, department)
                st.markdown(response_text)
                
                matched_cafe = None
                query_lower = user_query.lower()
                if "lumo" in query_lower:
                    matched_cafe = "Lumo Coffee"
                elif "coffy" in query_lower:
                    matched_cafe = "Coffy SAÜ"
                elif "adıbahçe" in query_lower or "adibahce" in query_lower:
                    matched_cafe = "Adıbahçe"
                elif "taş kafe" in query_lower or "tas kafe" in query_lower:
                    matched_cafe = "Taş Kafe"
                elif any(k in query_lower for k in ["kafe", "yoğun", "kalabalık"]):
                    matched_cafe = "Lumo Coffee"

                assistant_msg = {"role": "assistant", "content": response_text}
                if matched_cafe:
                    fig_inline = render_google_maps_populer_saatler(matched_cafe, "Salı günleri", datetime.now().hour)
                    chart_key = f"inline_chart_{len(st.session_state.messages)}"
                    st.plotly_chart(fig_inline, use_container_width=True, config={'displayModeBar': False}, key=chart_key)
                    assistant_msg["cafe_chart"] = matched_cafe

        st.session_state.messages.append(assistant_msg)

# ------------------------------------------
# SEKME 2: YEMEKHANE & DIREKT CANLI SABIS SAYFASI
# ------------------------------------------
with tab_food:
    st.subheader("🍱 SABİS Canlı Yemek Menüsü")
    st.caption("Sakarya Üniversitesi resmi SABİS yemek menüsü sistemi doğrudan ve canlı olarak entegre edilmiştir.")

    st.components.v1.iframe("https://menu.sabis.sakarya.edu.tr/", height=680, scrolling=True)
    
    st.markdown("---")
    st.link_button("🌐 SABİS Menü Sayfasını Yeni Sekmede Aç", "https://menu.sabis.sakarya.edu.tr/", use_container_width=True)

# ------------------------------------------
# SEKME 3: DİNAMİK KAFE YOĞUNLUK ANALİZİ & ÖNERİ MOTORU
# ------------------------------------------
with tab_cafe:
    st.subheader("☕ Kampüs Kafeleri Canlı & Saatlik Yoğunluk Analizi")
    st.caption("Google Maps 'Popüler Saatler' algoritması, güne özel doluluk eğrileri ve kampüs mekân önerileri.")

    col_filter1, col_filter2, col_filter3 = st.columns([2, 1.5, 1.5])
    with col_filter1:
        selected_cafe = st.selectbox("İncelemek İstediğiniz Kafeyi Seçin", list(CAFE_DATABASE.keys()))
    with col_filter2:
        selected_day = st.selectbox("Gün Seçin", ["Salı günleri", "Pazartesi günleri", "Çarşamba günleri", "Perşembe günleri", "Cuma günleri", "Cumartesi günleri", "Pazar günleri"])
    with col_filter3:
        time_mode = st.radio("Saat Modu:", ["🔴 Anlık Saat", "🎛️ Özel Saat Seç"], horizontal=True)

    current_live_hour = datetime.now().hour
    if "Özel Saat" in time_mode:
        selected_hour = st.slider("İncelemek İstediğiniz Saati Seçin (06:00 - 23:00)", min_value=6, max_value=23, value=14, step=1)
    else:
        selected_hour = current_live_hour

    best_cafe = None
    lowest_density = 999
    for c_name in CAFE_DATABASE.keys():
        d_val, _, _ = get_cafe_density_info(c_name, selected_day, selected_hour)
        if d_val < lowest_density and d_val > 0:
            lowest_density = d_val
            best_cafe = c_name

    if best_cafe:
        st.markdown(f"""
        <div class="recommend-card">
            <h4 style="margin:0; color:#166534;">💡 SAÜ Asistan Önerisi ({selected_day} - Saat {selected_hour:02d}:00)</h4>
            <p style="margin:4px 0 0 0; color:#15803d;">Şu an kampüste ders çalışmak veya rahatça oturmak için <b>en sakin ve müsait mekân</b>: 
            <b><u>{best_cafe}</u></b> (Doluluk Oranı: <b>%{lowest_density}</b>)</p>
        </div>
        """, unsafe_allow_html=True)

    density_val, status_str, status_desc = get_cafe_density_info(selected_cafe, selected_day, selected_hour)
    cafe_tags = CAFE_DATABASE.get(selected_cafe, {}).get("tags", [])

    c_col1, c_col2 = st.columns([1, 2])
    with c_col1:
        tags_html = "".join([f'<span class="tag-badge">{t}</span>' for t in cafe_tags])
        st.markdown(f"""
        <div class="gmaps-card">
            <h3 style="margin:0; color:#202124;">{selected_cafe}</h3>
            <p style="margin:2px 0 10px 0; color:#5f6368; font-size:13px;">İncelenen Saat: <b>{selected_hour:02d}:00</b> ({selected_day})</p>
            <h1 style="margin:0; color:#1d5d63; font-size:44px;">%{density_val}</h1>
            <p style="margin:0; font-weight:600; color:#374151;">Doluluk Oranı</p>
            <hr style="margin:12px 0;">
            <p style="margin:0; font-size:15px;"><strong>Durum:</strong> {status_str}</p>
            <p style="margin:4px 0 10px 0; color:#5f6368; font-size:13px;">{status_desc}</p>
            <div>{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with c_col2:
        st.markdown('<div class="gmaps-card">', unsafe_allow_html=True)
        fig_gmaps = render_google_maps_populer_saatler(selected_cafe, selected_day, selected_hour)
        st.plotly_chart(fig_gmaps, use_container_width=True, config={'displayModeBar': False}, key=f"tab_cafe_chart_{selected_cafe}_{selected_day}")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# SEKME 4: Gelişmiş ULAŞIM & SAKUS CANLI TAKİP
# ------------------------------------------
with tab_bus:
    st.subheader("🚌 SAÜ Ulaşım Rehberi & SAKUS Canlı Otobüs Takip")
    st.caption("Kampüs otobüs hatları, ilk/son sefer saatleri ve Sakarya Büyükşehir SAKUS canlı konum haritası.")

    bus_sub_tab1, bus_sub_tab2, bus_sub_tab3 = st.tabs([
        "🌐 SAKUS Canlı Otobüs Haritası", 
        "🚌 Hat Detayları & Sefer Saatleri", 
        "💳 Kart, Ücretler & Kampüs Taksi"
    ])

    with bus_sub_tab1:
        st.info("💡 **SAKUS Canlı Harita:** Aşağıdaki ekrandan kampüse gelen otobüslerin haritadaki canlı konumlarını anlık izleyebilirsiniz.")
        st.components.v1.iframe("https://sakus.sakarya.bel.tr", height=650, scrolling=True)
        st.markdown("---")
        st.link_button("🌐 SAKUS Haritasını Tam Ekran Aç", "https://sakus.sakarya.bel.tr", use_container_width=True)

    with bus_sub_tab2:
        selected_bus_line = st.selectbox("İncelemek İstediğiniz Otobüs Hattını Seçin:", list(BUS_LINES_DATA.keys()))
        b_info = BUS_LINES_DATA[selected_bus_line]

        bc1, bc2 = st.columns([1.2, 2])
        with bc1:
            st.markdown(f"""
            <div class="bus-card">
                <h3 style="margin:0; color:#002855;">{selected_bus_line.split('(')[0]}</h3>
                <p style="color:#64748b; margin-bottom:12px;">{b_info['desc']}</p>
                <hr style="margin:8px 0;">
                <p style="margin:6px 0;"><b>⏱️ Çalışma Sıklığı:</b> <span style="color:#16a34a; font-weight:600;">{b_info['freq']}</span></p>
                <p style="margin:6px 0;"><b>🌅 İlk Sefer (Kampüs):</b> <b>{b_info['first_bus']}</b></p>
                <p style="margin:6px 0;"><b>🌙 Son Sefer (Kampüs):</b> <b>{b_info['last_bus']}</b></p>
            </div>
            """, unsafe_allow_html=True)

        with bc2:
            st.markdown(f"""
            <div class="bus-card">
                <h4 style="margin:0 0 10px 0; color:#002855;">📍 Güzergah ve Durak Hattı</h4>
                <p style="font-size:15px; line-height:1.6; color:#1e293b;">{b_info['route']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 📌 Diğer Kampüs Hatları Özet Tablosu")
        bus_rows = []
        for name, data in BUS_LINES_DATA.items():
            bus_rows.append({
                "Hat Adı": name.split('(')[0].strip(),
                "Kapsam": name.split('(')[1].replace(')', '') if '(' in name else "",
                "Sıklık": data["freq"],
                "İlk Sefer": data["first_bus"],
                "Son Sefer": data["last_bus"]
            })
        st.table(pd.DataFrame(bus_rows))

    with bus_sub_tab3:
        uc1, uc2 = st.columns(2)
        with uc1:
            st.markdown("""
            <div class="info-card">
                <h4>💳 Kart54 & Ulaşım Ücretleri</h4>
                <p>• <b>Öğrenci Kart54 Biniş Ücreti:</b> İndirimli öğrenci tarifesi uygulanır.</p>
                <p>• <b>Temassız Kredi / Banka Kartı:</b> Kart54 olmadan tüm temassız kartlarla otobüslere binebilirsiniz.</p>
                <p>• <b>Kart Dolum Noktaları:</b> Kampüs Helikopter Pisti durağında ve Mavi Durak'ta Otomatik Kiosk bulunmaktadır.</p>
            </div>
            <div class="info-card">
                <h4>🚌 Kampüs İçi Ring Hizmeti</h4>
                <p>• Kampüs içi fakülteler arası ring otobüsleri hafta içi ders saatlerinde <b>10 dakikada bir</b> hareket eder.</p>
                <p>• Kütüphane ➔ Mühendislik ➔ İlahiyat ➔ Rektörlük hattını takip eder.</p>
            </div>
            """, unsafe_allow_html=True)

        with uc2:
            st.markdown("""
            <div class="info-card">
                <h4>🚕 SAÜ Kampüs Taksi & Gece Ulaşımı</h4>
                <p>Gece otobüs seferleri bittiğinde veya acil durumlarda Kampüs Taksi durağı 24 saat hizmet vermektedir.</p>
                <p><b>📍 Konum:</b> SAÜ Helikopter Pist Girişi / Kafe Karşısı</p>
                <p><b>📞 Taksi Durağı İletişim:</b> 0 (264) 211 11 00 (Örnek Durak Hattı)</p>
            </div>
            <div class="info-card">
                <h4>🚐 Serdivan Mavi Durak Minibüsleri</h4>
                <p>• Mavi Durak - Kampüs arası çalışan mavi minibüsler nakit ödeme ile yolcu almaktadır.</p>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------
# SEKME 5: GELİŞMİŞ NOT, PROJE & HARF NOTU HESAPLAYICI
# ------------------------------------------
with tab_calc:
    st.subheader("🧮 SAÜ Gelişmiş Not, Proje & Harf Notu Hesaplayıcı")
    st.warning("⚠️ **SAÜ Final Barajı Kuralı:** Yıl içi not ortalamanız kaç olursa olsun, dersten geçebilmek için **Final sınavından EN AZ 50 puan** alma şartı vardır.")

    # 1. HEDEF HARF NOTU SEÇİMİ
    st.markdown("### 1️⃣ Hedef Harf Notunu Seçin")
    selected_letter = st.selectbox(
        "Hedeflediğiniz Harf Notunu Seçin",
        list(SAU_LETTER_GRADES.keys()),
        index=0
    )
    target_score = SAU_LETTER_GRADES[selected_letter]
    st.info(f"🎯 **Seçilen Harf Notu Hedef Puanı:** **{target_score}** / 100")

    st.markdown("---")
    st.markdown("### 2️⃣ Yıl İçi Değerlendirme Bileşenleri (Vize, Proje, Lab vb.)")

    # 2. BİLEŞEN GİRDİLERİ
    c_vize, c_proje, c_lab = st.columns(3)
    
    with c_vize:
        st.markdown("##### 📝 Vize Sınavı")
        vize_not = st.number_input("Vize Notunuz", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
        vize_oran = st.slider("Vize Etki Oranı (%)", min_value=10, max_value=80, value=40, step=5)

    with c_proje:
        st.markdown("##### 💻 Proje / Ödev (Opsiyonel)")
        proje_not = st.number_input("Proje / Ödev Notunuz", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        proje_oran = st.slider("Proje/Ödev Etki Oranı (%)", min_value=0, max_value=50, value=0, step=5)

    with c_lab:
        st.markdown("##### 🧪 Lab / Quiz (Opsiyonel)")
        lab_not = st.number_input("Lab / Quiz Notunuz", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        lab_oran = st.slider("Lab/Quiz Etki Oranı (%)", min_value=0, max_value=50, value=0, step=5)

    # Toplam Yıl İçi Oranı ve Otomatik Final Oranı Hesaplama
    total_yilici_oran = vize_oran + proje_oran + lab_oran
    final_oran = 100 - total_yilici_oran

    st.markdown("---")
    
    if total_yilici_oran >= 100:
        st.error(f"❌ Yıl içi değerlendirme oranlarının toplamı **%{total_yilici_oran}** oldu! Final sınavına oran kalmadı (Toplam %100'den küçük olmalıdır). Lütfen oranları ayarlayın.")
    else:
        st.success(f"📊 **Yıl İçi Toplam Etki Oranı:** %{total_yilici_oran} &nbsp;|&nbsp; 🎯 **Otomatik Hesaplanan Final Etki Oranı:** **%{final_oran}**")

        if st.button("🧮 Gereken Final Sınavı Notunu Hesapla", use_container_width=True):
            # Yıl içi kazanılan toplam puanlar
            vize_puan = vize_not * (vize_oran / 100.0)
            proje_puan = proje_not * (proje_oran / 100.0)
            lab_puan = lab_not * (lab_oran / 100.0)
            
            kazanilan_puan = vize_puan + proje_puan + lab_puan
            gereken_puan = target_score - kazanilan_puan
            req_final = gereken_puan / (final_oran / 100.0)

            st.markdown("---")
            st.markdown("### 📈 Hesaplama Sonuç Raporu")
            
            # Detaylı Puan Özet Paneli
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.markdown(f"""
                <div class="info-card">
                    <h4>📥 Cebinizdeki Puanlar (Şu Ana Kadar)</h4>
                    <p>• Vize Katkısı: <b>{vize_puan:.2f} puan</b> (%{vize_oran})</p>
                    <p>• Proje/Ödev Katkısı: <b>{proje_puan:.2f} puan</b> (%{proje_oran})</p>
                    <p>• Lab/Quiz Katkısı: <b>{lab_puan:.2f} puan</b> (%{lab_oran})</p>
                    <hr style="margin:8px 0;">
                    <p style="font-size:16px;"><b>Toplam Yıl İçi Birikimi:</b> <span style="color:#002855; font-weight:700;">{kazanilan_puan:.2f} / {total_yilici_oran} puan</span></p>
                </div>
                """, unsafe_allow_html=True)

            with r_col2:
                # Durum Değerlendirme Kartı
                if req_final < 50:
                    st.markdown(f"""
                    <div class="info-card" style="border-left-color:#eab308;">
                        <h4 style="color:#854d0e;">⚠️ SAÜ Final Barajı Kuralı Devrede</h4>
                        <p>Matematiksel hesaplamaya göre <b>{selected_letter.split(' ')[0]}</b> almak için <b>{req_final:.1f}</b> almanız yeterli görünse de;</p>
                        <p><b>SAÜ kuralı gereği Final sınavından EN AZ 50.0 almanız şarttır!</b></p>
                        <h3 style="color:#166534; margin:10px 0 0 0;">🎯 Finalde Almanız Gereken Not: 50.0</h3>
                    </div>
                    """, unsafe_allow_html=True)
                elif req_final > 100:
                    st.markdown(f"""
                    <div class="info-card" style="border-left-color:#ef4444;">
                        <h4 style="color:#991b1b;">❌ Hedef Harf Notu Yüksek Kaldı</h4>
                        <p>Hedeflenen <b>{selected_letter}</b> ({target_score} puan) için Final sınavından <b>{req_final:.1f}</b> almanız gerekiyor (100 üzeri puan almak imkansızdır).</p>
                        <p>💡 Lütfen hedefinizi bir alt harf notuna (örn. BA veya BB) güncelleyiniz.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="info-card" style="border-left-color:#16a34a;">
                        <h4 style="color:#166534;">🎉 Hedef Ulaşılabilir!</h4>
                        <p>Hedeflenen <b>{selected_letter}</b> harf notunu garantilemek için Final sınavından almanız gereken minimum not:</p>
                        <h2 style="color:#002855; margin:10px 0 0 0;">🎯 Final Notu: {req_final:.1f}</h2>
                    </div>
                    """, unsafe_allow_html=True)