import React from 'react';
import './App.css';
import InputForm from './components/InputForm';

function App() {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [hostedAppUrl, setHostedAppUrl] = React.useState(null);

  const handleGenerateApp = async (url) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('Sending request with URL:', url);
      const response = await fetch('http://localhost:8000/generate-app', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        let errorMessage;
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || 'Failed to generate app';
        } catch (e) {
          errorMessage = 'Failed to generate app: ' + response.status;
        }
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      console.log('Success response:', data);
      setHostedAppUrl(data.url);
    } catch (err) {
      console.error('Error generating app:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>✨ 90's Website Beautifier</h1>
        <p>Transform your outdated website into a modern, sleek design with our AI-powered service</p>
      </header>
      
      <main className="app-main">
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <h3>Transforming Your Website</h3>
            <p>Our AI is analyzing your website's structure and content...</p>
            <p className="loading-note">This process may take a minute or two to complete</p>
          </div>
        )}

        {hostedAppUrl && (
          <div className="success-container">
            <h3>🎉 Success!</h3>
            <p>Your modernized website is ready at:</p>
            <a href={hostedAppUrl} target="_blank" rel="noopener noreferrer">{hostedAppUrl}</a>
          </div>
        )}

        <InputForm onSubmit={handleGenerateApp} isLoading={loading} />

        {error && (
          <div className="error-container">
            <h3>⚠️ Error Occurred</h3>
            <p>{error}</p>
          </div>
        )}
      </main>
      
      <footer className="app-footer">
        <p>Built with ❤️ using React, FastAPI and <a href="https://e2b.dev" target="_blank" rel="noopener noreferrer">E2B Sandboxes</a></p>
      </footer>
    </div>
  );
}

export default App;