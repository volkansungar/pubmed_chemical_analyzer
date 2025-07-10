import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [chemical, setChemical] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!chemical.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await axios.get('http://127.0.0.1:8000/api/v1/search', {
        params: { chemical: chemical, limit: 10 }
      });
      setResults(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Bilinmeyen bir hata oluştu.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="App">
      <h1>PubMed Kimyasal Etki Analizörü</h1>
      <div className="search-bar">
        <input
          type="text"
          value={chemical}
          onChange={(e) => setChemical(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Örn: aspirin, ibuprofen..."
          disabled={isLoading}
        />
        <button onClick={handleSearch} disabled={isLoading}>
          {isLoading ? 'Aranıyor...' : 'Ara'}
        </button>
      </div>

      {isLoading && <div className="status-message">Sonuçlar yükleniyor...</div>}
      {error && <div className="error-message">Hata: {error}</div>}

      {results.length > 0 && (
        <ul className="results-list">
          {results.map((item) => (
            <li key={item.pmid} className="article-card">
              <h3>{item.title}</h3>
              <p>
                <strong>Dergi:</strong> {item.journal} | <strong>Tarih:</strong> {item.publication_date}
              </p>
              <p>
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  Makaleye Git
                </a>
              </p>
              <div className="analysis-section">
                <h4>Analiz Sonuçları</h4>
                {Object.keys(item.analysis.results).length > 0 ? (
                  Object.entries(item.analysis.results).map(([category, sentences]) => (
                    <div key={category}>
                      <h5>{category}</h5>
                      <ul>
                        {sentences.map((sentence, index) => (
                          <li key={index}>{sentence}</li>
                        ))}
                      </ul>
                    </div>
                  ))
                ) : (
                  <p>Bu özette ilgili bir bulguya rastlanmadı.</p>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;