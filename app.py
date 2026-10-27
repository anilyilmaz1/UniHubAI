import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime, date
import calendar
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

    /* Girdi Kutuları (Selectbox, Text Input, Date Input) Siyah Font ve Beyaz Arka Plan */
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
    .macro-badge {
        background-color: #e2e8f0;
        color: #1e293b;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 4px;
    }
    .gmaps-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. KAFE YOĞUNLUK VERİ TABANI & GOOGLE MAPS GRAFİK MOTORU
# ==========================================
CAFE_HOURLY_DATA = {
    "Lumo Coffee": [0, 5, 15, 35, 65, 85, 95, 90, 80, 70, 55, 30, 15, 5, 0, 0, 0, 0],
    "Coffy SAÜ": [0, 10, 25, 50, 80, 95, 90, 85, 75, 85, 90, 60, 30, 10, 0, 0, 0, 0],
    "Adıbahçe": [0, 0, 10, 20, 45, 70, 80, 85, 90, 95, 85, 65, 35, 10, 0, 0, 0, 0],
    "Taş Kafe": [0, 5, 15, 30, 60, 75, 70, 65, 55, 45, 35, 20, 10, 0, 0, 0, 0, 0]
}

HOURS_LABELS = [f"{h:02d}" for h in range(6, 24)]

def get_current_cafe_density(cafe_name: str) -> tuple:
    current_hour = datetime.now().hour
    if current_hour < 6 or current_hour >= 24:
        return 0, "🟢 Kapalı / Sakin", "Şu an kafeler kapalı veya boş."
    
    idx = current_hour - 6
    density = CAFE_HOURLY_DATA.get(cafe_name, [30]*18)[idx]
    
    if density >= 80:
        return density, "🔴 Çok Yoğun (Pik Saat)", "Oturacak masa bulmak zor olabilir."
    elif density >= 50:
        return density, "🟡 Orta Yoğunluk", "Masa bulunabilir, sipariş sırası makul."
    else:
        return density, "🟢 Sakin & Müsait", "Rahatça ders çalışabilir veya oturabilirsiniz."

def render_google_maps_populer_saatler(cafe_name: str, day_name: str = "Salı günleri"):
    current_hour = datetime.now().hour
    raw_data = CAFE_HOURLY_DATA.get(cafe_name, [30]*18)
    
    bar_colors = []
    for h in range(6, 24):
        if h == current_hour:
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
# 5. DİNAMİK SABİS TARİH BAZLI SCRAPING & MAKRO HESAPLAMA
# ==========================================
def calculate_macros_from_kcal(name: str, kcal: int):
    name_lower = name.lower()
    if kcal == 0:
        return "0g", "0g", "0g"
    
    if "çorba" in name_lower:
        p = max(2, int(kcal * 0.12 / 4))
        c = max(5, int(kcal * 0.60 / 4))
        f = max(1, int(kcal * 0.28 / 9))
    elif any(k in name_lower for k in ["döner", "kebap", "et", "tavuk", "köfte"]):
        p = max(15, int(kcal * 0.35 / 4))
        c = max(5, int(kcal * 0.20 / 4))
        f = max(8, int(kcal * 0.45 / 9))
    elif any(k in name_lower for k in ["pilav", "makarna", "börek"]):
        p = max(4, int(kcal * 0.10 / 4))
        c = max(25, int(kcal * 0.70 / 4))
        f = max(3, int(kcal * 0.20 / 9))
    elif "ayran" in name_lower or "cacık" in name_lower:
        p = 4
        c = 5
        f = 4
    elif "tatlı" in name_lower or "helva" in name_lower:
        p = 3
        c = max(30, int(kcal * 0.75 / 4))
        f = max(4, int(kcal * 0.20 / 9))
    else:
        p = max(3, int(kcal * 0.15 / 4))
        c = max(10, int(kcal * 0.50 / 4))
        f = max(2, int(kcal * 0.35 / 9))
        
    return f"{p}g", f"{c}g", f"{f}g"

