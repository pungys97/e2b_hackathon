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
          <label htmlFor="website-url">Enter Your Website URL</label>
          <input
            type="text"
            id="website-url"
            placeholder="https://your-old-website.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
            className={error ? 'input-error' : ''}
            autoFocus
          />
          {error && <p className="error-message">{error}</p>}
        </div>
        
        <button type="submit" className="submit-button" disabled={isLoading}>
          {isLoading ? 'Transforming Website...' : 'Transform My Website'}
        </button>
      </form>
      
      <div className="form-info">
        <h3>How It Works</h3>
        <ul>
          <li>Enter any outdated website URL to begin the transformation</li>
          <li>Our AI analyzes the design, content, and structure</li>
          <li>We generate a modern React application using OpenAI and E2B Sandboxes</li>
          <li>Receive a beautifully redesigned version of your website</li>
          <li>Download the complete source code for your new site</li>
        </ul>
      </div>
    </div>
  );
}

export default InputForm;