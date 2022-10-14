import os
import sys
import interface
import threading

from PIL import Image
from PyQt5 import QtWidgets
from datetime import datetime


class SystemDialog():
    def __init__(self):
        self.icon_critical = QtWidgets.QMessageBox.Icon.Critical
        self.icon_warning = QtWidgets.QMessageBox.Icon.Warning
        self.icon_info = QtWidgets.QMessageBox.Icon.Information

        self.btn_ok = QtWidgets.QMessageBox.StandardButton.Ok
        self.btn_close = QtWidgets.QMessageBox.StandardButton.Close

    def dialog_handler(self, title, message, icon, status, buttons, path=None):
        self.dialog = QtWidgets.QMessageBox()
        self.dialog.setWindowTitle(title)
        self.dialog.setText(message)
        self.dialog.setIcon(icon)

        if status == "converted":
            self.show = self.dialog.addButton("Show", self.dialog.ButtonRole.YesRole)
            self.ok = self.dialog.addButton(buttons[0])
            threading.Thread(target=self.click_show, daemon=True, args=[path]).start()
        else:
            for i in range(len(buttons)):
                self.dialog.addButton(buttons[i])

        self.dialog.exec_()

    def click_show(self, path):
        while True:
            if self.dialog.clickedButton() == self.show:
                os.system(rf"explorer.exe {path}")
                break

            if self.dialog.clickedButton() == self.ok:
                break

class ImageConverter(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._sys = SystemDialog()
        self.ui = interface.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.Convert.setEnabled(False)
        self.ui.widthLine.setVisible(False)
        self.ui.heightLine.setVisible(False)
        self.ui.sizeLabel_2.setVisible(False)
        self.ui.nameLine.setVisible(False)
        self.connect_btns()

        self.extensions = ["png", "jpg", "jpeg", "pdf", "bmp", "ico", "webp", "tiff"]
        self.invalid_symbols = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]
        self.save_path = os.getcwd() + "\\export"
        self.ui.pathFileLine.setText(self.save_path)
        self.quality = int(self.ui.qualLineBox.text())
        self.byte = 1048576

        self.label_filesize = None
        self.filename = None
        self.filesize = None
        self.file_path = None
        self.save_file_path = None
        self.set_ext = None
        self.set_ext_format = None

    def init_img(self):
        self.file_path = self.ui.cFile_line.text()

        if os.path.exists(self.file_path):
            self.input_image = Image.open(self.file_path)
            with self.input_image:
                self.convert()
        else:
            self._sys.dialog_handler("FileNotFoundError", "Could not find file with this path.",
                                self._sys.icon_critical, "error", [self._sys.btn_close])

    def upload_file(self):
        try:
            self.file_path = QtWidgets.QFileDialog.getOpenFileName()
            extension = self.file_path[0].split("/")[-1].split(".")[1]

            if extension in self.extensions:
                self.ui.cFile_line.setText(self.file_path[0])
                self.ui.Convert.setEnabled(True)

                self.label_filesize = round(os.stat(self.file_path[0]).st_size/self.byte, 2)
                self.ui.label_2.setText(str(self.label_filesize) + " MB")
                self.set_ext = self.ui.toLine.currentText()
            else:
                self._sys.dialog_handler("Extension error", "Invalid file format!",
                                self._sys.icon_critical, "error", [self._sys.btn_close])
        except IndexError:
            pass

    def save_file_p(self):
        try:
            self.save_file_path = QtWidgets.QFileDialog.getExistingDirectory()

            if len(self.save_file_path) > 0:
                self.ui.pathFileLine.setText(self.save_file_path)
            else:
                self.ui.pathFileLine.setText(self.save_path)
        except IndexError:
            pass

    def convert(self):
        if len(self.ui.nameLine.text()) > 0:
            self.filename = self.ui.nameLine.text()
        else:
            self.filename = "converted_{0}".format(datetime.strftime(datetime.now(), "%H-%M-%S"))

        self.save_file_path = self.ui.pathFileLine.text()
        save_path = self.save_file_path + f"\\{self.filename}.{self.set_ext}"

        if self.filesize and self.filesize[0] > 0 and self.filesize[1] > 0:
            resized_input_image = self.input_image.resize(self.filesize[1])
            resized_input_image.save(save_path, format=self.set_ext_format, quality=self.quality, subsampling=0)
        else:
            self.input_image.save(save_path, format=self.set_ext_format, quality=self.quality, subsampling=0)

        self._sys.dialog_handler("Succesfull", f"The converted image is saved as:\n{save_path}!",
                            self._sys.icon_info, "converted", [self._sys.btn_ok], self.save_file_path)

    def connect_btns(self):
        self.ui.Convert.clicked.connect(self.init_img)
        self.ui.cFile.clicked.connect(self.upload_file)
        self.ui.pathFileBtn.clicked.connect(self.save_file_p)
        self.ui.toLine.currentTextChanged.connect(self.change_ext)
        self.ui.cSize.currentTextChanged.connect(self.change_size_setting)
        self.ui.cName.currentTextChanged.connect(self.change_name_setting)
        self.ui.qualLineBox.valueChanged.connect(self.change_qualituy_setting)

    def change_qualituy_setting(self):
        self.quality = self.ui.qualLineBox.value()

    def change_size_setting(self):
        if self.ui.cSize.currentText() == "Output size":
            self.ui.widthLine.setValue(0)
            self.ui.heightLine.setValue(0)
            self.ui.widthLine.setVisible(False)
            self.ui.heightLine.setVisible(False)
            self.ui.sizeLabel_2.setVisible(False)
        else:
            self.ui.widthLine.setVisible(True)
            self.ui.heightLine.setVisible(True)
            self.ui.sizeLabel_2.setVisible(True)
            self.ui.widthLine.textChanged.connect(self.change_size)
            self.ui.heightLine.textChanged.connect(self.change_size)

    def change_name_setting(self):
        if self.ui.cName.currentText() == "Output name":
            self.ui.nameLine.clear()
            self.ui.nameLine.setVisible(False)
        else:
            self.ui.nameLine.setVisible(True)
            self.ui.nameLine.textChanged.connect(self.change_name)

    def change_size(self):
        self.filesize = (self.ui.widthLine.value(), self.ui.heightLine.value())

    def change_name(self):
        for invalid_symbol in self.invalid_symbols:
            if not invalid_symbol in self.ui.nameLine.text():
                self.filename = self.ui.nameLine.text()

            else:
                self.ui.nameLine.clear()
                self._sys.dialog_handler("Symbol error", 
                                "The file name cannot contain the following characters:\n\\ / : * ? \" < > |",
                                self._sys.icon_warning, "error", [self._sys.btn_ok])

    def change_ext(self):
        self.set_ext = self.ui.toLine.currentText()
        self.set_ext_format = self.set_ext

        if self.set_ext == "jpg": self.set_ext_format = "jpeg"


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ImageConverter()
    window.show()
    app.exec_()