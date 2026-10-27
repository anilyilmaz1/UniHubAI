# 🎓 UniHub Academic AI - SAÜ Akıllı Kampüs Asistanı

UniHub Academic AI, Sakarya Üniversitesi öğrencilerinin kampüs yaşamını kolaylaştırmak, akademik süreçlerde zaman kaybını önlemek ve tek bir noktadan tüm kampüs verilerine ulaşmalarını sağlamak amacıyla geliştirilmiş yapay zeka destekli bir dijital kampüs portalıdır.

---

## 🚀 Öne Çıkan Özellikler

- 💬 **Akıllı Akademik AI Asistan:** SAÜ akademik takvimi, vize/final tarihleri ve fakülte/bölüme özel staj yönergeleri hakkında %100 doğru ve hızlı yanıtlar.
- 🍱 **SABİS Canlı Yemekhane & Besin Değerleri:** SABİS sisteminden çekilen günlük yemek menüsü, kalori ve makro besin değerleri (protein, karbonhidrat, yağ).
- ☕ **Kafe Yoğunluk Analizi:** Kampüsteki kafelerin (*Lumo, Coffy, Adıbahçe, Taş Kafe*) saatlik tahmini doluluk durumları ve görsel grafikleri.
- 🚌 **Ulaşım & SAKUS Rehberi:** Kampüs hatları (*4, 15, 24, 54*) güzergah bilgileri ve canlı SAKUS otobüs takip erişimi.
- 🧮 **SAÜ Not & Baraj Hesaplayıcı:** Vize notuna göre dersten geçmek için gereken final puanını ve SAÜ'nün **50 final baraj kuralını** hesaplayan araç.

---

## 🛠️ Kullanılan Teknolojiler

- **Arayüz:** Streamlit, Custom HTML/CSS (SAÜ Kurumsal Tema)
- **Yapay Zeka (LLM):** Groq API (`llama-3.3-70b` / `qwen3.8-27b`)
- **Veri Çekme (Scraping):** BeautifulSoup4, Requests
- **Görselleştirme & Veri:** Pandas, Plotly Express

---

## 💻 Yerel Kurulum & Çalıştırma

1. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt