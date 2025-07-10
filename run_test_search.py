# Bu dosyayı backend klasörünün dışında, ana dizinde oluşturun
# ve terminalde `python run_test_search.py` komutuyla çalıştırın.

import sys
import os

# Backend modüllerine erişim için sys.path'e ekleme yapıyoruz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Servislerimizi import ediyoruz
from app.services.pubmed_service import search_and_fetch_articles
from app.services.nlp_service import analyze_text_with_spacy  # Tercih edilen, daha gelişmiş yöntem

if __name__ == "__main__":
    # Test edilecek kimyasal
    chemical_to_search = "paracetamol toxicity"  # Daha spesifik bir arama yapalım

    # 1. Adım: Veri Toplama
    # PubMed'den ilgili makaleleri çek
    found_articles = search_and_fetch_articles(chemical_to_search, max_results=10)

    if not found_articles:
        print("Arama bir sonuç döndürmedi.")
    else:
        print(f"\n--- '{chemical_to_search}' için bulunan ve işlenen sonuçlar ---")

        # 2. Adım: Veri İşleme
        # Bulunan her makale için NLP analizi yap
        for i, article in enumerate(found_articles, 1):
            print(f"\n Makale {i}: {article.title}")
            print(f"   Dergi: {article.journal} | URL: {article.url}")

            if article.abstract:
                # Özet metnini NLP servisimize göndererek analiz et
                analysis_results = analyze_text_with_spacy(article.abstract)

                print("   --- Analiz Sonuçları ---")
                if not analysis_results:
                    print("     -> Bu özette tanımlı anahtar kelimeleri içeren bir cümle bulunamadı.")
                else:
                    for category, sentences in analysis_results.items():
                        print(f"     -> Kategori: {category}")
                        for sentence in sentences:
                            print(f"        - \"{sentence}\"")
            else:
                print("   -> Bu makale için özet metni mevcut değil, analiz yapılamadı.")