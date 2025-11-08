"""
SimpleAgent - Main FastAPI Application
Handles HTTP requests, file uploads, and query processing
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import zipfile
import shutil
from typing import Optional

from app.agent.agent import SimpleAgent
from app.utils.file_processor import FileProcessor
from app.utils.output_manager import OutputManager
from app.config import settings

app = FastAPI(title="SimpleAgent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path("app/static")
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Create output directory
output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main UI"""
    html_file = Path("app/static/index.html")
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>SimpleAgent</h1><p>Please create the frontend files.</p>")


@app.post("/api/query")
async def process_query(
    query: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Process user query and generate output (codebase or text file)
    """
    try:
        # Initialize agent
        agent = SimpleAgent()
        
        # Process uploaded file if provided
        file_content = None
        if file and file.filename:
            file_processor = FileProcessor()
            file_content = await file_processor.process_uploaded_file(file)
        
        # Combine query with file content if available
        full_query = query
        if file_content:
            full_query = f"{query}\n\nAdditional context from uploaded file:\n{file_content}"
        
        # Process query with agent
        result = await agent.process_query(full_query)
        
        # Generate output
        output_manager = OutputManager()
        output_path = await output_manager.generate_output(result, query)
        
        return JSONResponse({
            "success": True,
            "message": "Query processed successfully",
            "output_type": result["type"],
            "output_path": str(output_path),
            "download_url": f"/api/download/{output_path.name}"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/api/download/{filename}")
async def download_output(filename: str):
    """Download generated output file"""
    output_path = output_dir / filename
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if filename.endswith(".zip"):
        return FileResponse(
            path=str(output_path),
            filename=filename,
            media_type="application/zip"
        )
    else:
        return FileResponse(
            path=str(output_path),
            filename=filename,
            media_type="text/plain"
        )


@app.get("/api/query-templates")
async def get_query_templates():
    """Get predefined query templates for users"""
    templates = [
        {
            "name": "Web Application",
            "query": "Create a simple web application with a todo list feature using HTML, CSS, and JavaScript"
        },
        {
            "name": "Data Analysis",
            "query": "Create a Python script to analyze a CSV file and generate visualizations"
        },
        {
            "name": "API Service",
            "query": "Create a REST API service with FastAPI that handles user authentication"
        },
        {
            "name": "CLI Tool",
            "query": "Create a command-line tool in Python to manage file operations"
        },
        {
            "name": "Database Application",
            "query": "Create a database application with CRUD operations using SQLite and Python"
        }
    ]
    return JSONResponse({"templates": templates})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)


