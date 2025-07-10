# backend/app/api/v1/routes.py

from fastapi import APIRouter, Query, HTTPException
from typing import List

# Servislerimizi ve şemalarımızı import ediyoruz
from app.services import pubmed_service, nlp_service
from .schemas import AnalyzedArticleSchema, AnalysisResultSchema

# FastAPI router nesnesini oluşturuyoruz.
# Tüm bu dosyadaki endpoint'ler bu router'a eklenecek.
router = APIRouter()


@router.get("/search", response_model=List[AnalyzedArticleSchema])
async def search_chemical_effects(
        chemical: str = Query(..., min_length=3, description="Etkileri araştırılacak kimyasalın adı"),
        limit: int = Query(10, ge=1, le=50, description="Getirilecek maksimum makale sayısı")
):
    """
    Verilen bir kimyasal için PubMed'de arama yapar, makale özetlerini çeker,
    NLP ile analiz eder ve sonuçları döndürür.
    """
    # 1. Adım: Veri Toplama
    try:
        articles = pubmed_service.search_and_fetch_articles(chemical_name=chemical, max_results=limit)
        if not articles:
            # HTTPException, FastAPI'ye standart bir HTTP hata yanıtı döndürmesini söyler.
            raise HTTPException(status_code=404, detail="Belirtilen kimyasal için makale bulunamadı.")
    except Exception as e:
        # Genel bir sunucu hatası durumunda
        raise HTTPException(status_code=500, detail=f"PubMed servis hatası: {e}")

    # 2. Adım: Veri İşleme ve Yanıtı Hazırlama
    analyzed_results = []
    for article in articles:
        analysis_data = {"results": {}}  # Default boş analiz
        if article.abstract:
            # NLP servisimizi kullanarak özeti analiz et
            analysis_data["results"] = nlp_service.analyze_text_with_spacy(article.abstract)

        # Makale verilerini ve analiz sonucunu tek bir nesnede birleştir
        analyzed_article = AnalyzedArticleSchema(
            **article.model_dump(),  # Pydantic modelini dictionary'e çevirir
            analysis=AnalysisResultSchema(**analysis_data)
        )
        analyzed_results.append(analyzed_article)

    return analyzed_results