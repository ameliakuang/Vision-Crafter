import { useState } from 'react';
import './App.css';

function App() {
  const [description, setDescription] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateImages = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/generate-images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate images');
      }

      const data = await response.json();
      console.log('Data received from generate-images: ', data);
      if (data.results) {
        setResults(data.results);
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      console.error('Error details:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Vision Crafter</h1>
        <p className="subtitle">Transform your ideas into visual masterpieces</p>
      </header>
      
      <main className="App-main">
        <div className="input-section">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the image you want to generate..."
            rows={4}
            className="description-input"
          />
          
          <button 
            onClick={generateImages} 
            disabled={loading || !description}
            className="generate-button"
          >
            {loading ? 'Generating...' : 'Generate Images'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Creating your masterpieces... This may take a few moments.</p>
          </div>
        )}

        {results.length > 0 && (
          <div className="gallery">
            {results.map((item, index) => (
              <div key={index} className="gallery-item">
                <div className="image-container">
                  <img 
                    src={item.url}
                    alt={`Generated image ${index + 1}`}
                    onError={(e) => {
                      console.error('Image failed to load:', e);
                    }}
                  />
                </div>
                <div className="prompt-text">
                  <p>{item.prompt}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;