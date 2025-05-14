#!/usr/bin/env python3

import sys
import os
import json
import psutil
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
                             QCheckBox, QComboBox)
from PyQt5.QtCore import QThread, pyqtSignal
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import socket

def load_config():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".creds.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    else:
        return {}

def save_config(config_data):
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".creds.json")
    try:
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
    except IOError as e:
        QMessageBox.critical(None, "Error", f"Could not save configuration: {e}")

class FTPServerThread(QThread):
    started = pyqtSignal(str)
    stopped = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, ip_address, port, username, password, root_path, parent=None):
        super().__init__(parent)
        self.ip_address = ip_address
        self.port = int(port)
        self.username = username
        self.password = password
        self.root_path = root_path
        self.server = None
        self._is_running = False

    def run(self):
        authorizer = DummyAuthorizer()
        authorizer.add_user(self.username, self.password, self.root_path, perm='elradfmw')
        handler = FTPHandler
        handler.authorizer = authorizer
        try:
            address = (self.ip_address, self.port)
            self.server = FTPServer(address, handler)
            self.started.emit(f"FTP server started on {self.ip_address}:{self.port}")
            self._is_running = True
            self.server.serve_forever()
        except socket.error as e:
            self.error.emit(f"Error starting FTP server: {e}")
        except Exception as e:
            self.error.emit(f"An unexpected error occurred: {e}")
        finally:
            self._is_running = False
            self.stopped.emit()

    def stop(self):
        if self.server and self._is_running:
            self.server.close_all()
            self._is_running = False

class FTPServerSetup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WTFTP")
        self.setGeometry(100, 100, 400, 350)
        self.ftp_thread = None
        self.config = load_config()
        self.initUI()

    def get_local_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except socket.error:
            return "127.0.0.1"

    def detect_drives(self):
        drives = []
        user = os.getlogin()
        possible_mount_prefixes = [f"/media/{user}/", "/mnt/"]
        for partition in psutil.disk_partitions():
            if partition.mountpoint != '/':
                for prefix in possible_mount_prefixes:
                    if partition.mountpoint.startswith(prefix):
                        drives.append(partition.mountpoint)
                        break
                if "media" in partition.mountpoint and not partition.mountpoint.startswith(f"/media/{user}/"):
                    drives.append(partition.mountpoint)
        return drives

    def update_drive_dropdown(self, checked):
        self.drive_dropdown.clear()
        if checked:
            drives = self.detect_drives()
            self.drive_dropdown.addItems(drives)
            self.drive_dropdown.setEnabled(True)
        else:
            self.drive_dropdown.setEnabled(False)

    def initUI(self):
        ip_label = QLabel("IP Address:")
        port_label = QLabel("Port:")
        username_label = QLabel("Username:")
        password_label = QLabel("Password:")
        self.status_label = QLabel("Idle")
        self.use_external_drive_checkbox = QCheckBox("Use External Drive:")
        self.drive_dropdown = QComboBox()
        self.drive_dropdown.setEnabled(False)
        external_drive_label = QLabel("Selected Path:")
        self.selected_path_label = QLabel(self.config.get("external_drive_path", "/"))
        default_ip = self.get_local_ip_address()
        self.ip_input = QLineEdit(default_ip)
        self.port_input = QLineEdit(str(self.config.get("port", 2121)))
        self.username_input = QLineEdit(self.config.get("username", "admin"))
        self.password_input = QLineEdit(self.config.get("password", "12345"))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.startButton = QPushButton("Start Server")
        self.stopButton = QPushButton("Stop Server")
        self.stopButton.setEnabled(False)
        self.use_external_drive_checkbox.setChecked(self.config.get("use_external_drive", False))
        self.update_drive_dropdown(self.use_external_drive_checkbox.isChecked())

        input_layout = QVBoxLayout()
        input_layout.addWidget(ip_label)
        input_layout.addWidget(self.ip_input)
        input_layout.addWidget(port_label)
        input_layout.addWidget(self.port_input)
        input_layout.addWidget(username_label)
        input_layout.addWidget(self.username_input)
        input_layout.addWidget(password_label)
        input_layout.addWidget(self.password_input)
        input_layout.addWidget(self.use_external_drive_checkbox)
        input_layout.addWidget(self.drive_dropdown)
        input_layout.addWidget(external_drive_label)
        input_layout.addWidget(self.selected_path_label)
        input_layout.addWidget(self.status_label)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.startButton)
        button_layout.addWidget(self.stopButton)
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.startButton.clicked.connect(self.start_ftp)
        self.stopButton.clicked.connect(self.stop_ftp)
        self.use_external_drive_checkbox.stateChanged.connect(self.update_drive_dropdown)
        self.drive_dropdown.currentIndexChanged.connect(self.update_selected_path)

        if self.use_external_drive_checkbox.isChecked():
            drives = self.detect_drives()
            self.drive_dropdown.addItems(drives)
            if self.config.get("external_drive_path") in drives:
                self.drive_dropdown.setCurrentText(self.config.get("external_drive_path"))
            elif drives:
                self.selected_path_label.setText(drives[0])
                self.config["external_drive_path"] = drives[0]
                save_config(self.config)
            self.drive_dropdown.setEnabled(True)
        else:
            self.drive_dropdown.setEnabled(False)

    def update_selected_path(self, index):
        if index >= 0:
            self.selected_path_label.setText(self.drive_dropdown.currentText())
            self.config["external_drive_path"] = self.drive_dropdown.currentText()
            save_config(self.config)
        else:
            self.selected_path_label.setText("/")
            self.config["external_drive_path"] = "/"
            save_config(self.config)

    def start_ftp(self):
        ip_address = self.ip_input.text()
        port = self.port_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        root_path = "/"
        if self.use_external_drive_checkbox.isChecked():
            root_path = self.drive_dropdown.currentText()

        if not ip_address or not port or not username or not password:
            QMessageBox.warning(self, "Warning", "Please fill in all the details.")
            return
        try:
            int(port)
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid port number.")
            return

        self.config["username"] = username
        self.config["password"] = password
        self.config["port"] = int(port)
        self.config["use_external_drive"] = self.use_external_drive_checkbox.isChecked()
        self.config["external_drive_path"] = root_path
        save_config(self.config)

        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.status_label.setText("Starting server...")
        self.ftp_thread = FTPServerThread(ip_address, port, username, password, root_path, self)
        self.ftp_thread.started.connect(self.show_message)
        self.ftp_thread.error.connect(self.show_error)
        self.ftp_thread.start()

    def stop_ftp(self):
        if self.ftp_thread and self.ftp_thread.isRunning():
            self.status_label.setText("Stopping server...")
            self.ftp_thread.stop()
            self.ftp_thread.wait()
            self.ftp_thread = None
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.status_label.setText("Server stopped.")
        else:
            self.status_label.setText("No server running.")
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)

    def show_message(self, message):
        QMessageBox.information(self, "Info", message)
        if message.startswith("FTP server started"):
            self.status_label.setText("Server running")
        elif message == "FTP server stopped.":
            self.status_label.setText("Server stopped.")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.status_label.setText("Error")

    def closeEvent(self, event):
        self.stop_ftp()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = FTPServerSetup()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
