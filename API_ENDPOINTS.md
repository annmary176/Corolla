# API Endpoints Reference

## Base URL
```
http://localhost:8001
```

## Test Analysis Endpoints

### POST /analyze-test1 (Reading Test)

**Request Body:**
```json
{
  "user_id": "user_123",
  "test_id": "reading_test_1",
  "text_content": "The girl has a hat...",
  "words_read": 45,
  "total_words": 50,
  "reading_time_ms": 25000,
  "max_reading_time_ms": 30000,
  "pronunciation_errors": 3
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "test_id": "reading_test_1",
  "test_type": "reading",
  "array": [0.9, 0.83, 45.0, 0.18]
}
```

**Array Values Explanation:**
- Index 0: reading_accuracy (words_read / total_words)
- Index 1: reading_time (normalized time score)
- Index 2: words_read (raw word count, 0-50 scale)
- Index 3: pronunciation_penalty (errors / 17)

---

### POST /analyze-test2 (Logic Test)

**Request Body:**
```json
{
  "user_id": "user_123",
  "test_id": "logic_test_1",
  "questions_attempted": 10,
  "correct_answers": 8,
  "total_questions": 10,
  "logic_time_ms": 45000,
  "max_logic_time_ms": 60000,
  "logical_errors": 2
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "test_id": "logic_test_1",
  "test_type": "logic",
  "array": [0.8, 0.75, 1.0, 0.1]
}
```

**Array Values Explanation:**
- Index 0: logic_accuracy (correct_answers / total_questions)
- Index 1: logic_time (normalized time score)
- Index 2: questions_ratio (questions_attempted / total_questions)
- Index 3: logical_error_penalty (errors / 20)

---

### POST /analyze-test3 (Writing/Grammar Test)

**Request Body:**
```json
{
  "user_id": "user_123",
  "test_id": "writing_test_1",
  "text_written": "The cat is running...",
  "words_written": 42,
  "total_words": 50,
  "writing_time_ms": 35000,
  "max_writing_time_ms": 45000,
  "spelling_errors": 2
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "test_id": "writing_test_1",
  "test_type": "grammar_writing",
  "array": [0.9, 0.78, 42.0, 0.1]
}
```

**Array Values Explanation:**
- Index 0: grammar_score (1 - errors/20)
- Index 1: writing_time (normalized time score)
- Index 2: word_count (raw word count, 0-50 scale)
- Index 3: spelling_error_penalty (errors / 20)

---

### POST /analyze-test4 (Speaking/Audio Test)

**Request Body (multipart/form-data):**
```
form_data: {
  "data": '{"user_id":"user_123","test_id":"speaking_test_1",...}',
  "audio_file": <binary audio data>
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "test_id": "speaking_test_1",
  "test_type": "speaking_audio",
  "array": [0.87, 0.82, 0.85, 0.89],
  "transcribed_text": "The quick brown fox",
  "expected_text": "The quick brown fox"
}
```

**Array Values Explanation:**
- Index 0: speaking_accuracy (text similarity cosine)
- Index 1: speaking_time (normalized time score)
- Index 2: transcription_confidence (word match ratio)
- Index 3: audio_quality (length ratio)

---

## Petal Prediction Endpoints

### POST /predict-reading

**Purpose:** Get reading risk prediction from normalized values

**Request Body:**
```json
{
  "values": [0.9, 0.83, 45.0, 0.18]
}
```

**Response:**
```json
{
  "success": true,
  "test_type": "reading",
  "prediction": {
    "reading_score": 0.85,
    "reading_risk": 0,
    "reading_confidence": 0.92
  }
}
```

---

### POST /predict-logic

**Purpose:** Get logic risk prediction from normalized values

**Request Body:**
```json
{
  "values": [0.8, 0.75, 1.0, 0.1]
}
```

**Response:**
```json
{
  "success": true,
  "test_type": "logic",
  "prediction": {
    "logic_score": 0.78,
    "logic_risk": 0,
    "logic_confidence": 0.88
  }
}
```

---

### POST /predict-writing

**Purpose:** Get writing risk prediction from normalized values

**Request Body:**
```json
{
  "values": [0.9, 0.78, 42.0, 0.1]
}
```

**Response:**
```json
{
  "success": true,
  "test_type": "writing",
  "prediction": {
    "writing_score": 0.82,
    "writing_risk": 0,
    "writing_confidence": 0.94
  }
}
```

---

### POST /predict-memory

**Purpose:** Get memory risk prediction from normalized values

