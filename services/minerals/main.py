"""
Minerals Predictor Service
Machine learning service for mineral analysis and prediction.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import logging
import uuid
from datetime import datetime
import json
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Minerals Predictor Service",
    description="Machine learning service for mineral analysis and prediction",
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

# Pydantic models
class MineralSample(BaseModel):
    sample_id: str
    location: Dict[str, float] = Field(..., description="Latitude and longitude coordinates")
    depth_meters: float = Field(..., gt=0)
    soil_ph: float = Field(..., ge=0, le=14)
    moisture_content: float = Field(..., ge=0, le=100)
    temperature_celsius: float
    elemental_composition: Dict[str, float] = Field(..., description="Elemental percentages")

class PredictionRequest(BaseModel):
    samples: List[MineralSample]
    prediction_type: str = Field(..., description="Type of prediction: 'mineral_type', 'quality_grade', 'extraction_feasibility'")

class PredictionResult(BaseModel):
    sample_id: str
    predicted_mineral: Optional[str] = None
    confidence_score: float = Field(..., ge=0, le=1)
    quality_grade: Optional[str] = None
    extraction_feasibility: Optional[bool] = None
    estimated_yield: Optional[float] = None
    recommendations: List[str] = []

class PredictionResponse(BaseModel):
    request_id: str
    timestamp: datetime
    results: List[PredictionResult]
    model_version: str
    processing_time_seconds: float

class ModelInfo(BaseModel):
    model_name: str
    version: str
    accuracy: float
    last_trained: datetime
    features: List[str]
    supported_predictions: List[str]

class TrainingRequest(BaseModel):
    dataset_name: str
    model_type: str = Field(..., description="Type of model: 'random_forest', 'xgboost', 'neural_network'")
    features: List[str]
    target_column: str
    validation_split: float = Field(0.2, ge=0.1, le=0.5)

# Mock ML model implementation
class MineralPredictor:
    def __init__(self):
        self.models = {}
        self.model_info = {
            "mineral_classifier": ModelInfo(
                model_name="Mineral Type Classifier",
                version="1.0.0",
                accuracy=0.87,
                last_trained=datetime.now(),
                features=["soil_ph", "depth_meters", "moisture_content", "temperature_celsius", "Fe", "Cu", "Au", "Ag"],
                supported_predictions=["mineral_type", "quality_grade"]
            ),
            "feasibility_predictor": ModelInfo(
                model_name="Extraction Feasibility Predictor",
                version="1.0.0", 
                accuracy=0.92,
                last_trained=datetime.now(),
                features=["depth_meters", "quality_grade", "location", "environmental_factors"],
                supported_predictions=["extraction_feasibility", "estimated_yield"]
            )
        }
        
        # Initialize with mock models
        self._initialize_mock_models()
    
    def _initialize_mock_models(self):
        """Initialize mock ML models for demonstration"""
        # This would typically load trained models from disk
        self.models["mineral_classifier"] = self._create_mock_classifier()
        self.models["feasibility_predictor"] = self._create_mock_regressor()
    
    def _create_mock_classifier(self):
        """Create a mock classifier"""
        class MockClassifier:
            def predict(self, features):
                # Mock prediction logic
                minerals = ["Iron Ore", "Copper", "Gold", "Silver", "Platinum", "Lithium"]
                return np.random.choice(minerals, len(features))
            
            def predict_proba(self, features):
                # Mock probability predictions
                return np.random.random((len(features), 6))
        
        return MockClassifier()
    
    def _create_mock_regressor(self):
        """Create a mock regressor"""
        class MockRegressor:
            def predict(self, features):
                # Mock yield predictions
                return np.random.uniform(0.1, 0.9, len(features))
        
        return MockRegressor()
    
    def _extract_features(self, sample: MineralSample) -> np.array:
        """Extract features from mineral sample"""
        features = [
            sample.soil_ph,
            sample.depth_meters,
            sample.moisture_content,
            sample.temperature_celsius
        ]
        
        # Add elemental composition features
        common_elements = ["Fe", "Cu", "Au", "Ag", "Pt", "Li", "Si", "Al"]
        for element in common_elements:
            features.append(sample.elemental_composition.get(element, 0.0))
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, samples: List[MineralSample], prediction_type: str) -> List[PredictionResult]:
        """Make predictions on mineral samples"""
        results = []
        
        for sample in samples:
            features = self._extract_features(sample)
            
            if prediction_type == "mineral_type":
                mineral = self.models["mineral_classifier"].predict(features)[0]
                probabilities = self.models["mineral_classifier"].predict_proba(features)[0]
                confidence = np.max(probabilities)
                
                # Determine quality grade based on confidence and composition
                quality_grade = self._determine_quality_grade(sample, confidence)
                
                result = PredictionResult(
                    sample_id=sample.sample_id,
                    predicted_mineral=mineral,
                    confidence_score=float(confidence),
                    quality_grade=quality_grade,
                    recommendations=self._generate_recommendations(sample, mineral)
                )
                
            elif prediction_type == "extraction_feasibility":
                feasibility_score = self.models["feasibility_predictor"].predict(features)[0]
                is_feasible = feasibility_score > 0.5
                estimated_yield = feasibility_score * 100  # Convert to percentage
                
                result = PredictionResult(
                    sample_id=sample.sample_id,
                    confidence_score=float(feasibility_score),
                    extraction_feasibility=is_feasible,
                    estimated_yield=float(estimated_yield),
                    recommendations=self._generate_feasibility_recommendations(sample, is_feasible)
                )
                
            else:
                # Combined prediction
                mineral = self.models["mineral_classifier"].predict(features)[0]
                mineral_confidence = np.max(self.models["mineral_classifier"].predict_proba(features)[0])
                feasibility_score = self.models["feasibility_predictor"].predict(features)[0]
                
                result = PredictionResult(
                    sample_id=sample.sample_id,
                    predicted_mineral=mineral,
                    confidence_score=float(mineral_confidence),
                    quality_grade=self._determine_quality_grade(sample, mineral_confidence),
                    extraction_feasibility=feasibility_score > 0.5,
                    estimated_yield=float(feasibility_score * 100),
                    recommendations=self._generate_comprehensive_recommendations(sample, mineral, feasibility_score)
                )
            
            results.append(result)
        
        return results
    
    def _determine_quality_grade(self, sample: MineralSample, confidence: float) -> str:
        """Determine quality grade based on sample and confidence"""
        if confidence > 0.8:
            return "Premium"
        elif confidence > 0.6:
            return "High"
        elif confidence > 0.4:
            return "Medium"
        else:
            return "Low"
    
    def _generate_recommendations(self, sample: MineralSample, mineral: str) -> List[str]:
        """Generate recommendations for mineral extraction"""
        recommendations = []
        
        if sample.depth_meters > 100:
            recommendations.append("Consider deep drilling techniques")
        
        if sample.moisture_content > 50:
            recommendations.append("Implement drainage systems before extraction")
        
        if mineral in ["Gold", "Platinum"]:
            recommendations.append("Use specialized extraction methods for precious metals")
        
        return recommendations
    
    def _generate_feasibility_recommendations(self, sample: MineralSample, is_feasible: bool) -> List[str]:
        """Generate feasibility-specific recommendations"""
        if not is_feasible:
            return ["Extraction not economically viable at current market conditions"]
        
        recommendations = ["Proceed with detailed geological survey"]
        
        if sample.depth_meters < 50:
            recommendations.append("Surface mining techniques recommended")
        else:
            recommendations.append("Underground mining required")
        
        return recommendations
    
    def _generate_comprehensive_recommendations(self, sample: MineralSample, mineral: str, feasibility: float) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []
        recommendations.extend(self._generate_recommendations(sample, mineral))
        recommendations.extend(self._generate_feasibility_recommendations(sample, feasibility > 0.5))
        return list(set(recommendations))  # Remove duplicates

# Global predictor instance
predictor = MineralPredictor()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"service": "Minerals Predictor", "status": "healthy", "version": "1.0.0"}

@app.post("/predict", response_model=PredictionResponse)
async def predict_minerals(request: PredictionRequest):
    """Make mineral predictions"""
    start_time = datetime.now()
    
    try:
        # Validate prediction type
        valid_types = ["mineral_type", "quality_grade", "extraction_feasibility", "comprehensive"]
        if request.prediction_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid prediction type. Must be one of: {valid_types}"
            )
        
        # Make predictions
        results = predictor.predict(request.samples, request.prediction_type)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return PredictionResponse(
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            results=results,
            model_version="1.0.0",
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction processing failed")

@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List available models"""
    return list(predictor.model_info.values())

