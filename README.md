## 📑 how to use
**1. [Setup Awal (Hanya Sekali)](#-setup-awal-hanya-sekali)**
**2. [Tambahkan Script ke QGIS](#-tambahkan-script-ke-qgis)**
**3. [Jalankan Tool](#-jalankan-tool)**


**1. Setup Awal**
Langkah ini diperlukan untuk mempersiapkan *environment* Python dan semua dependensi (termasuk TensorFlow) yang dibutuhkan oleh model DSFANet agar dapat berjalan secara optimal.
1. **Unduh Repositori:** Unduh (*download*) atau klon (*clone*) seluruh isi folder repositori ini ke komputer Anda.
2. **Buka Terminal / Command Prompt (CMD):** Buka terminal dan arahkan direktori aktif ke dalam folder repositori yang telah diunduh.
3. **Jalankan Script Instalasi:** Eksekusi perintah berikut untuk memulai setup otomatis:

```bash
python install_env.py
```


**2. Tambahkan Script ke QGIS**
1. Buka QGIS.
2. Pada panel Processing Toolbox (Ctrl+Alt+T), cari ikon gear/dropdown dan pilih Add Script to Toolbox....
3. Pilih file  **dsfa_qgis.py**
4. Script akan muncul di bawah kelompok Geokom Kelompok 2 -> DSFANet Change Detection.

**3. Jalankan Tools**
1. Buka tool tersebut.
2. Pengguna tidak perlu mengisi kolom **Path Python Executable Eksternal** (biarkan kosong).
3. Script QGIS akan secara otomatis mencari direktori default instalasi
```bash
tf_dsfa
```
di komputer anda (baik di folder user maupun ProgramData) dan langsung menggunakannya.
