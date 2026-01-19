from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from sentence_transformers import SentenceTransformer, util
import json
import tempfile
import os
from data_logger import log_test_data
import sys

# Import petal modules for prediction
try:
    import petal_reading
    import petal_logic
    import petal_writing
    import petal_memory
    PETAL_MODULES_AVAILABLE = True
except ImportError:
    PETAL_MODULES_AVAILABLE = False

try:
    from faster_whisper import WhisperModel  # type: ignore
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    WhisperModel = None

app = FastAPI(title="AI Test Analysis API")

# Load models lazily
model = None
whisper = None

def get_model():
    """Lazy load sentence transformer model"""
    global model
    if model is None:
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not load SentenceTransformer: {e}")
    return model

def get_whisper():
    """Lazy load whisper model"""
    global whisper
    if whisper is None and WHISPER_AVAILABLE:
        try:
            whisper = WhisperModel("base")
        except Exception as e:
            print(f"Warning: Could not load Whisper: {e}")
    return whisper

# ============ DATA MODELS ============

class Test1Data(BaseModel):
    """Reading Test Data Model"""
    user_id: str
    test_id: str
    text_content: str  # The text that was supposed to be read
    words_read: int  # Number of words successfully read
    total_words: int  # Total words in the passage
    reading_time_ms: int  # Time taken to read in milliseconds
    max_reading_time_ms: int  # Maximum allowed time
    pronunciation_errors: int  # Count of pronunciation errors (0-17)

class Test2Data(BaseModel):
    """Logic Test Data Model"""
    user_id: str
    test_id: str
    questions_attempted: int  # Should be around 16 for standard test
    correct_answers: int  # Number of correct answers
    total_questions: int  # Total questions (typically 16)
    logic_time_ms: int  # Time taken for logic test in milliseconds
    max_logic_time_ms: int  # Maximum allowed time
    logical_errors: int  # Count of logical errors (0-20)

class Test3Data(BaseModel):
    """Grammar/Writing Test Data Model"""
    user_id: str
    test_id: str
    text_written: str  # The text that was written
    words_written: int  # Number of words written
    total_words: int  # Total words expected
    writing_time_ms: int  # Time taken to write in milliseconds
    max_writing_time_ms: int  # Maximum allowed time
    spelling_errors: int  # Count of spelling errors (0-20)

class Test4Data(BaseModel):
    """Speaking/Audio Test Data Model"""
    user_id: str
    test_id: str
    expected_text: str  # What should have been spoken
    speaking_time_ms: int  # Duration of speaking
    max_speaking_time_ms: int  # Maximum allowed time
    audio_file: Optional[str] = None  # Path to audio file

# ============ PETAL PREDICTION MODELS ============

class PetalPredictionRequest(BaseModel):
    """Request model for petal predictions"""
    values: List[float]  # 4 normalized values

class ConsolidatedAnalysisRequest(BaseModel):
    """Request for consolidated analysis with all tests"""
    user_id: str
    test_id: str
    reading_values: List[float]  # Test1: 4 values from reading test
    logic_values: List[float]    # Test2: 4 values from logic test
    writing_values: List[float]  # Test3: 4 values from writing test
    memory_values: List[float]   # Test4: 4 values from memory test

# ============ HELPER FUNCTIONS ============

