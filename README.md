# Steam Cracker Anomaly Detection & Prescriptive RCA Engine

Aplikasi demonstrasi proof-of-concept (POC) untuk deteksi dini anomali multivariate sensor dan rekomendasi tindakan mitigasi cepat pada unit Steam Cracker.

---

## 1. Landasan Ilmiah (Verified Research Papers)

Arsitektur model dan sistem inferensi dalam repositori ini dibangun berdasarkan riset ilmiah terverifikasi:
- **GDN (Graph Deviation Network)**: [arXiv:2106.06947](https://arxiv.org/abs/2106.06947) - Mempelajari relasi struktural antar sensor proses untuk mendeteksi deviasi sebelum alarm batas absolut terpicu.
- **DCdetector**: [arXiv:2306.10347](https://arxiv.org/abs/2306.10347) - Representasi kontras multi-skala waktu untuk anomali transien dan degradasi bertahap.
- **Equipment Health Index**: [arXiv:2405.04990](https://arxiv.org/abs/2405.04990) - Estimasi degradasi kesehatan aset mengacu pada standar vibrasi mesin industri ISO 10816-3.
- **Causal Fault Attribution**: [arXiv:2203.11321](https://arxiv.org/abs/2203.11321) - Pelacakan perambatan gangguan proses dan penentuan akar penyebab trip.
- **Knowledge Graph-Enhanced RAG**: [arXiv:2406.18114](https://arxiv.org/abs/2406.18114) - Ekstraksi basis pengetahuan failure mode untuk rekomendasi tindakan preskriptif ke operator.

---

## 2. Struktur Repositori

```
.
├── app.py                      # Entry point aplikasi Streamlit demo
├── requirements.txt            # Daftar pustaka Python untuk deployment
├── .gitignore                  # Filter data sensitif dan file non-kode
├── README.md                   # Panduan instalasi dan deployment
└── src/                        # Modul inti aplikasi
    ├── pipeline/
    │   └── replay_loader.py    # Modul pembaca dan replay timeseries
    ├── models/
    │   └── health_index.py     # Engine kalkulasi Health Index (0-100%)
    └── app/                    # Komponen antarmuka pengguna
```

---

## 3. Cara Menjalankan Aplikasi Secara Lokal

### Prasyarat
- Python 3.10 atau versi yang lebih baru
- Virtual environment (direkomendasikan)

### Langkah Instalasi

1. **Clone Repositori**:
   ```bash
   git clone https://github.com/Azka-Nabihan/SCC-Caliber.git
   cd SCC-Caliber
   ```

2. **Buat dan Aktifkan Virtual Environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan Aplikasi Streamlit**:
   ```bash
   streamlit run app.py
   ```

---

## 4. Panduan Deployment (Cloud Hosting)

Aplikasi ini siap dideploy langsung ke berbagai layanan cloud:
- **Streamlit Community Cloud**: Hubungkan repositori GitHub ini, pilih file utama `app.py`, lalu deploy.
- **HuggingFace Spaces**: Buat Space baru dengan SDK Streamlit, lalu hubungkan repo ini.
- **Render / Railway / VPS**: Jalankan container atau service dengan perintah:
  ```bash
  streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
  ```
