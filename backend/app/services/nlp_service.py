# backend/app/services/nlp_service.py

import re
from typing import Dict, List, Set

# --- YAKLAŞIM 2 İÇİN GEREKLİ KÜTÜPHANE ---
# Terminalde şu komutları çalıştırarak kurmanız gerekir:
# pip install spacy
# python -m spacy download en_core_web_sm
import spacy

# spaCy modelini bir kere yükleyip tekrar tekrar kullanmak performansı artırır.
# Modelin yüklenmesi birkaç saniye sürebilir.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy 'en_core_web_sm' modeli bulunamadı.")
    print("Lütfen 'python -m spacy download en_core_web_sm' komutunu çalıştırın.")
    nlp = None

# Analiz için kullanılacak anahtar kelime setleri
# Bu listeleri projenizin ihtiyacına göre genişletebilirsiniz.
KEYWORD_CATEGORIES = {
    "Yan Etkiler": [
        "side effect", "adverse reaction", "adverse event", "toxicity", "risk",
        "complication", "harm", "danger", "contraindication", "headache", "nausea"
    ],
    "Faydalar ve Etkinlik": [
        "effective", "efficacy", "benefit", "improvement", "treatment", "cure",
        "reduction", "prevention", "therapeutic", "positive effect", "relieve"
    ],
    "Nötr veya Bulgular": [
        "study", "investigate", "results", "finding", "observation", "conclusion",
        "effect", "impact", "association"
    ]
}


def analyze_text_simple(text: str) -> Dict[str, List[str]]:
    """
    Yaklaşım 1: Metindeki anahtar kelimeleri basitçe arar.

    Args:
        text (str): Analiz edilecek metin (makale özeti).

    Returns:
        Dict[str, List[str]]: Hangi kategoride hangi kelimelerin bulunduğunu gösteren bir sözlük.
    """
    if not text:
        return {}

    text_lower = text.lower()
    found_keywords = {}

    for category, keywords in KEYWORD_CATEGORIES.items():
        category_found = []
        for keyword in keywords:
            if keyword in text_lower:
                category_found.append(keyword)
        if category_found:
            found_keywords[category] = sorted(list(set(category_found)))

    return found_keywords


def analyze_text_with_spacy(text: str) -> Dict[str, List[str]]:
    """
    Yaklaşım 2: spaCy kullanarak metni cümlelere ayırır ve ilgili cümleleri bulur.

    Args:
        text (str): Analiz edilecek metin (makale özeti).

    Returns:
        Dict[str, List[str]]: Her kategori için anahtar kelime içeren cümlelerin listesi.
    """
    if not text or not nlp:
        return {}

    doc = nlp(text)
    found_sentences = {category: [] for category in KEYWORD_CATEGORIES}

    # Anahtar kelimeleri daha hızlı arama için bir sete dönüştürelim
    keywords_flat: Set[str] = {keyword for sublist in KEYWORD_CATEGORIES.values() for keyword in sublist}

    for sent in doc.sents:
        sent_lower = sent.text.lower()

        # Cümlede herhangi bir anahtar kelime var mı diye hızlıca kontrol et
        if any(keyword in sent_lower for keyword in keywords_flat):
            # Hangi kategoriye ait olduğunu bul
            for category, keywords in KEYWORD_CATEGORIES.items():
                if any(keyword in sent_lower for keyword in keywords):
                    found_sentences[category].append(sent.text.strip())
                    # Bir cümleyi birden fazla kategoriye eklememek için döngüden çık
                    break

                    # Boş kalan kategorileri sonuçtan temizle
    return {category: sentences for category, sentences in found_sentences.items() if sentences}
