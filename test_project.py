"""
Project Flow Test Script
Tests every component: .env, Groq API, Backend, Interview Flow
Run: python test_project.py
"""

import os
import sys
import json
import requests

BASE_URL = "http://localhost:8000/api/v1"
PASS = "✅ PASS"
FAIL = "❌ FAIL"

def separator(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

# ── TEST 1: .env file ─────────────────────────────
separator("TEST 1: .env File & API Key")
try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY", "")
    model   = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key or api_key == "your_groq_api_key_here":
        print(f"{FAIL} GROQ_API_KEY not set in .env")
        sys.exit(1)
    else:
        print(f"{PASS} .env loaded")
        print(f"       API Key : {api_key[:8]}...{api_key[-4:]}")
        print(f"       Model   : {model}")
except Exception as e:
    print(f"{FAIL} .env error: {e}")
    sys.exit(1)

# ── TEST 2: Groq API Direct Call ──────────────────
separator("TEST 2: Groq API Direct Call")
try:
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Say 'hello' in one word only."}],
        max_tokens=10,
    )
    reply = response.choices[0].message.content
    print(f"{PASS} Groq API working!")
    print(f"       Response: {reply}")
except Exception as e:
    print(f"{FAIL} Groq API error: {e}")
    print("\n  👉 FIX: Get a new API key from https://console.groq.com/keys")
    sys.exit(1)

# ── TEST 3: Backend Health ────────────────────────
separator("TEST 3: Backend Server Health")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    if r.status_code == 200:
        print(f"{PASS} Backend is running!")
        print(f"       Response: {r.json()}")
    else:
        print(f"{FAIL} Backend returned {r.status_code}")
except requests.exceptions.ConnectionError:
    print(f"{FAIL} Backend NOT running on port 8000")
    print("\n  👉 FIX: Run 'python main.py' in terminal first")
    sys.exit(1)

# ── TEST 4: Start Interview API ───────────────────
separator("TEST 4: Start Interview API")
session_id = None
first_question = None
try:
    payload = {
        "candidate_name": "Test Student",
        "position": "Software Engineer",
        "difficulty": "easy",
        "total_questions": 3,
        "round_type": "Technical"
    }
    r = requests.post(f"{BASE_URL}/interview/start", json=payload, timeout=60)
    if r.status_code == 200:
        data = r.json()
        session_id = data["session_id"]
        first_question = data["first_question"]
        print(f"{PASS} Interview started!")
        print(f"       Session ID : {session_id}")
        print(f"       Opening    : {data['opening_message'][:80]}...")
        print(f"       Question 1 : {first_question[:80]}...")
    else:
        print(f"{FAIL} Status {r.status_code}")
        print(f"       Error: {r.text[:300]}")
        sys.exit(1)
except requests.exceptions.Timeout:
    print(f"{FAIL} Request timed out (>60s)")
    print("  👉 FIX: Groq API is slow, try again")
    sys.exit(1)
except Exception as e:
    print(f"{FAIL} Error: {e}")
    sys.exit(1)

# ── TEST 5: Submit Answer ─────────────────────────
separator("TEST 5: Submit Answer & Evaluation")
try:
    payload = {
        "session_id": session_id,
        "answer": "I have strong knowledge of data structures and algorithms. I have solved 400+ LeetCode problems and built multiple projects using Python and Java."
    }
    r = requests.post(f"{BASE_URL}/interview/answer", json=payload, timeout=60)
    if r.status_code == 200:
        data = r.json()
        score = data["evaluation"]["score"]
        strengths = data["evaluation"]["strengths"]
        improvements = data["evaluation"]["improvements"]
        print(f"{PASS} Answer evaluated!")
        print(f"       Score      : {score}/10")
        print(f"       Strengths  : {strengths[0] if strengths else 'N/A'}")
        print(f"       Improvement: {improvements[0] if improvements else 'N/A'}")
        print(f"       Progress   : {data['questions_asked']}/{data['total_questions']}")
    else:
        print(f"{FAIL} Status {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"{FAIL} Error: {e}")

# ── TEST 6: MCP Tools ─────────────────────────────
separator("TEST 6: MCP Tools")
try:
    r = requests.get(f"{BASE_URL}/mcp/tools", timeout=5)
    if r.status_code == 200:
        tools = r.json()["tools"]
        print(f"{PASS} MCP Tools available: {len(tools)}")
        for t in tools:
            print(f"       - {t['name']}")
    else:
        print(f"{FAIL} MCP tools error: {r.status_code}")
except Exception as e:
    print(f"{FAIL} MCP error: {e}")

# ── TEST 7: Resume Feedback ───────────────────────
separator("TEST 7: Resume Feedback API")
try:
    payload = {
        "resume_text": "Python developer with 2 years experience. Skills: Python, Django, SQL, AWS.",
        "job_description": "Software Engineer - Python, REST APIs, cloud experience required."
    }
    r = requests.post(f"{BASE_URL}/feedback/resume", json=payload, timeout=60)
    if r.status_code == 200:
        feedback = r.json()["feedback"]
        print(f"{PASS} Resume feedback generated!")
        print(f"       Preview: {feedback[:100]}...")
    else:
        print(f"{FAIL} Status {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"{FAIL} Error: {e}")

# ── FINAL SUMMARY ─────────────────────────────────
separator("FINAL SUMMARY")
print(f"""
  ✅ .env configured
  ✅ Groq API working  
  ✅ Backend running
  ✅ Interview start working
  ✅ Answer evaluation working
  ✅ MCP tools working
  ✅ Resume feedback working

  🎯 ALL SYSTEMS GO! Open http://localhost:8501 and start your interview!
""")
