"""
Lightweight version of AI Test Analysis API without heavy model dependencies
Focuses on core scoring logic
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import tempfile
import os

app = FastAPI(title="AI Test Analysis API Lite")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ DATA MODELS ============

class Test1Data(BaseModel):
    """Reading Test Data Model"""
    user_id: str
    test_id: str
    text_content: str
    words_read: int
    total_words: int
    reading_time_ms: int
    max_reading_time_ms: int
    pronunciation_errors: int

class Test2Data(BaseModel):
    """Logic Test Data Model"""
    user_id: str
    test_id: str
    questions_attempted: int
    correct_answers: int
    total_questions: int
    logic_time_ms: int
    max_logic_time_ms: int
    logical_errors: int

class Test3Data(BaseModel):
    """Grammar/Writing Test Data Model"""
    user_id: str
    test_id: str
    text_written: str
    words_written: int
    total_words: int
    writing_time_ms: int
    max_writing_time_ms: int
    spelling_errors: int

class Test4Data(BaseModel):
    """Speaking/Audio Test Data Model"""
    user_id: str
    test_id: str
    expected_text: str
    speaking_time_ms: int
    max_speaking_time_ms: int

# ============ HELPER FUNCTIONS ============

def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Normalize a score to a given range"""
    return max(min_val, min(max_val, score))

def compute_time_score(time_ms: int, max_time_ms: int, range_max: float = 10.0) -> float:
    """Compute time score (faster = higher score, max score = range_max)"""
    if max_time_ms == 0:
        return 0.0
    time_ratio = time_ms / max_time_ms
    score = range_max * (1 - time_ratio)
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
    
    - reading_accuracy: 0-1 (words_read / total_words)
    - reading_time: 0-10 (normalized time score)
    - words_read: 0-50 (words_read / total_words * 50)
    - pronunciation_error: 0-1 (pronunciation_errors / 17)
    """
    
    # 1. Reading Accuracy (0-1)
    reading_accuracy = normalize_score(
        data.words_read / data.total_words if data.total_words > 0 else 0.0,
        0.0, 1.0
    )
    
    # 2. Reading Time (0-10)
    reading_time_score = compute_time_score(data.reading_time_ms, data.max_reading_time_ms, 10.0)
    
    # 3. Words Read (0-50)
    words_read_score = compute_word_count_score(data.words_read, data.total_words)
    
    # 4. Pronunciation Error (0-1, normalized from 0-17)
    pronunciation_penalty = normalize_score(data.pronunciation_errors / 17, 0.0, 1.0)
    
    test1_results = [
        round(reading_accuracy, 2),
        round(reading_time_score, 2),
        round(words_read_score, 2),
        round(pronunciation_penalty, 2)
    ]
    
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
    
    - logic_accuracy: 0-1 (correct_answers / total_questions)
    - logic_time: 0-10 (normalized time score)
    - questions_attempted: 0-16 (questions attempted, always 16 for standard test)
    - logical_error: 0-1 (logical_errors / 20)
    """
    
    # 1. Logic Accuracy (0-1)
    logic_accuracy = normalize_score(
        data.correct_answers / data.total_questions if data.total_questions > 0 else 0.0,
        0.0, 1.0
    )
    
    # 2. Logic Time (0-10)
    logic_time_score = compute_time_score(data.logic_time_ms, data.max_logic_time_ms, 10.0)
    
    # 3. Questions Attempted (always 16 for standard test, or actual value)
    # This is the raw count, typically 16
    questions_attempted_value = min(data.questions_attempted, 16)  # Cap at 16
    
    # 4. Logical Error (0-1, normalized from 0-20)
    logical_error_penalty = normalize_score(data.logical_errors / 20, 0.0, 1.0)
    
    test2_results = [
        round(logic_accuracy, 2),
        round(logic_time_score, 2),
        round(questions_attempted_value, 2),
        round(logical_error_penalty, 2)
    ]
    
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
    
    - grammar_score: 0-1 (inverse of spelling error ratio)
    - writing_time: 0-10 (normalized time score)
    - word_count: 0-50 (words_written / total_words * 50)
    - spelling_errors: 0-1 (spelling_errors / 20)
    """
    
    # 1. Grammar Score (0-1)
    grammar_score = normalize_score(1.0 - (data.spelling_errors / 20), 0.0, 1.0)
    
    # 2. Writing Time (0-10)
    writing_time_score = compute_time_score(data.writing_time_ms, data.max_writing_time_ms, 10.0)
    
    # 3. Word Count (0-50)
    word_count_score = compute_word_count_score(data.words_written, data.total_words)
    
    # 4. Spelling Errors (0-1, normalized from 0-20)
    spelling_error_penalty = normalize_score(data.spelling_errors / 20, 0.0, 1.0)
    
    test3_results = [
        round(grammar_score, 2),
        round(writing_time_score, 2),
        round(word_count_score, 2),
        round(spelling_error_penalty, 2)
    ]
    
    return {
        "user_id": data.user_id,
        "test_id": data.test_id,
        "test_type": "grammar_writing",
        "array": test3_results
    }

@app.post("/analyze-test4")
async def analyze_test4(data: Test4Data):
    """
    Analyze Speaking Test (without audio processing in lite version)
    Returns: [speaking_accuracy, speaking_time, test_completion, audio_quality]
    """
    
    # 1. Speaking Accuracy (0-1) - placeholder in lite version
    speaking_accuracy = 0.0
    
    # 2. Speaking Time (0-10)
    speaking_time_score = compute_time_score(data.speaking_time_ms, data.max_speaking_time_ms, 10.0)
    
    # 3. Test Completion (always 1.0 if data provided)
    test_completion = 1.0
    
    # 4. Audio Quality (0-1) - placeholder in lite version
    audio_quality = 1.0
    
    test4_results = [
        round(speaking_accuracy, 2),
        round(speaking_time_score, 2),
        round(test_completion, 2),
        round(audio_quality, 2)
    ]
    
    return {
        "user_id": data.user_id,
        "test_id": data.test_id,
        "test_type": "speaking_audio",
        "array": test4_results,
        "expected_text": data.expected_text
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Test Analysis API (Lite)",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """API Information"""
    return {
        "name": "AI Test Analysis API (Lightweight Version)",
        "version": "1.0.0",
        "description": "Fast API for analyzing reading, logic, grammar/writing, and speaking tests",
        "endpoints": {
            "test1": "/analyze-test1 (POST) - Reading Test Analysis",
            "test2": "/analyze-test2 (POST) - Logic Test Analysis",
            "test3": "/analyze-test3 (POST) - Grammar/Writing Test Analysis",
            "test4": "/analyze-test4 (POST) - Speaking Test Analysis",
            "health": "/health (GET) - Health Check"
        },
        "swagger_docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
