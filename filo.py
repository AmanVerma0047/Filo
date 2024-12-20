#------------------------
#Author:Aman Verma
#date:11-12-2024
#Build:v0.1.4
#software:Filo
#------------------------
import sys
import os
import json
import subprocess
import platform
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QListWidgetItem,
    QMenu,
    QLabel
)
from PyQt5.QtCore import Qt, QMimeData, QUrl,QTimer
from PyQt5.QtGui import QDrag, QPixmap, QIcon

class FiloApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Filo - by Aman Verma")
        self.setGeometry(200, 200, 600, 500)

        self.workspace_file = None

        # Applying color scheme
        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: white;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #444;
                padding: 10px;
                color: white;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        self.init_ui()
        self.check_workspace_load()

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
        self.file_list.startDrag = self.startDrag
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        # Connect double-click to open file
        self.file_list.itemDoubleClicked.connect(self.open_file)
        # Placeholder Text
        self.placeholder_label = QLabel("Drag files here\n<small>right click to view options</small>")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: gray; font-size: 16px;")
        self.placeholder_label.setTextFormat(Qt.RichText)
        self.placeholder_label.setWordWrap(True)

        # Add widgets to layout
        layout.addWidget(self.placeholder_label)
        layout.addWidget(self.file_list)

        self.main_widget.setLayout(layout)

        # Update placeholder visibility initially
        self.update_placeholder_visibility()



    def open_file(self, item):
        # Get the file path from the clicked item
        file_path = item.text()

        # Check the operating system and open the file accordingly
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', file_path])
            elif platform.system() == 'Linux':  # Linux
                subprocess.Popen(['xdg-open', file_path])
            else:  # Windows
                subprocess.Popen(['start', file_path], shell=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open the file: {str(e)}")





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
                    self.add_file_item(file_path)
            event.accept()
            self.update_placeholder_visibility()

    def startDrag(self, event):  # Add event as a parameter
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
                self.add_file_item(folders)

        for file in files:
            if file not in self.get_all_files():
                self.add_file_item(file)

        self.update_placeholder_visibility()

    def add_file_item(self, file_path):
        # Create a list item for each file/folder
        list_item = QListWidgetItem(file_path)

        # Set the item icon for image files
        if file_path.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
            pixmap = QPixmap(file_path).scaled(100, 100, Qt.KeepAspectRatio)
            list_item.setIcon(QIcon(pixmap))

        # Set the tooltip to show the file's directory
        directory = os.path.dirname(file_path)
        list_item.setToolTip(f"Path: {directory}")

        # Add the item to the list
        self.file_list.addItem(list_item)
        self.update_placeholder_visibility()

    def clear_files(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to clear the clipboard?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.file_list.clear()
            self.update_placeholder_visibility()

    def get_all_files(self):
        return [self.file_list.item(i).text() for i in range(self.file_list.count())]

    def save_workspace(self):
        if not self.workspace_file:
            options = QFileDialog.Options()
            self.workspace_file, _ = QFileDialog.getSaveFileName(
                self, "Save Workspace", "", "JSON Files (*.json)", options=options
            )
        if self.workspace_file:
            with open(self.workspace_file, 'w') as file:
                json.dump(self.get_all_files(), file)
            QMessageBox.information(self, "Saved", "Workspace saved successfully.")

    def load_workspace(self):
        options = QFileDialog.Options()
        workspace_file, _ = QFileDialog.getOpenFileName(
            self, "Open Workspace", "", "JSON Files (*.json)", options=options
        )
        if workspace_file:
            self.workspace_file = workspace_file
            with open(workspace_file, 'r') as file:
                files = json.load(file)
                self.file_list.clear()
                for file_path in files:
                    self.add_file_item(file_path)
            self.update_placeholder_visibility()

    def check_workspace_load(self):
        response = QMessageBox.question(
            self,
            "Load Workspace",
            "Do you want to load a workspace?",
            QMessageBox.Yes | QMessageBox.No
        )
        if response == QMessageBox.Yes:
            self.load_workspace()

    def closeEvent(self, event):
        confirm = QMessageBox.question(
            self,
            "Save Workspace",
            "Do you want to save your workspace before exiting?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        )
        if confirm == QMessageBox.Yes:
            self.save_workspace()
            event.accept()
        elif confirm == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

    def show_temporary_message(self, message):
        temp_label = QLabel(message, self)
        temp_label.setStyleSheet("background-color: black; color: white; padding: 5px; border-radius: 25px;")
        temp_label.setAlignment(Qt.AlignCenter)
        temp_label.setGeometry((self.width() - 200) // 2, 10, 200, 30)
        temp_label.show()

        # Hide the label after 1 second
        QTimer.singleShot(1000, temp_label.deleteLater)

    def show_context_menu(self, position):
        menu = QMenu()

        add_action = menu.addAction("Add Files/Folders")
        clear_action = menu.addAction("Clear Clipboard")
        add_save_workspace = menu.addAction("Save Workspace")
        add_load_workspace = menu.addAction("Load Workspace")
        always_on_top_action = menu.addAction("Show on Top")
        action = menu.exec_(self.file_list.viewport().mapToGlobal(position))

        # Check if the window is already set to "Always on Top" and update the action text accordingly
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            always_on_top_action.setText("Disable Always on Top")
        else:
            always_on_top_action.setText("Enable Always on Top")


        if action == add_action:
            self.add_files()
        elif action == clear_action:
            self.clear_files()
        elif action == add_save_workspace:
            self.save_workspace()
        elif action == add_load_workspace:
            self.load_workspace()
        elif action == always_on_top_action:
            self.toggle_always_on_top()

    def update_placeholder_visibility(self):
        if self.file_list.count() == 0:
            self.placeholder_label.show()
        else:
            self.placeholder_label.hide()

    def toggle_always_on_top(self):
        # Check current state and toggle the "Always on Top" setting
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)            
            #showing message show on top enabled
            self.show_temporary_message("Show on Top Disabled!")
        else:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            #showing message show on top enabled
            self.show_temporary_message("Show on Top Enabled!")


        
        # Apply the new flag settings
        self.show()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FiloApp()
    window.show()
    sys.exit(app.exec_())
