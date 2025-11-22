"""
BookGen LLM Service - FastAPI Application with Custom Training
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import os
from dotenv import load_dotenv
import motor.motor_asyncio

from .ml.data_schema import (
    TrainingExampleRequest,
    TrainingJobRequest, 
    TextGenerationRequest,
    TextGenerationResponse,
    DatasetStats
)
from .ml.data_importer import TrainingDataImporter
from .ml.llm_trainer import LLMTrainer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="BookGen Custom LLM Training Service",
    description="Custom LLM training service for generating domain-specific books with GPT-2 fine-tuning",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
database = None
data_importer = None
llm_trainer = None

# Background task status tracking
training_jobs = {}
import_jobs = {}

DATA_IMPORTER_NOT_INITIALIZED = "Data importer not initialized"
LLM_TRAINER_NOT_INITIALIZED = "LLM trainer not initialized"


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global database, data_importer, llm_trainer
    
    try:
        # Connect to MongoDB
        database_url = os.getenv("DATABASE_URL")
        db_name = os.getenv("MONGODB_DB_NAME", "bookgen_ai")
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        client = motor.motor_asyncio.AsyncIOMotorClient(database_url)
        database = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Initialize services
        data_importer = TrainingDataImporter(database)
        llm_trainer = LLMTrainer(database, models_dir=os.getenv("MODELS_DIR", "./models"))
        
        # Create necessary directories
        os.makedirs(os.getenv("MODELS_DIR", "./models"), exist_ok=True)
        os.makedirs(os.getenv("TRAINING_DATA_DIR", "./data"), exist_ok=True)
        os.makedirs(os.getenv("OUTPUT_DIR", "./output"), exist_ok=True)
        os.makedirs(os.getenv("LOGS_DIR", "./logs"), exist_ok=True)
        
        logger.info("LLM Training Service initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if database:
        database.client.close()
        logger.info("Database connection closed")


# ============================================
# Root and Health Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BookGen Custom LLM Training Service",
        "version": "2.0.0",
        "features": [
            "Kaggle GPU fine-tuned distilgpt2 (BookGen v1)",
            "Domain-specific fine-tuning and fallback model support",
            "Real-time inference",
            "MongoDB training data storage",
            "Automated validation & benchmarking scripts"
        ],
        "status": "ready" if database else "initializing"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not database:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        # Test database connection
        await database.command('ping')
        
        return {
            "status": "healthy",
            "database": "connected",
            "services": {
                "data_importer": "ready" if data_importer else "not_initialized",
                "llm_trainer": "ready" if llm_trainer else "not_initialized"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


# ============================================
# Training Data Management Endpoints
# ============================================

@app.post("/data/import/file")
async def import_data_from_file(
    file_path: str,
    domain_id: str,
    domain_name: str,
    niche_id: Optional[str] = None,
    niche_name: Optional[str] = None,
    content_type: str = "data_gov",
    background_tasks: BackgroundTasks = None
):
    """Import training data from JSON file"""
    if not data_importer:
        raise HTTPException(status_code=503, detail=DATA_IMPORTER_NOT_INITIALIZED)
    
    try:
        imported, skipped, errors = await data_importer.import_from_json_file(
            file_path, domain_id, domain_name, niche_id, niche_name, content_type
        )
        
        return {
            "message": "Data import completed",
            "imported_examples": imported,
            "skipped_examples": skipped,
            "errors": errors,
            "file_path": file_path,
            "domain_id": domain_id,
            "niche_id": niche_id
        }
        
    except Exception as e:
        logger.error(f"Error importing data from file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/data/import/directory")
async def import_data_from_directory(
    directory_path: str,
    domain_id: str,
    domain_name: str,
    niche_id: Optional[str] = None,
    niche_name: Optional[str] = None,
    content_type: str = "data_gov"
):
    """Import training data from all JSON files in directory"""
    if not data_importer:
        raise HTTPException(status_code=503, detail=DATA_IMPORTER_NOT_INITIALIZED)
    
    try:
        results = await data_importer.import_from_directory(
            directory_path, domain_id, domain_name, niche_id, niche_name, content_type
        )
        
        total_imported = sum(result[0] for result in results.values())
        total_skipped = sum(result[1] for result in results.values())
        
        return {
            "message": "Directory import completed",
            "total_imported": total_imported,
            "total_skipped": total_skipped,
            "files_processed": len(results),
            "file_results": results,
            "directory_path": directory_path
        }
        
    except Exception as e:
        logger.error(f"Error importing data from directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/data/examples", response_model=str)
async def add_training_example(example: TrainingExampleRequest):
    """Add a single training example"""
    if not data_importer:
        raise HTTPException(status_code=503, detail=DATA_IMPORTER_NOT_INITIALIZED)
    
    try:
        example_id = await data_importer.add_single_example(example)
        return example_id
        
    except Exception as e:
        logger.error(f"Error adding training example: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/stats")
async def get_dataset_stats(
    domain_id: str,
    niche_id: Optional[str] = None
) -> DatasetStats:
    """Get dataset statistics"""
    if not data_importer:
        raise HTTPException(status_code=503, detail=DATA_IMPORTER_NOT_INITIALIZED)
    
    try:
        stats = await data_importer.get_dataset_stats(domain_id, niche_id)
        if not stats:
            raise HTTPException(status_code=404, detail="No data found for specified domain/niche")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dataset stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/domains")
async def list_domains():
    """List all available domains with training data"""
    if not data_importer:
        raise HTTPException(status_code=503, detail=DATA_IMPORTER_NOT_INITIALIZED)
    
    try:
        domains = await data_importer.list_domains()
        return {"domains": domains}
        
    except Exception as e:
        logger.error(f"Error listing domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/data/clear")
async def clear_training_data(
    domain_id: Optional[str] = None,
    niche_id: Optional[str] = None
):
    """Clear training data"""
    if not data_importer:
        raise HTTPException(status_code=503, detail="Data importer not initialized")
    
    try:
        deleted_count = await data_importer.clear_training_data(domain_id, niche_id)
        
        scope = "all data"
        if domain_id:
            scope = f"domain '{domain_id}'"
            if niche_id:
                scope += f" niche '{niche_id}'"
        
        return {
            "message": f"Cleared {deleted_count} training examples from {scope}",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Model Training Endpoints
# ============================================

@app.post("/train", response_model=str)
async def start_training(
    request: TrainingJobRequest,
    background_tasks: BackgroundTasks
):
    """Start a new training job"""
    if not llm_trainer:
        raise HTTPException(status_code=503, detail=LLM_TRAINER_NOT_INITIALIZED)
    
    try:
        job_id = await llm_trainer.start_training_job(
            request,
            progress_callback=lambda job_id, epoch, total_epochs, status, **kwargs: 
                training_jobs.update({
                    job_id: {
                        "epoch": epoch,
                        "total_epochs": total_epochs,
                        "status": status,
                        "progress": (epoch / total_epochs) * 100 if total_epochs > 0 else 0,
                        **kwargs
                    }
                })
        )
        
        return job_id
        
    except Exception as e:
        logger.error(f"Error starting training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/train/status/{job_id}")
async def get_training_status(job_id: str):
    """Get training job status"""
    if not llm_trainer:
        raise HTTPException(status_code=503, detail=LLM_TRAINER_NOT_INITIALIZED)
    
    try:
        job = await llm_trainer.get_training_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Training job not found")
        
        # Merge with real-time progress if available
        real_time_progress = training_jobs.get(job_id, {})
        
        return {
            "job": job.dict(),
            "real_time_progress": real_time_progress
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/train/jobs")
async def list_training_jobs(
    domain_id: Optional[str] = None,
    limit: int = 50
):
    """List training jobs"""
    if not llm_trainer:
        raise HTTPException(status_code=503, detail=LLM_TRAINER_NOT_INITIALIZED)
    
    try:
        jobs = await llm_trainer.list_training_jobs(domain_id, limit)
        return {"jobs": [job.dict() for job in jobs]}
        
    except Exception as e:
        logger.error(f"Error listing training jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Model Management Endpoints
# ============================================

@app.get("/models")
async def list_models(domain_id: Optional[str] = None):
    """List available trained models"""
    if not llm_trainer:
        raise HTTPException(status_code=503, detail=LLM_TRAINER_NOT_INITIALIZED)
    
    try:
        models = await llm_trainer.get_available_models(domain_id)
        return {"models": [model.dict() for model in models]}
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Text Generation Endpoints
# ============================================

@app.post("/generate", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    """Generate text using trained model"""
    if not llm_trainer:
        raise HTTPException(status_code=503, detail=LLM_TRAINER_NOT_INITIALIZED)
    
    try:
        response = await llm_trainer.generate_text(request)
        return response
        
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Utility Endpoints
# ============================================

@app.get("/supported-domains")
async def get_supported_domains():
    """Get list of supported domains"""
    domains = os.getenv("SUPPORTED_DOMAINS", "").split(",")
    
    domain_info = {
        "ai_ml": "AI & Machine Learning",
        "automation": "Automation & Productivity",
        "healthtech": "Health Technology",
        "cybersecurity": "Cybersecurity",
        "creator_economy": "Creator Economy",
        "web3": "Web3 & Blockchain",
        "ecommerce": "E-commerce",
        "data_analytics": "Data Analytics",
        "gaming": "Gaming",
        "kids_parenting": "Kids & Parenting",
        "nutrition": "Nutrition & Wellness",
        "recipes": "Recipes & Cooking"
    }
    
    return {
        "supported_domains": [
            {
                "id": domain_id.strip(),
                "name": domain_info.get(domain_id.strip(), domain_id.strip().replace("_", " ").title())
            }
            for domain_id in domains if domain_id.strip()
        ]
    }


@app.get("/template/training-data")
async def get_training_data_template():
    """Get training data JSON template"""
    from .ml.data_importer import create_example_template
    
    template = [create_example_template()]
    
    return {
        "template": template,
        "description": "Use this template for creating training data JSON files",
        "required_fields": ["prompt", "completion"],
        "optional_fields": [
            "quality_score", "chapter_type", "target_audience",
            "training_weight", "tags", "metadata"
        ]
    }


@app.get("/status/system")
async def get_system_status():
    """Get comprehensive system status"""
    if not database:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Get database stats
        stats = await database.command("dbStats")
        
        # Check if we're currently training
        is_training = llm_trainer.is_training if llm_trainer else False
        current_job = llm_trainer.current_job.dict() if llm_trainer and llm_trainer.current_job else None
        
        # Count records in collections
        training_data_count = await database.llm_training_data.count_documents({})
        models_count = await database.llm_models.count_documents({"is_active": True})
        jobs_count = await database.llm_training_jobs.count_documents({})
        
        return {
            "service_status": "running",
            "database": {
                "connected": True,
                "name": stats.get("db"),
                "collections": stats.get("collections", 0),
                "data_size": f"{stats.get('dataSize', 0) / (1024*1024):.2f} MB"
            },
            "training": {
                "is_training": is_training,
                "current_job": current_job,
                "active_jobs": len([j for j in training_jobs.values() if j.get("status") == "training"])
            },
            "data": {
                "training_examples": training_data_count,
                "trained_models": models_count,
                "total_jobs": jobs_count
            },
            "real_time_jobs": len(training_jobs)
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", 8001)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
