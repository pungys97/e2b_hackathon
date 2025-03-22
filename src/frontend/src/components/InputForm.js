import React, { useState } from 'react';
import './InputForm.css';

function InputForm({ onSubmit, isLoading }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Basic URL validation
    if (!url) {
      setError('Please enter a URL');
      return;
    }
    
    try {
      new URL(url); // Check if URL is valid
      setError('');
      onSubmit(url);
    } catch (err) {
      setError('Please enter a valid URL (e.g., https://example.com)');
    }
  };

  return (
    <div className="input-form-container">
      <form className="input-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="website-url">Website URL</label>
          <input
            type="text"
            id="website-url"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
            className={error ? 'input-error' : ''}
          />
          {error && <p className="error-message">{error}</p>}
        </div>
        
        <button type="submit" className="submit-button" disabled={isLoading}>
          {isLoading ? 'Generating...' : 'Generate React App'}
        </button>
      </form>
      
      <div className="form-info">
        <h3>How it works</h3>
        <ul>
          <li>Enter a website URL to analyze</li>
          <li>Our AI extracts key content and features</li>
          <li>E2B Sandboxes generate and test a React app</li>
          <li>Download the generated app code</li>
        </ul>
      </div>
    </div>
  );
}

export default InputForm;