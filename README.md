
***

```markdown
# 🛰️ Panduan Penggunaan DSFANet di QGIS

Selamat datang di repositori **DSFANet - Kelompok 2**. Panduan ini akan membantu Anda melakukan konfigurasi awal dan menjalankan *tool* deteksi perubahan lahan (*change detection*) menggunakan metode DSFANet langsung dari perangkat lunak QGIS.

---

## 🛠️ Setup Awal (Hanya Sekali)

Langkah ini diperlukan untuk mempersiapkan *environment* Python dan semua dependensi (termasuk TensorFlow) yang dibutuhkan oleh model DSFANet agar dapat berjalan secara optimal.

1. **Unduh Repositori:** Unduh (*download*) atau klon (*clone*) seluruh isi folder repositori ini ke komputer Anda.
2. **Buka Terminal / Command Prompt (CMD):** Buka terminal dan arahkan direktori aktif ke dalam folder repositori yang telah diunduh.
3. **Jalankan Script Instalasi:** Eksekusi perintah berikut untuk memulai setup otomatis:
```bash
python install_env.py