**Request Body:**
```json
{
  "values": [0.92, 0.70, 0.89, 0.85]
}
```

**Response:**
```json
{
  "success": true,
  "test_type": "memory",
  "prediction": {
    "memory_score": 0.84,
    "memory_risk": 0,
    "memory_confidence": 0.90
  }
}
```

---

## Consolidated Analysis Endpoint

### POST /consolidated-analysis

**Purpose:** Analyze all 4 tests together and get comprehensive results

**Request Body:**
```json
{
  "user_id": "student_001",
  "test_id": "batch_001",
  "reading_values": [0.9, 0.83, 45.0, 0.18],
  "logic_values": [0.8, 0.75, 1.0, 0.1],
  "writing_values": [0.9, 0.78, 42.0, 0.1],
  "memory_values": [0.92, 0.70, 0.89, 0.85]
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "student_001",
  "test_id": "batch_001",
  "petal_predictions": {
    "reading": {
      "reading_score": 0.85,
      "reading_risk": 0,
      "reading_confidence": 0.92
    },
    "logic": {
      "logic_score": 0.78,
      "logic_risk": 0,
      "logic_confidence": 0.88
    },
    "writing": {
      "writing_score": 0.82,
      "writing_risk": 0,
      "writing_confidence": 0.94
    },
    "memory": {
      "memory_score": 0.84,
      "memory_risk": 0,
      "memory_confidence": 0.90
    }
  },
  "analysis_data": {
    "reading_score": 0.85,
    "logic_score": 0.78,
    "writing_score": 0.82,
    "memory_score": 0.84,
    "reading_time": 0.83,
    "logic_time": 0.75,
    "writing_time": 0.78,
    "memory_time": 0.70
  },
  "consolidated_scores": {
    "avg_reading": 0.85,
    "avg_logic": 0.78,
    "avg_writing": 0.82,
    "avg_memory": 0.84,
    "overall_average": 0.82
  }
}
```

---

## Utility Endpoints

### GET /

**Purpose:** Get API information

**Response:**
```json
{
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
```

---

### GET /health

**Purpose:** Check API server health

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Test Analysis API",
  "version": "1.0.0"
}
```

---

## Data Models (Pydantic)

### PetalPredictionRequest
```python
{
  "values": List[float]  # 4 normalized values
}
```

### ConsolidatedAnalysisRequest
```python
{
  "user_id": str,
  "test_id": str,
  "reading_values": List[float],  # 4 values
  "logic_values": List[float],    # 4 values
  "writing_values": List[float],  # 4 values
  "memory_values": List[float]    # 4 values
}
```

---

## Error Handling

### Missing Models
If trained models are missing:

**Response:**
```json
{
  "success": false,
  "error": "Petal modules not available",
  "test_type": "reading"
}
```

### Validation Error
If request body is invalid:

**Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "values"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 422 | Unprocessable Entity (wrong data types) |
| 500 | Server Error (API crashed) |

---

## Example cURL Commands

### Test Reading Analysis
```bash
curl -X POST http://localhost:8001/analyze-test1 \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "test_id": "reading_test_1",
    "text_content": "The girl has a hat",
    "words_read": 5,
    "total_words": 5,
    "reading_time_ms": 5000,
    "max_reading_time_ms": 10000,
    "pronunciation_errors": 0
  }'
```

### Test Consolidated Analysis
```bash
curl -X POST http://localhost:8001/consolidated-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student_001",
    "test_id": "batch_001",
    "reading_values": [0.9, 0.83, 45.0, 0.18],
    "logic_values": [0.8, 0.75, 1.0, 0.1],
    "writing_values": [0.9, 0.78, 42.0, 0.1],
    "memory_values": [0.92, 0.70, 0.89, 0.85]
  }'
```

---

## Integration Notes

1. All endpoints expect JSON input (except test4 which takes multipart)
2. All responses include success status or error message
3. Normalized values are always 0-1 float (except some 0-50 for counts)
4. Risk values: 0 = Low Risk, 1 = High Risk
5. Confidence values: 0-1 float representing model certainty
6. CORS is enabled for all origins
7. No authentication required (add if needed for production)

---

## Performance Notes

- Average response time: 100-500ms
- Cold start (first request): 2-5 seconds
- Model loading: ~30 seconds on first run
- Subsequent requests: ~200-300ms

---

## Future Enhancements

1. Add `/decision-tree-analysis` endpoint for disorder prediction
2. Add `/generate-report` for PDF report generation
3. Add `/save-results` for database persistence
4. Add authentication/authorization
5. Add rate limiting
6. Add input validation for data ranges
