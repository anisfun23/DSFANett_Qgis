## 📑 how to use
**1. [Setup Awal (Hanya Sekali)](#-setup-awal-hanya-sekali)**
**2. [Tambahkan Script ke QGIS](#-tambahkan-script-ke-qgis)**
**3. [Jalankan Tool](#-jalankan-tool)**
**4. [Parameter GUI](#-Parameter-GUI)**


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
di komputer anda (baik di folder user maupun ProgramData) dan langsung menggunakann 


**4. Parameter GUI:**
Parameter yang akan digunakan di QGIS adalah sebagai berikut
- INPUT_T1: Layer Raster Citra T1 (Sebelum)
- INPUT_T2: Layer Raster Citra T2 (Sesudah)
- UNCHANGED_MASK: Layer Raster Mask Unchanged (Opsional, jika kosong akan dihitung otomatis via CVA)
- EPOCHS: Jumlah iterasi training model (default: 2000)
- LEARNING_RATE: Learning rate optimizer (default: 1e-4)
- REGULARIZATION: Parameter regularisasi (default: 1e-4)
- TRAINING_SAMPLES: Jumlah piksel sampel training (default: 3000)
- ITERATIONS: Jumlah iterasi DSFA (default: 10)
- EXTERNAL_PYTHON: Path ke python.exe eksternal yang terinstal TensorFlow (Opsional)
- OUTPUT: Layer raster baru untuk menyimpan hasil Peta Perubahan (Change Map) dan Magnitude Perubahan (Magnitude Map).


## KELOMPOK 2
- **Irfani Anis** 25/562364/PGE/01721
- **Adriyasyah** 25/573033/PGE/01771
- **Salman Najib** 25/574949/PGE/01782
- **Cipriano Pereira** 25/571768/PGE/01766
- **Sulpisius Sihombing** 25/565756/PGE/01735
- **Sadiqullah Stanikzai** 25/562699/PGE/01729

## Reference
```bash
https://github.com/wwdAlger/DSFANet.git
```
