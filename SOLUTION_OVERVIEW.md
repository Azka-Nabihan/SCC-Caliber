# Ringkasan Solusi: Deteksi Dini Anomali dan Rekomendasi Tindakan Plant ZCU

Dokumen ini ditujukan untuk rekan satu tim dan siapa pun yang ingin memahami cara kerja sistem SCC-Caliber tanpa harus membaca tumpukan kode program.

---

## 1. Masalah yang Diselesaikan

Di pabrik petrokimia Chandra Asri (khususnya unit Steam Cracker / Plant ZCU), kompresor gas retak KO-3201 memegang peranan vital. Jika mesin ini mati mendadak, seluruh rangkaian proses perengkahan gas ikut terhenti.

Sistem alarm ruang kendali (DCS) konvensional memiliki kelemahan mendasar:
* Alarm baru berbunyi saat getaran menembus batas tinggi (45 mikron).
* Di titik tersebut, komponen mekanikal di dalam mesin biasanya sudah terlanjur mengalami aus atau kerusakan fisik.
* Jeda waktu bagi operator untuk bertindak sangat sempit sebelum sistem proteksi otomatis mematikan mesin secara darurat (trip di 75 mikron).

Contoh nyatanya tercatat pada insiden historis AR-2026-ZCU-0142. Kompresor KO-3201 mati mendadak dan memicu henti pabrik selama 32 jam, dengan kerugian riil sebesar 1,584 juta dolar AS. Akar masalahnya berawal dari kebocoran kecil pada tabung pendingin oli (cooler HE-3301). Air pendingin merembes ke sistem pelumas, merusak daya lumas oli, lalu mengikis bantalan babbitt sampai getaran melonjak dan memicu trip.

Tantangannya: bagaimana kita bisa menangkap gejala awal kerusakan tersebut belasan jam sebelum alarm ruang kendali berbunyi, sehingga pabrik tidak perlu mati darurat?

---

## 2. Pendekatan Solusi

Solusi ini dirancang bukan untuk meramal masa depan secara spekulatif, melainkan mendeteksi penyimpangan hubungan antar-sensor proses lebih awal, lalu langsung menghubungkannya dengan prosedur perbaikan yang sudah terbukti di lapangan.

Pendekatan kami bertumpu pada tiga hal sederhana:
1. Mendeteksi deviasi sebelum batas alarm tersentuh. Alih-alih menunggu satu sensor getaran melewati batas bahaya, sistem memantau keterkaitan antara enam sensor proses sekaligus. Hubungan janggal antara laju alir, tekanan, suhu, arus listrik, dan getaran ditangkap sebagai sinyal awal.
2. Menghitung risiko dengan rumus produksi pabrik. Potensi kerugian dihitung langsung dari kapasitas produksi riil dan durasi henti, bukan dari angka perkiraan abstrak.
3. Memberikan rekomendasi yang bersumber dari arsip resmi. Prosedur penanganan diambil langsung dari dokumen investigasi kegagalan pabrik (RCA), bukan teks karangan kecerdasan buatan.

Hasilnya, sistem mampu memberikan waktu peringatan dini (lead time) 16 jam mendahului alarm DCS 45 mikron, atau 46 jam sebelum trip darurat. Jeda waktu ini memberi kesempatan bagi tim pabrik untuk beralih dari henti darurat 32 jam ke henti terencana (controlled shutdown) selama 8 jam, menghemat potensi kerugian hingga 1,188 juta dolar AS.

---

## 3. Alur Kerja Sistem (Pipeline)

Sistem bekerja dalam alur empat tahap yang saling berkesinambungan, mulai dari penerimaan data mentah di lapangan hingga penyajian keputusan di ruang kendali:

