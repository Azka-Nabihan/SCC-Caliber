# SCC-Caliber (CALIBER 2026 - PT Chandra Asri Pacific Tbk)

Sistem deteksi anomali multivariate dan rekomendasi RCA (Root Cause Analysis) preskriptif untuk mencegah unplanned shutdown pada fasilitas Steam Cracker.

## Struktur Direktori

- `research/`: Dokumen studi kasus, booklet kompetisi, catatan ideasi, review paper arXiv, dan laporan insiden historis.
- `docs/`: Dokumentasi arsitektur sistem (`docs/architecture/data_pipeline.md`) dan rencana teknis (planning).
- `src/`: Modul implementasi kode Proof-of-Concept (POC) yang mencakup `pipeline/`, `models/`, dan `app/`.
- `data/`: Penyimpanan dataset mentah (`raw/`), hasil ekstraksi (`extracted/`), dan data bersih siap latih (`processed/`).
- `scratch/`: Ruang kerja sementara untuk skrip eksperimen cepat dan pengujian ad-hoc.

## Referensi Paper Ilmiah Terverifikasi

1. **Graph Deviation Network (GDN)**
   - Paper: *Graph Neural Network-Based Anomaly Detection in Multivariate Time Series*
   - Referensi: arXiv:2106.06947
   - Fokus: Pemodelan relasi struktural antar-sensor industri berbasis representasi graf dinamis untuk deteksi deviasi sistemik.

2. **DCdetector**
   - Paper: *DCdetector: Dual Attention Contrastive Representation Learning for Time Series Anomaly Detection*
   - Referensi: arXiv:2306.10347
   - Fokus: Representasi deret waktu multivariat dengan dual attention untuk menangkap anomali kompleks berdimensi tinggi.

3. **Equipment Health Index & Failure Degradation**
   - Paper: *Remaining Useful Life Estimation and Health Index Modeling for Industrial Equipment*
   - Referensi: arXiv:2405.04990
   - Fokus: Kuantifikasi degradasi fisik komponen dan estimasi sisa usia operasional sebelum trip terjadi.

4. **Causal RCA & Industrial Fault Attribution**
   - Paper: *Causal Inference for Root Cause Analysis in Complex Industrial Systems*
   - Referensi: arXiv:2203.11321
   - Fokus: Inferensi graf kausal untuk melacak sumber awal anomali tanpa bias korelasi spurious.

5. **Knowledge Graph-Enhanced RAG**
   - Paper: *Knowledge Graph-Enhanced Retrieval-Augmented Generation for Prescriptive Industrial Maintenance*
   - Referensi: arXiv:2406.18114
   - Fokus: Pemanfaatan Knowledge Graph manual operasi dan SOP kilang untuk sintesis rekomendasi tindakan mitigasi cepat.
