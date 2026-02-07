#!/usr/bin/env python3
"""
Test script for CurricuForge backend endpoints.
Run this after starting the FastAPI server to validate Gemini and Hugging Face integration.
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test the /health endpoint"""
    print("\n=== Testing /health ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_home():
    """Test the / endpoint"""
    print("\n=== Testing / ===")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_generate_curriculum():
    """Test the /generate endpoint (requires GEMINI_API_KEY)"""
    print("\n=== Testing /generate (Gemini) ===")
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ Skipped: GEMINI_API_KEY not set in .env")
        return
    
    try:
        payload = {
            "courseTitle": "Introduction to Python",
            "courseLevel": "Beginner",
            "duration": "8 weeks",
            "audience": "High school students",
            "requirements": "Basic computer literacy",
            "description": "A foundational course in Python programming basics"
        }
        response = requests.post(f"{BASE_URL}/generate", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        result = response.json()
        if "output" in result:
            print(f"Response (first 300 chars): {result['output'][:300]}...")
        else:
            print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_huggingface_summarize():
    """Test the /huggingface/summarize endpoint"""
    print("\n=== Testing /huggingface/summarize ===")
    
    try:
        sample_text = (
            "Python is a high-level, interpreted programming language known for its simplicity and readability. "
            "It supports multiple programming paradigms including procedural, object-oriented, and functional programming. "
            "Python is widely used in web development, data science, machine learning, and automation. "
            "Its large standard library and extensive ecosystem of third-party packages make it a popular choice for developers. "
            "The language emphasizes code readability and reduces the cost of program maintenance."
        )
        
        payload = {
            "text": sample_text,
            "max_length": 100,
            "min_length": 30
        }
        
        response = requests.post(f"{BASE_URL}/huggingface/summarize", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("CurricuForge Backend Test Suite")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print("Make sure the server is running: uvicorn main:app --reload")
    
    # Run tests
    test_home()
    test_health()
    test_generate_curriculum()
    test_huggingface_summarize()
    
    print("\n" + "=" * 50)
    print("Test suite complete!")