def fetch_sau_menu_by_date(target_date: date):
    """SABİS'ten seçilen tarihe özel canlı yemek menüsünü çeker"""
    # 1. Hafta Sonu Kontrolü
    if target_date.weekday() in [5, 6]:
        return None, "HAFTA_SONU"

    # 2. 28 Ekim (Arefe Yarım Gün) ve 29 Ekim Resmi Tatil Kontrolü
    if target_date.month == 10 and target_date.day in [28, 29]:
        return None, "29_EKIM_TATIL"
    
    # 3. Diğer Resmi Tatiller
    if (target_date.month == 1 and target_date.day == 1) or \
       (target_date.month == 4 and target_date.day == 23) or \
       (target_date.month == 5 and target_date.day in [1, 19]) or \
       (target_date.month == 7 and target_date.day == 15) or \
       (target_date.month == 8 and target_date.day == 30):
        return None, "RESMI_TATIL"

    formatted_date_str = target_date.strftime("%Y-%m-%d")
    url = f"https://menu.sabis.sakarya.edu.tr/?tarih={formatted_date_str}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.find_all(['div', 'td', 'li', 'p', 'span'])
            
            items = []
            for elem in elements:
                t = elem.get_text(strip=True)
                if "kcal" in t and ("-" in t or "–" in t):
                    parts = re.split(r'[-–]', t)
                    if len(parts) >= 2:
                        dish_name = parts[0].strip()
                        kcal_str = re.search(r'\d+', parts[1])
                        kcal_val = int(kcal_str.group()) if kcal_str else 0
                        
                        if dish_name and not any(x['name'] == dish_name for x in items):
                            p, c, f = calculate_macros_from_kcal(dish_name, kcal_val)
                            items.append({
                                "name": dish_name,
                                "kcal": kcal_val,
                                "protein": p,
                                "carb": c,
                                "fat": f
                            })
            
            if len(items) == 0:
                return None, "EMPTY_SABIS"
            else:
                return items, "OK"
    except Exception as e:
        print(f"Scraping Hatası: {e}")

    return None, "EMPTY_SABIS"

