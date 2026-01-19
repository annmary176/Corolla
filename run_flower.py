from flask import Flask, request, jsonify
import json

from petal_memory import predict_mem
from petal_logic import predict_logic
from petal_reading import predict_read
from petal_writing import predict_write

app = Flask(__name__)

# ============ PETAL PREDICTION ENDPOINTS ============

@app.route("/predict-reading", methods=["POST"])
def predict_reading_endpoint():
    """
    Predict reading risk from test1 data
    Input: JSON with array of 4 normalized values
    Returns: Petal analysis for reading
    """
    try:
        data = request.json
        test_array = data.get("array", [0, 0, 0, 0])
        
        # Call petal_reading prediction
        result = predict_read(test_array)
        
        return jsonify({
            "success": True,
            "test_type": "reading",
            "reading_score": result.get("reading_score", 0),
            "reading_risk": result.get("reading_risk", 0),
            "reading_confidence": result.get("reading_confidence", 0)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "test_type": "reading"
        }), 400

@app.route("/predict-logic", methods=["POST"])
def predict_logic_endpoint():
    """
    Predict logic risk from test2 data
    Input: JSON with array of 4 normalized values
    Returns: Petal analysis for logic
    """
    try:
        data = request.json
        test_array = data.get("array", [0, 0, 0, 0])
        
        # Call petal_logic prediction
        result = predict_logic(test_array)
        
        return jsonify({
            "success": True,
            "test_type": "logic",
            "logic_score": result.get("logic_score", 0),
            "logic_risk": result.get("logic_risk", 0),
            "logic_confidence": result.get("logic_confidence", 0)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "test_type": "logic"
        }), 400

@app.route("/predict-writing", methods=["POST"])
def predict_writing_endpoint():
    """
    Predict writing risk from test3 data
    Input: JSON with array of 4 normalized values
    Returns: Petal analysis for writing
    """
    try:
        data = request.json
        test_array = data.get("array", [0, 0, 0, 0])
        
        # Call petal_writing prediction
        result = predict_write(test_array)
        
        return jsonify({
            "success": True,
            "test_type": "writing",
            "writing_score": result.get("writing_score", 0),
            "writing_risk": result.get("writing_risk", 0),
            "writing_confidence": result.get("writing_confidence", 0)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "test_type": "writing"
        }), 400

@app.route("/predict-memory", methods=["POST"])
def predict_memory_endpoint():
    """
    Predict memory risk from test4 data
    Input: JSON with array of 4 normalized values
    Returns: Petal analysis for memory
    """
    try:
        data = request.json
        test_array = data.get("array", [0, 0, 0, 0])
        
        # Call petal_memory prediction
        result = predict_mem(test_array)
        
        return jsonify({
            "success": True,
            "test_type": "memory",
            "memory_score": result.get("memory_score", 0),
            "memory_risk": result.get("memory_risk", 0),
            "memory_confidence": result.get("memory_confidence", 0)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "test_type": "memory"
        }), 400

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Petal Analysis API"
    })

if __name__ == "__main__":
    app.run(debug=True)