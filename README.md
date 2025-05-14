![screenshot of the tool](/sc/sc.png)

# WTF-TP: Your Simple FTP Server

WTF-TP is a simple FTP server application built using Python and PyQt5. It allows you to quickly set up a local FTP server for file sharing.

## Features

* **Easy Setup:** Quickly configure and start an FTP server.
* **User Authentication:** Control access to your files with username and password authentication.
* **Directory Selection:** Choose the directory you want to share via FTP.
* **Graphical Interface:** A user-friendly interface for managing your FTP server.
* **User Configurable username and password:** Configure the default username and password in the creds.json file.

## Pre-Requisites
* Need to be in same Wifi connection as your linux machine.
* Currently only developed for Debain based linux distros with Apt package manager.
* Mobile Hotspot is also counted as being in same wifi connection.
* The external drive is to be mounted before accesing it through the tool.

## Requirements

* Python 3
* PyQt5
* pyftpdlib

## Installation

1.  **Clone the repository:**
    ```bash
    mkdir wtftp
    cd wtftp
    git clone <repository_url>
    ```
2.  **Install the requirements:**
    ```bash
    python3 -m pip install pyftpdlib
    ```
3.  **Make it as an executable**
    ```bash
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
