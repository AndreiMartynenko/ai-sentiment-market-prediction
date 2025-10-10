#!/usr/bin/env python3
"""
AI Sentiment Market Prediction - ML Service
Advanced sentiment analysis service for dissertation project
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    pipeline,
    Pipeline
)
import torch
from scipy.special import softmax
import yfinance as yf
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import joblib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Pydantic models
class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")
    model: Optional[str] = Field("finbert", description="Model to use for analysis")

class AnalyzeBatchRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to analyze")
    model: Optional[str] = Field("finbert", description="Model to use for analysis")

class AnalyzeResponse(BaseModel):
    sentiment: str = Field(..., description="Sentiment label")
    confidence: float = Field(..., description="Confidence score")
    model: str = Field(..., description="Model used")
    text: str = Field(..., description="Original text")

class ModelInfo(BaseModel):
    name: str
    description: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_date: str
    dataset_size: int

class PerformanceMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    total_predictions: int
    correct_predictions: int
    model_name: str
    last_updated: str

# ML Service Class
class SentimentMLService:
    def __init__(self):
        self.models = {}
        self.model_info = {}
        self.performance_metrics = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """Load all available sentiment analysis models"""
        model_configs = {
            "finbert": {
                "path": "ProsusAI/finbert",
                "description": "Financial sentiment analysis model",
                "max_length": 512
            },
            "roberta": {
                "path": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "description": "Twitter sentiment analysis model",
                "max_length": 512
            },
            "distilbert": {
                "path": "distilbert-base-uncased-finetuned-sst-2-english",
                "description": "General sentiment analysis model",
                "max_length": 512
            }
        }
        
        for model_name, config in model_configs.items():
            try:
                logger.info(f"Loading model: {model_name}")
                pipeline_obj = pipeline(
                    "sentiment-analysis",
                    model=config["path"],
                    device=0 if self.device == "cuda" else -1,
                    return_all_scores=True
                )
                self.models[model_name] = pipeline_obj
                self.model_info[model_name] = {
                    "name": model_name,
                    "description": config["description"],
                    "accuracy": 0.0,  # Will be updated with real metrics
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1_score": 0.0,
                    "training_date": "2024-01-01",
                    "dataset_size": 0
                }
                logger.info(f"Successfully loaded model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {e}")
    
    def analyze_text(self, text: str, model_name: str = "finbert") -> AnalyzeResponse:
        """Analyze sentiment of a single text"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not available")
        
        try:
            # Get prediction
            results = self.models[model_name](text)
            
            # Extract best result
            best_result = max(results[0], key=lambda x: x['score'])
            
            return AnalyzeResponse(
                sentiment=best_result['label'].upper(),
                confidence=round(best_result['score'], 4),
                model=model_name,
                text=text
            )
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    def analyze_batch(self, texts: List[str], model_name: str = "finbert") -> List[AnalyzeResponse]:
        """Analyze sentiment of multiple texts"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not available")
        
        try:
            results = []
            for text in texts:
                result = self.analyze_text(text, model_name)
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.models.keys())
    
    def get_model_info(self, model_name: str) -> ModelInfo:
        """Get information about a specific model"""
        if model_name not in self.model_info:
            raise ValueError(f"Model {model_name} not found")
        
        info = self.model_info[model_name]
        return ModelInfo(**info)
    
    def get_model_performance(self, model_name: str) -> PerformanceMetrics:
        """Get performance metrics for a model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        # Load or calculate performance metrics
        if model_name not in self.performance_metrics:
            # Calculate basic metrics (in real implementation, load from database)
            self.performance_metrics[model_name] = PerformanceMetrics(
                accuracy=0.85,  # Placeholder
                precision=0.82,
                recall=0.88,
                f1_score=0.85,
                total_predictions=1000,
                correct_predictions=850,
                model_name=model_name,
                last_updated=datetime.now().isoformat()
            )
        
        return self.performance_metrics[model_name]
    
    def evaluate_model(self, model_name: str, test_data: List[Dict]) -> Dict[str, float]:
        """Evaluate model performance on test data"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        # This would be implemented with actual test data
        # For now, return placeholder metrics
        return {
            "accuracy": 0.85,
            "precision": 0.82,
            "recall": 0.88,
            "f1_score": 0.85
        }

# Initialize ML service
ml_service = SentimentMLService()

# FastAPI app
app = FastAPI(
    title="AI Sentiment Market Prediction - ML Service",
    description="Advanced sentiment analysis service for financial market prediction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Sentiment Market Prediction - ML Service",
        "version": "1.0.0",
        "status": "healthy",
        "available_models": ml_service.get_available_models()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": len(ml_service.models),
        "device": ml_service.device
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_sentiment(request: AnalyzeRequest):
    """Analyze sentiment of a single text"""
    try:
        result = ml_service.analyze_text(request.text, request.model)
        return result
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_batch", response_model=List[AnalyzeResponse])
async def analyze_batch_sentiment(request: AnalyzeBatchRequest):
    """Analyze sentiment of multiple texts"""
    try:
        results = ml_service.analyze_batch(request.texts, request.model)
        return results
    except Exception as e:
        logger.error(f"Error in batch analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def get_available_models():
    """Get list of available models"""
    return {
        "models": ml_service.get_available_models(),
        "count": len(ml_service.models)
    }

@app.get("/models/{model_name}/info", response_model=ModelInfo)
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    try:
        info = ml_service.get_model_info(model_name)
        return info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/models/{model_name}/performance", response_model=PerformanceMetrics)
async def get_model_performance(model_name: str):
    """Get performance metrics for a model"""
    try:
        performance = ml_service.get_model_performance(model_name)
        return performance
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/models/{model_name}/evaluate")
async def evaluate_model(model_name: str, test_data: List[Dict]):
    """Evaluate model performance"""
    try:
        metrics = ml_service.evaluate_model(model_name, test_data)
        return {
            "model": model_name,
            "metrics": metrics,
            "evaluated_at": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/stats")
async def get_service_stats():
    """Get service statistics"""
    return {
        "total_models": len(ml_service.models),
        "available_models": ml_service.get_available_models(),
        "device": ml_service.device,
        "service_uptime": "N/A",  # Would track actual uptime
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Run the service
    uvicorn.run(
        "ml_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
