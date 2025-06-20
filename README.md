#  Real-Time AIS Monitoring System

A real-time web-based system for capturing and displaying AIS (Automatic Identification System) messages from GPS devices using multithreading and socket programming.

🔗 **Live Demo**: [https://real-time-ais.onrender.com](https://real-time-ais.onrender.com)  
🧪 **Demo Login**:  
`Username: shruti`  
`Password: 12345`

---

## 📌 Features

- ⏱️ Real-time AIS message capture using sockets and multithreading
- ✅ Regex-based validation and filtering of incoming GPS data
- 🌍 Flask-powered web interface to display:
  - Live **location (lat/lon)**
  - **Speed**
  - **Battery status**
- 📁 Auto-logging of parsed AIS messages into CSV format
- 🧩 Modular support for various message types: `PVT`, `LGN`, `HEL`, `EMR`

---

## 🛠️ Tech Stack

- **Python**
- **Flask**
- **Sockets**
- **Multithreading**
- **Regular Expressions**
- **CSV Handling**

---

## 🚀 Run Locally

```bash
# Clone the repository
git clone https://github.com/shruti5155/real-time-ais.git
cd real-time-ais

# (Optional but recommended) Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
