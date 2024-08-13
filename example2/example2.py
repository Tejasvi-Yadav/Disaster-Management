from qgis.core import QgsRasterLayer, QgsProject, QgsMessageLog
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QDialog
from osgeo import gdal
import os
import time
from threading import Thread

from .resources import *
from .example2_dialog import Example2Dialog

class Example2:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', f'example2_{locale}.qm')

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&example2')
        self.first_start = True
        self.previous_raster_layer = None  # Initialize the previous raster layer reference

    def tr(self, message):
        return QCoreApplication.translate('example2', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True,
                   add_to_menu=True, add_to_toolbar=True, status_tip=None,
                   whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip:
            action.setStatusTip(status_tip)

        if whats_this:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/example2/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Example2 Plugin'),
            callback=self.run,
            parent=self.iface.mainWindow()
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&example2'), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work."""
        if self.first_start:
            self.first_start = False
            self.dlg = Example2Dialog()

        if hasattr(self, 'dlg') and self.dlg:
            result = self.dlg.exec_()
            if result == QDialog.Accepted:
                self.image_folder = self.dlg.get_file_path_1()
                self.base_image_path = self.dlg.get_file_path_2()
                self.output_path = self.dlg.get_file_path_3()

                QgsMessageLog.logMessage(f"Image Folder: {self.image_folder}", 'Example2')
                QgsMessageLog.logMessage(f"Base Image Path: {self.base_image_path}", 'Example2')
                QgsMessageLog.logMessage(f"Output Path: {self.output_path}", 'Example2')

                if not os.path.isdir(self.image_folder):
                    QgsMessageLog.logMessage(f"Error: The folder '{self.image_folder}' does not exist.", 'Example2')
                    return

                if not os.path.isfile(self.base_image_path):
                    QgsMessageLog.logMessage(f"Error: The base image '{self.base_image_path}' does not exist.", 'Example2')
                    return

                if not os.path.isdir(os.path.dirname(self.output_path)):
                    QgsMessageLog.logMessage(f"Error: The directory '{os.path.dirname(self.output_path)}' does not exist.", 'Example2')
                    return

                Thread(target=self.monitor_folder, daemon=True).start()
        else:
            QgsMessageLog.logMessage("Dialog not initialized properly.", 'Example2')

    def monitor_folder(self, check_interval=10, max_idle_time=60):
        processed_files = set()
        last_update_time = time.time()

        while True:
            # List all image files in the directory
            image_files = [os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
            new_images = [f for f in image_files if f not in processed_files]

            if new_images:
                last_update_time = time.time()
                processed_files.update(new_images)
                self.merge_images(self.base_image_path, new_images, self.output_path)
                QgsMessageLog.logMessage(f"New images detected and processed: {new_images}", 'Example2')
            else:
                if time.time() - last_update_time > max_idle_time:
                    QgsMessageLog.logMessage("No new images detected for the specified time. Stopping folder monitoring.", 'Example2')
                    break

            time.sleep(check_interval)

    def add_raster_layer(self, image_path):
        layer_name = os.path.basename(image_path)
        raster_layer = QgsRasterLayer(image_path, layer_name)
        
        if raster_layer.isValid():
            QgsProject.instance().addMapLayer(raster_layer)
            self.previous_raster_layer = raster_layer  # Update the previous layer reference
            QgsMessageLog.logMessage(f"Raster layer '{layer_name}' added to QGIS project.", 'Example2')
        else:
            QgsMessageLog.logMessage(f"Failed to add raster layer '{layer_name}'.", 'Example2')

    def merge_images(self, base_image_path, new_images, output_path):
        # Check if base image exists
        if os.path.exists(base_image_path):
            base_image = gdal.Open(base_image_path)
            QgsMessageLog.logMessage(f"Base image '{base_image_path}' loaded successfully.", 'Example2')
        else:
            QgsMessageLog.logMessage(f"Error: Base image '{base_image_path}' not found.", 'Example2')
            return

        try:
            # Open new images
            datasets = [base_image] + [gdal.Open(img) for img in new_images]
            QgsMessageLog.logMessage(f"{len(new_images)} new images loaded.", 'Example2')
            
            # Merge images
            updated_image = gdal.Warp(output_path, datasets, format='GTiff')
            QgsMessageLog.logMessage(f"Updated merged image saved to '{output_path}'.", 'Example2')
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error during image merging: {str(e)}", 'Example2')
        
        finally:
            # Close the GDAL datasets
            for ds in datasets:
                ds = None
            QgsMessageLog.logMessage("GDAL datasets closed.", 'Example2')

            # Remove the previous raster layer if it exists
            if hasattr(self, 'previous_raster_layer') and self.previous_raster_layer:
                QgsProject.instance().removeMapLayer(self.previous_raster_layer.id())
                QgsMessageLog.logMessage("Previous raster layer removed from QGIS project.", 'Example2')
            else:
                QgsMessageLog.logMessage("No previous raster layer found to remove.", 'Example2')

            # Add the new raster layer to QGIS
            self.add_raster_layer(output_path)
            QgsMessageLog.logMessage(f"New raster layer '{os.path.basename(output_path)}' added to QGIS project.", 'Example2')
