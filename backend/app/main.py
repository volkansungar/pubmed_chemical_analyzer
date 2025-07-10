from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Bu satırı import edin
from .api.v1.routes import router as api_v1_router

app = FastAPI(
    title="PubMed Chemical Analyzer API",
    description="Bilimsel makalelerden kimyasal etkilerini analiz eden bir API.",
    version="1.0.0"
)

# --- CORS AYARLARI ---
# Frontend'in çalışacağı adreslerin listesi
origins = [
    "http://localhost",
    "http://localhost:3000", # React development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Belirtilen kaynaklardan gelen isteklere izin ver
    allow_credentials=True,
    allow_methods=["*"], # Tüm metodlara (GET, POST, vb.) izin ver
    allow_headers=["*"], # Tüm başlıklara izin ver
)
# --- CORS AYARLARI BİTTİ ---


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "PubMed Chemical Analyzer API'sine hoş geldiniz! Dokümantasyon için /docs adresini ziyaret edin."}

app.include_router(api_v1_router, prefix="/api/v1", tags=["Analysis"])