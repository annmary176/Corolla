# AI Test Analysis API

A FastAPI-based service for analyzing multiple types of assessment tests including reading, logic, grammar/writing, and speaking tests with AI-powered scoring.

## Features

- **Test 1 - Reading Analysis**: Evaluates reading accuracy, speed, word count, and pronunciation
- **Test 2 - Logic Analysis**: Assesses logical reasoning, time efficiency, and error detection
- **Test 3 - Grammar/Writing Analysis**: Analyzes grammar, writing speed, word count, and spelling
- **Test 4 - Speaking/Audio Analysis**: Uses Whisper AI for transcription and semantic similarity analysis
- **Consolidated Analysis**: Analyze multiple tests in a single request

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python api.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Test 1 - Reading Analysis

**Endpoint**: `POST /analyze-test1`

**Request Body**:
```json
{
  "user_id": "user123",
  "test_id": "test_001",
  "text_content": "The quick brown fox jumps over the lazy dog",
  "words_read": 8,
  "total_words": 9,
  "reading_time_ms": 5000,
  "max_reading_time_ms": 10000,
  "pronunciation_errors": 2
}
```

**Response**:
```json
{
  "user_id": "user123",
  "test_id": "test_001",
  "test_type": "reading",
  "results": [
    0.89,  // reading_accuracy (0-1)
    0.5,   // reading_time_score (0-10)
    0.45,  // words_read_score (0-50)
    0.12   // pronunciation_error_penalty (0-17)
  ],
  "metrics": {
    "reading_accuracy": 0.89,
    "reading_time_score": 0.5,
    "words_read_score": 0.45,
    "pronunciation_error_penalty": 0.12
  }
}
```

### 2. Test 2 - Logic Analysis

**Endpoint**: `POST /analyze-test2`

**Request Body**:
```json
{
  "user_id": "user123",
  "test_id": "test_002",
  "questions_attempted": 16,
  "correct_answers": 12,
  "total_questions": 16,
  "logic_time_ms": 8000,
  "max_logic_time_ms": 15000,
  "logical_errors": 4
}
```

**Response**:
```json
{
  "user_id": "user123",
  "test_id": "test_002",
  "test_type": "logic",
  "results": [
    0.75,  // logic_accuracy (0-1)
    0.47,  // logic_time_score (0-10)
    1.0,   // questions_attempted_ratio (0-1)
    0.2    // logical_error_penalty (0-20)
  ],
  "metrics": {
    "logic_accuracy": 0.75,
    "logic_time_score": 0.47,
    "questions_attempted_ratio": 1.0,
    "logical_error_penalty": 0.2
  }
}
```

### 3. Test 3 - Grammar/Writing Analysis

**Endpoint**: `POST /analyze-test3`

**Request Body**:
```json
{
  "user_id": "user123",
  "test_id": "test_003",
  "text_written": "The cat is sitting on the mat",
  "words_written": 6,
  "total_words": 8,
  "writing_time_ms": 6000,
  "max_writing_time_ms": 12000,
  "spelling_errors": 1
}
```

**Response**:
```json
{
  "user_id": "user123",
  "test_id": "test_003",
  "test_type": "grammar_writing",
  "results": [
    0.95,  // grammar_score (0-1)
    0.5,   // writing_time_score (0-10)
    0.38,  // word_count_score (0-50)
    0.05   // spelling_error_penalty (0-20)
  ],
  "metrics": {
    "grammar_score": 0.95,
    "writing_time_score": 0.5,
    "word_count_score": 0.38,
    "spelling_error_penalty": 0.05
  }
}
```

### 4. Test 4 - Speaking/Audio Analysis

**Endpoint**: `POST /analyze-test4`

**Request Format**: `multipart/form-data`

**Form Fields**:
- `data` (string): JSON with test metadata
- `audio_file` (file): MP3/WAV audio file

**Data JSON Structure**:
```json
{
  "user_id": "user123",
  "test_id": "test_004",
  "expected_text": "The quick brown fox jumps over the lazy dog",
  "speaking_time_ms": 7000,
  "max_speaking_time_ms": 15000
}
```

**Response**:
```json
{
  "user_id": "user123",
  "test_id": "test_004",
  "test_type": "speaking_audio",
  "results": [
    0.87,  // speaking_accuracy (0-1)
    0.53,  // speaking_time_score (0-10)
    0.89,  // transcription_confidence (0-1)
    0.88   // audio_quality (0-1)
  ],
  "transcribed_text": "The quick brown fox jumps over the lazy dog",
  "expected_text": "The quick brown fox jumps over the lazy dog",
  "metrics": {
    "speaking_accuracy": 0.87,
    "speaking_time_score": 0.53,
    "transcription_confidence": 0.89,
    "audio_quality": 0.88
  }
}
```

### 5. Analyze All Tests

**Endpoint**: `POST /analyze-all-tests`

Combines multiple test analyses in a single request.

## Scoring Ranges

| Test | Metric 1 | Metric 2 | Metric 3 | Metric 4 |
|------|----------|----------|----------|----------|
| Test 1 (Reading) | Accuracy (0-1) | Time (0-10) | Words (0-50) | Pronunciation (0-17) |
| Test 2 (Logic) | Accuracy (0-1) | Time (0-10) | Attempted (0-1) | Logical Error (0-20) |
| Test 3 (Grammar) | Score (0-1) | Time (0-10) | Words (0-50) | Spelling (0-20) |
| Test 4 (Speaking) | Accuracy (0-1) | Time (0-10) | Confidence (0-1) | Quality (0-1) |

## Example Usage with cURL

### Test 1 - Reading
```bash
curl -X POST "http://localhost:8000/analyze-test1" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "test_id": "test_001",
    "text_content": "Sample text",
    "words_read": 8,
    "total_words": 10,
    "reading_time_ms": 5000,
    "max_reading_time_ms": 10000,
    "pronunciation_errors": 2
  }'
```

### Test 4 - Speaking (with audio)
```bash
curl -X POST "http://localhost:8000/analyze-test4" \
  -F "data={\"user_id\":\"user123\",\"test_id\":\"test_004\",\"expected_text\":\"Hello world\",\"speaking_time_ms\":3000,\"max_speaking_time_ms\":10000}" \
  -F "audio_file=@/path/to/audio.wav"
```

## Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .

CMD ["python", "api.py"]
```

Build and run:
```bash
docker build -t ai-test-api .
docker run -p 8000:8000 ai-test-api
```

## Dependencies

- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI web server
- **Pydantic**: Data validation using Python type annotations
- **Sentence Transformers**: For semantic similarity analysis
- **Faster Whisper**: Speech-to-text AI model
- **PyTorch**: Deep learning framework

## Notes

- Ensure audio files are in supported formats (WAV, MP3)
- The Whisper model requires significant RAM on first load
- Pronunciation errors should be counted and passed to the API
- All time values should be in milliseconds
- Error counts should be normalized to their respective ranges

## License

MIT
