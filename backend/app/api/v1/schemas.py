# backend/app/api/v1/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# Bu schema'yı daha önce oluşturmuştuk.
class ArticleSchema(BaseModel):
    """
    PubMed'den çekilen bir makalenin yapılandırılmış halini temsil eder.
    """
    pmid: str = Field(..., description="Makalenin benzersiz PubMed ID'si")
    title: str = Field(..., description="Makalenin başlığı")
    abstract: Optional[str] = Field(None, description="Makalenin özeti")
    publication_date: str = Field(..., description="Yayınlanma tarihi")
    journal: str = Field(..., description="Yayınlandığı derginin adı")
    url: str = Field(..., description="Makalenin PubMed'deki URL'i")

# --- YENİ EKLENEN SCHEMALAR ---

class AnalysisResultSchema(BaseModel):
    """
    NLP servisinden dönen analiz sonuçlarının yapısını tanımlar.
    Örn: {"Yan Etkiler": ["...cümle 1...", "...cümle 2..."]}
    """
    results: Dict[str, List[str]] = Field(..., description="Kategori bazlı bulunan cümleler")

class AnalyzedArticleSchema(ArticleSchema):
    """
    Makale verilerini ve o makaleye ait analiz sonucunu bir arada tutar.
    ArticleSchema'dan kalıtım alarak tüm alanlarını miras alır.
    """
    analysis: AnalysisResultSchema = Field(..., description="Makale özeti için NLP analizi sonucu")

# API'mizin en dış katmanda döndüreceği yanıtın şeması
# Bu, analiz edilmiş makalelerin bir listesi olacak.
class SearchResponseSchema(BaseModel):
    data: List[AnalyzedArticleSchema]