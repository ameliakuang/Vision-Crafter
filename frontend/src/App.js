import { useState } from 'react';
import './App.css';

function App() {
  const [description, setDescription] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPrompts, setSelectedPrompts] = useState([]);

  const generateImages = async () => {
    try {
      setLoading(true);
      setError(null);
      setResults([]);
      
      const requestBody = selectedPrompts.length > 0
        ? { selected_prompts: selectedPrompts, description: description }
        : { description: description };

      if (selectedPrompts.length === 0 && (!description || !description.trim())) {
        setError("Please enter a description or select images to regenerate.");
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/generate-images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Failed to generate images' }));
        throw new Error(errorData.error || 'Failed to generate images');
      }

      const data = await response.json();
      console.log('Data received from generate-images: ', data);
      if (data.results) {
        setResults(data.results);
        setSelectedPrompts([]);
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

  const handleImageSelect = (prompt) => {
    if (selectedPrompts.includes(prompt)) {
      setSelectedPrompts(selectedPrompts.filter(p => p !== prompt));
    } else {
      setSelectedPrompts([...selectedPrompts, prompt]);
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
            placeholder={selectedPrompts.length > 0 ? "Optionally add more details for regeneration..." : "Describe the image you want to generate..."}
            rows={4}
            className="description-input"
          />
          
          <button 
            onClick={generateImages} 
            disabled={loading || (selectedPrompts.length === 0 && !description)}
            className="generate-button"
          >
            {loading ? 'Generating...' : selectedPrompts.length > 0 ? 'Regenerate Selected Images' : 'Generate Images'}
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
              <div 
                key={index} 
                className={`gallery-item ${selectedPrompts.includes(item.prompt) ? 'selected' : ''}`}
                onClick={() => handleImageSelect(item.prompt)}
              >
                <div className="image-container">
                  <img 
                    src={item.url}
                    alt={`Generated image ${index + 1}`}
                    onError={(e) => {
                      console.error('Image failed to load:', e);
                    }}
                  />
                  {selectedPrompts.includes(item.prompt) && (
                    <div className="selected-indicator">✓</div>
                  )}
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