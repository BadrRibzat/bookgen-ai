"""
Training data schema for Custom LLM
Defines structure for storing training examples in MongoDB
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class TrainingExample(BaseModel):
    """
    Core training example model for storing in MongoDB
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Content fields
    prompt: str = Field(..., min_length=10, max_length=2048, description="Input prompt for training")
    completion: str = Field(..., min_length=50, max_length=8192, description="Expected completion/response")
    
    # Categorization
    domain_id: str = Field(..., description="Domain ID from backend (ai_ml, automation, etc.)")
    domain_name: str = Field(..., description="Human-readable domain name")
    niche_id: Optional[str] = Field(None, description="Specific niche within domain")
    niche_name: Optional[str] = Field(None, description="Human-readable niche name")
    
    # Content metadata
    content_type: str = Field(default="manual", description="Source type: manual, data_gov, scraping, etc.")
    chapter_type: Optional[str] = Field(None, description="Chapter type: introduction, conclusion, etc.")
    target_audience: Optional[str] = Field(None, description="Beginner, Intermediate, Advanced")
    language: str = Field(default="en", description="Content language")
    
    # Quality metrics
    quality_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Quality score 0-1")
    word_count: int = Field(default=0, ge=0, description="Word count of completion")
    readability_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Flesch reading ease score")
    
    # Training metadata
    training_weight: float = Field(default=1.0, ge=0.0, le=10.0, description="Training weight/importance")
    is_validated: bool = Field(default=False, description="Whether content has been manually validated")
    validation_notes: Optional[str] = Field(None, description="Notes from validation process")
    
    # Source tracking
    source_file: Optional[str] = Field(None, description="Original file path/name")
    source_url: Optional[str] = Field(None, description="Original URL if scraped")
    data_gov_dataset: Optional[str] = Field(None, description="Data.gov dataset identifier")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_for_training: Optional[datetime] = Field(None, description="Last time used in training")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Content tags for filtering")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        
    def to_training_format(self) -> Dict[str, str]:
        """Convert to format suitable for model training"""
        return {
            "prompt": self.prompt,
            "completion": self.completion,
            "domain": self.domain_name,
            "weight": self.training_weight
        }


