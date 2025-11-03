"""
BookGen LLM Service - FastAPI Application
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

from .ml.service import LLMServiceManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="BookGen LLM Service",
    description="Custom LLM service for generating domain-specific books",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
llm_service = None

# Request/Response models
class TrainingImportRequest(BaseModel):
    file_path: str
    domain: str
    niche: Optional[str] = None
    content_type: str = "manual"

class TrainingDirectoryRequest(BaseModel):
    directory_path: str
    domain: str
    niche: Optional[str] = None

class BookGenerationRequest(BaseModel):
    domain: str
    niche: str
    purpose: str
    target_length: int = 5000
    output_format: str = 'pdf'

class StatusResponse(BaseModel):
    initialized: bool
    model_exists: bool
    mongodb_connected: bool
    training_examples: int
    available_domains: List[str]
    model_size: int
    last_training: Optional[str]

# Background tasks
training_status = {"status": "idle", "progress": 0, "message": ""}
generation_status = {"status": "idle", "progress": 0, "message": ""}

@app.on_event("startup")
async def startup_event():
    """Initialize LLM service on startup"""
    global llm_service
    try:
        service_manager = LLMServiceManager()
        llm_service = await service_manager.__aenter__()
        logger.info("LLM Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global llm_service
    if llm_service:
        await llm_service.cleanup()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BookGen LLM Service is running",
        "version": "1.0.0",
        "service": "ready" if llm_service else "initializing"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return {"status": "healthy", "service": "running"}

@app.get("/status", response_model=Dict[str, Any])
async def get_status():
    """Get current model and service status"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        status = await llm_service.get_model_status()
        return status
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/training/import")
async def import_training_data(
    file_path: str,
    domain: str, 
    niche: str = None,
    content_type: str = "manual"
):
    """Import manually collected training data"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = await llm_service.import_training_data(file_path, domain, niche, content_type)
        
        if success:
            return {
                "message": "Training data imported successfully",
                "file_path": file_path,
                "domain": domain,
                "niche": niche
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to import training data")
    
    except Exception as e:
        logger.error(f"Error importing training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/training/import-directory")
async def import_training_directory(
    directory_path: str,
    domain: str,
    niche: str = None
):
    """Import all training data files from a directory"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = await llm_service.import_training_directory(directory_path, domain, niche)
        
        if success:
            return {
                "message": "Training data directory imported successfully",
                "directory_path": directory_path,
                "domain": domain,
                "niche": niche
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to import training directory")
    
    except Exception as e:
        logger.error(f"Error importing training directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/training/prepare")
async def prepare_training_data(domain: str, niche: str = None):
    """Prepare training data from MongoDB for model training"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = await llm_service.prepare_training_data(domain, niche)
        
        if success:
            return {"message": "Training data prepared successfully", "domain": domain, "niche": niche}
        else:
            raise HTTPException(status_code=500, detail="Failed to prepare training data")
    
    except Exception as e:
        logger.error(f"Error preparing training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/training/train")
async def train_model(domain: str, niche: str = None, background_tasks: BackgroundTasks = None):
    """Train the model with prepared data from MongoDB"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Start background training task
    if background_tasks:
        background_tasks.add_task(_train_model_task, domain, niche)
    
    return {
        "message": "Model training started",
        "domain": domain,
        "niche": niche,
        "task_id": "train_model"
    }

async def _train_model_task(domain: str, niche: str = None):
    """Background task for model training"""
    global training_status
    
    try:
        training_status["status"] = "training"
        training_status["progress"] = 0
        training_status["message"] = f"Starting model training for {domain}/{niche}"
        
        success = await llm_service.train_model(domain, niche)
        
        if success:
            training_status["status"] = "completed"
            training_status["progress"] = 100
            training_status["message"] = "Model training completed successfully"
        else:
            training_status["status"] = "failed"
            training_status["message"] = "Model training failed"
        
    except Exception as e:
        training_status["status"] = "failed"
        training_status["message"] = f"Training error: {str(e)}"
        logger.error(f"Model training task failed: {e}")

@app.get("/training/status")
async def get_training_status():
    """Get training task status"""
    return training_status

@app.post("/generate/book")
async def generate_book(request: BookGenerationRequest, background_tasks: BackgroundTasks):
    """Generate a book"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Start background generation task
    task_id = f"generate_{request.domain}_{request.niche}_{request.purpose}".replace(' ', '_').lower()
    
    background_tasks.add_task(
        _generate_book_task,
        request.domain,
        request.niche,
        request.purpose,
        request.target_length,
        request.output_format,
        task_id
    )
    
    return {
        "message": "Book generation started",
        "domain": request.domain,
        "niche": request.niche,
        "purpose": request.purpose,
        "task_id": task_id
    }

async def _generate_book_task(domain: str, niche: str, purpose: str, 
                            target_length: int, output_format: str, task_id: str):
    """Background task for book generation"""
    global generation_status
    
    try:
        generation_status["status"] = "generating"
        generation_status["progress"] = 0
        generation_status["message"] = f"Generating book for {domain}/{niche}"
        
        output_path = await llm_service.generate_book(
            domain, niche, purpose, target_length, output_format
        )
        
        if output_path:
            generation_status["status"] = "completed"
            generation_status["progress"] = 100
            generation_status["message"] = f"Book generated successfully: {output_path}"
            generation_status["output_path"] = output_path
        else:
            generation_status["status"] = "failed"
            generation_status["message"] = "Book generation failed"
        
    except Exception as e:
        generation_status["status"] = "failed"
        generation_status["message"] = f"Generation error: {str(e)}"
        logger.error(f"Book generation task failed: {e}")

@app.get("/generate/status")
async def get_generation_status():
    """Get book generation status"""
    return generation_status

@app.get("/generate/download/{filename}")
async def download_book(filename: str):
    """Download generated book"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    file_path = Path(llm_service.output_dir) / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/data/domains")
async def list_available_domains():
    """List available training domains from MongoDB"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        domains = await llm_service.list_training_domains()
        return {"available_domains": domains}
    except Exception as e:
        logger.error(f"Error listing domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/data/clear")
async def clear_training_data(domain: str = None, niche: str = None):
    """Clear training data from MongoDB"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = await llm_service.clear_training_data(domain, niche)
        
        if success:
            message = f"Training data cleared successfully"
            if domain:
                message += f" for domain: {domain}"
            if niche:
                message += f" and niche: {niche}"
            return {"message": message}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear training data")
    
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/model/reset")
async def reset_model():
    """Reset/reinitialize the model"""
    if not llm_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Reinitialize model
        success = await llm_service.initialize_model()
        
        if success:
            return {"message": "Model reset successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset model")
    
    except Exception as e:
        logger.error(f"Error resetting model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility endpoints
@app.get("/docs-redirect")
async def docs_redirect():
    """Redirect to API documentation"""
    return {"message": "Visit /docs for API documentation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
