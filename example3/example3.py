from qgis.core import (
    QgsProject,
    QgsRasterLayer
)
from qgis.PyQt.QtCore import (
    QSettings,
    QTranslator,
    QCoreApplication,
    QTimer
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from .resources import *
from .example3_dialog import Example3Dialog
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from osgeo import gdal, gdalconst

class Example3:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', 'example3_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Example3')
        self.first_start = None
        self.observer = None
        self.directory_path = None
        self.last_image_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.stop_if_no_new_images)

    def tr(self, message):
        return QCoreApplication.translate('Example3', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ':/plugins/example3/icon.png'
        self.add_action(icon_path, text=self.tr(u'Start Monitoring'), callback=self.start_monitoring, parent=self.iface.mainWindow())
        self.first_start = True

    def unload(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.timer.stop()
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Example3'), action)
            self.iface.removeToolBarIcon(action)

    def start_monitoring(self):
        if self.first_start:
            self.first_start = False
            self.dlg = Example3Dialog()  # Example3Dialog

        result = self.dlg.exec_()
        if result:
            # Get the directory path from the dialog
            self.directory_path = self.dlg.directoryLineEdit_1.text()
            if os.path.isdir(self.directory_path):
                self.timer.start(120000)  # Check every 2 minutes
                self.observer = Observer()
                event_handler = self.RasterFileEventHandler(self.process_new_image)
                self.observer.schedule(event_handler, self.directory_path, recursive=False)
                self.observer.start()
            else:
                self.iface.messageBar().pushCritical("Error", "The specified path is not a valid directory.")

    def process_new_image(self, file_path):
        self.last_image_time = time.time()
        self.load_and_merge_raster_layers(file_path)

    def stop_if_no_new_images(self):
        if time.time() - self.last_image_time > 120:
            self.iface.messageBar().pushInfo("Stop", "No new images detected for more than 2 minutes. Stopping the monitoring process.")
            self.unload()

    def load_and_merge_raster_layers(self, new_raster_path):
        """Load the new raster, merge with existing rasters, and update QGIS project."""

        # Check if there's already a raster layer
        layers = QgsProject.instance().mapLayersByType(QgsRasterLayer)
        if layers:
            # Get the existing layer (assumed to be the last one in the list)
            existing_layer = layers[-1]
            existing_path = existing_layer.dataProvider().dataSourceUri()
            if not self.merge_rasters(existing_path, new_raster_path):
                self.iface.messageBar().pushCritical("Merge Error", "Failed to merge the rasters.")
                return

            # Remove the old raster layer from QGIS
            QgsProject.instance().removeMapLayer(existing_layer.id())

        # Load the new raster layer
        new_layer = QgsRasterLayer(new_raster_path, "New Layer")
        if new_layer.isValid():
            QgsProject.instance().addMapLayer(new_layer)
            self.iface.messageBar().pushInfo("Layer Added", "New raster layer added to the project.")
        else:
            self.iface.messageBar().pushCritical("Layer Error", "Failed to load the new raster layer.")

    def merge_rasters(self, existing_raster_path, new_raster_path):
        """Merge existing and new rasters with overlap handling."""
        # Open existing raster
        existing_ds = gdal.Open(existing_raster_path)
        new_ds = gdal.Open(new_raster_path)
        if existing_ds is None or new_ds is None:
            return False

        # Create a virtual raster file to store the merged result
        driver = gdal.GetDriverByName('GTiff')
        output_path = os.path.join(os.path.dirname(new_raster_path), 'merged_output.tif')
        if driver is None:
            return False
        
        # Set up geotransform and projection based on the existing raster
        geotransform = existing_ds.GetGeoTransform()
        projection = existing_ds.GetProjection()
        
        # Define the output raster size (take into account the extent of both rasters)
        x_size = max(existing_ds.RasterXSize, new_ds.RasterXSize)
        y_size = max(existing_ds.RasterYSize, new_ds.RasterYSize)

        # Create the output raster dataset
        out_ds = driver.Create(output_path, x_size, y_size, existing_ds.RasterCount, gdalconst.GDT_Float32)
        if out_ds is None:
            return False

        out_ds.SetGeoTransform(geotransform)
        out_ds.SetProjection(projection)

        # Merge rasters
        for i in range(1, existing_ds.RasterCount + 1):
            existing_band = existing_ds.GetRasterBand(i)
            new_band = new_ds.GetRasterBand(i)
            out_band = out_ds.GetRasterBand(i)

            # Read data from both rasters
            existing_data = existing_band.ReadAsArray()
            new_data = new_band.ReadAsArray()

            merged_data = new_data  
            out_band.WriteArray(merged_data)
            out_band.FlushCache()

        out_ds.FlushCache()
        return True

    class RasterFileEventHandler(FileSystemEventHandler):
        def __init__(self, process_new_image_callback):
            self.process_new_image_callback = process_new_image_callback

        def on_modified(self, event):
            if not event.is_directory and event.src_path.lower().endswith(('.tif', '.tiff')):
                self.process_new_image_callback(event.src_path)


