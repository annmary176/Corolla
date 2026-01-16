#!/usr/bin/env python3
"""
Test script for AI Test Analysis API
Run this script to test all endpoints with sample data
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_response(response: requests.Response, title: str):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"Status Code: {response.status_code}")

def test_health_check():
    """Test health endpoint"""
    print("\n[1] Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check Response")
    return response.status_code == 200

def test_reading_analysis():
    """Test reading test analysis"""
    print("\n[2] Testing Reading Analysis (Test 1)...")
    
    payload = {
        "user_id": "user_001",
        "test_id": "reading_test_001",
        "text_content": "The quick brown fox jumps over the lazy dog",
        "words_read": 8,
        "total_words": 9,
        "reading_time_ms": 5000,
        "max_reading_time_ms": 10000,
        "pronunciation_errors": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze-test1",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "Reading Test Analysis Response")
    return response.status_code == 200

def test_logic_analysis():
    """Test logic test analysis"""
    print("\n[3] Testing Logic Analysis (Test 2)...")
    
    payload = {
        "user_id": "user_001",
        "test_id": "logic_test_001",
        "questions_attempted": 16,
        "correct_answers": 12,
        "total_questions": 16,
        "logic_time_ms": 8000,
        "max_logic_time_ms": 15000,
        "logical_errors": 4
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze-test2",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "Logic Test Analysis Response")
    return response.status_code == 200

def test_grammar_analysis():
    """Test grammar/writing test analysis"""
    print("\n[4] Testing Grammar/Writing Analysis (Test 3)...")
    
    payload = {
        "user_id": "user_001",
        "test_id": "writing_test_001",
        "text_written": "The cat is sitting on the mat",
        "words_written": 6,
        "total_words": 8,
        "writing_time_ms": 6000,
        "max_writing_time_ms": 12000,
        "spelling_errors": 1
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze-test3",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "Grammar/Writing Test Analysis Response")
    return response.status_code == 200

def test_speaking_analysis():
    """Test speaking/audio test analysis (without actual audio)"""
    print("\n[5] Testing Speaking Analysis (Test 4 - Without Audio)...")
    
    data = {
        "user_id": "user_001",
        "test_id": "speaking_test_001",
        "expected_text": "The quick brown fox jumps over the lazy dog",
        "speaking_time_ms": 7000,
        "max_speaking_time_ms": 15000
    }
    
    files = {
        'data': (None, json.dumps(data)),
        'audio_file': (None, None)  # No audio file provided
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze-test4",
        data={'data': json.dumps(data)}
    )
    print_response(response, "Speaking Test Analysis Response (No Audio)")
    return response.status_code == 200

def test_multiple_tests():
    """Test analyzing multiple tests at once"""
    print("\n[6] Testing Multiple Tests Analysis...")
    
    test1_data = {
        "user_id": "user_001",
        "test_id": "combo_test_001",
        "text_content": "Sample text",
        "words_read": 8,
        "total_words": 10,
        "reading_time_ms": 5000,
        "max_reading_time_ms": 10000,
        "pronunciation_errors": 2
    }
    
    test2_data = {
        "user_id": "user_001",
        "test_id": "combo_test_001",
        "questions_attempted": 16,
        "correct_answers": 13,
        "total_questions": 16,
        "logic_time_ms": 7000,
        "max_logic_time_ms": 15000,
        "logical_errors": 3
    }
    
    test3_data = {
        "user_id": "user_001",
        "test_id": "combo_test_001",
        "text_written": "Writing sample text here",
        "words_written": 4,
        "total_words": 6,
        "writing_time_ms": 6000,
        "max_writing_time_ms": 12000,
        "spelling_errors": 0
    }
    
    payload = {
        "test1_data": test1_data,
        "test2_data": test2_data,
        "test3_data": test3_data
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze-all-tests",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "Multiple Tests Analysis Response")
    return response.status_code == 200

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  AI Test Analysis API - Test Suite")
    print("="*60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Reading Analysis", test_reading_analysis),
        ("Logic Analysis", test_logic_analysis),
        ("Grammar Analysis", test_grammar_analysis),
        ("Speaking Analysis", test_speaking_analysis),
        ("Multiple Tests", test_multiple_tests),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
            time.sleep(0.5)  # Slight delay between requests
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print("-"*60)
    print(f"Total: {total_passed}/{total_tests} tests passed")
    print("="*60)

if __name__ == "__main__":
    try:
        run_all_tests()
    except ConnectionError:
        print("\n❌ Error: Could not connect to API at " + BASE_URL)
        print("   Make sure the API server is running: python api.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