# ==========================================
# 6. AKADEMİK BİLGİ TABANI (KNOWLEDGE BASE)
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
# 7. GROQ AI CEVAP ENTEGRASYONU
# ==========================================
def generate_academic_response(messages_history, student_faculty: str, student_dept: str) -> str:
    if not client:
        return "⚠️ GROQ_API_KEY bulunamadı. Lütfen Hugging Face Secrets alanına GROQ_API_KEY ekleyin."

    menu_items, status = fetch_sau_menu_by_date(date.today())
    if menu_items and status == "OK":
        menu_summary = "\n".join([f"• {m['name']} ({m['kcal']} kcal - P:{m['protein']} C:{m['carb']} F:{m['fat']})" for m in menu_items])
    else:
        menu_summary = "Bugün yemekhanede yemek servisi bulunmamaktadır (Resmi Tatil / Hafta Sonu)."

    system_prompt = f"""
    Sen Sakarya Üniversitesi (SAÜ) öğrencilerinin resmi Akıllı Kampüs Asistanısın. Öğrencilerin zaman kaybetmeden doğru bilgiye ulaşmalarını sağlamak senin ana görevindir.
    
    [ÖĞRENCİ PROFİLİ]
    - Fakülte: {student_faculty if student_faculty else "Genel SAÜ Öğrencisi"}
    - Bölüm: {student_dept if student_dept else "Belirtilmedi"}

    [GÜNCEL SİSTEM VERİLERİ]
    🌐 BUGÜNKÜ SABİS YEMEK MENÜSÜ VE BESİN DEĞERLERİ:
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
# 8. SESSION STATE İLKELENDİRME
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba! Ben SAÜ Akıllı Kampüs Asistanı. Akademik takvim, bölümüne özel staj rehberi, not hesabı, canlı kafe yoğunluğu ve günün yemek menüsü hakkında kafana takılan her şeyi sorabilirsin. 🎓"}
    ]

# ==========================================
# 9. SOL MENÜ (ÖĞRENCİ PROFİLİ & QUICK LINKS)
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
# 10. ANA EKRAN SEKMELİ YAPI
# ==========================================
st.title("💬 SAÜ Akıllı Kampüs & Akademik Asistanı")
st.caption(f"Aktif Öğrenci Bağlamı: **{faculty}** {f'({department})' if department else ''}")

tab_chat, tab_food, tab_cafe, tab_bus, tab_calc = st.tabs([
    "💬 Akıllı AI Asistan", 
    "🍱 Yemekhane & Kalori", 
    "☕ Kafe Yoğunluk Analizi", 
    "🚌 Ulaşım & SAKUS", 
    "🧮 Not & Baraj Hesapla"
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
                fig_chat = render_google_maps_populer_saatler(message["cafe_chart"])
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
                    fig_inline = render_google_maps_populer_saatler(matched_cafe)
                    chart_key = f"inline_chart_{len(st.session_state.messages)}"
                    st.plotly_chart(fig_inline, use_container_width=True, config={'displayModeBar': False}, key=chart_key)
                    assistant_msg["cafe_chart"] = matched_cafe

        st.session_state.messages.append(assistant_msg)

# ------------------------------------------
# SEKME 2: YEMEKHANE & SADECE İÇİNDE BULUNULAN AYI GÖSTEREN TAKVİM
# ------------------------------------------
with tab_food:
    st.subheader("🍱 SABİS Canlı Yemek Menüsü & Besin Değerleri")
    st.caption("İstediğiniz tarihi seçerek SABİS yemekhanesindeki o güne özel menüyü ve besin değerlerini görebilirsiniz.")

    # İçinde bulunulan ayın ilk ve son günlerini dinamik olarak kısıtla
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    _, last_day_num = calendar.monthrange(today.year, today.month)
    last_day_of_month = date(today.year, today.month, last_day_num)

    selected_date = st.date_input(
        "🗓️ Menüsünü Görmek İstediğiniz Tarihi Seçin (Sadece İçinde Bulunduğumuz Ay Seçilebilir)", 
        value=today,
        min_value=first_day_of_month,
        max_value=last_day_of_month
    )
    
    menu_items, status = fetch_sau_menu_by_date(selected_date)

    if status == "HAFTA_SONU":
        st.warning(f"⚠️ **{selected_date.strftime('%d.%m.%Y')}** tarihi Hafta Sonu gününe denk gelmektedir. **Hafta sonları üniversite yemekhanesinde yemek hizmeti sunulmamaktadır.**")
    elif status == "29_EKIM_TATIL":
        st.warning(f"🇹🇷 **{selected_date.strftime('%d.%m.%Y')} (Arefe / 29 Ekim Cumhuriyet Bayramı)** Resmi Tatil olması sebebiyle üniversite yemekhanesinde yemek servisi yapılmamaktadır.")
    elif status == "RESMI_TATIL":
        st.warning(f"⚠️ **{selected_date.strftime('%d.%m.%Y')}** tarihi Resmi Tatil olması sebebiyle yemekhane kapalıdır.")
    elif status == "EMPTY_SABIS" or not menu_items:
        st.info(f"ℹ️ **{selected_date.strftime('%d.%m.%Y')}** tarihi için SABİS sisteminde yayınlanmış bir yemek menüsü bulunmamaktadır.")
    else:
        total_kcal = sum([item['kcal'] for item in menu_items])
        st.info(f"💡 **{selected_date.strftime('%d.%m.%Y')} Menüsü Toplam Kalorisi:** ~{total_kcal} kcal")

        for item in menu_items:
            st.markdown(f"""
            <div class="info-card">
                <h4 style="margin:0 0 8px 0; color:#002855;">🍽️ {item['name']}</h4>
                <div>
                    <span class="macro-badge">🔥 {item['kcal']} kcal</span>
                    <span class="macro-badge">🥩 Protein: {item['protein']}</span>
                    <span class="macro-badge">🌾 Karbonhidrat: {item['carb']}</span>
                    <span class="macro-badge">🥑 Yağ: {item['fat']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------
# SEKME 3: KAFE YOĞUNLUK ANALİZİ
# ------------------------------------------
with tab_cafe:
    st.subheader("☕ Kampüs Kafeleri Canlı & Saatlik Yoğunluk Analizi")
    st.caption("Google Maps 'Popüler Saatler' algoritması ve arayüzü ile kampüs kafelerinin doluluk durumları.")

    col_select1, col_select2 = st.columns([2, 1])
    with col_select1:
        selected_cafe = st.selectbox("İncelemek İstediğiniz Kafeyi Seçin", list(CAFE_HOURLY_DATA.keys()))
    with col_select2:
        selected_day = st.selectbox("Gün Seçin", ["Salı günleri", "Pazartesi günleri", "Çarşamba günleri", "Perşembe günleri", "Cuma günleri", "Cumartesi günleri", "Pazar günleri"])

    density_val, status_str, status_desc = get_current_cafe_density(selected_cafe)

    c_col1, c_col2 = st.columns([1, 2])
    with c_col1:
        st.markdown(f"""
        <div class="gmaps-card">
            <h3 style="margin:0; color:#202124;">{selected_cafe}</h3>
            <h1 style="margin:10px 0 0 0; color:#1d5d63; font-size:42px;">%{density_val}</h1>
            <p style="margin:0; font-weight:600;">Doluluk Oranı</p>
            <hr style="margin:12px 0;">
            <p style="margin:0; font-size:15px;"><strong>Durum:</strong> {status_str}</p>
            <p style="margin:5px 0 0 0; color:#5f6368; font-size:13px;">{status_desc}</p>
        </div>
        """, unsafe_allow_html=True)

    with c_col2:
        st.markdown('<div class="gmaps-card">', unsafe_allow_html=True)
        fig_gmaps = render_google_maps_populer_saatler(selected_cafe, selected_day)
        st.plotly_chart(fig_gmaps, use_container_width=True, config={'displayModeBar': False}, key="tab_cafe_main_chart")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# SEKME 4: ULAŞIM & SAKUS REHBERİ
# ------------------------------------------
with tab_bus:
    st.subheader("🚌 Kampüs Otobüs Hatları & SAKUS Canlı Takip")
    
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("""
        <div class="info-card">
            <h4>🚌 4 Nolu Hat (Kampüs - Gar - Çark Cad.)</h4>
            <p><strong>Sıklık:</strong> 3 - 5 Dakikada Bir</p>
            <p><strong>Güzergah:</strong> Esentepe Kampüsü ➔ Mavi Durak ➔ Çark Caddesi ➔ Sakarya Garı</p>
        </div>
        <div class="info-card">
            <h4>🚌 15 Nolu Hat (Kampüs - Serdivan AVM)</h4>
            <p><strong>Sıklık:</strong> 7 - 10 Dakikada Bir</p>
            <p><strong>Güzergah:</strong> Kampüs ➔ Serdivan AVM ➔ Cadde54 ➔ Kampüs Ring</p>
        </div>
        """, unsafe_allow_html=True)
    
    with b2:
        st.markdown("""
        <div class="info-card">
            <h4>🚌 24 Nolu Hat (Kampüs - Kent Park)</h4>
            <p><strong>Sıklık:</strong> 10 Dakikada Bir</p>
            <p><strong>Güzergah:</strong> Kampüs ➔ Mavi Durak ➔ Ofis Park ➔ Kent Park</p>
        </div>
        <div class="info-card">
            <h4>🚌 54 Nolu Hat (Kampüs - Otogar)</h4>
            <p><strong>Sıklık:</strong> 15 Dakikada Bir</p>
            <p><strong>Güzergah:</strong> Kampüs ➔ Şehirlerarası Otobüs Terminali</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.link_button("🌐 SAKUS Canlı Otobüs Konumlarını Haritada Gör", "https://sakus.sakarya.bel.tr", use_container_width=True)

# ------------------------------------------
# SEKME 5: NOT & BARAJ HESAPLAYICI
# ------------------------------------------
with tab_calc:
    st.subheader("🧮 SAÜ 'Kaç Alırsam Geçerim?' Not Hesaplayıcı")
    st.warning("⚠️ **SAÜ Önemli Kuralı:** Yıl içi not ortalamanız kaç olursa olsun, dersten geçebilmek için **Final sınavından EN AZ 50 puan** alma şartı vardır.")

    nc1, nc2 = st.columns(2)
    with nc1:
        v_not = st.number_input("Vize Notunuz", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
        v_oran = st.slider("Vize Etki Oranı (%)", min_value=10, max_value=90, value=40, step=5)
    with nc2:
        h_not = st.number_input("Hedef Ortalama (CC Standart Geçme = 50)", min_value=30.0, max_value=100.0, value=50.0, step=1.0)
        f_oran = 100 - v_oran
        st.info(f"Hesaplanan Final Etki Oranı: **%{f_oran}**")

    if st.button("🧮 Gereken Final Notunu Hesapla", use_container_width=True):
        v_katki = v_not * (v_oran / 100.0)
        req_final = (h_not - v_katki) / (f_oran / 100.0)

        st.markdown("---")
        if req_final < 50:
            st.warning(f"Matematiksel olarak **{req_final:.1f}** yeterli görünse de SAÜ Final Baraj kuralı nedeniyle finalden **EN AZ 50** almalısınız!")
            st.success("🎯 **Finalde Almanız Gereken Asgari Not: 50.0**")
        elif req_final > 100:
            st.error(f"❌ Hedeflenen {h_not} ortalama için gereken final notu **{req_final:.1f}** (100 üstü). Bütünleme sınavına hazırlanmanız gerekebilir.")
        else:
            st.success(f"🎯 **Hedeflenen {h_not} ortalama için Finalde Almanız Gereken Not: {req_final:.1f}**")