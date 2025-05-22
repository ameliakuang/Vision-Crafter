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
      
      // 创建多个并行请求
      const numRequests = 3; // 同时发送3个请求
      const requests = Array(numRequests).fill().map(() => 
        fetch('http://localhost:8000/api/generate-images', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ description }),
        })
      );

      // 并行执行所有请求
      const responses = await Promise.all(requests);
      
      // 检查所有响应是否成功
      const failedResponse = responses.find(response => !response.ok);
      if (failedResponse) {
        throw new Error('Failed to generate images');
      }

      // 并行处理所有响应数据
      const dataPromises = responses.map(response => response.json());
      const allData = await Promise.all(dataPromises);
      
      // 合并所有结果
      const combinedResults = allData.reduce((acc, data) => {
        if (data.results) {
          return [...acc, ...data.results];
        }
        return acc;
      }, []);

      console.log('All data received:', combinedResults);
      setResults(combinedResults);
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