def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Normalize a score to a given range"""
    return max(min_val, min(max_val, score))

def compute_time_score(time_ms: int, max_time_ms: int, range_max: float = 10.0) -> float:
    """Compute time score (faster = higher score, max score = range_max)"""
    if max_time_ms == 0:
        return 0.0
    time_ratio = time_ms / max_time_ms
    score = max_time_ms * (1 - time_ratio) / (max_time_ms / range_max) if time_ms > 0 else range_max
    return normalize_score(score, 0.0, range_max)

def compute_word_count_score(words_count: int, total_words: int) -> float:
    """Compute word count score normalized to 0-50 scale"""
    if total_words == 0:
        return 0.0
    return normalize_score((words_count / total_words) * 50, 0.0, 50.0)

# ============ TEST ENDPOINTS ============

@app.post("/analyze-test1")
async def analyze_test1(data: Test1Data):
    """
    Analyze Reading Test
    Returns: [reading_accuracy, reading_time, words_read, pronunciation_error]
    """
    
    # 1. Reading Accuracy (0-1 float) - reduced significantly for realistic scoring (max 50%)
    reading_accuracy = normalize_score(data.words_read / data.total_words, 0.0, 1.0) if data.total_words > 0 else 0.0
    reading_accuracy = reading_accuracy * 0.5  # Max 50% accuracy
    
    # 2. Reading Time (0-10 float) - normalized time score
    reading_time_score = compute_time_score(data.reading_time_ms, data.max_reading_time_ms, 10.0)
    
    # 3. Words Read (words_read / total_words * 50)
    words_read_score = compute_word_count_score(data.words_read, data.total_words)
    
    # 4. Pronunciation Error (0-17 range, converted to penalty)
    pronunciation_penalty = normalize_score(data.pronunciation_errors / 17, 0.0, 1.0)
    
    test1_results = [
        round(reading_accuracy, 2),
        round(reading_time_score, 2),
        round(words_read_score, 2),
        round(pronunciation_penalty, 2)
    ]
    log_test_data(
        user_id=data.user_id,
        test_id=data.test_id,
        test_type="reading",
        input_data=data.dict(),
        output_array=test1_results
    )
    return {
        "user_id": data.user_id,
        "test_id": data.test_id,
        "test_type": "reading",
        "array": test1_results
    }

@app.post("/analyze-test2")
async def analyze_test2(data: Test2Data):
    """
    Analyze Logic Test
    Returns: [logic_accuracy, logic_time, questions_attempted, logical_error]
    """
    
    # 1. Logic Accuracy (0-1 float) - based on correct answers
    logic_accuracy = normalize_score(
        data.correct_answers / data.total_questions if data.total_questions > 0 else 0.0,
        0.0,
        1.0
    )
    
    # 2. Logic Time (0-10 float) - normalized time score
    logic_time_score = compute_time_score(data.logic_time_ms, data.max_logic_time_ms, 10.0)
    
    # 3. Questions Attempted (normalized, typically 16)
    questions_ratio = normalize_score(
        data.questions_attempted / data.total_questions if data.total_questions > 0 else 0.0,
        0.0,
        1.0
    )
    
    # 4. Logical Error (0-20 range, converted to penalty)
    logical_error_penalty = normalize_score(data.logical_errors / 20, 0.0, 1.0)
    
    test2_results = [
        round(logic_accuracy, 2),
        round(logic_time_score, 2),
        round(questions_ratio, 2),
        round(logical_error_penalty, 2)
    ]
    log_test_data(
        user_id=data.user_id,
        test_id=data.test_id,
        test_type="logic",
        input_data=data.dict(),
        output_array=test2_results
    )

    return {
        "user_id": data.user_id,
        "test_id": data.test_id,
        "test_type": "logic",
        "array": test2_results
    }

@app.post("/analyze-test3")
async def analyze_test3(data: Test3Data):
    """
    Analyze Grammar/Writing Test
    Returns: [grammar_score, writing_time, word_count, spelling_errors]
    """
    
    # 1. Grammar Score (0-1 float)
    grammar_score = normalize_score(1.0 - (data.spelling_errors / 20), 0.0, 1.0)
    
    # 2. Writing Time (0-10 float) - normalized time score
    writing_time_score = compute_time_score(data.writing_time_ms, data.max_writing_time_ms, 10.0)
    
    # 3. Word Count (words_written / total_words * 50)
    word_count_score = compute_word_count_score(data.words_written, data.total_words)
    
    # 4. Spelling Errors (0-20 range, converted to penalty)
    spelling_error_penalty = normalize_score(data.spelling_errors / 20, 0.0, 1.0)
    
    test3_results = [
        round(grammar_score, 2),
        round(writing_time_score, 2),
        round(word_count_score, 2),
        round(spelling_error_penalty, 2)
    ]
    log_test_data(
        user_id=data.user_id,
        test_id=data.test_id,
        test_type="grammar_writing",
        input_data=data.dict(),
        output_array=test3_results
    )
    return {
        "user_id": data.user_id,
        "test_id": data.test_id,
        "test_type": "grammar_writing",
        "array": test3_results
    }

@app.post("/analyze-test4")
async def analyze_test4(data: dict = Body(...)):
    """
    Analyze Memory Test
    Input: recall_accuracy (0-1), response_time (0-12), sequence_length (0-15), error_count (0-15)
    Returns: [recall_accuracy, response_time_score, sequence_score, error_score]
    """
    
    try:
        # Extract values
        recall_accuracy = data.get("recall_accuracy", 0.5)  # 0-1 range
        response_time = data.get("response_time", 6)  # 0-12 range (in seconds equivalent)
        sequence_length = data.get("sequence_length", 7.5)  # 0-15 range
        error_count = data.get("error_count", 7.5)  # 0-15 range
        
        # Normalize to 0-1 range for consistency
        recall_accuracy_norm = normalize_score(recall_accuracy, 0.0, 1.0)
        response_time_norm = normalize_score(response_time / 12, 0.0, 1.0)  # Convert to 0-1
        sequence_score = normalize_score(sequence_length / 15, 0.0, 1.0)  # Convert to 0-1
        error_penalty = normalize_score(error_count / 15, 0.0, 1.0)  # Convert to 0-1
        
        test4_results = [
            round(recall_accuracy_norm, 2),
            round(response_time_norm, 2),
            round(sequence_score, 2),
            round(1 - error_penalty, 2)  # Inverse: more errors = lower score
        ]
        
        log_test_data(
            user_id=data.get("user_id", "unknown"),
            test_id=data.get("test_id", "memory_test_1"),
            test_type="memory_recognition",
            input_data=data,
            output_array=test4_results,
            extra_data={
                "longest_sequence": data.get("longest_sequence_without_mistake", 0),
                "total_time_ms": data.get("total_time_ms", 0),
                "correct_answers": data.get("correct_answers", 0),
                "total_questions": data.get("total_questions", 0)
            }
        )
        
        return {
            "user_id": data.get("user_id", "unknown"),
            "test_id": data.get("test_id", "memory_test_1"),
            "test_type": "memory_recognition",
            "array": test4_results
        }
    except Exception as e:
        return {
            "error": f"Failed to analyze test4: {str(e)}",
            "user_id": data.get("user_id", "unknown"),
            "test_id": data.get("test_id", "memory_test_1")
        }

@app.post("/analyze-all-tests")
async def analyze_all_tests(
    test1_data: Optional[Test1Data] = Body(None),
    test2_data: Optional[Test2Data] = Body(None),
    test3_data: Optional[Test3Data] = Body(None),
):
    """
    Analyze multiple tests and return consolidated results
    """
    results = {
        "test1": None,
        "test2": None,
        "test3": None,
        "consolidated_scores": {}
    }
    
    all_scores = []
    
    if test1_data:
        test1_result = await analyze_test1(test1_data)
        results["test1"] = test1_result
        all_scores.extend(test1_result.get("array", []))
    
    if test2_data:
        test2_result = await analyze_test2(test2_data)
        results["test2"] = test2_result
        all_scores.extend(test2_result.get("array", []))
    
    if test3_data:
        test3_result = await analyze_test3(test3_data)
        results["test3"] = test3_result
        all_scores.extend(test3_result.get("array", []))
    
    if all_scores:
        results["consolidated_scores"] = {
            "average_score": round(sum(all_scores) / len(all_scores), 2),
            "total_tests": sum([test1_data is not None, test2_data is not None, test3_data is not None])
        }
    
    return results

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Test Analysis API",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """API Information"""
    return {
        "name": "AI Test Analysis API",
        "version": "1.0.0",
        "description": "API for analyzing reading, logic, grammar/writing, and speaking tests",
        "endpoints": {
            "test1": "/analyze-test1 (POST) - Reading Test Analysis",
            "test2": "/analyze-test2 (POST) - Logic Test Analysis",
            "test3": "/analyze-test3 (POST) - Grammar/Writing Test Analysis",
            "test4": "/analyze-test4 (POST) - Speaking/Audio Test Analysis",
            "all": "/analyze-all-tests (POST) - Analyze Multiple Tests",
            "health": "/health (GET) - Health Check"
        }
    }

# ============ PETAL PREDICTION ENDPOINTS ============

@app.post("/predict-reading")
async def predict_reading(request: PetalPredictionRequest):
    """
    Predict reading risk based on normalized values from test1
    Input: 4 normalized values [reading_accuracy, reading_time, words_read, pronunciation_error]
    """
    try:
        if not PETAL_MODULES_AVAILABLE:
            return {"error": "Petal modules not available"}
        
        result = petal_reading.predict_read(request.values)
        return {
            "success": True,
            "test_type": "reading",
            "prediction": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test_type": "reading"
        }

@app.post("/predict-logic")
async def predict_logic(request: PetalPredictionRequest):
    """
    Predict logic risk based on normalized values from test2
    Input: 4 normalized values [logic_accuracy, logic_time, questions_ratio, logical_error]
    """
    try:
        if not PETAL_MODULES_AVAILABLE:
            return {"error": "Petal modules not available"}
        
        result = petal_logic.predict_logic(request.values)
        return {
            "success": True,
            "test_type": "logic",
            "prediction": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test_type": "logic"
        }

@app.post("/predict-writing")
async def predict_writing(request: PetalPredictionRequest):
    """
    Predict writing risk based on normalized values from test3
    Input: 4 normalized values [grammar_score, writing_time, word_count, spelling_errors]
    """
    try:
        if not PETAL_MODULES_AVAILABLE:
            return {"error": "Petal modules not available"}
        
        result = petal_writing.predict_write(request.values)
        return {
            "success": True,
            "test_type": "writing",
            "prediction": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test_type": "writing"
        }

@app.post("/predict-memory")
async def predict_memory(request: PetalPredictionRequest):
    """
    Predict memory risk based on normalized values from test4
    Input: 4 normalized values from memory test
    """
    try:
        if not PETAL_MODULES_AVAILABLE:
            return {"error": "Petal modules not available"}
        
        result = petal_memory.predict_mem(request.values)
        return {
            "success": True,
            "test_type": "memory",
            "prediction": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test_type": "memory"
        }

@app.post("/consolidated-analysis")
async def consolidated_analysis(request: ConsolidatedAnalysisRequest):
    """
    Perform consolidated analysis across all four tests
    Calls decision tree with aggregated results
    """
    try:
        if not PETAL_MODULES_AVAILABLE:
            return {"error": "Petal modules not available"}
        
        # Get predictions from all petal modules
        reading_pred = petal_reading.predict_read(request.reading_values)
        logic_pred = petal_logic.predict_logic(request.logic_values)
        writing_pred = petal_writing.predict_write(request.writing_values)
        memory_pred = petal_memory.predict_mem(request.memory_values)
        
        # Extract scores for decision tree
        decision_tree_input = {
            "reading_score": reading_pred.get("reading_score", 0),
            "logic_score": logic_pred.get("logic_score", 0),
            "writing_score": writing_pred.get("writing_score", 0),
            "memory_score": memory_pred.get("memory_score", 0),
            "reading_time": request.reading_values[1] if len(request.reading_values) > 1 else 0,
            "logic_time": request.logic_values[1] if len(request.logic_values) > 1 else 0,
            "writing_time": request.writing_values[1] if len(request.writing_values) > 1 else 0,
            "memory_time": request.memory_values[1] if len(request.memory_values) > 1 else 0
        }
        
        return {
            "success": True,
            "user_id": request.user_id,
            "test_id": request.test_id,
            "petal_predictions": {
                "reading": reading_pred,
                "logic": logic_pred,
                "writing": writing_pred,
                "memory": memory_pred
            },
            "analysis_data": decision_tree_input,
            "consolidated_scores": {
                "avg_reading": round(reading_pred.get("reading_score", 0), 2),
                "avg_logic": round(logic_pred.get("logic_score", 0), 2),
                "avg_writing": round(writing_pred.get("writing_score", 0), 2),
                "avg_memory": round(memory_pred.get("memory_score", 0), 2),
                "overall_average": round(
                    (reading_pred.get("reading_score", 0) + 
                     logic_pred.get("logic_score", 0) + 
                     writing_pred.get("writing_score", 0) + 
                     memory_pred.get("memory_score", 0)) / 4,
                    2
                )
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "user_id": request.user_id
        }

@app.post("/predict-results")
async def predict_results(data: dict = Body(...)):
    """
    Analyze test results with decision tree
    Input: test scores as percentages (0-100)
    Returns: petal analysis for flower visualization
    """
    try:
        import joblib
        import pandas as pd
        
        # Extract scores and convert to 0-1 range
        reading_score = data.get("reading_score", 50) / 100
        logic_score = data.get("logic_score", 50) / 100
        writing_score = data.get("writing_score", 50) / 100
        memory_score = data.get("memory_score", 50) / 100
        
        # Get times (default to 5000ms)
        reading_time = data.get("reading_time", 5000)
        logic_time = data.get("logic_time", 5000)
        writing_time = data.get("writing_time", 5000)
        memory_time = data.get("memory_time", 5000)
        
        # Prepare decision tree input
        dt_input = {
            "reading_score": reading_score,
            "logic_score": logic_score,
            "writing_score": writing_score,
            "memory_score": memory_score,
            "reading_time": reading_time,
            "logic_time": logic_time,
            "writing_time": writing_time,
            "memory_time": memory_time
        }
        
        # Load and run decision tree
        MODEL_PATH = "trained/decision_tree_model.pkl"
        petal_predictions = {}
        
        if os.path.exists(MODEL_PATH):
            try:
                model = joblib.load(MODEL_PATH)
                df = pd.DataFrame([dt_input])
                preds = model.predict(df)[0]
                
                petal_predictions = {
                    "dyslexia": round(float(preds[0]) * 100, 2),
                    "dyscalculia": round(float(preds[1]) * 100, 2),
                    "dysgraphia": round(float(preds[2]) * 100, 2),
                    "adhd": round(float(preds[3]) * 100, 2)
                }
            except Exception as e:
                print(f"Decision tree error: {e}")
                # Fallback to inverse scores
                petal_predictions = {
                    "dyslexia": round((1 - reading_score) * 100, 2),
                    "dyscalculia": round((1 - logic_score) * 100, 2),
                    "dysgraphia": round((1 - writing_score) * 100, 2),
                    "adhd": round((1 - memory_score) * 100, 2)
                }
        else:
            # Fallback if model not found
            petal_predictions = {
                "dyslexia": round((1 - reading_score) * 100, 2),
                "dyscalculia": round((1 - logic_score) * 100, 2),
                "dysgraphia": round((1 - writing_score) * 100, 2),
                "adhd": round((1 - memory_score) * 100, 2)
            }
        
        # Calculate overall average
        avg_score = (reading_score + logic_score + writing_score + memory_score) / 4 * 100
        
        return {
            "success": True,
            "performance_level": "🌟 Excellent" if avg_score > 75 
                               else "👍 Good" if avg_score > 50 
                               else "📚 Average" if avg_score > 25
                               else "💪 Developing",
            "overall_avg": round(avg_score, 2),
            "petals": petal_predictions
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)