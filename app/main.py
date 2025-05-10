import os
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import logging

# Make sure the current directory is in the Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import application modules
from app.api.routes import router as api_router
from app.db.database import engine, Base

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables if they don't exist
# This is just a safety measure; normally, the setup_db.py script should be run
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create database tables automatically: {e}")
    print("Please run the setup_db.py script to initialize the database.")

# Initialize FastAPI app
app = FastAPI(
    title="Document Processor", 
    description="API for processing PDF documents and matching line items to products",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(api_router, prefix="/api")

# Upload directory path
UPLOAD_DIR = os.path.join("app", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Root endpoint that renders the main application page with document upload and listing
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Document Manager"}
    )

@app.get("/document_view/{document_id}", response_class=HTMLResponse)
async def document_view(request: Request, document_id: int):
    """
    Endpoint that renders the document viewing and processing page
    """
    return templates.TemplateResponse(
        "document_view.html", {"request": request, "title": "Document View", "document_id": document_id}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    ) 