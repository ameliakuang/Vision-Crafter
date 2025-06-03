import { useState, useEffect } from 'react';
import './App.css';

// Helper function to find and highlight keywords in text
// This function now takes the prompt text, its specific extracted features,
// the currently selected keywords, and the handler for keyword selection.
const HighlightedPrompt = ({ prompt, features, selectedKeywords, onFeatureSelect }) => {
  if (!features) {
    console.log(`No features found for prompt: ${prompt}`);
    return <span>{prompt}</span>;
  }

  console.log(`Processing prompt: "${prompt}"`);
  console.log('Features for this prompt:', features);

  const parts = [];
  const featureCategories = Object.keys(features);

  // Collect all keyword occurrences with their category and index in the prompt
  const keywordOccurrences = [];
  featureCategories.forEach(category => {
    if (!Array.isArray(features[category])) {
      console.warn(`Features for category ${category} is not an array:`, features[category]);
      return;
    }
    
    features[category].forEach(keyword => {
      if (keyword && keyword.length > 0) {
        // Find all occurrences of the keyword in the prompt, case-insensitive
        const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
        let match;
        while ((match = regex.exec(prompt)) !== null) {
          console.log(`Found match for "${keyword}" in category "${category}" at index ${match.index}`);
          keywordOccurrences.push({
            keyword: prompt.substring(match.index, match.index + keyword.length), // Use substring to get original casing
            category: category,
            startIndex: match.index,
            endIndex: match.index + keyword.length
          });
        }
      }
    });
  });

  // Sort occurrences by start index
  keywordOccurrences.sort((a, b) => a.startIndex - b.startIndex);
  console.log('Sorted keyword occurrences:', keywordOccurrences);

  let lastIndex = 0;

  keywordOccurrences.forEach(occurrence => {
    // Add text before the current highlight
    if (occurrence.startIndex > lastIndex) {
      parts.push(<span key={`text-${lastIndex}-${occurrence.startIndex}`}>{prompt.substring(lastIndex, occurrence.startIndex)}</span>);
    }

    // Add the highlighted span
    const isSelected = selectedKeywords.includes(occurrence.keyword);
    const key = `${occurrence.category}-${occurrence.keyword}-${occurrence.startIndex}`;

    parts.push(
      <span
        key={key}
        className={`highlight-${occurrence.category} ${isSelected ? 'selected-feature' : ''}`}
        onClick={(e) => {
          e.stopPropagation();
          onFeatureSelect(occurrence.keyword);
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
    console.log('No keywords found in prompt, returning original text');
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

      // Backend now returns prompts with their features combined
      if (data.results && data.prompts) {
        console.log('Received data from backend:', data);
        
        // Update state with new results and prompts
        setResults(data.results); // results should contain {prompt, url}

        // Map extracted features to prompts for easy lookup by prompt string
        const featuresByPrompt = {};
        
        // Map features from the combined prompts structure
        data.prompts.forEach((promptObj) => {
          console.log(`Mapping features for prompt: "${promptObj.text}"`);
          console.log('Features object:', promptObj.features);
          // Store features using the prompt text as the key
          featuresByPrompt[promptObj.text] = promptObj.features || {};
        });

        console.log('Final mapped features by prompt:', featuresByPrompt);
        setExtractedFeatures(featuresByPrompt);

        // Clear selections after successful generation, as feedback has been processed for this round
        setSelectedImages([]);
        setSelectedKeywords([]);

      } else {
        // Handle cases where backend response format is unexpected
        console.error('Invalid response format:', {
          hasResults: !!data.results,
          hasPrompts: !!data.prompts,
          data: data
        });
        throw new Error('Invalid response format: Missing results or prompts in backend response.');
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
            {results.map((item, index) => {
              console.log(`Rendering result ${index}:`, item);
              console.log('Looking up features for prompt:', item.prompt);
              console.log('Available features:', extractedFeatures[item.prompt]);
              return (
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
                        e.target.onerror = null;
                        e.target.src="/fallback-image.png";
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
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;