# Folder Structure Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merapikan dan memisahkan struktur direktori `SCC-Caliber` menjadi dua domain utama yang terisolasi dengan jelas: riset/studi kasus (`research/`, `docs/`) dan implementasi kodingan/POC (`src/`, `data/`).

**Architecture:** Membangun hirarki direktori standar engineering dan konsultansi bisnis. Dokumen kasus, ideasi, dan paper riset (arXiv) dikelompokkan ke dalam `research/`. Spesifikasi teknis disimpan di `docs/architecture/`. Struktur kodingan modular disiapkan di `src/` (pipeline, models, app) untuk mempermudah eksekusi POC hackathon.

**Tech Stack:** PowerShell, Git, Markdown, Python 3.11+.

---

### Task 1: Membuat Struktur Folder Baru

**Files:**
- Directories to create:
  - `research/casebook/`
  - `research/ideation/`
  - `research/papers/`
  - `research/reports/`
  - `docs/architecture/`
  - `src/pipeline/`
  - `src/models/`
  - `src/app/`
  - `data/raw/`
  - `data/processed/`

- [ ] **Step 1: Jalankan command pembuatan folder**

Run:
```powershell
New-Item -ItemType Directory -Force -Path `
  "research/casebook", `
  "research/ideation", `
  "research/papers", `
  "research/reports", `
  "docs/architecture", `
  "src/pipeline", `
  "src/models", `
  "src/app", `
  "data/raw", `
  "data/processed"
```
Expected: Seluruh direktori baru berhasil dibuat tanpa error.

- [ ] **Step 2: Verifikasi direktori baru**

Run:
```powershell
Get-ChildItem -Directory -Recurse | Where-Object { $_.FullName -match "research|src|docs|data" } | Select-Object FullName
```
Expected: Seluruh path direktori di atas terdaftar.

---

### Task 2: Migrasi Dokumen Riset, Kasus, dan Referensi

**Files:**
- Move:
  - `Booklet CALIBER 2026.pdf` -> `research/casebook/`
  - `Casebook CALIBER 2026.pdf` -> `research/casebook/`
  - `caliber_ideas_canvas.md` -> `research/ideation/`
  - `idea_steam_cracker_trip_canvas.md` -> `research/ideation/`
  - `dump__ide.md` -> `research/ideation/` (Isi file tidak diubah sama sekali)
  - `temp.md` -> `research/ideation/`
  - `references/*` -> `research/papers/`
  - `incident_loss_report.html` -> `research/reports/`

- [ ] **Step 1: Pindahkan file studi kasus resmi**

Run:
```powershell
Move-Item -Path "Booklet CALIBER 2026.pdf", "Casebook CALIBER 2026.pdf" -Destination "research/casebook/"
```
Expected: File berpindah ke `research/casebook/`.

- [ ] **Step 2: Pindahkan canvas ideasi dan catatan ide**

Run:
```powershell
Move-Item -Path "caliber_ideas_canvas.md", "idea_steam_cracker_trip_canvas.md", "dump__ide.md", "temp.md" -Destination "research/ideation/"
```
Expected: File ideasi berpindah ke `research/ideation/`. Isi file tetap utuh.

- [ ] **Step 3: Pindahkan materi referensi dan paper ilmiah**

Run:
```powershell
Get-ChildItem -Path "references/*" | ForEach-Object { Move-Item -Path $_.FullName -Destination "research/papers/" }
Remove-Item -Path "references" -Recurse -Force
```
Expected: Seluruh paper arXiv dan matriks referensi berpindah ke `research/papers/`, folder lama `references` terhapus bersih.

- [ ] **Step 4: Pindahkan laporan HTML visualisasi insiden**

Run:
```powershell
Move-Item -Path "incident_loss_report.html" -Destination "research/reports/"
```
Expected: File `incident_loss_report.html` berada di `research/reports/`.

---

### Task 3: Migrasi Dokumentasi Arsitektur & Manajemen Data

**Files:**
- Move:
  - `data_pipeline.md` -> `docs/architecture/`
  - `data/Supporting Data.zip` -> `data/raw/`
- Clean:
  - `scratch/Untitled.md` (hapus file kosong berukuran 0 byte)

- [ ] **Step 1: Pindahkan spesifikasi data pipeline ke folder arsitektur**

Run:
```powershell
Move-Item -Path "data_pipeline.md" -Destination "docs/architecture/"
```
Expected: `data_pipeline.md` berada di `docs/architecture/`.

- [ ] **Step 2: Rapikan file zip raw data ke folder raw**

Run:
```powershell
Move-Item -Path "data/Supporting Data.zip" -Destination "data/raw/"
```
Expected: `Supporting Data.zip` berada di `data/raw/`.

- [ ] **Step 3: Bersihkan file kosong tak terpakai di scratch**

Run:
```powershell
if (Test-Path "scratch/Untitled.md") { Remove-Item "scratch/Untitled.md" -Force }
```
Expected: `scratch/Untitled.md` terhapus.

---

### Task 4: Inisialisasi Modul Kode POC (`src/`)

**Files:**
- Create:
  - `src/__init__.py`
  - `src/pipeline/__init__.py`
  - `src/pipeline/replay_loader.py` (Placeholder skeleton untuk single-speed replay)
  - `src/models/__init__.py`
  - `src/models/health_index.py` (Placeholder skeleton untuk Weighted Health Index)
  - `src/app/__init__.py`

- [ ] **Step 1: Buat file init dan module entrypoints dasar**

Run:
```powershell
New-Item -ItemType File -Force -Path `
  "src/__init__.py", `
  "src/pipeline/__init__.py", `
  "src/pipeline/replay_loader.py", `
  "src/models/__init__.py", `
  "src/models/health_index.py", `
  "src/app/__init__.py"
```
Expected: File boilerplate modul Python terbuat.

- [ ] **Step 2: Isi skeleton dasar untuk replay loader**

Isi `src/pipeline/replay_loader.py`:
```python
"""
Data Ingestion & Single-Speed Replay Loader untuk POC Hackathon.
Membaca dataset timeseries dari data/extracted/ atau data/processed/.
"""

class ReplayLoader:
    def __init__(self, data_path: str):
        self.data_path = data_path

    def load(self):
        # Implementation in next task
        pass
```

- [ ] **Step 3: Isi skeleton dasar untuk health index engine**

Isi `src/models/health_index.py`:
```python
"""
Equipment Health Index Engine (0 - 100%).
Mengacu pada ISO 10816-3 dan limit operasional dari tim Teknik Kimia.
"""

class HealthIndexCalculator:
    def __init__(self, limits: dict):
        self.limits = limits

    def calculate(self, metrics: dict) -> float:
        # Implementation in next task
        return 100.0
```

---

### Task 5: Membuat README.md Direktori Root

**Files:**
- Create: `README.md`

- [ ] **Step 1: Tulis README.md sebagai panduan navigasi proyek**

Konten `README.md` mencakup:
- Deskripsi singkat proyek SCC-Caliber (CALIBER 2026).
- Struktur direktori beserta fungsi tiap folder.
- Lokasi spesifikasi data pipeline (`docs/architecture/data_pipeline.md`).
- Rujukan ilmiah utama (GDN: arXiv:2106.06947, DCdetector: arXiv:2306.10347, Graph-RAG: arXiv:2406.18114).

- [ ] **Step 2: Verifikasi struktur akhir proyek**

Run:
```powershell
Get-ChildItem | Select-Object Name, Mode
```
Expected di root hanya tersisa:
- `data/`
- `docs/`
- `research/`
- `scratch/`
- `src/`
- `GEMINI.md`
- `README.md`
