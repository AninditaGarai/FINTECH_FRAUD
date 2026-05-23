# AI Financial Risk Intelligence Platform

Runnable MVP for a fintech risk platform: financial ratio analysis, bankruptcy prediction, fraud anomaly detection, PDF extraction, sentiment analysis, analyst-style reports, and a React dashboard.

## Backend

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python -m ml.train_bankruptcy
uvicorn main:app --reload
```

The training script automatically looks for:

- `backend/data/data.csv`
- `C:\Users\USER\Downloads\archive (2)\data.csv`
- `DATASET_PATH` environment variable

API:

- `POST /upload_csv`
- `POST /upload_pdf`
- `POST /train`
- `GET /sentiment/{company}`
- `GET /market/correlation?symbols=AAPL,MSFT,JPM,V,MA`
- `GET /analyses`

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL and upload your CSV.

## Docker

```powershell
docker compose up --build
```
