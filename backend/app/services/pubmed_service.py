# backend/app/services/pubmed_service.py

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

from app.core.config import settings
from app.api.v1.schemas import ArticleSchema


def search_and_fetch_articles(chemical_name: str, max_results: int = 20) -> List[ArticleSchema]:
    """
    Belirtilen bir kimyasal için PubMed'de insan çalışmaları arar ve makale detaylarını getirir.

    Args:
        chemical_name (str): Aranacak kimyasalın adı (örn: "Aspirin").
        max_results (int): Getirilecek maksimum makale sayısı.

    Returns:
        List[ArticleSchema]: Bulunan makalelerin yapılandırılmış listesi.
    """
    print(f"'{chemical_name}' için PubMed'de arama başlatılıyor...")

    # 1. Adım: ESearch ile ilgili makalelerin PMID'lerini bulma
    # MeSH terimleri kullanarak daha isabetli sonuçlar elde etmeye çalışıyoruz.
    search_term = f'("{chemical_name}"[MeSH Terms] OR "{chemical_name}"[All Fields]) AND "humans"[MeSH Terms]'
    esearch_url = f"{settings.NCBI_API_BASE_URL}/esearch.fcgi"
    esearch_params = {
        "db": "pubmed",
        "term": search_term,
        "retmax": max_results,
        "retmode": "json"
    }

    try:
        search_response = requests.get(esearch_url, params=esearch_params)
        search_response.raise_for_status()  # HTTP hatası varsa exception fırlat
        search_data = search_response.json()
        pmids = search_data.get("esearchresult", {}).get("idlist", [])

        if not pmids:
            print("İlgili makale bulunamadı.")
            return []

        print(f"{len(pmids)} adet makale ID'si bulundu. Detaylar çekiliyor...")

    except requests.exceptions.RequestException as e:
        print(f"ESearch API hatası: {e}")
        return []

    # 2. Adım: EFetch ile PMID'leri kullanarak makale detaylarını çekme
    efetch_url = f"{settings.NCBI_API_BASE_URL}/efetch.fcgi"
    efetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml"
    }

    try:
        fetch_response = requests.get(efetch_url, params=efetch_params)
        fetch_response.raise_for_status()

        # 3. Adım: Gelen XML verisini ayrıştırma (parse) ve yapılandırma
        return _parse_pubmed_xml(fetch_response.text)

    except requests.exceptions.RequestException as e:
        print(f"EFetch API hatası: {e}")
        return []
    except ET.ParseError as e:
        print(f"XML parse hatası: {e}")
        return []


def _parse_pubmed_xml(xml_data: str) -> List[ArticleSchema]:
    """
    EFetch'ten gelen XML metnini ayrıştırır ve ArticleSchema listesine dönüştürür.
    Bu bir yardımcı (helper) fonksiyondur.
    """
    articles = []
    root = ET.fromstring(xml_data)

    for article_node in root.findall('.//PubmedArticle'):
        # Gerekli bilgileri XML ağacından dikkatlice çıkarıyoruz.
        # Bazı alanlar eksik olabileceğinden .find() ve .text kontrolü yapıyoruz.

        pmid_node = article_node.find('.//PMID')
        pmid = pmid_node.text if pmid_node is not None else ''

        title_node = article_node.find('.//ArticleTitle')
        title = title_node.text if title_node is not None else 'Başlık bulunamadı'

        abstract_node = article_node.find('.//AbstractText')
        abstract = abstract_node.text if abstract_node is not None else None

        journal_node = article_node.find('.//Journal/Title')
        journal = journal_node.text if journal_node is not None else 'Dergi bilgisi yok'

        # Tarih bilgisini birden fazla alandan aramamız gerekebilir
        pub_date_node = article_node.find('.//PubDate')
        year = pub_date_node.findtext('Year', 'N/A')
        month = pub_date_node.findtext('Month', 'N/A')
        day = pub_date_node.findtext('Day', 'N/A')
        publication_date = f"{year}-{month}-{day}"

        if not pmid:
            continue  # PMID yoksa bu kaydı atla

        article_data = {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "publication_date": publication_date,
            "journal": journal,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        }

        articles.append(ArticleSchema(**article_data))

    print(f"Başarıyla {len(articles)} adet makale işlendi.")
    return articles
