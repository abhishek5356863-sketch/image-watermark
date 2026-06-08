<p align="center">
  <h1 align="center">🛡️ StealthGuard</h1>
  <p align="center"><b>Secure Image & Audio Steganography Tool</b></p>
  <p align="center">Hide encrypted secret messages inside images and audio files — completely undetectable.</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.0.3-green?logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Encryption-AES--256-red?logo=letsencrypt&logoColor=white" />
  <img src="https://img.shields.io/badge/Steganography-EOF-purple" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

---

## 📖 About

**StealthGuard** is a web-based cybersecurity application that lets users securely hide encrypted messages inside **images** and **audio files** using **End-of-File (EOF) Steganography** combined with **AES-256 Encryption**.

The tool bridges **Data Science** (binary file manipulation) and **Cybersecurity** (password-protected cryptography) to ensure your sensitive data remains entirely invisible and undecipherable without the correct password.

> The output file retains its **original format and file size**, making the hidden data completely undetectable.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **AES-256 Encryption** | Messages are encrypted using the `cryptography` library (Fernet symmetric encryption) with PBKDF2-HMAC-SHA256 key derivation (100,000 iterations). |
| 🖼️ **Image Steganography** | Hide data inside PNG, JPG, JPEG, and BMP image files. |
| 🎵 **Audio Steganography** | Hide data inside MP3, WAV, OGG, FLAC, and M4A audio files. |
| 🎬 **Video Steganography** | Hide data inside MP4 video files. |
| 📁 **Zero Size Change** | EOF technique keeps the output file size virtually identical to the original — no suspicious bloating. |
| 🎨 **Premium Dark UI** | Responsive, glassmorphism-styled dark-mode interface with drag-and-drop, live previews, and 3D animations. |
| 👤 **User Authentication** | Secure login/register system with hashed passwords (Werkzeug) and session management. |
| ☁️ **Vercel Ready** | Pre-configured `vercel.json` for one-click serverless deployment. |
| 🔄 **Backward Compatible** | Decoder automatically detects EOF or legacy LSB-encoded files. |

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| [Python](https://python.org) | 3.8+ | Core programming language |
| [Flask](https://flask.palletsprojects.com) | 3.0.3 | Lightweight web framework |
| [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com) | 3.1.1 | ORM for SQLite database |
| [Werkzeug](https://werkzeug.palletsprojects.com) | (bundled) | Password hashing & file utilities |

### Cryptography & Steganography
| Technology | Version | Purpose |
|---|---|---|
| [Cryptography](https://cryptography.io) | 42.0.5 | AES-256 Fernet encryption & PBKDF2 key derivation |
| [Pillow (PIL)](https://pillow.readthedocs.io) | 11.1.0 | Image processing (legacy LSB fallback) |
| Custom EOF Engine | — | Appends encrypted data to end of media files |

### Frontend
| Technology | Purpose |
|---|---|
| HTML5 | Semantic page structure |
| Vanilla CSS | Premium dark-mode styling with glassmorphism & animations |
| JavaScript (ES6+) | Async form handling, drag-and-drop, live media previews |
| [Three.js](https://threejs.org) | 3D wireframe animations (shield & icosahedron) |
| [Google Fonts (Outfit)](https://fonts.google.com/specimen/Outfit) | Modern typography |

### Database
| Technology | Purpose |
|---|---|
| SQLite | Lightweight embedded database for user accounts |

### Deployment
| Technology | Purpose |
|---|---|
| [Vercel](https://vercel.com) | Serverless cloud hosting |
| `tempfile` | Handles file I/O in read-only serverless environments |

---

## 📂 Project Structure

```
StealthGuard/
│
├── app.py                  # 🚀 Main Flask application (routes, auth, API endpoints)
├── steganography.py        # 🔒 Core steganography engine (EOF encode/decode + LSB fallback)
├── requirements.txt        # 📦 Python dependencies
├── vercel.json             # ☁️  Vercel deployment configuration
├── check_db.py             # 🔍 Database inspection utility
├── test_add_user.py        # 🧪 Test script for adding users
├── .gitignore              # 🚫 Git ignore rules
├── README.md               # 📖 This file
│
├── static/                 # 🎨 Frontend static assets
│   ├── style.css           #    Main application stylesheet (dark theme)
│   ├── landing.css          #    Landing page stylesheet
│   ├── script.js           #    Client-side JS (forms, drag-drop, previews)
│   ├── bg.png              #    Background image asset
│   ├── abhishek.jpeg       #    Team member photo
│   ├── akshata.jpeg        #    Team member photo
│   ├── yuvraj.jpeg         #    Team member photo
│   ├── vasanth.jpeg        #    Team member photo
│   └── chanda.jpeg         #    Team member photo
│
├── templates/              # 🌐 Jinja2 HTML templates
│   ├── landing.html        #    Public landing/home page
│   ├── login.html          #    User login page
│   ├── register.html       #    User registration page
│   ├── index.html          #    Main app dashboard (encode/decode/profile)
│   ├── about.html          #    About Us / Team page
│   ├── privacy.html        #    Privacy Policy page
│   └── terms.html          #    Terms of Service page
│
├── uploads/                # 📤 Temporary uploaded files (auto-cleaned)
├── outputs/                # 📥 Generated steganography output files
└── venv/                   # 🐍 Python virtual environment (not committed)
```

---

## ⚙️ How It Works

### 🔒 Encoding (Hiding Data)
```
User Input (Image/Audio + Message + Password)
        │
        ▼
┌──────────────────────────┐
│  1. Encrypt message with │
│     AES-256 (Fernet)     │
│     using PBKDF2 key     │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  2. Read original media  │
│     file as raw bytes    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  3. Append EOF marker    │
│     + encrypted payload  │
│     to end of file       │
└──────────┬───────────────┘
           │
           ▼
   Output file (same format,
    same size, with hidden data)
```

### 🔓 Decoding (Extracting Data)
```
User Input (Encoded Media + Password)
        │
        ▼
┌──────────────────────────┐
│  1. Scan file bytes for  │
│     EOF marker           │
│     "====STEALTHGUARD====│
└──────────┬───────────────┘
           │
     ┌─────┴─────┐
     │  Found?   │
     └─────┬─────┘
       Yes │        No
           │         │
           ▼         ▼
┌────────────┐  ┌────────────┐
│ Extract &  │  │ Fallback:  │
│ decrypt    │  │ Try legacy │
│ EOF data   │  │ LSB method │
└────────────┘  └────────────┘
           │
           ▼
   Decrypted secret message
```

---

## 🚀 Getting Started

### Prerequisites
- [Python 3.8+](https://www.python.org/downloads/)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/abhishek5356863-sketch/image-watermark.git
   cd image-watermark
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

---

## ☁️ Deploying to Vercel

This project includes a pre-configured `vercel.json` for seamless serverless deployment.

1. Push your code to a GitHub repository.
2. Go to [Vercel](https://vercel.com/) and create a new project.
3. Import your GitHub repository.
4. Leave the default settings — Vercel will auto-detect Python and `requirements.txt`.
5. Click **Deploy**.

> **Note:** File uploads use `tempfile.gettempdir()` to comply with Vercel's read-only serverless filesystem.

---

## 📋 API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/` | Landing page | ❌ |
| `GET` | `/login` | Login page | ❌ |
| `POST` | `/login` | Authenticate user | ❌ |
| `GET` | `/register` | Registration page | ❌ |
| `POST` | `/register` | Create new account | ❌ |
| `GET` | `/app` | Main dashboard | ✅ |
| `POST` | `/api/encode` | Encode message into media file | ✅ |
| `POST` | `/api/decode` | Decode message from media file | ✅ |
| `GET` | `/about` | About / Team page | ❌ |
| `GET` | `/logout` | End session | ✅ |

---

## 🎨 Supported Media Formats

### Images
| Format | Extension | Status |
|---|---|---|
| PNG | `.png` | ✅ Supported |
| JPEG | `.jpg`, `.jpeg` | ✅ Supported |
| BMP | `.bmp` | ✅ Supported |

### Audio
| Format | Extension | Status |
|---|---|---|
| MP3 | `.mp3` | ✅ Supported |
| WAV | `.wav` | ✅ Supported |
| OGG | `.ogg` | ✅ Supported |
| FLAC | `.flac` | ✅ Supported |
| M4A | `.m4a` | ✅ Supported |

### Video
| Format | Extension | Status |
|---|---|---|
| MP4 | `.mp4` | ✅ Supported |

---

## ⚠️ Important Notes

- **Do NOT share encoded files via WhatsApp, Messenger, or iMessage** — these platforms compress and modify files, which will destroy the hidden data.
- **Always share via:** Email attachments, Google Drive, Slack (as file), or USB transfer.
- **The output file keeps its original format** — a `.jpg` stays `.jpg`, an `.mp3` stays `.mp3`.

---

## 👥 Team

| Name | Role |
|---|---|
| **Abhishek** | Lead Developer & Security Researcher |
| **Akshata** | Security Analyst & System Designer |
| **Yuvraj** | Full Stack Developer & AI Specialist |
| **Vasanth** | Cybersecurity Engineer & Network Architect |
| **Chanda** | Backend Developer & Database Architect |

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  <b>Built with 🔒 by the StealthGuard Team</b>
</p>
