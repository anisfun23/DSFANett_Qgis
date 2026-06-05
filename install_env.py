# -*- coding: utf-8 -*-
"""
***************************************************************************
*                                                                         *
*   DSFANet Environment Installer for QGIS Tool                           *
*   Kelompok 2 - Geokom                                                   *
*                                                                         *
***************************************************************************
"""

import os
import sys
import subprocess
import getpass


def find_conda():
    username = getpass.getuser()
    possible_paths = [
        # System Path (if configured)
        "conda",
        # User Local Miniconda
        f"C:\\Users\\{username}\\miniconda3\\Scripts\\conda.exe",
        # User Local Anaconda
        f"C:\\Users\\{username}\\anaconda3\\Scripts\\conda.exe",
        # ProgramData Miniconda
        "C:\\ProgramData\\miniconda3\\Scripts\\conda.exe",
        # ProgramData Anaconda
        "C:\\ProgramData\\anaconda3\\Scripts\\conda.exe",
        # LocalAppData Miniconda
        f"C:\\Users\\{username}\\AppData\\Local\\miniconda3\\Scripts\\conda.exe",
        # LocalAppData Anaconda
        f"C:\\Users\\{username}\\AppData\\Local\\anaconda3\\Scripts\\conda.exe",
    ]

    for path in possible_paths:
        try:
            # Check if command is executable
            subprocess.run(
                [path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            return path
        except (subprocess.SubprocessError, FileNotFoundError):
            continue

    return None


def main():
    print("=" * 60)
    print("       DSFANet Environment Installer untuk QGIS Tool")
    print("                 Kelompok 2 - Geokom")
    print("=" * 60)
    print("\nMencari instalasi Conda (Miniconda / Anaconda) di sistem Anda...")

    conda_path = find_conda()

    if not conda_path:
        print("\n[ERROR] Conda tidak ditemukan di direktori default.")
        print(
            "Silakan instal Miniconda terlebih dahulu sebelum menjalankan script ini:"
        )
        print("-> Download: https://docs.anaconda.com/miniconda/")
        print("Setelah menginstal, silakan jalankan kembali script ini.")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    print(f"[FOUND] Conda ditemukan di: {conda_path}")
    print("\nMemulai pembuatan Conda environment 'tf_dsfa' dengan Python 3.7...")
    print(
        "(Proses ini memerlukan koneksi internet dan memerlukan waktu beberapa menit)\n"
    )

    create_cmd = [
        conda_path,
        "create",
        "-y",
        "-n",
        "tf_dsfa",
        "python=3.7",
        "pip",
        "-c",
        "conda-forge",
        "--override-channels",
    ]

    try:
        subprocess.run(create_cmd, check=True)
        print("\n[SUCCESS] Environment 'tf_dsfa' berhasil dibuat.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Gagal membuat environment: {e}")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    # Step 2: Install dependencies
    print("\nMenginstal dependencies (TensorFlow 1.14.0, NumPy, SciPy, Matplotlib)...")
    install_deps_cmd = [
        conda_path,
        "run",
        "-n",
        "tf_dsfa",
        "python",
        "-m",
        "pip",
        "install",
        "tensorflow==1.14.0",
        "scipy==1.2.1",
        "numpy==1.16.4",
        "matplotlib==2.2.3",
    ]

    try:
        subprocess.run(install_deps_cmd, check=True)
        print("[SUCCESS] Dependencies utama berhasil diinstal.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Gagal menginstal dependencies: {e}")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    # Step 3: Downgrade protobuf
    print("\nMenurunkan versi protobuf untuk kompatibilitas TensorFlow...")
    install_proto_cmd = [
        conda_path,
        "run",
        "-n",
        "tf_dsfa",
        "python",
        "-m",
        "pip",
        "install",
        "protobuf<=3.20.0",
    ]

    try:
        subprocess.run(install_proto_cmd, check=True)
        print("[SUCCESS] Protobuf berhasil diturunkan versinya.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Gagal menyesuaikan protobuf: {e}")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    # Get env python path for feedback
    env_dir = os.path.dirname(os.path.dirname(conda_path))
    env_python = os.path.join(env_dir, "envs", "tf_dsfa", "python.exe")
    if not os.path.exists(env_python):
        # Alternative path format
        env_python = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(conda_path))),
            "envs",
            "tf_dsfa",
            "python.exe",
        )

    print("\n" + "=" * 60)
    print("       INSTALASI SELESAI DENGAN SUKSES!")
    print("=" * 60)
    print(f"\nPath Python Executable Anda:")
    print(f"👉 {env_python}")
    print("\nPanduan Penggunaan di QGIS:")
    print("1. Tambahkan script 'dsfa_qgis.py' ke QGIS Processing Toolbox.")
    print("2. Biarkan parameter 'Path Python Executable Eksternal' kosong,")
    print("   atau masukkan path di atas jika ingin menentukan secara manual.")
    print("3. Jalankan deteksi perubahan.")

    input("\nTekan Enter untuk keluar...")


if __name__ == "__main__":
    main()
