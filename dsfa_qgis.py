# -*- coding: utf-8 -*-
"""
***************************************************************************
*                                                                         *
*   This QGIS Processing script integrates the DSFANet                     *
*   (Deep Slow Feature Analysis Network) algorithm for change detection.  *
*                                                                         *
***************************************************************************
"""

import os
import sys
import tempfile
import subprocess
from typing import Any, Optional

import numpy as np
from osgeo import gdal

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProcessingParameterRasterDestination,
)

# Try to import internal DSFANet dependencies
try:
    import tensorflow as tf
    import scipy.io as sio
    from scipy.cluster.vq import kmeans as km

    HAS_INTERNAL_DEPS = True
except ImportError:
    HAS_INTERNAL_DEPS = False


class DSFANetProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    QGIS Processing Algorithm using DSFANet for unsupervised change detection.
    """

    INPUT_T1 = "INPUT_T1"
    INPUT_T2 = "INPUT_T2"
    UNCHANGED_MASK = "UNCHANGED_MASK"
    EPOCHS = "EPOCHS"
    LEARNING_RATE = "LEARNING_RATE"
    REGULARIZATION = "REGULARIZATION"
    TRAINING_SAMPLES = "TRAINING_SAMPLES"
    ITERATIONS = "ITERATIONS"
    GPU = "GPU"
    EXTERNAL_PYTHON = "EXTERNAL_PYTHON"
    OUTPUT_MAGNITUDE = "OUTPUT_MAGNITUDE"
    OUTPUT_BINARY = "OUTPUT_BINARY"
    DSFANET_FOLDER = "DSFANET_FOLDER"

    def name(self) -> str:
        return "dsfanet"

    def displayName(self) -> str:
        return "DSFANet Change Detection"

    def group(self) -> str:
        return "Geokom Kelompok 2"

    def groupId(self) -> str:
        return "geokom_kelompok2"

    def shortHelpString(self) -> str:
        return (
            "Deteksi perubahan citra satelit multi-temporal menggunakan DSFANet (Deep Slow Feature Analysis Network).\n\n"
            "Reference  = https://github.com/wwdAlger/DSFANet.git\n"
            "yang kemudian kita modifikasi kedalam QGIS\n\n"
            "Kelompok 2:\n"
            "- Irfani Anis 25/562364/PGE/01721\n"
            "- Adriyasyah 25/573033/PGE/01771\n"
            "- Salman Najib 25/574949/PGE/01782\n"
            "- Cipriano Pereira 25/571768/PGE/01766\n"
            "- Sulpisius Sihombing 25/565756/PGE/01735\n"
            "- Sadiqullah Stanikzai 25/562699/PGE/01729\n\n"
            "Pastikan Anda memiliki TensorFlow 1.x terinstal. Jika tidak terinstal di environment Python QGIS, "
            "Anda dapat memasukkan path python.exe eksternal (misal Anaconda/Venv) yang memiliki library tersebut."
        )

    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_T1, "Citra T1 (Sebelum)", optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_T2, "Citra T2 (Sesudah)", optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.UNCHANGED_MASK,
                "Mask Piksel Unchanged (Opsional, dihitung otomatis jika kosong)",
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.EPOCHS,
                "Jumlah Epoch Training",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=2000,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.LEARNING_RATE,
                "Learning Rate",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.0001,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.REGULARIZATION,
                "Regularization Parameter",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.0001,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.TRAINING_SAMPLES,
                "Jumlah Training Samples (trn)",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=3000,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ITERATIONS,
                "Max Iterations",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.GPU,
                "GPU ID (default '-1' untuk CPU, '0' untuk GPU)",
                defaultValue="-1",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.EXTERNAL_PYTHON,
                "Path Python Executable Eksternal (Opsional, untuk env TensorFlow eksternal)",
                defaultValue="",
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.DSFANET_FOLDER,
                "Path ke Folder Repository DSFANet",
                defaultValue=r"c:\workspace\Geokom_Kelompok 2\DSFANet",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_MAGNITUDE,
                "Peta Magnitude Perubahan (Magnitude Map)",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_BINARY,
                "Peta Biner Perubahan (Binary Change Map)",
                optional=False,
            )
        )

    def processAlgorithm(
        self,
        parameters: dict[str, Any],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> dict[str, Any]:

        # Retrieve layers
        layer_t1 = self.parameterAsRasterLayer(parameters, self.INPUT_T1, context)
        layer_t2 = self.parameterAsRasterLayer(parameters, self.INPUT_T2, context)
        mask_layer = self.parameterAsRasterLayer(
            parameters, self.UNCHANGED_MASK, context
        )

        if layer_t1 is None or layer_t2 is None:
            raise QgsProcessingException("Input layer citra tidak valid!")

        # Retrieve parameters
        epochs = self.parameterAsInt(parameters, self.EPOCHS, context)
        lr = self.parameterAsDouble(parameters, self.LEARNING_RATE, context)
        reg = self.parameterAsDouble(parameters, self.REGULARIZATION, context)
        trn = self.parameterAsInt(parameters, self.TRAINING_SAMPLES, context)
        iterations = self.parameterAsInt(parameters, self.ITERATIONS, context)
        gpu = self.parameterAsString(parameters, self.GPU, context)
        external_python = (
            self.parameterAsString(parameters, self.EXTERNAL_PYTHON, context)
            .strip()
            .strip('"')
            .strip("'")
        )

        output_mag_path = self.parameterAsOutputLayer(
            parameters, self.OUTPUT_MAGNITUDE, context
        )
        output_bin_path = self.parameterAsOutputLayer(
            parameters, self.OUTPUT_BINARY, context
        )

        # Helper to load raster as numpy using GDAL
        def raster_to_numpy(raster):
            provider = raster.dataProvider()
            source_uri = provider.dataSourceUri()
            if not os.path.exists(source_uri):
                raise QgsProcessingException(
                    f"File raster tidak ditemukan di disk: {source_uri}"
                )
            ds = gdal.Open(source_uri)
            if ds is None:
                raise QgsProcessingException(f"Gagal membuka raster: {source_uri}")
            bands_data = []
            for b_idx in range(1, ds.RasterCount + 1):
                band = ds.GetRasterBand(b_idx)
                bands_data.append(band.ReadAsArray())
            arr = np.stack(bands_data, axis=-1)
            return arr, ds.GetGeoTransform(), ds.GetProjection()

        feedback.pushInfo("Membaca citra T1...")
        img1, geo_transform, projection = raster_to_numpy(layer_t1)
        feedback.pushInfo("Membaca citra T2...")
        img2, _, _ = raster_to_numpy(layer_t2)

        if img1.shape[0] != img2.shape[0] or img1.shape[1] != img2.shape[1]:
            raise QgsProcessingException(
                "Dimensi baris dan kolom citra T1 dan T2 harus sama!"
            )
        if img1.shape[2] != img2.shape[2]:
            raise QgsProcessingException(
                "Jumlah spectral band pada citra T1 dan T2 harus sama!"
            )

        # Process mask layer
        if mask_layer is not None:
            feedback.pushInfo("Membaca mask piksel unchanged...")
            mask_arr, _, _ = raster_to_numpy(mask_layer)
            if len(mask_arr.shape) == 3:
                mask_arr = mask_arr[:, :, 0]
            cva_mask = mask_arr.astype(np.uint8)
        else:
            feedback.pushInfo(
                "Mask tidak disediakan. Menghitung mask otomatis menggunakan CVA..."
            )
            h, w, b = img1.shape
            im1_flat = np.reshape(img1, (-1, b))
            im2_flat = np.reshape(img2, (-1, b))

            # Simple normalization for CVA calculation
            def norm_simple(data):
                mean = np.mean(data, axis=0)
                std = np.std(data, axis=0)
                std[std == 0] = 1.0
                return (data - mean) / std

            im1_n = norm_simple(im1_flat)
            im2_n = norm_simple(im2_flat)

            # Euclidean distance
            diff = np.sqrt(np.sum((im1_n - im2_n) ** 2, axis=-1))

            # Take the lowest 20% distance as unchanged training samples
            threshold = np.percentile(diff, 20.0)

            mask_flat = np.ones_like(diff, dtype=np.uint8)
            mask_flat[diff <= threshold] = 0
            cva_mask = np.reshape(mask_flat, (h, w))

        # Path to DSFANet folder
        dsfa_net_path = (
            self.parameterAsString(parameters, self.DSFANET_FOLDER, context)
            .strip()
            .strip('"')
            .strip("'")
        )
        if not os.path.exists(dsfa_net_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            fallback_path = os.path.join(script_dir, "DSFANet")
            if os.path.exists(fallback_path):
                dsfa_net_path = fallback_path
            else:
                raise QgsProcessingException(
                    f"Direktori DSFANet tidak ditemukan di: {dsfa_net_path} maupun {fallback_path}. "
                    "Pastikan parameter 'Path ke Folder Repository DSFANet' diisi dengan benar."
                )

        run_externally = bool(external_python.strip())

        if not run_externally and not HAS_INTERNAL_DEPS:
            feedback.pushInfo(
                "Dependency TensorFlow tidak ditemukan di environment QGIS."
            )
            feedback.pushInfo("Mencari path Python eksternal otomatis...")
            # Try to check if python is in path
            raise QgsProcessingException(
                "TensorFlow tidak terinstal di environment QGIS. Silakan tentukan 'Path Python Executable Eksternal' "
                "yang terinstal TensorFlow 1.x (misalnya: C:\\Users\\NamaUser\\anaconda3\\envs\\tf_env\\python.exe)."
            )

        all_magnitude = None
        change_map = None

        if run_externally:
            feedback.pushInfo(
                f"Menjalankan DSFANet menggunakan Python eksternal: {external_python}"
            )

            temp_dir = tempfile.mkdtemp()
            t1_path = os.path.join(temp_dir, "t1.npy").replace("\\", "/")
            t2_path = os.path.join(temp_dir, "t2.npy").replace("\\", "/")
            mask_path = os.path.join(temp_dir, "mask.npy").replace("\\", "/")
            out_mag_path_temp = os.path.join(temp_dir, "out_mag.npy").replace("\\", "/")
            out_bin_path_temp = os.path.join(temp_dir, "out_bin.npy").replace("\\", "/")

            np.save(t1_path, img1)
            np.save(t2_path, img2)
            np.save(mask_path, cva_mask)

            # Generate python runner script
            runner_code = f"""# -*- coding: utf-8 -*-
