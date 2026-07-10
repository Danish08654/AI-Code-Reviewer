# AI Code Reviewer

An AI-powered code review system that analyzes code for bugs, security issues, performance problems, and best practices using FastAPI + Groq Llama 3 + Streamlit UI.

---

# Features

 AI-powered code review

🐞 Bug detection

🔐 Security vulnerability analysis

⚡ Performance improvement suggestions

🧼 Code quality & best practices review

📄 Supports pasted code + file upload

🧠 Structured JSON-based AI responses

🎯 Clean and interactive Streamlit dashboard

---

# Tech Stack

Backend: FastAPI

AI Model: Groq (Llama 3)

Frontend: Streamlit

Language: Python 3.10+

Parsing: JSON + Regex safe extraction

API Communication: REST (requests)

# How It Works

User pastes or uploads code

Streamlit sends code to FastAPI

FastAPI sends code to LLM (Groq Llama 3)

AI returns structured JSON review

Backend parses and normalizes output

Frontend displays:

---

# Summary

Critical Issues

Medium Issues

Suggestions

Final Verdict

# Example Output

Input: def add(a, b): return a + b

# Output:

No critical issues

Suggests adding type hints

Suggests validation for production use

Verdict: NEEDS_CHANGES

----


# Future Improvements

GitHub PR integration

Multi-file repository review

Code diff visualization

Authentication system

History tracking (database)

AI auto-fix suggestions

CI/CD pipeline integration

---

# Author

Danish Zulfiqar

----
