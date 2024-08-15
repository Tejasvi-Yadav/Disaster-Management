from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLineEdit, QPushButton, QFileDialog
import os

class Example3Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        """Constructor."""
        super(Example3Dialog, self).__init__(parent)
        self.setupUi(self)

        # Connect buttons to methods
        self.submitButton.clicked.connect(self.handleSubmit)
        self.browseButton_1.clicked.connect(lambda: self.browseDirectory(1))
        self.browseButton_2.clicked.connect(lambda: self.browseDirectory(2))

    def setupUi(self, Dialog):
        # Basic UI setup
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        
        # Directory Line Edit 1
        self.directoryLineEdit_1 = QLineEdit(Dialog)
        self.directoryLineEdit_1.setGeometry(QtCore.QRect(20, 20, 260, 24))
        self.directoryLineEdit_1.setPlaceholderText("Enter directory path")
        
        # Browse Button 1
        self.browseButton_1 = QPushButton(Dialog)
        self.browseButton_1.setGeometry(QtCore.QRect(290, 20, 80, 24))
        self.browseButton_1.setText("Browse")
        
        # Directory Line Edit 2
        self.directoryLineEdit_2 = QLineEdit(Dialog)
        self.directoryLineEdit_2.setGeometry(QtCore.QRect(20, 60, 260, 24))
        self.directoryLineEdit_2.setPlaceholderText("Enter directory path")
        
        # Browse Button 2
        self.browseButton_2 = QPushButton(Dialog)
        self.browseButton_2.setGeometry(QtCore.QRect(290, 60, 80, 24))
        self.browseButton_2.setText("Browse")
        
        # Submit Button
        self.submitButton = QPushButton(Dialog)
        self.submitButton.setGeometry(QtCore.QRect(290, 100, 80, 24))
        self.submitButton.setText("Submit")
        
        # Button Box (for Cancel and Ok)
        self.button_box = QtWidgets.QDialogButtonBox(Dialog)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle("Example 3 Plugin")

    def handleSubmit(self):
        """Handle the submit button click event."""
        directory_path_1 = self.directoryLineEdit_1.text()
        directory_path_2 = self.directoryLineEdit_2.text()

        valid_1 = os.path.isdir(directory_path_1)
        valid_2 = os.path.isdir(directory_path_2)

        if valid_1 and valid_2:
            self.accept()  # Close the dialog and indicate success
        else:
            invalid_paths = []
            if not valid_1:
                invalid_paths.append(directory_path_1)
            if not valid_2:
                invalid_paths.append(directory_path_2)
            QtWidgets.QMessageBox.warning(self, "Invalid Path", f"The following paths are not valid directories:\n" + "\n".join(invalid_paths))

    def browseDirectory(self, edit_number):
        """Open a dialog to browse and select a directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            if edit_number == 1:
                self.directoryLineEdit_1.setText(directory)
            elif edit_number == 2:
                self.directoryLineEdit_2.setText(directory)