import sys
import os
import numpy as np

sys.path.append(r"{dsfa_net_path}")
import utils
from model import dsfa

img1 = np.load(r"{t1_path}")
img2 = np.load(r"{t2_path}")
cva_ind = np.load(r"{mask_path}")

img_shape = np.shape(img1)
bands = img_shape[-1]
net_shape = [128, 128, bands]

im1 = np.reshape(img1, newshape=[-1, bands])
im2 = np.reshape(img2, newshape=[-1, bands])

im1 = utils.normlize(im1)
im2 = utils.normlize(im2)

cva_ind = np.reshape(cva_ind, newshape=[-1])

class ArgsObj:
    epoch = {epochs}
    lr = {lr}
    reg = {reg}
    trn = {trn}
    iter = {iterations}
    gpu = '{gpu}'

args = ArgsObj()

differ = np.zeros(shape=[np.shape(im1)[0], bands, args.iter])
all_magnitude = None

for k1 in range(args.iter):
    print("Mengeksekusi iterasi ke-%d..." % (k1 + 1))
    i1, i2 = utils.getTrainSamples(cva_ind, im1, im2, args.trn)
    loss_log, vpro, fcx, fcy, bval = dsfa(
        xtrain=i1, ytrain=i2, xtest=im1, ytest=im2, net_shape=net_shape, args=args)
    imm, magnitude, differ_map = utils.linear_sfa(fcx, fcy, vpro, shape=img_shape)
    magnitude = np.reshape(magnitude, img_shape[0:-1])
    differ[:, :, k1] = differ_map
    if all_magnitude is None:
        all_magnitude = magnitude / np.max(magnitude)
    else:
        all_magnitude = all_magnitude + magnitude / np.max(magnitude)