@app.get("/models/{model_name}", response_model=ModelInfo)
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    if model_name not in predictor.model_info:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return predictor.model_info[model_name]

@app.post("/analyze-batch")
async def analyze_batch_file(file: UploadFile = File(...)):
    """Analyze a batch of samples from uploaded CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        # Read CSV file
        content = await file.read()
        df = pd.read_csv(pd.io.common.StringIO(content.decode('utf-8')))
        
        # Convert DataFrame to MineralSample objects
        samples = []
        for _, row in df.iterrows():
            # Extract elemental composition from columns
            elemental_cols = [col for col in df.columns if col.startswith('element_')]
            elemental_composition = {}
            for col in elemental_cols:
                element = col.replace('element_', '')
                elemental_composition[element] = float(row[col])
            
            sample = MineralSample(
                sample_id=str(row.get('sample_id', uuid.uuid4())),
                location={"lat": float(row['latitude']), "lon": float(row['longitude'])},
                depth_meters=float(row['depth_meters']),
                soil_ph=float(row['soil_ph']),
                moisture_content=float(row['moisture_content']),
                temperature_celsius=float(row['temperature_celsius']),
                elemental_composition=elemental_composition
            )
            samples.append(sample)
        
        # Make predictions
        results = predictor.predict(samples, "comprehensive")
        
        return {
            "batch_id": str(uuid.uuid4()),
            "samples_processed": len(samples),
            "results": results,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Batch analysis failed")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "service": "Minerals Predictor",
        "status": "healthy",
        "models_loaded": len(predictor.models),
        "available_models": list(predictor.model_info.keys()),
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)