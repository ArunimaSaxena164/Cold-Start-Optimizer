# Serverless Cold Start Optimization

## Setup

### Backend
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app:app --reload

### Frontend
cd frontend
npm install
npm run dev

Backend: http://127.0.0.1:8000  
Frontend: http://localhost:5173