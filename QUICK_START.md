# Quick Start Guide - Complete Data Pipeline

## What Was Implemented

Your complete data pipeline is now ready! Here's what connects:

```
Test 1 (Reading)  ➜ API Normalize ➜ localStorage
Test 2 (Logic)    ➜ API Normalize ➜ localStorage  
Test 3 (Writing)  ➜ API Normalize ➜ localStorage
Test 4 (Memory)   ➜ API Normalize ➜ localStorage
                       ⬇️
                   results.html
                   (Display results)
                       ⬇️
                   "Analyze with AI" button
                       ⬇️
           API /consolidated-analysis
                       ⬇️
    petal_reading.py → reading_score
    petal_logic.py → logic_score
    petal_writing.py → writing_score
    petal_memory.py → memory_score
                       ⬇️
        Display Petal Analysis in results.html
```

## Steps to Run

### 1. Start the API Server

Open a terminal and run:

```bash
# Navigate to project folder
cd C:\Users\asus\YoungAI\Corolla

# Activate virtual environment (if needed)
.venv\Scripts\Activate.ps1

# Start the API server on port 8001
python api.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### 2. Open Test Portal

Navigate to one of these in your browser:
- http://localhost:8001/test1.html (Reading Test)
- http://localhost:8001/test2.html (Logic Test)
- http://localhost:8001/test3.html (Writing Test)
- http://localhost:8001/test4.html (Memory Test)

**OR start from test1.html which will auto-route through all tests**

### 3. Complete All 4 Tests

Each test will:
1. Display questions/tasks
2. Collect student responses
3. Send to API for analysis
4. Receive normalized 4-value array
5. Auto-redirect to next test
6. Save results to browser's localStorage

### 4. View Results

After completing all 4 tests, you'll be redirected to:
- **http://localhost:8001/results.html**

Here you can:
- View individual test scores
- See performance summary
- Click "🧠 Analyze with AI (Petal System)" button

### 5. Run Petal Analysis

When you click the "Analyze with AI" button:

1. **Frontend** extracts 4 normalized values from each test
2. **Calls API** `/consolidated-analysis` endpoint
3. **API processes:**
   - Calls `petal_reading.predict_read()` 
   - Calls `petal_logic.predict_logic()`
   - Calls `petal_writing.predict_write()`
   - Calls `petal_memory.predict_mem()`
4. **Returns results:**
   - Each petal's score (0-100%)
   - Risk level (High/Low)
   - Model confidence
   - Overall average performance

### 6. View Analysis Results

Results display in results.html showing:
```
📖 Reading Analysis
Score: 75.3%
Risk Level: ✅ Low Risk
Confidence: 92.1%

🧩 Logic Analysis
Score: 68.9%
Risk Level: ⚠️ High Risk
Confidence: 87.4%

✍️ Writing Analysis
Score: 81.2%
Risk Level: ✅ Low Risk
Confidence: 94.0%

🧠 Memory Analysis
Score: 72.5%
Risk Level: ✅ Low Risk
Confidence: 89.6%

