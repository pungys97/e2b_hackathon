import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

from site_to_markdown import process_website_to_md
from src.react_engineer.engineer import ReactGPTEngineer

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

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
        prompt = process_website_to_md(str(request.url))
        # Initialize and run React GPT Engineer
        engineer = ReactGPTEngineer()

        built_site_url = engineer.run(prompt=prompt)
        return {"site_url": built_site_url}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Get server settings from environment
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    RELOAD = os.getenv("RELOAD", "True").lower() in ["true", "1", "yes"]
    
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)