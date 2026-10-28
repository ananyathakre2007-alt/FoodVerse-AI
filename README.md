# 🍽️ FoodVerse AI – Multimodal Food Intelligence Agent

React (frontend) + FastAPI (backend) + Gemini (Vision + Video + Audio + LLM) + SQLite (storage).

## Features
1. Food Recognition & Nutrition Analysis (image)
2. Food Freshness & Spoilage Detection (image)
3. Restaurant Hygiene & Safety Monitoring (image / video)
4. Smart Cooking Assistance (text / fridge photo / voice audio)
5. Personalised Meal Planning
6. History (SQLite)

## Requirements
- Python 3.10+  |  Node.js 18+
- (Optional) free Gemini API key: https://aistudio.google.com/apikey  (bina key ke DEMO MODE chalta hai)

## Run (2 terminals, VS Code me Ctrl+` )

### Terminal 1 – Backend
```
cd backend
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env   -> phir .env me GEMINI_API_KEY paste karo
uvicorn main:app --reload
```
Backend: http://127.0.0.1:8000  (API docs: /docs)

### Terminal 2 – Frontend
```
cd frontend
npm install
npm run dev
```
Open: http://localhost:5173

## Structure
```
FoodVerse-AI/
├── backend/   main.py (API) · ai_service.py (Gemini prompts) · database.py (SQLite)
└── frontend/  src/App.jsx · src/api.js · src/styles.css
```
Video/audio limit: 20MB. Ye tool sirf estimate deta hai, medical/legal advice nahi.