📊 Overall Assessment
Average Score: 74.5%
Performance: 👍 Good
```

## Data Flow Details

### Test → API Normalization

**Test 1 (Reading)** produces 4 values:
```json
{
  "array": [
    0.85,  // reading_accuracy (words_read / total_words)
    0.72,  // reading_time (time efficiency score)
    25.5,  // words_read (normalized count)
    0.12   // pronunciation_penalty (errors / 17)
  ]
}
```

**Test 2 (Logic)** produces 4 values:
```json
{
  "array": [
    0.80,  // logic_accuracy (correct / total)
    0.68,  // logic_time (time efficiency)
    0.95,  // questions_ratio (attempted / total)
    0.20   // logical_error_penalty (errors / 20)
  ]
}
```

**Test 3 (Writing)** produces 4 values:
```json
{
  "array": [
    0.88,  // grammar_score (1 - errors/20)
    0.75,  // writing_time (time efficiency)
    18.5,  // word_count (normalized)
    0.15   // spelling_error_penalty (errors / 20)
  ]
}
```

**Test 4 (Memory)** produces 4 values:
```json
{
  "array": [
    0.92,  // speaking_accuracy (text similarity)
    0.70,  // speaking_time (time efficiency)
    0.89,  // transcription_confidence (word match)
    0.85   // audio_quality (length ratio)
  ]
}
```

### Storage in localStorage

After each test, localStorage['testResults'] is updated:

```javascript
{
  "test1": {
    "type": "Reading",
    "array": [0.85, 0.72, 25.5, 0.12],
    "timestamp": "2026-01-17T..."
  },
  "test2": {
    "type": "Logic",
    "array": [0.80, 0.68, 0.95, 0.20],
    "timestamp": "2026-01-17T..."
  },
  "test3": {
    "type": "Grammar/Writing",
    "array": [0.88, 0.75, 18.5, 0.15],
    "timestamp": "2026-01-17T..."
  },
  "test4": {
    "type": "Memory",
    "array": [0.92, 0.70, 0.89, 0.85],
    "timestamp": "2026-01-17T..."
  }
}
```

### Analysis Request

results.html sends to `/consolidated-analysis`:

```json
POST http://localhost:8001/consolidated-analysis
{
  "user_id": "student_001",
  "test_id": "batch_001",
  "reading_values": [0.85, 0.72, 25.5, 0.12],
  "logic_values": [0.80, 0.68, 0.95, 0.20],
  "writing_values": [0.88, 0.75, 18.5, 0.15],
  "memory_values": [0.92, 0.70, 0.89, 0.85]
}
```

### Analysis Response

API returns:

```json
{
  "success": true,
  "user_id": "student_001",
  "test_id": "batch_001",
  "petal_predictions": {
    "reading": {
      "reading_score": 0.753,
      "reading_risk": 0,
      "reading_confidence": 0.921
    },
    "logic": {
      "logic_score": 0.689,
      "logic_risk": 1,
      "logic_confidence": 0.874
    },
    "writing": {
      "writing_score": 0.812,
      "writing_risk": 0,
      "writing_confidence": 0.940
    },
    "memory": {
      "memory_score": 0.725,
      "memory_risk": 0,
      "memory_confidence": 0.896
    }
  },
  "consolidated_scores": {
    "avg_reading": 0.753,
    "avg_logic": 0.689,
    "avg_writing": 0.812,
    "avg_memory": 0.725,
    "overall_average": 0.745
  }
}
```

## Troubleshooting

### "Connection refused" error
- Check that API server is running (`python api.py`)
- Verify it's running on port 8001
- Check firewall isn't blocking the port

### "Module not found" error
- Make sure you're in the correct directory
- Verify petal_*.py files exist
- Check trained models in trained/ folder

### Results not saving
- Open browser console (F12)
- Check for JavaScript errors
- Verify localStorage is enabled

### Petal analysis fails
- Check console for API errors
- Verify all trained models exist:
  - trained/reading_model.h5
  - trained/logic_model.h5
  - trained/writing_model.h5
  - trained/memory_model.h5
- Check model files aren't corrupted

## Next Steps

1. **Test the pipeline:**
   - Run through all 4 tests
   - Check results display correctly
   - Run petal analysis

2. **Verify data:**
   - Check browser's Application > localStorage
   - Verify array values match test performance
   - Check API responses in Network tab

3. **Integrate decision tree:**
   - Edit `/consolidated-analysis` endpoint
   - Add decision tree prediction
   - Return additional diagnosis info

4. **Database integration:**
   - Replace localStorage with database
   - Store historical results
   - Enable parent dashboard access

## Key Files Modified

- **api.py**: Added 4 petal endpoints + consolidated-analysis
- **results.html**: Added Petal Analysis UI + API integration
- **test1.html-test4.html**: Updated to check all tests before routing
- **PIPELINE_GUIDE.md**: Complete technical documentation
- **API_PORT_CONFIG.md**: Port configuration guide

## Success Indicators

✅ Test completes → Normalized data stored in localStorage
✅ Results.html shows test scores
✅ "Analyze with AI" button appears when all 4 tests done
✅ Click button → Petal analysis displays
✅ Each petal shows score, risk level, confidence

You're all set! Run `python api.py` and start testing! 🚀
