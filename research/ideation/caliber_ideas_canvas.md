# Masalah: Mitigasi Unplanned Plant Trip pada Steam Cracker
**Target Korporasi:** PT Chandra Asri Pacific Tbk (TPIA) — Kompleks Petrokimia Cilegon  

---

## 1. Overview Masalah (Mengapa Ini Sangat Kritis)

### Apa itu Steam Cracker & Plant Trip?
* **Jantung Kilang Petrokimia:** *Steam cracker* adalah fasilitas utama yang memecah bahan baku minyak (*Naphtha*) pada suhu ekstrem (750°C–875°C) menjadi bahan dasar plastik (*Ethylene & Propylene*).
* **Definisi Plant Trip:** Penghentian darurat otomatis oleh sistem keselamatan hardware (*SIL-3*) ketika parameter proses (suhu, tekanan, atau getaran kompresor) melampaui batas aman untuk mencegah ledakan atau kerusakan katastropik.

### Rincian Kerugian $1.2M – $2.5M per Insiden
* **1. Opportunity Loss ($500k – $1.2M):** Proses menyalakan ulang (*restart*) hingga produk kembali murni (*on-spec*) memakan waktu **24 hingga 72 jam**, menghilangkan potensi produksi 2.000–5.000 ton.
* **2. Flaring & Waste Feedstock ($300k – $600k):** Saat trip, ratusan ton gas hidrokarbon di dalam sistem terpaksa dialihkan ke cerobong api (*flare*) dan dibakar sia-sia demi alasan keselamatan.
* **3. Thermal Shock ($200k – $400k):** Penurunan suhu mendadak dari 850°C ke suhu ruang menimbulkan tegangan mekanis parah pada pipa reaktor (*radiant coil*), mempercepat kerusakan dan pembentukan kerak karbon (*coking*).
* **4. Biaya Re-start ($150k – $300k):** Konsumsi masif gas nitrogen untuk pembersihan pipa (*purging*) serta lonjakan konsumsi bahan bakar untuk memanaskan kembali tungku pembakaran (*furnace*).

### Frekuensi & Celah Peluang Operasional
* **Frekuensi:** *Full plant trip* (mati total) terjadi rata-rata **1–3 kali/tahun**, sedangkan *partial furnace trip* terjadi **5–10 kali/tahun**.
* **Alarm Flood:** Ruang kontrol menerima 1.200–3.500 alarm per hari, membuat operator mengalami *cognitive overload* dan terlambat mengenali bahaya nyata.
* **Jendela Peluang (Lead Time):** Anomali mikro pada data sensor sebenarnya sudah muncul **20 hingga 60 menit** sebelum alarm batas ambang konvensional berbunyi, memberi ruang intervensi jika operator dipandu dengan tepat.

---

## 2. Ide & Hipotesis Solusi (Azka's Sandbox)

*Gunakan bagian ini untuk menuangkan ide awal, alur kerja, atau arsitektur sistem yang ingin diajukan.*

### A. Konsep & Cara Kerja
* **Nama Ide / Solusi:** 
* **Alur Singkat:** *(Bagaimana alur dari data sensor pabrik hingga menghasilkan rekomendasi tindakan untuk operator?)*
* **Diferensiasi:** *(Mengapa pendekatan ini lebih pintar dibanding sistem DCS / SCADA bawaan pabrik?)*

### B. Implementasi & Guardrail Keselamatan
* **Data yang Digunakan:** *(Contoh: Suhu dinding furnace TMT, tekanan uap, getaran kompresor, log alarm).*
* **Batas Keamanan:** *(Bagaimana memastikan sistem ini tidak mengganggu sistem keselamatan hardware SIL-3?)*

### C. Target Dampak Bisnis
* **EBITDA Saving:** *(Contoh: Mencegah 1x full trip per tahun = mengamankan $1.5M+ EBITDA).*
* **Waktu Respon:** *(Memangkas waktu diagnosa operator dari 45 menit menjadi < 5 menit).*

---

## 3. Cheatsheet Rujukan Teknis (Opsional)

Rujukan pendukung sederhana jika ingin memperkuat argumen teknis di depan juri:
* **Deteksi Dini Anomali:** Model *TimesNet* ([arXiv:2210.02186](https://arxiv.org/abs/2210.02186)) dan *Anomaly Transformer* ([arXiv:2110.02642](https://arxiv.org/abs/2110.02642)) untuk menangkap anomali multivariat sensor sebelum alarm ambang batas berbunyi.
* **Diagnosa Kausal & Akar Masalah:** Model graf kausal ([arXiv:2604.17998](https://arxiv.org/abs/2604.17998), [arXiv:2412.14492](https://arxiv.org/abs/2412.14492)) untuk membedakan pemicu utama vs alarm turunan.
* **Benchmark Industri Kimia:** *Tennessee Eastman Process* ([arXiv:2303.05904](https://arxiv.org/abs/2303.05904)) sebagai standar validasi deteksi gangguan proses kimia.

---

## 4. Pertanyaan Kritis Penguji / Juri (Red-Teaming)

- [ ] Bagaimana cara menjamin rekomendasi AI tidak salah/halusinasi saat kondisi kilang tidak stabil?
- [ ] Apakah solusi ini bersifat *advisory* (rekomendasi ke operator) atau *closed-loop* (otomatis mengubah katup)?
- [ ] Bagaimana membuktikan sistem ini berhasil jika dalam 1 tahun kebetulan kilang tidak mengalami trip?
