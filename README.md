---
title: SAÜ Asistan
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
short_description: Sakarya Üniversitesi Akıllı Kampüs ve Akademik Asistanı
license: apache-2.0
---

# 🎓 SAÜ Akıllı Kampüs Asistanı

> Sakarya Üniversitesi öğrencileri için yapay zekâ destekli, tek noktadan kampüs asistanı.

> Proje ilk olarak *UniHub AI* adıyla başlatılmış, sonrasında *SAÜ Asistan* olarak yeniden adlandırılmıştır. Depo ve Space adresleri ilk ad olan `UniHubAI` ile kalmıştır.

🔗 **Canlı Demo:** [SAÜ Asistan Space](https://huggingface.co/spaces/Anil-yilmaz/UniHubAI)

💻 **GitHub:** [anilyilmaz1/UniHubAI](https://github.com/anilyilmaz1/UniHubAI)

---

## 🎯 Projenin Amacı

Öğrenciler; staj yönergesi, sınav takvimi, yemekhane menüsü, otobüs saatleri gibi bilgilere farklı sitelerden ve belgelerden ulaşmak zorunda kalıyor. SAÜ Asistan bu bilgileri tek bir arayüzde toplayarak öğrencilerin akademik ve günlük kampüs süreçlerinde **zaman kaybetmesini önlemeyi** amaçlar.

---

## ⚙️ Özellikler (5 Modül)

| # | Modül | Ne Yapar? |
|---|-------|-----------|
| 1 | **Akademik & Staj Asistanı** | Seçilen fakülte/bölüme özel staj yönergesi, mazeret dilekçesi, sınav takvimi ve yönetmelik rehberliği sunar. Uydurma bilgiyi en aza indirmek için *Zero-Hallucination Prompting* kullanır. |
| 2 | **Canlı Yemekhane** | SABİS'ten anlık menüyü çeker. |
| 3 | **Kafe Yoğunluk Analitiği** |  Taş Kafe, Lumo Coffee, Coffy SAÜ, Adıbahçe, Espressolab SAÜ ve Merkez Kütüphane Kafe için saatlik tahmini doluluğu interaktif grafikle gösterir. |
| 4 | **Not & Baraj Hesaplayıcı** | Vize notu ve hedef ortalamaya göre gereken final notunu hesaplar, "finalden en az 40 alma" şartını otomatik denetler. |
| 5 | **Ulaşım & SAKUS Rehberi** | 4, 15, 24K, 26, 16K ve 6 numaralı hatların saatlerini, güzergâhlarını ve canlı SAKUS harita takibini sunar. |

---

## 🛠️ Kullanılan Teknolojiler

| Alan | Teknoloji |
|------|-----------|
| **Arayüz** | Streamlit + özel CSS (SAÜ kurumsal rengi `#002855`, arka plan `#f3f7f8`) |
| **Yapay Zekâ (LLM)** | Groq API üzerinden `llama-3.3-70b-versatile` ve `qwen/qwen3.8-27b` |
| **Veri Çekme** | `requests`, `BeautifulSoup` (SABİS web scraping) |
| **Görselleştirme** | Plotly |
| **Veri İşleme** | pandas, pytz |
| **Yayınlama** | Hugging Face Spaces |

---

## 🚀 Nasıl Çalıştırılır?

> 💡 Kurulum yapmadan denemek için [canlı demoyu](https://huggingface.co/spaces/Anil-yilmaz/UniHubAI) kullanabilirsiniz.

**1. Depoyu klonlayın**
```bash
git clone https://github.com/anilyilmaz1/UniHubAI.git
cd UniHubAI
```

**2. Sanal ortam oluşturun ve bağımlılıkları yükleyin** (Python 3.10+)
```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

**3. Groq API anahtarını tanımlayın**

Anahtarı [console.groq.com](https://console.groq.com) adresinden ücretsiz alabilirsiniz.
```bash
# Linux / macOS
export GROQ_API_KEY="anahtariniz"

# Windows (PowerShell)
$env:GROQ_API_KEY="anahtariniz"
```

**4. Uygulamayı başlatın**
```bash
streamlit run app.py
```
Tarayıcıda `http://localhost:8501` adresi açılır.

---

## 📁 Proje Yapısı

```
UniHubAI/
├── app.py             # Ana Streamlit uygulaması
├── requirements.txt   # Bağımlılıklar
└── README.md
```

---

## 👥 Ekip

| İsim | Rol |
|------|-----|
| **Anıl YILMAZ** | Full-Stack & AI Developer (Kodlama, API & Sistem Mimarisi) |
| **Senanur ADIGÜZEL** | UI/UX Designer & Presenter (Sidebar Tasarımı & Sunum) |

---

## 📄 Lisans

Bu proje [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) lisansı ile yayınlanmıştır.