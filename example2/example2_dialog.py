from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QPushButton, QDialogButtonBox
from qgis.core import QgsMessageLog  # Import QgsMessageLog

class Example2Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Example2Dialog, self).__init__(parent)
        self.setupUi()
        self.setup_connections()

    def setupUi(self):
        self.mQgsFileWidget = QLineEdit(self)
        self.mQgsFileWidget_2 = QLineEdit(self)
        self.mQgsFileWidget_3 = QLineEdit(self)
        self.pushButton_ = QPushButton("Browse", self)
        self.pushButton_2 = QPushButton("Browse", self)
        self.pushButton_3 = QPushButton("Browse", self)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
       
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.mQgsFileWidget)
        layout.addWidget(self.pushButton_)
        layout.addWidget(self.mQgsFileWidget_2)
        layout.addWidget(self.pushButton_2)
        layout.addWidget(self.mQgsFileWidget_3)
        layout.addWidget(self.pushButton_3)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def setup_connections(self):
        self.pushButton_.clicked.connect(self.select_folder_1)
        self.pushButton_2.clicked.connect(self.select_folder_2)
        self.pushButton_3.clicked.connect(self.select_folder_3)
        self.button_box.accepted.connect(self.on_accept)  # Use on_accept method for Ok button
        self.button_box.rejected.connect(self.reject)  # Use rejected signal for Cancel button

    def select_folder_1(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder 1")
        if folder_path:
            self.mQgsFileWidget.setText(folder_path)

    def select_folder_2(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder 2")
        if folder_path:
            self.mQgsFileWidget_2.setText(folder_path)

    def select_folder_3(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder 3")
        if folder_path:
            self.mQgsFileWidget_3.setText(folder_path)

    def get_file_path_1(self):
        return self.mQgsFileWidget.text()

    def get_file_path_2(self):
        return self.mQgsFileWidget_2.text()

    def get_file_path_3(self):
        return self.mQgsFileWidget_3.text()

    def clear_fields(self):
        """Clears the input fields."""
        self.mQgsFileWidget.clear()
        self.mQgsFileWidget_2.clear()
        self.mQgsFileWidget_3.clear()

    def on_accept(self):
        """Called when the OK button is clicked."""
        QgsMessageLog.logMessage(f"Folder 1: {self.get_file_path_1()}", "Example2Dialog")
        QgsMessageLog.logMessage(f"Folder 2: {self.get_file_path_2()}", "Example2Dialog")
        QgsMessageLog.logMessage(f"Folder 3: {self.get_file_path_3()}", "Example2Dialog")

        self.clear_fields()  # Clear fields before accepting
        self.accept()  # Call the default accept method to close the dialog
