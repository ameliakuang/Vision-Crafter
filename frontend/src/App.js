import { useState, useEffect } from 'react';
import './App.css';

// Helper function to find and highlight keywords in text
// This function now takes the prompt text, its specific extracted features,
// the currently selected keywords, and the handler for keyword selection.
const HighlightedPrompt = ({ prompt, features, selectedKeywords, onFeatureSelect }) => {
  if (!features) {
    // If no features for this prompt, just return the original text
    return <span>{prompt}</span>;
  }

  const parts = [];
  const featureCategories = Object.keys(features);

  // Collect all keyword occurrences with their category and index in the prompt
  const keywordOccurrences = [];
  featureCategories.forEach(category => {
    features[category].forEach(keyword => {
      if (keyword && keyword.length > 0) {
        // Find all occurrences of the keyword in the prompt
        // Using a simple indexOf loop. For more complex scenarios, regex might still be needed,
        // but this is more reliable for exact phrase matching.
        let index = prompt.toLowerCase().indexOf(keyword.toLowerCase());
        while (index !== -1) {
          keywordOccurrences.push({
            keyword: prompt.substring(index, index + keyword.length), // Use substring to get original casing
            category: category,
            startIndex: index,
            endIndex: index + keyword.length
          });
          index = prompt.toLowerCase().indexOf(keyword.toLowerCase(), index + 1);
        }
      }
    });
  });

  // Sort occurrences by start index
  keywordOccurrences.sort((a, b) => a.startIndex - b.startIndex);

  let lastIndex = 0;

  keywordOccurrences.forEach(occurrence => {
    // Add text before the current highlight
    if (occurrence.startIndex > lastIndex) {
      parts.push(<span key={`text-${lastIndex}-${occurrence.startIndex}`}>{prompt.substring(lastIndex, occurrence.startIndex)}</span>);
    }

    // Add the highlighted span
    const isSelected = selectedKeywords.includes(occurrence.keyword); // Check if the specific keyword string is selected
    const key = `${occurrence.category}-${occurrence.keyword}-${occurrence.startIndex}`; // Unique key

    parts.push(
      <span
        key={key}
        className={`highlight-${occurrence.category} ${isSelected ? 'selected-feature' : ''}`}
        onClick={(e) => {
          e.stopPropagation();
          onFeatureSelect(occurrence.keyword); // Pass the exact keyword string
        }}
        title={`Category: ${occurrence.category}\nClick to select/deselect`}
      >
        {occurrence.keyword}
      </span>
    );

    lastIndex = occurrence.endIndex;
  });

  // Add any remaining text after the last highlight
  if (lastIndex < prompt.length) {
    parts.push(<span key={`text-${lastIndex}-${prompt.length}`}>{prompt.substring(lastIndex)}</span>);
  }

  // If no keywords found or processed, return the original prompt
  if (parts.length === 0 && prompt) {
      return <span>{prompt}</span>;
  }

  return <span>{parts}</span>;
};

// Helper function to escape regex special characters - No longer strictly needed with indexOf approach but keeping for now
// function escapeRegExp(string) {
//   return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
// }

