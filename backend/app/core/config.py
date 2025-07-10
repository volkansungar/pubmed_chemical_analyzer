# backend/app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Uygulama genelindeki konfigürasyonları yönetir.
    Ortam değişkenlerinden değerleri otomatik olarak okur.
    """
    NCBI_API_BASE_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    # Gelecekte buraya eklenebilir:
    # NCBI_API_KEY: str | None = None
    # DATABASE_URL: str = "sqlite:///./test.db"

# Kullanmak için bir settings nesnesi oluşturuyoruz.
settings = Settings()
