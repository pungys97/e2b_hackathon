from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Get settings from environment
API_TITLE = os.getenv("API_TITLE", "E2B GPT Engineer")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI(title=API_TITLE)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WebsiteRequest(BaseModel):
    url: HttpUrl

@app.post("/generate-app")
async def create_app(request: WebsiteRequest):
    try:
        print(request)
        # Placeholder for actual implementation
        return {"status": "success", "message": "App generated successfully", "files": [
            {"filename": "index.html", "content": "<!DOCTYPE html><html><body><h1>Generated App</h1></body></html>"},
            {"filename": "App.js", "content": "function App() { return <div>Generated App</div>; }"}
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Get server settings from environment
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    RELOAD = os.getenv("RELOAD", "True").lower() in ["true", "1", "yes"]
    
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)