| Tahap | Fokus Utama | Output Kunci |
| :--- | :--- | :--- |
| **Tahap 1: Data Ingestion & Sanitasi** | Pembersihan sinyal sensor dari anomali instrumen | Data deret waktu bersih siap inferensi |
| **Tahap 2: Deteksi Dini & Health Index** | Pemantauan graf sensor dan degradasi fisis aset | Status operasional gabungan (Early Warning / Amber) |
| **Tahap 3: Kontekstualisasi & Kartu Tindakan** | Penjodohan insiden, estimasi biaya, dan SOP resmi | Kartu tindakan preskriptif dan narasi shift briefing |
| **Tahap 4: Antarmuka Kendali (Dashboard)** | Penyajian terpadu kondisi armada dan simulasi risiko | Visualisasi telemetri, kurva P-F, dan tiket SAP |

---

### Rincian Input, Proses, dan Output Tiap Tahap

#### Tahap 1: Data Ingestion dan Pembersihan Data
* **Input**: Data deret waktu sensor proses dari sistem pencatat pabrik (PI System / DCS) yang mencakup laju alir, tekanan hisap dan buang, temperatur bearing, arus motor, getaran poros, serta status jalan mesin.
* **Proses**: Data dialirkan melalui tiga lapisan validasi:
  1. Batas fisik instrumen: Menyaring angka di luar skala operasional yang wajar.
  2. Pendeteksian sensor macet: Mendeteksi tag sensor yang nilainya tidak berubah dalam durasi panjang akibat kegagalan transmitter.
  3. Status operasional: Mengidentifikasi kondisi henti pabrik atau periode awal penyalaan mesin (start-up mask) agar fluktuasi transien tidak memicu alarm palsu.
* **Output**: Data telemetri bersih yang siap diproses oleh model komputasi tanpa distorsi derau instrumen.

#### Tahap 2: Deteksi Anomali dan Evaluasi Kesehatan Aset
* **Input**: Data telemetri bersih multi-sensor dan topologi keterkaitan alat pada diagram perpipaan (P&ID).
* **Proses**: Dua mesin evaluasi bekerja secara paralel:
  1. Graph Deviation Network (GDN): Memprediksi nilai normal masing-masing sensor dan menghitung deviasi korelasi multi-sensor secara simultan. Jika deviasi melebihi ambang batas secara persisten selama dua jam berturut-turut, sinyal anomali diaktifkan.
  2. Health Index Engine: Menghitung penalti keterdegradatan masing-masing parameter fisis terhadap batas aman desain (standar ISO 10816-3). Jika salah satu parameter mendekati batas kritis, penalti eskalasi terburuk otomatis diaktifkan.
  3. Triplet Logic: Menggabungkan status jalan, status anomali GDN, nilai Health Index, dan angka getaran aktual untuk menetapkan status operasional mesin secara tegas.
* **Output & Bukti Nyata (Jam 633)**: Pada kompresor KO-3201, getaran radial masih berada di angka normal 31,2 mikron (jauh di bawah alarm DCS 45 mikron) dan Health Index masih 98,6% (Normal). Namun, GDN mendeteksi deviasi korelasi dengan skor 10,72 (ambang batas: 3,11), sehingga sistem menetapkan status **Early Warning (Amber)** tepat 16 jam sebelum alarm DCS berbunyi.

#### Tahap 3: Kontekstualisasi dan Rekomendasi Preskriptif (Action Card)
* **Input**: Notifikasi status anomali, identitas aset (tag number), dan data telemetri jam berjalan.
* **Proses**: Sistem menyusun kartu tindakan terpadu (Action Card) melalui empat langkah terkoordinasi:
  1. Penjodohan Insiden Historis: Mencocokkan pola anomali dengan basis data 380 insiden kilang secara hierarkis (kecocokan tag, komponen alat, hingga kelas aset) dengan penyaring tanggal untuk mencegah kebocoran data masa depan.
  2. Kalkulasi Risiko Finansial: Menghitung selisih dampak kerugian produksi antara skenario henti darurat (uncontrolled trip) versus perbaikan terencana (controlled shutdown) menggunakan rumus kapasitas pabrik.
  3. Penarikan Rekomendasi Resmi: Mengambil prosedur mitigasi cepat (dalam 30 menit) dan rencana tindakan pencegahan permanen (CAPA) langsung dari dokumen investigasi resmi (RCA pabrik).
  4. Penyusunan Narasi Briefing: Mengonversi data teknis kartu tindakan menjadi paragraf ringkas untuk pergantian shift operator via AI Copilot (didukung jaring pengaman fallback deterministik 0 ms).
