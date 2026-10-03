
# Overview
## Data Source : 
- Production
- Downtime
- Equipment
- Incident
- Engineering
- EEnergy & HSE Data

## Purpose
- Integrate fragmented manufacturing data
- identify root causes
- prioritize alers
- track actions

# Flow
Data foundation -> Single pane of glass (dashboard) -> ai root cause -> action recommendation

# Data Foundation
## Production Data
Angka sensor telemetri tiap jam dari OSIsoft PI (suhu, getara, tekanan, arus listrik)

Menggunakan OSIsoft PI / AVEVA PI System : software untuk merekam dan menyimpan data sensor pabrik secara terus-menerus (time-series).
## Equipment Performace
Buku manual batas aman mesin (kapas statusnya normal, alarm, atau trip)
## Incident Database
Buku catatan 380 insiden masa lalu lengkap dengan jam downtime dan nilai kerugian dalam dolar
## RCA & Downtime
dokumen investigasi yang menjelaskan kenapa suatu alat bisa rusak.

| Dokumen | Alat yang Terkena Dampak | Gejala / Insiden Lapangan | Akar Masalah Sebenarnya (*True Root Cause*) |
| :--- | :--- | :--- | :--- |
| **RCA 1** | Pompa Umpan `PU-2101B` | *Mechanical seal* bocor, cairan kimia merembes. | **Sistem Kontrol DCS:** Tidak ada interlock proteksi laju alir minimum saat perpindahan tangki umpan, sehingga pompa berputar kering (*dry run*). |
| **RCA 2** | Kompresor Gas `KO-3201` | Kompresor mendadak mati (*trip*) akibat getaran tinggi. | **Kualitas Pelumas:** Oli pelumas terkontaminasi air karena pabrik tidak memiliki sensor pemantau air online (*water-in-oil*). |
| **RCA 3** | Pompa Air Pendingin `PM-4405B` | Motor terbakar dan mati karena bantalan (*bearing*) kepanasan (84 °C). | **SOP Pemeliharaan:** Jadwal pemberian gemuk (*greasing*) dipatok kaku per 12 bulan, padahal beban alat butuh pelumasan tiap 4 bulan. |
| **RCA 4** | Penukar Panas `HE-3301` | Saluran pipa mampet (*high fouling*) dan pabrik terpaksa menurunkan laju produksi. | **Bahan Baku & Alarm:** Umpan kimia mengandung fraksi berat di atas batas desain, dan tidak ada sistem alarm berbasis selisih tekanan pipa (dP). |
| **RCA 5** | *Blower* Produk `BL-5702` | Kipas industri bergetar hebat (11 mm/s) hingga harus dimatikan darurat. | **Prosedur Mekanikal:** Pemasangan kopling tidak sejajar (*misalignment*) dan tidak ada jadwal pemeriksaan rutin menggunakan laser alignment. |

# Single pane of Glass (SPOG)
Menggabungkan seluruh sistem yang terpisah ke dalam satu halaman terintegrasi. Informasi di dalam SPOG : 
1. Laju Produksi : Berapa ton polimer atau etilena yang sedang diproduksi saat ini
2. Efisiensi Energi : Berapa mengawatt listrik atau ton uap steam yang dikonsumsi per ton produk
3. Kepatuhan Emisi : Berapa emisi yang dihasilkan pembakaran gas di flare dan cerobong asap
4. Downtime Risk : mesin mana yang sedang mendekati batas bahaya, lengkap dengan prediksi sisa umur operasionalnya.

# Referensi Paper
* **Penyatuan Sinyal Sensorik Waktu Nyata:** Mengolah ribuan tag telemetri sensor OSIsoft PI tanpa jeda waktu memakai [TimesNet (arXiv:2210.02186)](https://arxiv.org/abs/2210.02186) dan [Anomaly Transformer (arXiv:2110.02642)](https://arxiv.org/abs/2110.02642).
* **Visualisasi Pohon Kausalitas di Layar:** Menampilkan akar masalah di layar secara grafis memakai [Causally Guided Transformer (arXiv:2604.17998)](https://arxiv.org/abs/2604.17998) dan agen interaktif [FaultExplainer (arXiv:2412.14492)](https://arxiv.org/abs/2412.14492).
* **Batasan Fisika pada Angka Rekomendasi:** Menjamin nilai rekomendasi di layar mematuhi hukum termodinamika kimia via [Stiff-PINN Process Control (arXiv:2011.04520)](https://arxiv.org/abs/2011.04520) dan tolok ukur industri [Tennessee Eastman Process (arXiv:2303.05904)](https://arxiv.org/abs/2303.05904).

# Jobdesk
| Bidang | Penanggung Jawab | Fokus Tugas Utama | Output Konkret untuk Proposal |
| :--- | :--- | :--- | :--- |
| **Teknik Kimia** (2 Orang) | Rekan Tim | 1. Membedah P&ID, batas operasi aman, dan mekanisme kerusakan fisik (kavitasi, coking, surge, fouling).<br>2. Validasi kausalitas: memastikan hubungan antar-variabel masuk akal secara fisika/kimia, bukan sekadar korelasi palsu.<br>3. Menyusun rekomendasi mitigasi SOP lapangan dan hitungan neraca massa/kerugian produksi riil. | - Matriks batas parameter proses per unit alat.<br>- Alur logika sebab-akibat (pohon kegagalan/RCA fisik).<br>- Rekomendasi tindakan korektif untuk operator lapangan. |
| **Teknik Komputer** (1 Orang) | Azka | 1. Merancang arsitektur sistem dan alur data (integrasi data OSIsoft PI, log insiden, dan sistem pemeliharaan).<br>2. Memilih dan merancang model AI: deteksi anomali runtun waktu (multivariate time-series) dan perumusan graf kausal (causal AI).<br>3. Merancang visualisasi dasbor terpadu (mockup UI/UX) dan sistem otomatisasi peringatan dini. | - Diagram arsitektur data dan alur komputasi sistem.<br>- Spesifikasi model AI deteksi anomali dan inferensi kausal.<br>- Desain tampilan dasbor (wireframe) dan alur kerja peringatan. |
