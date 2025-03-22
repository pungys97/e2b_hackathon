import React from 'react';
import './App.css';
import InputForm from './components/InputForm';

function App() {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const handleGenerateApp = async (url) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/generate-app', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate app');
      }
      
      const data = await response.json();
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
        <h1>E2B GPT Engineer</h1>
        <p>Generate React apps from websites using AI</p>
      </header>
      
      <main className="app-main">
        <InputForm onSubmit={handleGenerateApp} isLoading={loading} />
        
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Analyzing website and generating app...</p>
            <p className="loading-note">This may take a minute or two</p>
          </div>
        )}
        
        {error && (
          <div className="error-container">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}
        
        {/*{results && !loading && <ResultsView results={results} />}*/}
      </main>
      
      <footer className="app-footer">
        <p>Created with E2B Sandboxes</p>
      </footer>
    </div>
  );
}

export default App;