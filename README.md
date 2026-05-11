# StealthGuard: Secure Image Steganography 🔒

StealthGuard is a web-based cybersecurity tool that allows users to securely hide secret messages inside images using **Least Significant Bit (LSB) Steganography** combined with **AES Encryption**. 

This interdisciplinary project bridges **Data Science** (image pixel manipulation) and **Cybersecurity** (password-protected cryptography) to ensure that your sensitive data remains entirely invisible to the naked eye and undecipherable without the correct password.

## 🌟 Features
- **AES-256 Encryption**: Messages are securely encrypted using the `cryptography` library (Fernet symmetric encryption) and PBKDF2 key derivation.
- **LSB Steganography**: Data is hidden in the Least Significant Bits of the image's RGB channels, meaning the image looks completely unaltered to the human eye.
- **Lossless Export**: Watermarked images are strictly saved as `.png` files to prevent compression algorithms (like JPEG) from destroying the hidden data.
- **Modern UI**: A responsive, premium dark-mode interface with drag-and-drop file support.
- **Vercel Ready**: Pre-configured for seamless serverless deployment.

## 🛠️ Tech Stack
- **Backend**: Python, Flask
- **Image Processing**: Pillow (PIL)
- **Encryption**: Cryptography (Fernet)
- **Frontend**: HTML5, Vanilla CSS, JavaScript

## 🚀 Running Locally

### Prerequisites
Make sure you have [Python 3.8+](https://www.python.org/downloads/) installed on your computer.

### Installation
1. Clone the repository or download the project folder.
2. Open a terminal in the project directory and install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask web server:
   ```bash
   python app.py
   ```
4. Open your web browser and navigate to `http://127.0.0.1:5000`.

## 🌐 Deploying to Vercel
This project includes a `vercel.json` configuration file, making it ready for 1-click deployment to Vercel's serverless infrastructure.

1. Upload your code to a GitHub repository.
2. Go to [Vercel](https://vercel.com/) and create a new project.
3. Import your GitHub repository.
4. Leave the default settings (Vercel will automatically detect Python and your `requirements.txt`).
5. Click **Deploy**.

*(Note: File uploads use the system's temporary directory to comply with Vercel's read-only serverless environment.)*

## ⚠️ Important Note on Usage
If you send your output image (`secret_image.png`) through messaging apps that compress images (like WhatsApp, Messenger, or standard iMessage/SMS), the hidden data **will be destroyed**. Always share the file via uncompressed methods like Email, Google Drive, or Slack (as a file).
