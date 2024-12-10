import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QMimeData, QUrl
from PyQt5.QtGui import QDrag, QPixmap


class FileClipboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Clipboard")
        self.setGeometry(200, 200, 500, 400)
        self.init_ui()

    def init_ui(self):
        # Main Widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Layout
        layout = QVBoxLayout()

        # File List
        self.file_list = QListWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.setDragEnabled(True)
        self.file_list.setDragDropMode(QListWidget.InternalMove)
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dropEvent = self.dropEvent
        self.file_list.startDrag = self.start_drag  # Overriding startDrag

        # Buttons
        add_button = QPushButton("Add Files/Folders")
        add_button.clicked.connect(self.add_files)

        clear_button = QPushButton("Clear Clipboard")
        clear_button.clicked.connect(self.clear_files)

        # Add widgets to layout
        layout.addWidget(self.file_list)
        layout.addWidget(add_button)
        layout.addWidget(clear_button)

        self.main_widget.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path not in self.get_all_files():
                    self.file_list.addItem(file_path)
            event.accept()

    def start_drag(self, event):  # Add event as a parameter
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        # Prepare drag data
        drag = QDrag(self.file_list)
        mime_data = QMimeData()

        # Create a list of file URLs
        file_paths = [os.path.abspath(item.text()) for item in selected_items]
        mime_data.setUrls([QUrl.fromLocalFile(file) for file in file_paths])

        drag.setMimeData(mime_data)

        # Add visual feedback (optional)
        pixmap = QPixmap(200, 50)
        pixmap.fill(Qt.lightGray)
        drag.setPixmap(pixmap)

        # Start the drag operation
        drag.exec_(Qt.CopyAction)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        folders = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folders:
            if folders not in self.get_all_files():
                self.file_list.addItem(folders)

        for file in files:
            if file not in self.get_all_files():
                self.file_list.addItem(file)

    def clear_files(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to clear the clipboard?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.file_list.clear()

    def get_all_files(self):
        return [self.file_list.item(i).text() for i in range(self.file_list.count())]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileClipboard()
    window.show()
    sys.exit(app.exec_())
