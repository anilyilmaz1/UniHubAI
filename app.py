import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime, date
from bs4 import BeautifulSoup
from groq import Groq
import plotly.graph_objects as go
import pytz
import re

# ==========================================
# 1. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="SAÜ Akıllı Asistan",
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
    "4 Nolu Hat (Kampüs - Çark Cad. - Gar - Sakarya Park)": {
        "freq": "50 Dakikada Bir",
        "first_bus": "06:50",
        "last_bus": "23:05",
        "route": "Esentepe Kampüsü ➔ Kampüs Yolu ➔ Mavi Durak ➔ Çark Caddesi ➔ Adapazarı Garı ➔ Sakarya Park",
        "desc": "Alışveriş merkezleri (Serdivan AVM / Cadde54) ve kafeler bölgesine direkt ulaşım sağlar."
    },
    "15 Nolu Hat (Kampüs - Tunatan - Gar - Yeni Stad)": {
        "freq": "45 Dakikada Bir",
        "first_bus": "06:35",
        "last_bus": "23:10",
        "route": "Esentepe Kampüsü ➔ Üniversite Cad. ➔ Tunatan ➔ Adapazarı Garı ➔ Sakarya Stadyumu",
        "desc": "Kampüsten merkeze ve gar bölgesine ulaşım için en sık çalışan ana hattır."
    },
    "26 Nolu Hat (Kampüs - Serdivan Devlet Hastanesi - Adapazarı Garı - Sakarya Stadyumu)": {
        "freq": "30 Dakikada Bir",
        "first_bus": "06:25",
        "last_bus": "23:20",
        "route": "Esentepe Kampüsü ➔ Diş Hastanesi ➔ Serdivan Devlet Hastanesi ➔ Adapazarı Garı ➔ Sakarya Stadyumu",
        "desc": "Serdivan Devlet Hastanesi istikametine gidecek öğrenciler için ideal hattır."
    },
    "24K Nolu Hat (Kampüs - Korucuk)": {
        "freq": "Genelde Saatte Bir",
        "first_bus": "06:30",
        "last_bus": "23:00",
        "route": "Esentepe Kampüsü ➔ Mavi Durak ➔ Serdivan AVM ➔ Sakarya Valiliği ➔ Korucuk",
        "desc": "Korucukta ikamet eden öğrencilerin aktarmasız gitmesini sağlar."
    },
    "6 Nolu Hat (Kampüs - Orta Garaj)": {
        "freq": "30 - 40 Dakikada Bir",
        "first_bus": "06:20",
        "last_bus": "23:00",
        "route": "Esentepe Kampüsü ➔ Sabahattin Zaim Yurdu ➔ Beşköprü Talebe Yurdu ➔ Araştırma Hastanesi ➔ Orta Garaj",
        "desc": "Orta garajtan ilçelere aktarma yapmak isteyen öğrenciler için ideal hattır."
    },
    "16K Nolu Hat (Kampüs - Adapazarı Yurt )": {
        "freq": "Yaklaşık 2 Saatte Bir",
        "first_bus": "06:45",
        "last_bus": "20:00",
        "route": "Kampüs ➔ Mavi Durak ➔ Serdivan AVM ➔ Adapazarı Yurt ➔ Süleymanbey",
        "desc": "Adapazarı yurdunda barınan öğrenciler için kampüsten aktarmasız gitmesini sağlar."
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
# 6. CHATBOT İÇİN MENÜ BİLGİSİ
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
# 7. GENEL SAÜ MEVZUATI VE FAKÜLTE ÖZEL DOKÜMAN TABANI
# ==========================================
SAU_GENEL_MEVZUAT = """
[SAÜ AKADEMİK TAKVİM VE TARİHLER]
- Güz Dönemi Vize Sınavları: 18 - 24 Kasım
- Güz Dönemi Final Sınavları: 6 - 17 Ocak
- Bütünleme Sınavları: 25 - 31 Ocak
- Bahar Dönemi Ders Kayıtları: 10 - 14 Şubat

[SAÜ NOT SİSTEMİ VE FİNAL BARAJ KURALI]
- FİNAL BARAJI KURALI: Yıl içi ortalaması ne olursa olsun, öğrencinin dersten geçebilmesi için Final veya Bütünleme sınavından EN AZ 40 ALMASI ZORUNLUDUR! (Final notu 39 olan öğrenci FF ile dersten kalır).
- Harf Notu Sınırları: AA (90-100), BA (85-89), BB (75-84), CB (65-74), CC (50-64 Standart Geçer), DC (45-49 Şartlı Geçer), DD (40-44 Şartlı Geçer), FF (0-39 Başarısız).

[ÇAP (ÇİFT ANADAL) VE YAN DAL MEVZUATI]
- ÇAP Başvuru Şartları: Öğrencinin başvurduğu yarıyıla kadar lisans programındaki tüm dersleri başarmış olması, AGNO'sunun en az 3.00/4.00 olması ve sınıfında başarı sıralaması itibarıyla en üst %20'lik dilimde bulunması gerekir. Başvurular 3. veya 5. yarıyıl başında yapılır.
- Yan Dal Başvuru Şartları: Tüm dersleri başarmış olmak ve AGNO'sunun en az 2.50/4.00 olması gerekir. 3., 4. veya 5. yarıyıl başında başvurulabilir.

[YATAY GEÇİŞ KURALLARI]
- Kurum İçi / Kurumlar Arası Yatay Geçiş: AGNO en az 2.80 olmalı, başarısız ders bulunmamalıdır.
- Ek Madde 1 (YKS Puanı ile): Kayıt olunan yıldaki YKS puanı, geçmek istenen diploma programının o yıldaki taban puanına eşit veya yüksek ise AGNO'ya bakılmaksızın yatay geçiş yapılabilir.

[MAZERET VE TEK DERS SINAV KURALLARI]
- Mazeret Sınavı: Sınav haftasını takip eden ilk 3 iş günü içinde fakülte sekreterliğine dilekçe verilir.
- Tek Ders Sınavı: Mezuniyet için tüm derslerini tamamlamış, sadece 1 başarısız (FF) dersi kalan öğrencilere verilir.
"""

# FAKÜLTE BAZLI DİNAMİK BİLGİ TABANI (5 ANA FAKÜLTE)
FACULTY_KNOWLEDGE = {
    "Mühendislik Fakültesi": """
    [MÜHENDİSLİK FAKÜLTESİ ÖZEL YÖNERGESİ]
    - Staj Kuralı: Toplam 40 İş Günü zorunlu staj vardır (Staj-1: 20 gün donanım/yazılım/tasarım, Staj-2: 20 gün saha/organizasyon).
    - Başvuru Zamanı: SABİS Staj Formu doldurulup staj başlamadan EN GEÇ 15 Gün önce Bölüm Staj Komisyonuna teslim edilir.
    - Bitirme Tasarımı (BSG): AGNO en az 2.00 olmalı ve 5. yarıyıldan başarısız (FF) ders bulunmamalıdır.
    - Devam Zorunluluğu: Laboratuvarlı/Uygulamalı derslerde %80, teorik derslerde %70 devam şartı vardır.
    """,
    
    "İşletme Fakültesi": """
    [İŞLETME FAKÜLTESİ ÖZEL YÖNERGESİ (7+1 MODELİ)]
    - 7+1 Uygulamalı Eğitim Modeli: Öğrenciler 7 dönem kampüste ders alır, 8. yarıyılın tamamını (16 hafta) anlaşmalı kurumlarda tam zamanlı çalışarak geçirir.
    - 7+1 Başvuru Şartı: 8. yarıyıla geçerken alttan en fazla 3 başarısız (FF) dersi olan öğrenciler tam zamanlı işyeri eğitimine gidebilir.
    - Sigorta & Ücret: SGK sigortası üniversite tarafından, ücret ise anlaşmalı firma tarafından karşılanır.
    """,
    
    "İlahiyat Fakültesi": """
    [İLAHİYAT FAKÜLTESİ ÖZEL YÖNERGESİ]
    - Zorunlu Hazırlık Sınıfı: Zorunlu Arapça hazırlık sınıfı bulunmaktadır.
    - Mesleki Staj & Uygulama: 7. ve 8. yarıyıllarda Milli Eğitim Bakanlığı (MEB) okullarında ve Diyanet kurumlarında öğretmenlik/mesleki staj uygulaması yapılır.
    """,
    
    "Fen-Edebiyat Fakültesi": """
    [FEN-EDEBİYAT FAKÜLTESİ ÖZEL YÖNERGESİ]
    - Staj Kuralı: İsteğe bağlı ve zorunlu stajlar toplam 20 iş günüdür.
    - Evrak Teslimi: Staj başvuru evrakları staj başlangıcından en geç 10 gün önce Fakülte Öğrenci İşlerine teslim edilir.
    - Laboratuvar Katılımı: Fen bölümlerinde (Kimya, Fizik, Biyoloji) laboratuvar derslerine %80 devam zorunludur.
    """,
    
    "Siyasal Bilgiler Fakültesi": """
    [SİYASAL BİLGİLER FAKÜLTESİ ÖZEL YÖNERGESİ]
    - Kurumsal Staj & 7+1: Bölüm bazlı olarak 7+1 uygulamalı eğitimi ve isteğe bağlı kurum stajları desteklenmektedir.
    - Kamusal Stajlar: Kaymakamlık, Valilik ve Bakanlık staj başvuruları için fakülte dekanlığından resmi onay belgesi alınmalıdır.
    """
}

FACULTY_URLS = {
    "Mühendislik Fakültesi": "https://mf.sakarya.edu.tr",
    "İşletme Fakültesi": "https://isletme.sakarya.edu.tr",
    "İlahiyat Fakültesi": "https://ilahiyat.sakarya.edu.tr",
    "Fen-Edebiyat Fakültesi": "https://fef.sakarya.edu.tr",
    "Siyasal Bilgiler Fakültesi": "https://sbf.sakarya.edu.tr",
    "Diğer": "https://ogris.sakarya.edu.tr"
}

# ==========================================
# 8. GROQ AI CEVAP ENTEGRASYONU
# ==========================================
def generate_academic_response(messages_history, student_faculty: str, student_dept: str) -> str:
    if not client:
        return "⚠️ GROQ_API_KEY bulunamadı. Lütfen Hugging Face Secrets alanına GROQ_API_KEY ekleyin."

    menu_summary = fetch_today_menu_summary()
    faculty_doc = FACULTY_KNOWLEDGE.get(student_faculty, "Genel SAÜ mevzuatı geçerlidir.")
    faculty_url = FACULTY_URLS.get(student_faculty, "https://ogris.sakarya.edu.tr")

    # Fakülte ismi girilmemişse genel etiket kullan
    faculty_label = student_faculty if student_faculty else "SAÜ"

    system_prompt = f"""
    Sen Sakarya Üniversitesi (SAÜ) resmi Akıllı Kampüs Asistanısın.
    
    [AKTİF ÖĞRENCİ PROFİLİ]
    - Fakülte: {student_faculty if student_faculty else "Genel SAÜ Öğrencisi"}
    - Bölüm: {student_dept if student_dept else "Belirtilmedi"}
    - Fakülte Web Sitesi: {faculty_url}

    [GÜNCEL SİSTEM VERİLERİ]
    🌐 BUGÜNKÜ SABİS YEMEK MENÜSÜ:
    {menu_summary}

    📘 GENEL SAÜ MEVZUAT BİLGİSİ:
    {SAU_GENEL_MEVZUAT}

    🏢 SEÇİLİ FAKÜLTEYE ÖZEL YÖNERGE VE DOKÜMAN:
    {faculty_doc}

    [MİSYON VE YANIT KURALLARI]
    1. Öğrenciye yanıt verirken {student_faculty} yönergesini ve genel SAÜ mevzuatını esas al.
    2. Öğrenciyi Öğrenci İşleri'ne veya duyurulara yönlendirirken KESİNLİKLE doğrudan tıklanabilir Markdown link formatını kullan (asla ters tırnak veya kod bloğu içine alma):
       👉 [{faculty_label} Öğrenci İşleri]({faculty_url})
    3. Not hesaplama sorularında SAÜ'nün FİNALDEN EN AZ 40 ALMA BARAJI kuralını kesinlikle hatırlat!
    4. SADECE yukarıda verilen bilgilere dayanarak yanıt ver. Verilerde olmayan bir bilgiyi uydurma; bilmiyorsan bunu açıkça söyle ve öğrenciyi Öğrenci İşleri'ne yönlendir.
    """

    full_messages = [{"role": "system", "content": system_prompt}] + messages_history

    candidate_models = [
        "qwen/qwen3.8-27b",
        "llama-3.3-70b-versatile",
        "llama3-8b-8192"
    ]

    last_error = ""
    for model_name in candidate_models:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=full_messages,
                temperature=0.3,
                max_tokens=800
            )
            return completion.choices[0].message.content
        except Exception as e:
            last_error = str(e)
            continue

    return f"⚠️ Bağlantı Hatası: {last_error}"

