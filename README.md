# 🏀 BB Insider – Shot Map Analysis (CLI & Web)

BB Insider is a basketball match analysis tool extended with a **web-based shot map visualization system**.

This repository combines:
- The **original BB Insider CLI tool**
- A **FastAPI backend**
- A **web frontend** for interactive shot map generation

---

## 🔧 Features

- Download and process basketball match data by match ID
- Extract and normalize shot events
- Shot maps by court zones
- Filters:
  - Team (`home`, `away`, `home & away`)
  - Player
- Normalized half-court visualization
- Match processing progress tracking
- PNG shot map output

---

## 📁 Project Structure

```text
web_bbinsider/
├── api.py
├── function_shotmap.py
├── core/
│   ├── analyzeShots.py
│   ├── match_processor.py
│   ├── progress_store.py
│   └── ...
├── web/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── matches/   # ignored (generated match data)
├── tmp/       # ignored (generated images)
└── README.md
⚙️ Requirements
Python 3.10+

Libraries:

pip install requests tabulate Pillow fastapi uvicorn matplotlib

🌐 Web Usage
Start server
uvicorn api:app --reload
Open browser
http://127.0.0.1:8000/
🧪 Development Notes
function_shotmap.py and api.py can be debugged standalone (no server required)

Frontend changes may require hard refresh (Ctrl + F5)

Generated data is intentionally excluded from Git

📜 Credits
Original BB Insider
Core match parsing and analysis logic is based on the original BB Insider project.
All rights to the original implementation belong to its original author radszy (https://github.com/radszy).

Web Extension
Web interface, API layer, and shot map visualization developed by Sergi Martínez i Bragós.

This project extends the original codebase for analytical and educational purposes.

📌 License
Intended for personal and educational use.
For commercial usage, consult the original author.


---

# 📄 .gitignore (aligned with the project)

```gitignore
# ===============================
# Python
# ===============================
__pycache__/
*.py[cod]
*.pyo
*.pyd

# ===============================
# Virtual environments
# ===============================
.venv/
venv/
env/

# ===============================
# IDEs / Editors
# ===============================
.vscode/
.idea/
*.swp

# ===============================
# OS files
# ===============================
.DS_Store
Thumbs.db

# ===============================
# Generated project data
# ===============================
matches/
tmp/

# ===============================
# Matplotlib / cache
# ===============================
.matplotlib/

# ===============================
# Logs
# ===============================
*.log