---
title: UniHub AI
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
short_description: Sakarya Üniversitesi Akıllı Kampüs ve Akademik Asistanı
license: apache-2.0
---

# 🎓 UniHub AI - SAÜ Akıllı Kampüs Asistanı

UniHub AI, Sakarya Üniversitesi (SAÜ) öğrencilerinin akademik süreçlerde zaman kaybetmesini önlemek, ders ve staj yönetmeliklerinden canlı yemekhane menüsüne ve kafe yoğunluk grafiklerine kadar tüm kampüs ihtiyaçlarını tek bir noktada toplayan yapay zekâ destekli dijital asistandır.

---

## 🚀 Canlı Demo & Bağlantılar
- **Canlı Uygulama (Space):** [UniHub AI Space](https://huggingface.co/spaces/Anil-yilmaz/UniHubAI)
- **GitHub Deposu:** [Anil-yilmaz/hackathon-starter](https://github.com/Anil-yilmaz/UniHubAI)

---

## ⚙️ Sistem Mimarisi ve Çalışma Mantığı

Uygulama, öğrencilerin kampüs içi bilgi erişimini hızlandırmak için **5 entegre modül ve dinamik bağlam (context) yapısı** ile çalışır:

1. **1. Modül (Bölüm Bazlı Akademik & Staj Asistanı):** Öğrencinin seçtiği fakülte ve bölüm bağlamına özel %100 doğru staj yönergesi, mazeret dilekçesi, sınav takvimi ve akademik yönetmelik rehberliği sağlar (Zero-Hallucination Prompting).
2. **2. Modül (Canlı SABİS Scraping & Besin Değerleri):** `BeautifulSoup` ve `requests` ile SABİS yemekhane sisteminden anlık çekilen menü verisini işler; yemek bazlı kalori ve makro besin öğelerini (protein, karbonhidrat, yağ) hesaplayarak sunar.
3. **3. Modül (Kafe Yoğunluk Analitiği):** Kampüsteki populer kafelerin (*Lumo Coffee, Coffy SAÜ, Adıbahçe, Taş Kafe*) saatlik tahmini doluluk oranlarını Plotly interaktif sütun grafikleriyle görselleştirir.
4. **4. Modül (SAÜ Not & Baraj Hesaplayıcı):** Vize notu ve hedef ortalamaya göre gereken final puanını hesaplarken, SAÜ'nün **"Finalden en az 50 alma zorunluluğu"** kuralını otomatik denetler.
5. **5. Modül (Ulaşım & SAKUS Rehberi):** Kampüs otobüs hatlarının (*4, 15, 24, 54*) kalkış saatlerini, güzergahlarını ve canlı SAKUS harita takibini erişime sunar.

---

## 🛠️ Öne Çıkan Teknolojiler & Tasarım Detayları

Proje, yüksek performanslı bir kullanıcı deneyimi için modern araçlarla geliştirilmiştir:

- **Arayüz & Kurumsal Kimlik:** Streamlit altyapısı üzerine enjekte edilen özel CSS ile Sakarya Üniversitesi kurumsal lacivert (`#002855`) ve `#f3f7f8` açık gri arka plan renk paleti.
- **Yapay Zekâ (LLM):** Groq API altyapısı üzerinden yüksek hızlı `llama-3.3-70b-versatile` ve `qwen/qwen3.8-27b` modelleri.
- **Veri İşleme &