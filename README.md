# E2B GPT Engineer

A tool that generates React applications from websites using AI with E2B sandboxes.

## Project Structure

- `src/backend/`: FastAPI backend service
  - `main.py`: Main FastAPI application
  - `scraper.py`: Website content extraction functionality
- `src/frontend/`: React frontend
  - React components and application logic

## Setup

### Backend

1. Install dependencies:
```bash
pip install -e .
```

2. Run the backend:
```bash
cd src/backend
python main.py
```

The backend will be available at http://localhost:8000.

### Frontend

1. Install dependencies:
```bash
cd src/frontend
npm install
```

2. Start the React development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000.

## Usage

1. Enter a website URL in the input field
2. Click "Generate React App"
3. The application will analyze the website and generate a React app based on its content

## Technologies

- Backend: FastAPI, BeautifulSoup4, Python
- Frontend: React
- AI Integration: OpenAI
- Sandboxes: E2B