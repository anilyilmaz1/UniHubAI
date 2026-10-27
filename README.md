# 🎓 UniHub Academic AI - Sakarya Üniversitesi Akıllı Kampüs Asistanı

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-API-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)

**UniHub Academic AI**, Sakarya Üniversitesi (SAÜ) öğrencilerinin akademik takvim, sınav tarihleri, fakülte/bölüm bazlı staj başvuru süreçleri, mazeret dilekçeleri ve günlük kampüs yaşamı hakkındaki sorularına anında yanıt veren **kişiselleştirilmiş akıllı chatbot platformudur**.

---

## 🚀 Öne Çıkan Özellikler

* 🎓 **Fakülte ve Bölüm Bağlamı (Contextual AI):** Sol menüden seçilen fakülte ve bölüme göre (Örn: *Bilgisayar Mühendisliği 40 Günlük Stajı* veya *İşletme Fakültesi 7+1 Mesleki Uygulaması*) özelleştirilmiş yanıtlar üretir.
* 📅 **Akademik Takvim & Sınav Rehberi:** Vize, final, bütünleme, mazeret sınavı başvuru tarihleri ve tek ders sınav kurallarını anında yanıtlar.
* 📝 **Adım Adım Staj Süreçleri:** Staj formlarının indirilmesinden SGK girişlerine, staj defterinin teslimine kadar tüm süreci rehber eşliğinde sunar.
* 🌐 **SABİS Canlı Yemekhane Menüsü:** Sakarya Üniversitesi SABİS sisteminden (`menu.sabis.sakarya.edu.tr`) web scraping altyapısıyla günün canlı yemek menüsünü çekip gösterir.
* ⚡ **Hızlı Sorular (Quick Prompts):** Öğrencilerin en çok sorduğu sorular için tek tıkla sorgu çalıştırma butonları içerir.

---

## 🛠️ Teknoloji Yığını

* **Arayüz (Frontend):** Streamlit
* **Yapay Zeka (LLM Orchestration):** Groq API (`qwen/qwen3.8-27b`)
* **Veri Çekme (Web Scraping):** BeautifulSoup4, Requests
* **Veri İşleme:** Pandas
* **Dağıtım (Deployment):** Hugging Face Spaces / GitHub

---

## 💻 Kurulum ve Çalıştırma

### 1. Repoyu Klonlayın
```bash
git clone [https://github.com/kullanici-adi/unihub-academic-ai.git](https://github.com/kullanici-adi/unihub-academic-ai.git)
cd unihub-academic-ai