# ==========================================
# 9. SESSION STATE İLKELENDİRME
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba! Ben SAÜ Akıllı Kampüs Asistanı. Akademik takvim, fakültenize özel staj yönergeleri, ÇAP/Yan Dal, sınav barajları, otobüs hatları ve yemek menüsü hakkında kafana takılan her şeyi sorabilirsin. 🎓"}
    ]

# ==========================================
# 10. SOL MENÜ (ÖĞRENCİ PROFİLİ & QUICK LINKS)
# ==========================================
st.markdown("""
<style>
    /* ==========================================
       1. SIDEBAR TASARIMI VE RENKLERİ
       ========================================== */
    [data-testid="stSidebar"] {
        background-color: #0b192c !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    .sidebar-link-card {
        display: flex;
        align-items: center;
        padding: 9px 12px;
        margin-bottom: 6px;
        background-color: rgba(255, 255, 255, 0.08);
        color: #ffffff !important;
        text-decoration: none !important;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        transition: all 0.2s ease-in-out;
    }
    .sidebar-link-card:hover {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
        color: #ffffff !important;
        transform: translateX(3px);
    }

    [data-testid="stSidebar"] button {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    [data-testid="stSidebar"] button * {
        color: #0b192c !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] div[data-testid="column"]:nth-child(1) button:hover {
        background-color: #dc2626 !important;
        border-color: #dc2626 !important;
    }
    [data-testid="stSidebar"] div[data-testid="column"]:nth-child(1) button:hover * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] div[data-testid="column"]:nth-child(2) button:hover {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
    }
    [data-testid="stSidebar"] div[data-testid="column"]:nth-child(2) button:hover * {
        color: #ffffff !important;
    }

    /* ==========================================
       2. SOHBET BALONLARI VE INPUT STİLLERİ (YENİ)
       ========================================== */
    [data-testid="stChatInput"] {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
    }

    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #f8fafc !important;
        border-radius: 10px !important;
        border-left: 4px solid #2563eb !important;
        margin-bottom: 8px !important;
    }

    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        margin-bottom: 8px !important;
    }

    [data-testid="stChatMessage"] a {
        color: #2563eb !important;
        font-weight: 600 !important;
        text-decoration: underline !important;
    }

    div[data-testid="stChatInput"] {
    position: sticky !important;
    bottom: 0px !important;
    z-index: 999 !important;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
    background-color: var(--background-color) !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 2px; font-size: 22px;'>🎓 SAÜ Asistan</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.8; font-size: 11px; margin-bottom: 8px;'>Sakarya Üniversitesi Öğrenci Platformu</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 🎓 Profil Seçimleri
    st.markdown("<h3 style='font-size: 14px; margin-bottom: 4px;'>🎓 Profil Bilgileri</h3>", unsafe_allow_html=True)
    
    faculty = st.selectbox(
        "Fakülteniz",
        options=list(FACULTY_KNOWLEDGE.keys()),
        index=0,
        help="Fakültenizi seçin"
    )
    
    department = st.text_input(
        "Bölümünüz",
        value="",
        placeholder="Örn: ÇEKO, Bilgisayar Müh.",
        help="Bölüm adınız"
    )

    st.markdown("---")

    # 🔗 Hızlı Kısayollar
    st.markdown("<h3 style='font-size: 14px; margin-bottom: 6px;'>🔗 Hızlı Kısayollar</h3>", unsafe_allow_html=True)
    st.markdown("""
    <a href="https://sabis.sakarya.edu.tr" target="_blank" class="sidebar-link-card">🔗 &nbsp; SABİS Öğrenci Sistemi</a>
    <a href="https://yemek.sakarya.edu.tr" target="_blank" class="sidebar-link-card">🍽️ &nbsp; SABİS Yemek Menüsü</a>
    <a href="https://sakus.sakarya.bel.tr" target="_blank" class="sidebar-link-card">🚌 &nbsp; SAKUS Canlı Otobüs Takip</a>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 🧹 İşlem Butonları
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🧹 Temizle", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
    with col_b2:
        chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.get("messages", [])])
        st.download_button(
            label="📥 İndir",
            data=chat_text,
            file_name="sau_asistan_sohbet.txt",
            mime="text/plain",
            use_container_width=True
        )
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
# SEKME 1: AKILLI CHATBOT (FAKÜLTE & BÖLÜM ODAKLI)
# ------------------------------------------
with tab_chat:
    st.markdown("##### ⚡ Hızlı Soru Kısayolları:")
    
    q_cat1, q_cat2 = st.columns(2)
    prompt_to_send = None

    with q_cat1:
        st.caption("🎓 Akademik & Fakülte Mevzuatı:")
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            if st.button("📅 Vize & Final Tarihleri", use_container_width=True):
                prompt_to_send = "Vize ve final sınav tarihleri ne zaman?"
            if st.button("📝 Fakültemin Staj Yönergesi", use_container_width=True):
                prompt_to_send = f"{faculty} {department if department else ''} öğrencisiyim. Staj yaparken izlemem gereken adımlar ve kurallar nelerdir?"
        with q_col2:
            if st.button("🎓 ÇAP Şartları Nedir?", use_container_width=True):
                prompt_to_send = "SAÜ'de Çift Anadal (ÇAP) yapma şartları nelerdir?"
            if st.button("🔄 Yatay Geçiş Kuralları", use_container_width=True):
                prompt_to_send = "SAÜ yatay geçiş başvuru şartları ve Ek Madde 1 kuralları nedir?"

    with q_cat2:
        st.caption("🎪 Kampüs & Yaşam:")
        q_col3, q_col4 = st.columns(2)
        with q_col3:
            if st.button("☕ Lumo Yoğun mu?", use_container_width=True):
                prompt_to_send = "Lumo Coffee ve Coffy şu an kalabalık mı?"
            if st.button("🍱 Bugün Yemekte Ne Var?", use_container_width=True):
                prompt_to_send = "Bugün yemekhanede hangi yemekler var?"
        with q_col4:
            if st.button("🧮 Vize 45 Aldım Geçer miyim?", use_container_width=True):
                prompt_to_send = "Vizeden 45 aldım, dersten CC ile geçmek için finalden kaç almam lazım?"
            if st.button("🚌 Otogar Otobüsü Kaçta?", use_container_width=True):
                prompt_to_send = "Otogara giden 26 nolu otobüsün ilk ve son sefer saatleri nedir?"

    st.markdown("---")

    # 1. Sohbet Geçmişi Listeleme (Avatarlar Eklendi)
    for idx, message in enumerate(st.session_state.messages):
        avatar_icon = "🤖" if message["role"] == "assistant" else "🧑‍🎓"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])
            if "cafe_chart" in message:
                fig_chat = render_google_maps_populer_saatler(message["cafe_chart"], "Salı günleri", datetime.now().hour)
                st.plotly_chart(fig_chat, use_container_width=True, config={'displayModeBar': False}, key=f"chat_hist_chart_{idx}")

    # 2. Mesaj Girişi ve Yanıt Üretme (Avatarlar Eklendi)
    user_query = st.chat_input("Akademik takvim, fakülte staj kuralı, ÇAP, otobüs veya kampüs hakkında sorun...")
    if prompt_to_send:
        user_query = prompt_to_send

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(user_query)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(f"{faculty} bilgi tabanı ve SAÜ mevzuatı taranıyor..."):
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
            st.rerun()  # Yeni mesaj girildiğinde buton tıklamasıyla çakışmayı önler

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
    st.subheader("☕ Kampüs Kafeleri Canlı & Saatlik Yoğunlık Analizi")
    st.caption("Google Maps 'Popüler Saatler' algoritması, güne özel doluluk eğrileri ve kampüs mekân önerileri.")

    # 🇹🇷 Türkiye Saat Dilimini ve Gün Adlarını Tanımlıyoruz
    turkey_tz = pytz.timezone('Europe/Istanbul')
    now_tr = datetime.now(turkey_tz)
    
    days_tr = [
        "Pazartesi günleri", 
        "Salı günleri", 
        "Çarşamba günleri", 
        "Perşembe günleri", 
        "Cuma günleri", 
        "Cumartesi günleri", 
        "Pazar günleri"
    ]
    
    today_tr_name = days_tr[now_tr.weekday()] # Türkiye saatine göre bugünkü gün

    col_filter1, col_filter2, col_filter3 = st.columns([2, 1.5, 1.5])
    with col_filter1:
        selected_cafe = st.selectbox("İncelemek İstediğiniz Kafeyi Seçin", list(CAFE_DATABASE.keys()))
    with col_filter2:
        # Özel saat seçildiğinde kullanıcının seçtiği günü al, aksi halde bugünü varsayılan yap
        selected_day_input = st.selectbox("Gün Seçin", days_tr, index=now_tr.weekday())
    with col_filter3:
        time_mode = st.radio("Saat Modu:", ["🔴 Anlık Saat", "🎛️ Özel Saat Seç"], horizontal=True)

    # ⏰ Saat Modu Mantığı (Türkiye Saati & Canlı Gün Senkronizasyonu)
    if "Özel Saat" in time_mode:
        selected_hour = st.slider("İncelemek İstediğiniz Saati Seçin (06:00 - 23:00)", min_value=6, max_value=23, value=14, step=1)
        selected_day = selected_day_input
    else:
        selected_hour = now_tr.hour
        selected_day = today_tr_name  # Anlık saatte otomatik Türkiye gününü alıyoruz

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
                <p>• Kampüs içi fakülteler arası ring otobüsleri hafta içi ders saatlerinde yaklaşık <b>15 dakikada bir</b> hareket eder.</p>
                <p>• Otobüs Durakları ➔ Mühendislik ➔ İlahiyat ➔ Fen Fakültesi ➔ Kafeterya ➔ Kütüphane ➔ BESYO ➔ ÇIKIŞ KAPISI hattını takip eder.</p>
            </div>
            """, unsafe_allow_html=True)

        with uc2:
            st.markdown("""
            <div class="info-card">
                <h4>🚕 SAÜ Kampüs Taksi & Gece Ulaşımı</h4>
                <p>Gece otobüs seferleri bittiğinde veya acil durumlarda Kampüs Taksi durağı 24 saat hizmet vermektedir.</p>
                <p><b>📍 Konum:</b> Kampüs Dışı</p>
                <p><b>📞 Taksi Durağı İletişim:</b> 0 (264) 200 00 00 (Örnek Durak Hattı)</p>
            </div>
            <div class="info-card">
                <h4>🚐 Kampüs Minibüsleri</h4>
                <p>• Adapazarı Gar - Kampüs arası çalışan mavi minibüsler nakit ödeme ile yolcu almaktadır.</p>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------
# SEKME 5: GELİŞMİŞ NOT, PROJE & HARF NOTU HESAPLAYICI (40 BARAJLI)
# ------------------------------------------
with tab_calc:
    st.subheader("🧮 SAÜ Gelişmiş Not, Proje & Harf Notu Hesaplayıcı")
    st.warning("⚠️ **SAÜ Final Barajı Kuralı:** Yıl içi not ortalamanız kaç olursa olsun, dersten geçebilmek için **Final sınavından EN AZ 40 puan** alma şartı vardır.")

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
    st.markdown("### 2️⃣ Yıl İçi Değerlendirme Bileşenleri (Vize & 3 Adet Opsiyonel Ödev/Proje)")

    # 2. BİLEŞEN GİRDİLERİ
    col_vize, col_ek1 = st.columns(2)
    with col_vize:
        st.markdown("##### 📝 Vize Sınavı")
        vize_not = st.number_input("Vize Notunuz", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
        vize_oran = st.slider("Vize Etki Oranı (%)", min_value=10, max_value=80, value=30, step=5)

    with col_ek1:
        st.markdown("##### 💻 1. Ödev / Proje (Opsiyonel)")
        proje1_not = st.number_input("1. Ödev/Proje Notunuz", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        proje1_oran = st.slider("1. Ödev/Proje Etki Oranı (%)", min_value=0, max_value=40, value=0, step=5)

    col_ek2, col_ek3 = st.columns(2)
    with col_ek2:
        st.markdown("##### 📁 2. Ödev / Proje (Opsiyonel)")
        proje2_not = st.number_input("2. Ödev/Proje Notunuz", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        proje2_oran = st.slider("2. Ödev/Proje Etki Oranı (%)", min_value=0, max_value=40, value=0, step=5)

    with col_ek3:
        st.markdown("##### 🧪 3. Ödev / Lab / Quiz (Opsiyonel)")
        proje3_not = st.number_input("3. Ödev/Lab Notunuz", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        proje3_oran = st.slider("3. Ödev/Lab Etki Oranı (%)", min_value=0, max_value=40, value=0, step=5)

    # Toplam Yıl İçi Oranı ve Otomatik Final Oranı Hesaplama
    total_yilici_oran = vize_oran + proje1_oran + proje2_oran + proje3_oran
    final_oran = 100 - total_yilici_oran

    st.markdown("---")
    
    if total_yilici_oran >= 100:
        st.error(f"❌ Yıl içi değerlendirme oranlarının toplamı **%{total_yilici_oran}** oldu! Final sınavına oran kalmadı (Toplam %100'den küçük olmalıdır). Lütfen oranları ayarlayın.")
    else:
        st.success(f"📊 **Yıl İçi Toplam Etki Oranı:** %{total_yilici_oran} &nbsp;|&nbsp; 🎯 **Otomatik Hesaplanan Final Etki Oranı:** **%{final_oran}**")

        if st.button("🧮 Gereken Final Sınavı Notunu Hesapla", use_container_width=True):
            # Yıl içi kazanılan toplam puanlar
            vize_puan = vize_not * (vize_oran / 100.0)
            p1_puan = proje1_not * (proje1_oran / 100.0)
            p2_puan = proje2_not * (proje2_oran / 100.0)
            p3_puan = proje3_not * (proje3_oran / 100.0)

            kazanilan_puan = vize_puan + p1_puan + p2_puan + p3_puan
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
                    <p>• 1. Ödev/Proje Katkısı: <b>{p1_puan:.2f} puan</b> (%{proje1_oran})</p>
                    <p>• 2. Ödev/Proje Katkısı: <b>{p2_puan:.2f} puan</b> (%{proje2_oran})</p>
                    <p>• 3. Ödev/Lab Katkısı: <b>{p3_puan:.2f} puan</b> (%{proje3_oran})</p>
                    <hr style="margin:8px 0;">
                    <p style="font-size:16px;"><b>Toplam Yıl İçi Birikimi:</b> <span style="color:#002855; font-weight:700;">{kazanilan_puan:.2f} / {total_yilici_oran} puan</span></p>
                </div>
                """, unsafe_allow_html=True)

            with r_col2:
                # Durum Değerlendirme Kartı (SAÜ Final Barajı = 40)
                if req_final < 40:
                    st.markdown(f"""
                    <div class="info-card" style="border-left-color:#eab308;">
                        <h4 style="color:#854d0e;">⚠️ SAÜ Final Barajı Kuralı Devrede</h4>
                        <p>Matematiksel olarak <b>{selected_letter.split(' ')[0]}</b> almak için <b>{req_final:.1f}</b> almanız yeterli görünse de;</p>
                        <p><b>SAÜ kuralı gereği Final sınavından EN AZ 40.0 almanız şarttır!</b></p>
                        <h3 style="color:#166534; margin:10px 0 0 0;">🎯 Finalde Almanız Gereken Asgari Not: 40.0</h3>
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