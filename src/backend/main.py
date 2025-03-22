from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="E2B GPT Engineer")

class WebsiteRequest(BaseModel):
    url: HttpUrl

@app.post("/generate-app")
async def create_app(request: WebsiteRequest):
    try:
        # Placeholder for actual implementation
        return {"status": "success", "message": "App generated successfully", "files": [
            {"filename": "index.html", "content": "<!DOCTYPE html><html><body><h1>Generated App</h1></body></html>"},
            {"filename": "App.js", "content": "function App() { return <div>Generated App</div>; }"}
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)