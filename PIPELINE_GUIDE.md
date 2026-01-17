# Data Pipeline Guide - Corolla AI Testing System

## Overview
This document describes the complete data flow from test execution through analysis and results display.

## Data Flow Architecture

```
Test 1 (Reading)     Test 2 (Logic)      Test 3 (Writing)    Test 4 (Memory)
  ↓                    ↓                    ↓                   ↓
API /analyze-test1   API /analyze-test2  API /analyze-test3  API /analyze-test4
  ↓                    ↓                    ↓                   ↓
Normalized 4 vals    Normalized 4 vals   Normalized 4 vals   Normalized 4 vals
  ↓                    ↓                    ↓                   ↓
localStorage (testResults)
  ↓
results.html (Display + "Analyze with AI" button)
  ↓
API /consolidated-analysis
  ├→ petal_reading.predict_read() → reading_score
  ├→ petal_logic.predict_logic() → logic_score
  ├→ petal_writing.predict_write() → writing_score
  └→ petal_memory.predict_mem() → memory_score
  ↓
Display Petal Analysis Results in results.html
```

## Component Details

### 1. Test Files (test1.html - test4.html)

**Flow:**
1. Student completes test (reading, logic, writing, memory)
2. Test data sent to API endpoint (`http://localhost:8001`)
3. API returns 4 normalized values
4. Results saved to `localStorage['testResults'][testX]`
5. Redirect to next test OR to results.html if all tests complete

**API Endpoints:**
- `POST /analyze-test1` → Returns: `[reading_accuracy, reading_time, words_read, pronunciation_penalty]`
- `POST /analyze-test2` → Returns: `[logic_accuracy, logic_time, questions_ratio, logical_error_penalty]`
- `POST /analyze-test3` → Returns: `[grammar_score, writing_time, word_count, spelling_error_penalty]`
- `POST /analyze-test4` → Returns: `[speaking_accuracy, speaking_time, transcription_confidence, audio_quality]`

### 2. Results.html

**Features:**
- Displays test results from localStorage
- Shows summary statistics
- When all 4 tests complete: Shows "Analyze with AI (Petal System)" button
- Button triggers `analyzePetals()` function

**Petal Analysis Process:**
1. Extracts 4 normalized values from each test
2. Calls `POST /consolidated-analysis` with:
   ```json
   {
     "user_id": "string",
     "test_id": "string",
     "reading_values": [float, float, float, float],
     "logic_values": [float, float, float, float],
     "writing_values": [float, float, float, float],
     "memory_values": [float, float, float, float]
   }
   ```
3. Displays petal predictions with scores and risk levels

### 3. API Backend (api.py)

**New Endpoints:**

#### POST /predict-reading
- Input: 4 normalized reading values
- Calls: `petal_reading.predict_read()`
- Returns: reading_score, reading_risk, reading_confidence

#### POST /predict-logic
- Input: 4 normalized logic values
- Calls: `petal_logic.predict_logic()`
- Returns: logic_score, logic_risk, logic_confidence

#### POST /predict-writing
- Input: 4 normalized writing values
- Calls: `petal_writing.predict_write()`
- Returns: writing_score, writing_risk, writing_confidence

#### POST /predict-memory
- Input: 4 normalized memory values
- Calls: `petal_memory.predict_mem()`
- Returns: memory_score, memory_risk, memory_confidence

#### POST /consolidated-analysis
- Input: All 4 tests' normalized values
- Process:
  1. Calls all 4 petal prediction endpoints
  2. Aggregates results
  3. Calculates overall average
- Returns: All petal predictions + consolidated scores

### 4. Petal Modules

Each module (`petal_reading.py`, `petal_logic.py`, `petal_writing.py`, `petal_memory.py`):
- Takes 4 normalized values as input
- Loads trained TensorFlow model
- Performs prediction
- Returns:
  - `{test_type}_score`: 0-1 float (performance score)
  - `{test_type}_risk`: 0 or 1 (risk level)
  - `{test_type}_confidence`: 0-1 float (model confidence)

## Data Normalization

All test data is normalized to 0-1 range by `/analyze-test{N}` endpoints:

**Test 1 (Reading):**
1. `reading_accuracy`: words_read / total_words (0-1)
2. `reading_time`: normalized time score (0-10 → scaled)
3. `words_read`: (words_read / total_words) * 50 (0-50 → scaled)
4. `pronunciation_penalty`: errors / 17 (0-1)

**Test 2 (Logic):**
1. `logic_accuracy`: correct_answers / total_questions (0-1)
2. `logic_time`: normalized time score (0-10 → scaled)
3. `questions_ratio`: questions_attempted / total_questions (0-1)
4. `logical_error_penalty`: errors / 20 (0-1)

**Test 3 (Writing):**
1. `grammar_score`: 1 - (errors / 20) (0-1)
2. `writing_time`: normalized time score (0-10 → scaled)
3. `word_count`: (words_written / total_words) * 50 (0-50 → scaled)
4. `spelling_error_penalty`: errors / 20 (0-1)

**Test 4 (Memory):**
1. `speaking_accuracy`: text similarity (0-1)
2. `speaking_time`: normalized time score (0-10 → scaled)
3. `transcription_confidence`: word match ratio (0-1)
4. `audio_quality`: length ratio (0-1)

## Key Storage

### localStorage Keys:
- `testResults`: Object containing all test results
  ```js
  {
    "test1": { "type": "Reading", "array": [...], "timestamp": "..." },
    "test2": { "type": "Logic", "array": [...], "timestamp": "..." },
    "test3": { "type": "Grammar/Writing", "array": [...], "timestamp": "..." },
    "test4": { "type": "Memory", "array": [...], "timestamp": "..." }
  }
  ```

## Testing Flow

1. Start with any test file (test1.html, test2.html, etc.)
2. Complete test → API analysis → localStorage update
3. Redirect to next test or results.html
4. From results.html: View test results + click "Analyze with AI"
5. See petal predictions and risk assessments

## Requirements

- Python FastAPI server running on `http://localhost:8001`
- TensorFlow trained models in `trained/` folder:
  - `reading_model.h5`
  - `logic_model.h5`
  - `writing_model.h5`
  - `memory_model.h5`
- CSV data files in `data/` folder
- Petal module imports available in api.py

## API Configuration

**Current Port:** `8001` (configured in test*.html files)
**Main API Port:** Should match the FastAPI uvicorn port

To change API port, update:
1. All test files: `const API_URL = "http://localhost:{PORT}/analyze-test{N}"`
2. Results.html: `const API_BASE_URL = "http://localhost:{PORT}"`
3. FastAPI: `uvicorn.run(app, host="0.0.0.0", port={PORT})`

## Error Handling

- If API unavailable: Tests redirect to next test anyway
- If models missing: Fallback predictions used
- If localStorage unavailable: Tests still complete
- All errors logged to console

## Future Enhancements

1. Decision tree integration for comprehensive analysis
2. Persistent database storage instead of localStorage
3. Parent/teacher dashboard
4. Historical data tracking
5. Personalized recommendations based on risk levels
