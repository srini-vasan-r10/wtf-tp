# WTF-TP: Your Simple FTP Server

WTF-TP is a simple FTP server application built using Python and PyQt5. It allows you to quickly set up a local FTP server for file sharing.

## Features

* **Easy Setup:** Quickly configure and start an FTP server.
* **User Authentication:** Control access to your files with username and password authentication.
* **Directory Selection:** Choose the directory you want to share via FTP.
* **Graphical Interface:** A user-friendly interface for managing your FTP server.

## Requirements

* Python 3
* PyQt5
* pyftpdlib

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd wtftp
    ```
2.  **Install the requirements:**
    ```bash
    python3 -m pip install pyftpdlib
    ```
3.  **Make it as an executable**
    ```bash
    cd /locationtourdir/wtf-tp.py
    chmod +x ./wtf-tp.py
    ```
4.  **Run the file**
    ```bash
    ./wtf-tp.py
    ```

## Usage

1.  Launch the WTF-TP application.
2.  Configure the FTP server settings, including IP address, port, username, password, and the directory to share.
3.  Click "Start Server" to start the FTP server.
4.  Share your files!

## License

[MIT License](LICENSE)