* **Output & Bukti Nyata (Jam 633)**: Kasus kompresor KO-3201 langsung terhubung dengan insiden AR-2026-ZCU-0142 (kebocoran pendingin oli HE-3301). Sistem menyajikan potensi penghematan 1,188 juta dolar AS (downtime berkurang dari 32 jam menjadi 8 jam) serta instruksi inspeksi pelumas dan suku cadang bearing yang harus segera disiapkan.

#### Tahap 4: Antarmuka Kendali Tunggal dan Eksekusi Keputusan (Single Pane of Glass)
* **Input**: Seluruh hasil telemetri, skor anomali, kartu tindakan, dan matriks keandalan armada aset.
* **Proses**: Dasbor interaktif Streamlit memetakan data ke dalam tiga modul kerja:
  1. Cockpit Eksekutif & Briefing: Menyajikan indikator visual kondisi aset, tombol narasi shift briefing, dan tiket perintah kerja SAP (Work Order).
  2. Analisis Telemetri & Decision Simulator: Menampilkan grafik tren multi-sensor, diagram alur proses (P&ID), serta kurva keputusan P-F interaktif yang memperlihatkan peningkatan biaya per jam jika tindakan mitigasi ditunda.
  3. Matriks Risiko Armada ZCU: Memetakan status risiko 56 peralatan di Plant ZCU (17 mesin rotasi, 10 sistem kelistrikan, dan 29 bejana statis) berdasarkan kelas kekritisan dan potensi kerugian.
* **Output**: Operator dan pimpinan unit memperoleh visibilitas instan dengan latensi di bawah 2 milidetik untuk memutuskan jadwal pemeliharaan terencana tanpa keraguan data.

---

## 4. Model AI yang Digunakan dan Perannya

Di dalam sistem ini, kita tidak menggunakan sembarang AI untuk semua hal. AI hanya digunakan di dua tempat spesifik di mana komputasi statistik dan pengolahan bahasa benar-benar memberikan nilai tambah:

### A. Graph Deviation Network (GDN)
* **Jenis Model**: Deep Learning berbasis graf (PyTorch).
* **Tahap Penggunaan**: Tahap 2 (Deteksi Anomali Sensor).
* **Peran**:  
  Memetakan relasi antar-enam sensor pada kompresor KO-3201 (laju alir umpan, tekanan hisap/buang, arus motor, suhu bearing, getaran radial poros, dan kapasitas pabrik).  
  Model memprediksi nilai masing-masing sensor pada langkah berikutnya berdasarkan nilai-nilai sebelumnya. Ketika nilai aktual sensor menyimpang signifikan dari prediksi normalnya, model menghitung skor deviasi berbasis residual terstandarisasi. Jika skor melampaui ambang batas selama dua jam berturut-turut, sinyal anomali diaktifkan.

### B. Large Language Model (Google Gemini Flash / Flash-Lite API)
* **Jenis Model**: Generative AI / LLM via cloud API.
* **Tahap Penggunaan**: Tahap 3 (Operational Copilot untuk Shift Briefing dan Simulasi Skenario).
* **Peran**:  
  1. Merangkum fakta teknis dari kartu tindakan menjadi satu paragraf ringkas (maksimal 60 kata) dengan gaya bahasa briefing pergantian shift untuk para operator ruang kendali.  
  2. Menjawab pertanyaan skenario operasional yang diajukan operator (misalnya dampak jika laju produksi diturunkan 10%, atau ambang batas suhu oli pelumas).