# Final binary map using k-means
change_map = np.reshape(utils.kmeans(np.reshape(all_magnitude, [-1])), img_shape[0:-1])

np.save(r"{out_mag_path_temp}", all_magnitude)
np.save(r"{out_bin_path_temp}", change_map)
print("Proses selesai sukses!")
"""
            runner_script_path = os.path.join(temp_dir, "runner.py")
            with open(runner_script_path, "w", encoding="utf-8") as f:
                f.write(runner_code)

            # Subprocess execution
            env = os.environ.copy()
            env["CUDA_VISIBLE_DEVICES"] = gpu
            # Clear QGIS python environment paths to prevent version/library conflicts
            if "PYTHONPATH" in env:
                del env["PYTHONPATH"]
            if "PYTHONHOME" in env:
                del env["PYTHONHOME"]

            p = subprocess.Popen(
                [external_python, runner_script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            # Stream stdout to QGIS Processing Feedback
            while True:
                line = p.stdout.readline()
                if not line and p.poll() is not None:
                    break
                if line:
                    feedback.pushInfo(line.strip())

            rc = p.poll()
            if rc != 0:
                raise QgsProcessingException(
                    f"Proses Python eksternal gagal dengan return code {rc}"
                )

            # Load results
            if os.path.exists(out_mag_path_temp) and os.path.exists(out_bin_path_temp):
                all_magnitude = np.load(out_mag_path_temp)
                change_map = np.load(out_bin_path_temp)
            else:
                raise QgsProcessingException(
                    "File output tidak ditemukan setelah eksekusi eksternal selesai."
                )

            # Cleanup temp files
            try:
                for f_temp in [
                    t1_path,
                    t2_path,
                    mask_path,
                    out_mag_path_temp,
                    out_bin_path_temp,
                    runner_script_path,
                ]:
                    if os.path.exists(f_temp):
                        os.remove(f_temp)
                os.rmdir(temp_dir)
            except Exception as e:
                feedback.pushInfo(
                    f"Info cleanup: Gagal menghapus beberapa file temp ({str(e)})"
                )

        else:
            # Internal direct execution (QGIS Python Environment)
            feedback.pushInfo("Menjalankan DSFANet di dalam internal QGIS Python...")

            if dsfa_net_path not in sys.path:
                sys.path.append(dsfa_net_path)

            import utils
            from model import dsfa

            img_shape = np.shape(img1)
            bands = img_shape[-1]
            net_shape = [128, 128, bands]

            im1 = np.reshape(img1, newshape=[-1, bands])
            im2 = np.reshape(img2, newshape=[-1, bands])

            im1 = utils.normlize(im1)
            im2 = utils.normlize(im2)

            cva_ind = np.reshape(cva_mask, newshape=[-1])

            class ArgsObj:
                epoch = epochs
                lr = lr
                reg = reg
                trn = trn
                iter = iterations
                gpu = gpu

            args = ArgsObj()

            os.environ["CUDA_VISIBLE_DEVICES"] = gpu
            differ = np.zeros(shape=[np.shape(im1)[0], bands, args.iter])

            for k1 in range(args.iter):
                if feedback.isCanceled():
                    break
                feedback.pushInfo(f"Mengeksekusi iterasi ke-{k1 + 1}...")
                i1, i2 = utils.getTrainSamples(cva_ind, im1, im2, args.trn)

                loss_log, vpro, fcx, fcy, bval = dsfa(
                    xtrain=i1,
                    ytrain=i2,
                    xtest=im1,
                    ytest=im2,
                    net_shape=net_shape,
                    args=args,
                )

                imm, magnitude, differ_map = utils.linear_sfa(
                    fcx, fcy, vpro, shape=img_shape
                )
                magnitude = np.reshape(magnitude, img_shape[0:-1])
                differ[:, :, k1] = differ_map

                if all_magnitude is None:
                    all_magnitude = magnitude / np.max(magnitude)
                else:
                    all_magnitude = all_magnitude + magnitude / np.max(magnitude)

            if feedback.isCanceled():
                raise QgsProcessingException("Algoritma dibatalkan oleh pengguna.")

            change_map = np.reshape(
                utils.kmeans(np.reshape(all_magnitude, [-1])), img_shape[0:-1]
            )

        # Helper to write numpy back to GeoTIFF using GDAL
        def numpy_to_raster(arr, output_path, geo_trans, proj):
            driver = gdal.GetDriverByName("GTiff")
            height, width = arr.shape

            # Map dtype
            if arr.dtype == np.uint8:
                gdal_type = gdal.GDT_Byte
            else:
                gdal_type = gdal.GDT_Float32

            out_ds = driver.Create(output_path, width, height, 1, gdal_type)
            if out_ds is None:
                raise QgsProcessingException(
                    f"Gagal membuat output raster di: {output_path}"
                )

            out_ds.SetGeoTransform(geo_trans)
            out_ds.SetProjection(proj)
            out_band = out_ds.GetRasterBand(1)
            out_band.WriteArray(arr)
            out_band.FlushCache()
            out_ds = None

        feedback.pushInfo("Menulis output raster...")
        # Write outputs
        # Scale change_map to 0-255 for better default visualization in QGIS
        change_map_scaled = (change_map * 255).astype(np.uint8)
        numpy_to_raster(
            all_magnitude.astype(np.float32), output_mag_path, geo_transform, projection
        )
        numpy_to_raster(change_map_scaled, output_bin_path, geo_transform, projection)

        feedback.pushInfo("Peta Magnitude dan Peta Biner Perubahan berhasil dibuat!")

        return {
            self.OUTPUT_MAGNITUDE: output_mag_path,
            self.OUTPUT_BINARY: output_bin_path,
        }

    def createInstance(self):
        return self.__class__()
