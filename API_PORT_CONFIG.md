# API Port Configuration

## Issue Found
- **API Server Port:** 8000 (from api.py line 578)
- **Test Files Port:** 8001 (configured in test1.html-test4.html)
- **Results.html Port:** 8000 (configured in results.html)

## IMPORTANT: Port Alignment

You have two options:

### Option 1: Change API to Port 8001 (Recommended for existing test files)

Edit **api.py** (last line):
```python
# Change from:
uvicorn.run(app, host="0.0.0.0", port=8000)

# To:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Option 2: Change Test Files to Port 8000

Edit all test files:
- test1.html
- test2.html
- test3.html
- test4.html

Change:
```javascript
// From:
const API_URL = "http://localhost:8001/analyze-test1";

// To:
const API_URL = "http://localhost:8000/analyze-test1";
```

Also update results.html (line ~117):
```javascript
// From:
const API_BASE_URL = "http://localhost:8000";

// To:
const API_BASE_URL = "http://localhost:8001";
```

## How to Run

### Start the API Server

Using the existing port 8000:
```bash
python api.py
# or
cd C:\Users\asus\YoungAI\Corolla
.venv\Scripts\python.exe api.py
```

### Access Tests

1. Open http://localhost:8000/test1.html
2. Complete all 4 tests
3. View results at http://localhost:8000/results.html
4. Click "Analyze with AI (Petal System)" to run analysis

## Verification

After applying one of the options above:

1. Check that test files and API are using same port
2. Start API server
3. Run test1.html
4. Check browser console (F12) for any fetch errors
5. If successful, you'll see API response in console

## Troubleshooting

**Error: "Failed to fetch from API"**
- Check that API server is running
- Verify ports match between HTML files and api.py
- Check CORS settings (currently no CORS restrictions)

**Error: "Petal modules not available"**
- Make sure petal_reading.py, petal_logic.py, petal_writing.py, petal_memory.py exist
- Check trained models exist in trained/ folder
- Check all imports in api.py are correct