function App() {
  const [description, setDescription] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedImages, setSelectedImages] = useState([]);
  const [extractedFeatures, setExtractedFeatures] = useState({});
  const [selectedKeywords, setSelectedKeywords] = useState([]);

  const generateImages = async () => {
    try {
      setLoading(true);
      setError(null);
      // Optional: Clear previous results, selected states if you want a clean slate on new generation
      // setResults([]);
      // setSelectedImages([]);
      // setExtractedFeatures({});
      // setSelectedKeywords([]);


      // Prepare the feedback object
      const feedback = {
          // Send the prompts of selected images as liked_prompts
          liked_prompts: selectedImages,
          // Send the selected keywords as liked_style_keywords
          liked_style_keywords: selectedKeywords
      };

      // Determine if it's the very first generation ever (no description, no selected images, no selected keywords)
      // This check is primarily for frontend UX to prevent empty initial requests.
      const isInitialAttempt = !description && selectedImages.length === 0 && selectedKeywords.length === 0;

      if (isInitialAttempt) {
           setError("Please enter a description to start generating images.");
           setLoading(false);
           return;
      }

      // Request body always includes description and feedback
      const requestBody = {
          description: description,
          feedback: feedback
      };

      console.log("Sending request body:", requestBody);

      const response = await fetch('http://localhost:8000/api/generate-images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Failed to generate images' }));
        throw new Error(errorData.error || `Failed to generate images: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Data received from generate-images: ', data);

      // Backend now returns prompts, extracted_features, and results
      if (data.results && data.prompts && data.extracted_features) {
        // Update state with new results and prompts
        setResults(data.results); // results should contain {prompt, url}

        // Map extracted features to prompts for easy lookup by prompt string
        const featuresByPrompt = {};
         // Assuming data.prompts and data.extracted_features are aligned by index
         // data.extracted_features is { "0": {features}, "1": {features}, ... }
         // We need to map this to { prompt_string: {features} }
         data.prompts.forEach((prompt, index) => {
             // Ensure the index exists in extracted_features (robustness)
             if (data.extracted_features.hasOwnProperty(index.toString())) {
                 featuresByPrompt[prompt] = data.extracted_features[index.toString()];
             } else {
                 featuresByPrompt[prompt] = {}; // No features found for this prompt
                 console.warn(`No extracted features found for prompt index ${index}`);
             }
         });
        setExtractedFeatures(featuresByPrompt);

        // Clear selections after successful generation, as feedback has been processed for this round
        setSelectedImages([]);
        setSelectedKeywords([]);

      } else {
        // Handle cases where backend response format is unexpected
        throw new Error('Invalid response format: Missing results, prompts, or extracted_features in backend response.');
      }
    } catch (err) {
      console.error('Error details:', err);
      // Display a user-friendly error message
      setError(`Error generating images: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handler for selecting/deselecting images for regeneration
  const handleImageSelect = (prompt) => {
    // If the prompt is already selected, remove it. Otherwise, add it.
    if (selectedImages.includes(prompt)) {
      setSelectedImages(selectedImages.filter(p => p !== prompt));
    } else {
      setSelectedImages([...selectedImages, prompt]);
    }
     // Optional: You might want to clear selected keywords when images are selected for regeneration, or vice versa, depending on desired UX.
     // For now, we keep them independent as requested.
  };

  // Handler for selecting/deselecting keywords for feedback
    const handleFeatureSelect = (keyword) => {
        // If the keyword is already selected, remove it. Otherwise, add it.
        if (selectedKeywords.includes(keyword)) {
            setSelectedKeywords(selectedKeywords.filter(k => k !== keyword));
        } else {
            setSelectedKeywords([...selectedKeywords, keyword]);
        }
        // Optional: Clear selected images here if keyword selection should override image selection. Keeping independent for now.
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
            placeholder={(selectedImages.length > 0 || selectedKeywords.length > 0) ? "Optionally add more details or refine your description for regeneration..." : "Describe the image you want to generate..."}
            rows={4}
            className="description-input"
          />
          
          <button 
            onClick={generateImages} 
            disabled={loading || (!description && selectedImages.length === 0 && selectedKeywords.length === 0)}
            className="generate-button"
          >
            {loading ? 'Generating...' : (selectedImages.length > 0 || selectedKeywords.length > 0) ? 'Regenerate' : 'Generate Images'}
          </button>
        </div>

        {/* Display Selected Keywords */}
        {selectedKeywords.length > 0 && (
            <div className="selected-features-display">
                Selected Keywords: {selectedKeywords.join(', ')}
            </div>
        )}

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
                className={`gallery-item ${selectedImages.includes(item.prompt) ? 'selected' : ''}`}
              >
                <div className="image-container" onClick={() => handleImageSelect(item.prompt)}>
                  <img 
                    src={item.url}
                    alt={`Generated image ${index + 1}`}
                    onError={(e) => {
                      console.error('Image failed to load:', `Index ${index}`, item.prompt, e);
                      // Optionally set a fallback image or remove the item
                      e.target.onerror = null; // Prevent infinite loops
                      e.target.src="/fallback-image.png"; // Provide a path to a local fallback image if you have one
                       // Or hide the image container/item:
                       // e.target.parentElement.style.display = 'none';
                    }}
                  />
                  {selectedImages.includes(item.prompt) && (
                    <div className="selected-indicator">✓</div>
                  )}
                </div>
                <div className="prompt-text">
                  <HighlightedPrompt
                      prompt={item.prompt}
                      features={extractedFeatures[item.prompt]}
                      selectedKeywords={selectedKeywords}
                      onFeatureSelect={handleFeatureSelect}
                  />
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