* **Batasan Ketat**:  
  Model bahasa ini tidak diizinkan mengarang angka kerugian, rumus fisika, atau prosedur tindakan baru. Seluruh konteks rekayasa proses, ambang batas instrumen, dan data insiden disuntikkan secara terstruktur melalui mekanisme RAG lokal yang terkunci.

---

## 5. Batasan Tegas: Bagian AI/ML vs Bagian Deterministik (Rule-Based)

Untuk menjamin keselamatan dan akurasi di pabrik kimia, sistem membagi tanggung jawab secara kaku antara komponen berbasis model statistik/AI dan komponen aturan deterministik:

| Komponen Sistem | Sifat Pendekatan | Cara Kerja dan Landasan |
| :--- | :--- | :--- |
| **Pendeteksian Pola Hubungan Antar Sensor** | **AI / Deep Learning** (GDN) | Model statistik graf yang mempelajari deviasi residual nilai prediksi vs sensor riil. |
| **Ringkasan Narasi Shift Briefing** | **AI / LLM** (Gemini) | Perangkum teks dari data terstruktur ke format komunikasi ruang kendali. |
| **Simulasi Tanya-Jawab Operator (What-If)** | **AI / LLM** (Gemini RAG) | Jawaban kontekstual berbasis batasan data operasional kilang. |
| **Kalkulasi Health Index (0-100%)** | **Deterministik** (Rule-Based) | Formula penalti terbobot matematis mengacu pada standar vibrasi ISO 10816-3. Tidak menggunakan AI. |
| **Penentuan Status Operasional Mesin** | **Deterministik** (Rule-Based) | Logika tiga serangkai yang mengevaluasi status jalan mesin, status anomali GDN, skor Health Index, dan nilai getaran fisik. |
| **Perhitungan Kerugian & Penghematan Finansial** | **Deterministik** (Fisika Proses) | Rumus pasti: Durasi Downtime (jam) x Laju Pabrik (55 Ton/Jam) x Harga Gas (900 USD/Ton). |
| **Pencarian Riwayat Insiden Kilang** | **Deterministik** (Database Query) | Pencocokan berjenjang (Tag spesifik, komponen, kelas aset) dengan penyaring tanggal untuk mencegah kebocoran data masa depan. |
| **Rekomendasi Tindakan Darurat & CAPA** | **Deterministik** (Knowledge Base) | Data murni disalin dari dokumen resmi investigasi pabrik (RCA 2 dan RCA 4). Tidak ada teks yang dikarang oleh model. |
| **Jaring Pengaman Copilot (Fallback 0 ms)** | **Deterministik** (Template Guardrail) | Jika koneksi internet atau API AI terputus, sistem seketika menyajikan ringkasan berbasis template terverifikasi tanpa jeda waktu. |

Dengan pembagian ini, tidak ada satu pun keputusan kritis keselamatan atau angka kerugian finansial yang bergantung pada perkiraan probabilitas atau halusinasi AI.

---

## 6. Landasan Ilmiah, Referensi, dan Realitas Implementasi

Kami membedakan secara jujur antara metode yang benar-benar kami bangun dalam kode program dan konsep yang berfungsi sebagai referensi atau inspirasi konseptual:

### A. Metode yang Benar-Benar Diimplementasikan dalam Kode
1. **Graph Deviation Network (GDN)**: Rujukan utama dari Deng & Hooi, AAAI 2021 ([arXiv:2106.06947](https://arxiv.org/abs/2106.06947)).  
   * **Yang Diambil**: Arsitektur graph attention yang menyematkan identitas sensor (embeddings), model prediksi langkah berikutnya via neural network, serta perhitungan skor deviasi menggunakan residual yang dinormalisasi dengan median dan interquartile range (IQR).  
   * **Penyesuaian Nyata**: Pada paper aslinya, struktur graf dibentuk secara otomatis oleh algoritma (learned top-k graph). Di kode kita, graf sengaja dikunci mengikuti topologi fisik diagram perpipaan dan instrumentasi (P&ID) 6-node milik kompresor KO-3201. Hal ini membuat komputasi jauh lebih ringan, stabil, dan perilakunya dapat dijelaskan secara langsung oleh insinyur proses.
2. **Kalkulasi Health Index Berbasis Domain**: Rujukan dari metodologi [arXiv:2405.04990](https://arxiv.org/abs/2405.04990) (*Reliability Engineering & System Safety*, 2024).  
   * **Yang Diambil**: Perumusan indeks kesehatan aset 0-100% tanpa pengawasan (unsupervised) dengan menanamkan batas batas fisik rekayasa sebagai pembobot penalti.
3. **Standar Vibrasi Industri ISO 10816-3 dan API 670**  
   * **Yang Diambil**: Batasan ambang batas zona operasi normal (< 30/45 mikron), alarm DCS (45 mikron), dan trip mekanikal darurat (75 mikron) untuk mesin rotasi industri berat (Class IV).
4. **Evidence-Grounded Generative Agent**: Mengacu pada prinsip penalaran berbasis bukti [arXiv:2607.22385](https://arxiv.org/abs/2607.22385).  
   * **Yang Diambil**: Membatasi ruang jawab model bahasa (LLM) hanya pada fakta operasional dan batasan teknis pabrik tanpa memberi ruang bagi model untuk mengarang prosedur atau angka kerugian.
5. **Dokumen Resmi Investigasi Pabrik Chandra Asri (RCA 2 dan RCA 4)**  
   * **Yang Diambil**: Kronologi insiden nyata kompresor KO-3201 (AR-2026-ZCU-0142) dan cooler HE-3301, penyebab kegagalan fisik (kebocoran pendingin oli, degradasi film minyak, ausnya babbitt bearing), serta butir-butir tindakan korektif dan preventif (CAPA).

### B. Referensi yang Berfungsi sebagai Inspirasi Konseptual (Tidak Di-code dari Nol)
1. **DCdetector** ([arXiv:2306.10347](https://arxiv.org/abs/2306.10347), KDD 2023)  
   * **Inspirasi**: Konsep membedakan antara anomali lonjakan sesaat (transien) dan degradasi jangka panjang secara bertahap menggunakan dual-attention.  
   * **Fakta**: Arsitektur jaringan saraf tiruan DCdetector tidak diimplementasikan di pipeline utama karena model GDN dengan penahan persistence dua jam sudah cukup untuk mendeteksi degradasi 16 jam lebih awal.
2. **Alarm-Based Root Cause Analysis** ([arXiv:2203.11321](https://arxiv.org/abs/2203.11321), IEEE 2022)  
   * **Inspirasi**: Gagasan menelusuri alarm pemicu pertama (first-out alarm) dan perambatan kegagalan proses.  
   * **Fakta**: Kita mengekstrak kontributor deviasi tertinggi (`top_contributors`) dari residual GDN dan memetakannya ke rantai proses fisik P&ID, yang selanjutnya akan ditingkatkan menjadi pencari semantik vektor pada fase Hackathon.
3. **Knowledge Graph-Enhanced RAG** ([arXiv:2406.18114](https://arxiv.org/abs/2406.18114), 2025)  
   * **Inspirasi**: Prinsip menyandarkan jawaban model bahasa pada basis data pengetahuan terstruktur agar tidak berhalusinasi.  
   * **Fakta**: Kita tidak memasang sistem basis data graf eksternal (seperti Neo4j), melainkan menggunakan struktur file JSON terindeks yang langsung memasok konteks ke prompt model bahasa.
4. **TimesNet: 2D-Variation Modeling** ([arXiv:2210.02186](https://arxiv.org/abs/2210.02186), ICLR 2023)  
   * **Inspirasi & Rencana Hackathon**: Model peramalan deret waktu periodik untuk mengestimasi sisa waktu operasi (Remaining Useful Life). Di MVP saat ini digantikan oleh kurva P-F kuadratik fisika proses.

### C. Tabel Rujukan Ilmiah dan Dokumen Resmi Pabrik

| Rujukan / Sumber | Identifikasi & Tautan Resmi | Status Implementasi | Peran dalam Solusi SCC-Caliber |
| :--- | :--- | :--- | :--- |
| **Graph Deviation Network (GDN)** | [arXiv:2106.06947](https://arxiv.org/abs/2106.06947) (AAAI 2021) | **Diimplementasikan Penuh** | Model inti deteksi dini anomali korelasi 6 sensor P&ID kompresor KO-3201 (PyTorch). |
| **Health Index via Domain Knowledge** | [arXiv:2405.04990](https://arxiv.org/abs/2405.04990) (RESS 2024) | **Diimplementasikan Penuh** | Landasan perumusan skor kesehatan mesin 0-100% berbasis bobot batas fisik. |
| **Standar Proteksi Mesin Industri** | ISO 10816-3 & API 670 | **Diimplementasikan Penuh** | Penentuan batas normal (<30/45 µm), alarm (45 µm), dan trip (75 µm) mesin Class IV. |
| **Evidence-Grounded Generative Agent** | [arXiv:2607.22385](https://arxiv.org/abs/2607.22385) (2026) | **Diimplementasikan Penuh** | Arsitektur Copilot Shift Briefing dan Tanya-Jawab What-If bebas halusinasi via Gemini API. |
| **Investigasi Resmi Pabrik (RCA 2 & RCA 4)** | Dokumen Investigasi Internal Chandra Asri | **Diimplementasikan Penuh** | Data riil insiden KO-3201 (AR-2026-ZCU-0142), kerugian $1,584M, dan langkah resmi CAPA. |
| **Basis Data Rekayasa Proses Plant ZCU** | Lembar Analisis Teknik Kimia ZCU | **Diimplementasikan Penuh** | Taksonomi 56 aset ZCU, batas sensor, dan rumus kapasitas 55 Ton/Jam x $900/Ton. |
| **DCdetector (Contrastive Learning)** | [arXiv:2306.10347](https://arxiv.org/abs/2306.10347) (KDD 2023) | **Inspirasi Konseptual** | Wawasan pembelajaran kontras multi-skala waktu tanpa rekonstruksi data. |
| **Alarm-Based Root Cause Analysis** | [arXiv:2203.11321](https://arxiv.org/abs/2203.11321) (IEEE 2022) | **Inspirasi & Target Hackathon** | Dasar pengembangan pencarian semantik vektor pada 380 riwayat insiden kilang. |
| **Knowledge Graph Enhanced FMEA** | [arXiv:2406.18114](https://arxiv.org/abs/2406.18114) (JIII 2025) | **Inspirasi Konseptual** | Wawasan penautan taksonomi kegagalan terstruktur (diwujudkan via JSON RAG lokal). |
| **TimesNet (Temporal 2D-Variation)** | [arXiv:2210.02186](https://arxiv.org/abs/2210.02186) (ICLR 2023) | **Target Fase Hackathon** | Model peramalan laju degradasi getaran dan sisa umur pakai (RUL) di babak 24 jam. |

---

## 7. Hasil dan Manfaat Utama

Ketika sistem ini dijalankan pada rekaman data uji kompresor KO-3201:

1. **Memberikan Jendela Penanganan 16 Jam Lebih Awal**  
   Peringatan awal terpicu pada jam ke-633, saat getaran masih di angka 31,2 mikron. Alarm DCS baru akan berbunyi di jam ke-649 (45 mikron), dan trip darurat baru terjadi di jam ke-679 (75 mikron). Operator memiliki 16 jam penuh sebelum alarm darurat berbunyi.

2. **Menghindari Kerugian Finansial Sebesar 1,188 Juta Dolar AS**  
   Dengan intervensi dini, tim pabrik dapat menjadwalkan penurunan kapasitas secara bertahap dan melakukan perbaikan terkendali selama 8 jam (biaya produksi hilang: 396 ribu dolar AS). Hal ini mencegah mesin hancur dan mati darurat selama 32 jam seperti kejadian riil di masa lalu (kerugian: 1,584 juta dolar AS).

3. **Keputusan yang Terang dan Dapat Dipertanggungjawabkan**  
   Operator tidak disuguhi angka skor anomali yang membingungkan tanpa arahan. Sistem langsung menyajikan apa akar masalah fisiknya, riwayat kejadian serupa, suku cadang yang harus disiapkan di gudang (SAP Work Order), dan langkah SOP lapangan yang harus diambil.

4. **Kinerja Ringan dan Andal**  
   Sistem penarikan data dasbor bekerja secara instan (kecepatan respon di bawah 2 milidetik) tanpa beban komputasi berat di sisi antarmuka, serta tetap berfungsi penuh meskipun koneksi internet ke layanan kecerdasan buatan terputus total.

---

## 8. Rencana Pengembangan Lanjutan: Fase Hackathon 24 Jam dan Skalabilitas Pabrik

Sistem yang dibangun saat ini adalah fondasi MVP terverifikasi pada satu mesin paling kritis (Kompresor KO-3201). Ketika tim melangkah ke babak Hackathon 24 Jam, fokus utama kami adalah melakukan ekspansi vertikal dan horizontal berdasarkan empat pilar strategis:

### A. Empat Pilar Pengembangan Hackathon

1. **Pilar 1: Ekspansi Skala Unit ZCU (Trio Alat Kritis dan 4 Arketipe Aset)**  
   * **Target Utama**: Memperluas pemantauan mendalam dari Kompresor KO-3201 ke dua peralatan pendukung krusial di sekitarnya: Penukar Panas Lube-Oil HE-3301 (peralatan statis pemicu kontaminasi air) dan Pompa Umpan PU-2101B (peralatan rotasi hidraulik).  
   * **4 Arketipe Modular**: Mengelompokkan seluruh 56 aset Plant ZCU ke dalam 4 template analitik proses:
     - Arketipe Rotary (Kompresor KO, Pompa PU, Blower BL): Parameter getaran radial, suhu bearing, arus motor, dan tekanan buang.
     - Arketipe Static Thermal (Penukar Panas HE): Parameter beda tekanan (dP), suhu fluida keluar, dan laju pengotoran pipa (fouling factor).
     - Arketipe Static Hydraulic (Kolom Fraksinasi DA, Separator Drum FA): Parameter beda tekanan tray dan level cairan.
     - Arketipe Electrical (Motor Besar, Trafo TR): Parameter suhu gulungan kumparan dan beban arus listrik.

2. **Pilar 2: Peningkatan Kedalaman Model AI (Auto-GDN dan TimesNet RUL)**  
   * **Auto-GDN (Dynamic Graph Learning)**: Mengembangkan model GDN yang mampu mempelajari keterkaitan graf sensor secara mandiri (learnable adjacency) dari data normal operasi, sehingga penambahan sensor baru tidak memerlukan pemetaan topologi manual.
   * **Peramalan Sisa Umur Pakai (TimesNet)**: Mengintegrasikan model deep learning TimesNet (arXiv:2210.02186) untuk memproyeksikan tren degradasi getaran dan laju pengotoran termal secara periodik, menghasilkan estimasi Remaining Useful Life (RUL) yang lebih dinamis melengkapi kurva P-F fisika proses.
   * **Pelacakan Propagasi Kausal**: Mengotomatisasi pembuktian jalur perambatan gangguan dari sensor sumber (misalnya dP cooler) ke sensor penerima (getaran bearing) guna memastikan operator menangani akar masalah, bukan sekadar gejala luar.

3. **Pilar 3: Pencarian Semantik Terintegrasi dan Simulasi Finansial Multi-Plant**  
   * **Incident Semantic Embedding Matcher**: Meng-upgrade mesin pencari insiden dari aturan tabel kaku menjadi pencocokan berbasis representasi vektor teks pada 380 riwayat insiden kilang Chandra Asri (total kerugian tercatat 67,19 juta dolar AS). Operator cukup mengetik gejala lapangan dalam bahasa alami untuk menemukan preseden kasus serupa.
   * **Simulasi Keputusan Interaktif Terpadu**: Menyediakan kontrol interaktif di dasbor untuk menguji skenario penurunan kapasitas produksi (rate reduction) secara dinamis terhadap laju kenaikan getaran dan kalkulasi kerugian oportunitas harian.

4. **Pilar 4: Pembelajaran Mandiri Berkelanjutan dengan Peninjauan Manusia (Closed-Loop HITL Auto-Learning)**  
   * **Kepatuhan Tata Kelola Keselamatan Pabrik**: Di lingkungan kilang petrokimia, sistem kendali cerdas tidak boleh mengubah aturan keselamatan secara otomatis tanpa verifikasi manusia (Management of Change). Kami merancang siklus pembelajaran mandiri yang menggabungkan kecepatan AI dengan ketelitian insinyur proses.
   * **Sintesis Draf Rekap Investigasi Otomatis (AI Post-Incident Recap)**: Begitu mesin mengalami henti operasional atau intervensi selesai, AI langsung mengumpulkan jendela telemetri 24 jam ke belakang, mengidentifikasi alarm pertama yang menyala (first-out alarm), menghitung durasi henti aktual, dan merangkum draf awal laporan investigasi 4M+1E (Man, Machine, Material, Method, Environment) beserta usulan tindakan pencegahan (CAPA).
   * **Gerbang Validasi Insinyur (Human-in-the-Loop Gate)**: Draf rekap tersebut disajikan kepada insinyur keandalan (Reliability Engineer / pengawas shift) di dasbor untuk ditinjau, disesuaikan temuan lapangannya, dan disahkan dengan otorisasi digital.
   * **Pembaruan Basis Pengetahuan Otomatis**: Setelah disetujui, insiden baru tersebut otomatis diindeks ke dalam basis data insiden kilang (menjadi kasus ke-381 dan seterusnya) serta memperkaya memori pencarian semantik dan kartu tindakan, sehingga sistem semakin cerdas dari waktu ke waktu tanpa risiko distorsi model.

---

### B. Roadmap Eksekusi 24 Jam Hackathon

Untuk menjamin seluruh fitur di atas selesai tepat waktu tanpa risiko kegagalan teknis saat demonstrasi akhir, pekerjaan 24 jam dibagi ke dalam 4 sprint terstruktur:

| Periode Waktu | Fokus Sprint | Target Hasil yang Dicapai |
| :--- | :--- | :--- |
| **Jam 00.00 sampai 06.00** | **Sprint 1: Ingestion & Arketipe Data** | Penyiapan jalur data untuk trio aset (KO-3201, HE-3301, PU-2101B) dan standarisasi skema 4 arketipe aset ZCU. |
| **Jam 06.00 sampai 12.00** | **Sprint 2: Training Auto-GDN & TimesNet** | Pelatihan model graf adaptif untuk korelasi multi-alat serta modul peramalan laju degradasi sisa waktu operasi (RUL). |
| **Jam 12.00 sampai 18.00** | **Sprint 3: Mesin Semantik & Dasbor SPOG** | Integrasi pencarian semantik vektor 380 insiden kilang, modul formulir peninjauan draf rekap insiden (HITL Approval Form), dan penyempurnaan dasbor interaktif kontrol beban What-If. |
| **Jam 18.00 sampai 24.00** | **Sprint 4: Pengujian Ketahanan & Demo Pitch** | Uji coba skenario ekstrem (red teaming), verifikasi latensi di bawah 2 milidetik, dan finalisasi skrip presentasi 5 menit juri. |