class TrainingDataset(BaseModel):
    """
    Collection of training examples for a specific domain/niche
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Dataset identification
    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    
    # Scope
    domain_id: str = Field(..., description="Target domain")
    domain_name: str = Field(..., description="Domain display name")
    niche_id: Optional[str] = Field(None, description="Target niche (optional)")
    niche_name: Optional[str] = Field(None, description="Niche display name")
    
    # Dataset statistics
    total_examples: int = Field(default=0, description="Total number of examples")
    validated_examples: int = Field(default=0, description="Number of validated examples")
    avg_quality_score: float = Field(default=0.0, description="Average quality score")
    total_word_count: int = Field(default=0, description="Total words in dataset")
    
    # Training configuration
    train_split: float = Field(default=0.8, ge=0.1, le=0.9, description="Training split ratio")
    validation_split: float = Field(default=0.1, ge=0.05, le=0.3, description="Validation split ratio")
    test_split: float = Field(default=0.1, ge=0.05, le=0.3, description="Test split ratio")
    
    # Status
    is_ready_for_training: bool = Field(default=False, description="Ready for model training")
    last_prepared: Optional[datetime] = Field(None, description="Last time dataset was prepared")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created dataset")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TrainingJob(BaseModel):
    """
    Training job tracking and configuration
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Job identification
    job_id: str = Field(..., description="Unique job identifier")
    name: str = Field(..., description="Human-readable job name")
    
    # Scope
    domain_id: str = Field(..., description="Target domain")
    domain_name: str = Field(..., description="Domain display name")
    niche_id: Optional[str] = Field(None, description="Target niche (optional)")
    niche_name: Optional[str] = Field(None, description="Niche display name")
    
    # Training configuration
    model_name: str = Field(default="gpt2", description="Base model name")
    model_size: str = Field(default="small", description="Model size variant")
    
    # Hyperparameters
    batch_size: int = Field(default=4, ge=1, le=32, description="Training batch size")
    learning_rate: float = Field(default=5e-5, ge=1e-6, le=1e-3, description="Learning rate")
    epochs: int = Field(default=3, ge=1, le=100, description="Number of training epochs")
    warmup_steps: int = Field(default=100, ge=0, description="Warmup steps")
    max_length: int = Field(default=512, ge=128, le=2048, description="Maximum sequence length")
    
    # Training data
    dataset_id: Optional[str] = Field(None, description="Dataset used for training")
    total_examples: int = Field(default=0, description="Total training examples")
    training_examples: int = Field(default=0, description="Examples used for training")
    validation_examples: int = Field(default=0, description="Examples used for validation")
    
    # Job status
    status: str = Field(default="pending", description="Job status: pending, running, completed, failed")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Training progress percentage")
    current_epoch: int = Field(default=0, description="Current training epoch")
    current_step: int = Field(default=0, description="Current training step")
    
    # Results
    final_loss: Optional[float] = Field(None, description="Final training loss")
    validation_loss: Optional[float] = Field(None, description="Final validation loss")
    perplexity: Optional[float] = Field(None, description="Model perplexity")
    
    # Model artifacts
    model_path: Optional[str] = Field(None, description="Path to saved model")
    checkpoint_path: Optional[str] = Field(None, description="Path to training checkpoint")
    tokenizer_path: Optional[str] = Field(None, description="Path to tokenizer")
    
    # Timing
    started_at: Optional[datetime] = Field(None, description="Training start time")
    completed_at: Optional[datetime] = Field(None, description="Training completion time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    total_duration_seconds: Optional[int] = Field(None, description="Total training duration")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_traceback: Optional[str] = Field(None, description="Full error traceback")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who started the job")
    
    # Hardware info
    device_used: Optional[str] = Field(None, description="Device used for training (cpu/cuda)")
    gpu_memory_used: Optional[float] = Field(None, description="Peak GPU memory usage (GB)")
    total_memory_used: Optional[float] = Field(None, description="Peak system memory usage (GB)")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ModelArtifact(BaseModel):
    """
    Trained model artifact metadata
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Model identification
    model_id: str = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Model display name")
    version: str = Field(..., description="Model version")
    
    # Scope
    domain_id: str = Field(..., description="Target domain")
    domain_name: str = Field(..., description="Domain display name")
    niche_id: Optional[str] = Field(None, description="Target niche (optional)")
    niche_name: Optional[str] = Field(None, description="Niche display name")
    
    # Model details
    base_model: str = Field(..., description="Base model name (gpt2, distilgpt2, etc.)")
    model_size: str = Field(..., description="Model size (small, medium, large)")
    parameters_count: Optional[int] = Field(None, description="Total model parameters")
    
    # Training info
    training_job_id: str = Field(..., description="Training job that created this model")
    training_examples: int = Field(..., description="Number of training examples used")
    training_epochs: int = Field(..., description="Number of training epochs")
    final_loss: Optional[float] = Field(None, description="Final training loss")
    validation_loss: Optional[float] = Field(None, description="Final validation loss")
    
    # File paths
    model_path: str = Field(..., description="Path to model files")
    tokenizer_path: str = Field(..., description="Path to tokenizer files")
    config_path: str = Field(..., description="Path to model config")
    
    # Performance metrics
    perplexity: Optional[float] = Field(None, description="Model perplexity")
    bleu_score: Optional[float] = Field(None, description="BLEU score on test set")
    rouge_scores: Optional[Dict[str, float]] = Field(None, description="ROUGE scores")
    
    # Usage statistics
    generation_count: int = Field(default=0, description="Number of times used for generation")
    last_used: Optional[datetime] = Field(None, description="Last time used for generation")
    avg_generation_time: Optional[float] = Field(None, description="Average generation time (seconds)")
    
    # Status
    is_active: bool = Field(default=True, description="Whether model is active/available")
    is_default: bool = Field(default=False, description="Whether this is the default model for domain")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # File size and storage
    model_size_mb: Optional[float] = Field(None, description="Model size in MB")
    storage_location: str = Field(default="local", description="Storage location: local, cloud, etc.")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Request/Response models for API
class TrainingExampleRequest(BaseModel):
    """Request model for creating training examples"""
    prompt: str = Field(..., min_length=10, max_length=2048)
    completion: str = Field(..., min_length=50, max_length=8192)
    domain_id: str
    domain_name: str
    niche_id: Optional[str] = None
    niche_name: Optional[str] = None
    content_type: str = "manual"
    chapter_type: Optional[str] = None
    target_audience: Optional[str] = None
    quality_score: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    source_file: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TrainingJobRequest(BaseModel):
    """Request model for starting training jobs"""
    domain_id: str
    niche_id: Optional[str] = None
    job_name: Optional[str] = None
    model_name: str = "gpt2"
    epochs: int = Field(default=3, ge=1, le=100)
    batch_size: int = Field(default=4, ge=1, le=32)
    learning_rate: float = Field(default=5e-5, ge=1e-6, le=1e-3)
    max_length: int = Field(default=512, ge=128, le=2048)


class TextGenerationRequest(BaseModel):
    """Request model for text generation"""
    prompt: str = Field(..., min_length=1, max_length=1024)
    domain_id: str
    niche_id: Optional[str] = None
    max_length: int = Field(default=512, ge=50, le=2048)
    temperature: float = Field(default=0.8, ge=0.1, le=2.0)
    top_p: float = Field(default=0.9, ge=0.1, le=1.0)
    top_k: int = Field(default=50, ge=1, le=100)
    repetition_penalty: float = Field(default=1.1, ge=1.0, le=2.0)
    do_sample: bool = True
    num_return_sequences: int = Field(default=1, ge=1, le=5)


# Response models
class TrainingExampleResponse(TrainingExample):
    """Response model for training examples"""


class TrainingJobResponse(TrainingJob):
    """Response model for training jobs"""


class ModelArtifactResponse(ModelArtifact):
    """Response model for model artifacts"""


class TextGenerationResponse(BaseModel):
    """Response model for text generation"""
    generated_text: List[str]
    prompt: str
    domain_id: str
    niche_id: Optional[str]
    model_used: str
    generation_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Utility models
class DatasetStats(BaseModel):
    """Dataset statistics model"""
    domain_id: str
    domain_name: str
    niche_id: Optional[str] = None
    niche_name: Optional[str] = None
    total_examples: int
    validated_examples: int
    avg_quality_score: float
    total_word_count: int
    avg_word_count: float
    content_types: Dict[str, int]
    chapter_types: Dict[str, int]
    target_audiences: Dict[str, int]
    quality_distribution: Dict[str, int]  # Low, Medium, High quality counts


class DomainSummary(BaseModel):
    """Domain training data summary"""
    domain_id: str
    domain_name: str
    total_examples: int
    total_niches: int
    trained_models: int
    last_training: Optional[datetime]
    avg_quality_score: float
    ready_for_training: bool
    niche_breakdown: List[Dict[str, Any]]