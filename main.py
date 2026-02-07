from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
from google import genai
from transformers import pipeline

"""
Backend for CurricuForge.

Integrations:
- Gemini (Google) for curriculum generation (requires GEMINI_API_KEY)
- Hugging Face (local) for text summarization and curriculum generation (no token needed)
"""

# Load environment variables
load_dotenv()

# API keys / URLs from environment (optional)
API_KEY = os.getenv("GEMINI_API_KEY")   # Gemini
HF_API_KEY = os.getenv("HF_API_KEY")    # Optional, only for Hugging Face cloud inference
IBM_API_KEY = os.getenv("IBM_API_KEY")  # IBM watsonx / Watson NLU
IBM_API_URL = os.getenv("IBM_API_URL")  # Endpoint URL for IBM text generation

if not API_KEY:
    print("⚠️ Warning: GEMINI_API_KEY not found. Gemini endpoint will fail.")

# ---------------- Hugging Face Local Pipelines ----------------

# 1) Text summarization (local BART model)
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print(f"⚠️ Warning: Could not load local Hugging Face summarizer - {e}")
    summarizer = None

"""
NOTE: For curriculum generation we now use a lightweight, rule-based text generator
instead of a heavy Hugging Face model, so it works on any machine with no tokens
and no model downloads.
"""

# If local summarizer not available, we can use the Hugging Face Inference API when HF_API_KEY is set
hf_inference_available = bool(HF_API_KEY)

# Gemini Client - moved inside function to avoid startup failure
# client = genai.Client(api_key=API_KEY)

app = FastAPI()

# CORS Fix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input Models
class CurriculumRequest(BaseModel):
    courseTitle: str
    courseLevel: str
    duration: str
    audience: str
    requirements: str
    description: str


class HFCurriculumRequest(BaseModel):
    """
    Same fields as CurriculumRequest, but routed to local Hugging Face instead of Gemini.
    """
    courseTitle: str
    courseLevel: str
    duration: str
    audience: str
    requirements: str
    description: str


def build_template_curriculum(req: HFCurriculumRequest) -> str:
    """
    Lightweight, rule-based curriculum generator (no ML, no tokens).
    This ensures the backend works everywhere, even without Hugging Face models.
    """
    title = req.courseTitle or "Untitled Course"
    level = req.courseLevel or "General"
    duration = req.duration or "4 weeks"
    audience = req.audience or "Learners"
    requirements = req.requirements or "No specific prerequisites"
    description = req.description or "Course overview not provided."

    weeks = 4
    # Try to extract number from duration like "8 weeks"
    for part in duration.split():
        if part.isdigit():
            weeks = max(1, min(12, int(part)))
            break

    lines = []
    lines.append(f"=== Course: {title} ===")
    lines.append(f"Level: {level}")
    lines.append(f"Duration: {duration}")
    lines.append(f"Target Audience: {audience}")
    lines.append("")
    lines.append("1. Course Overview")
    lines.append("------------------")
    lines.append(description)
    lines.append("")
    lines.append("2. Course Objectives")
    lines.append("--------------------")
    lines.append(f"- Build a strong foundation in {title}.")
    lines.append(f"- Apply {title} concepts to practical, real-world problems.")
    lines.append("- Develop confidence through hands-on activities and projects.")
    lines.append("")
    lines.append("3. Weekly Topic Plan")
    lines.append("--------------------")

    for i in range(1, weeks + 1):
        lines.append(f"Week {i}: Core Concepts and Practice")
        lines.append(f"- Introduce key ideas related to {title} suitable for {level} learners.")
        lines.append(f"- Guided examples tailored for {audience}.")
        lines.append("- Short practical exercises and reflections.")
        lines.append("")

    lines.append("4. Learning Outcomes (per week)")
    lines.append("--------------------------------")
    lines.append(f"- Explain the main ideas covered in week’s topics for {title}.")
    lines.append("- Apply concepts to simple scenarios or mini-tasks.")
    lines.append("- Reflect on progress and identify areas for improvement.")
    lines.append("")
    lines.append("5. Recommended Tools/Technologies")
    lines.append("---------------------------------")
    lines.append(f"- Core tools commonly used with {title}.")
    lines.append("- Note‑taking app or learning journal.")
    lines.append("- Online resources (videos, articles, tutorials).")
    lines.append("")
    lines.append("6. Mini Projects / Assignments")
    lines.append("--------------------------------")
    lines.append(f"- Weekly mini‑tasks that reinforce {title} concepts.")
    lines.append("- Short quizzes or reflections.")
    lines.append("- Collaborative activity or peer review (optional).")
    lines.append("")
    lines.append("7. Final Capstone Project")
    lines.append("--------------------------")
    lines.append(f"- Design a small project that integrates the most important ideas from {title}.")
    lines.append("- Include planning, implementation, and a short presentation or write‑up.")
    lines.append("")
    lines.append("8. Academic Optimization Suggestions")
    lines.append("------------------------------------")
    lines.append(f"- Align weekly topics and outcomes with institutional standards where {title} is taught.")
    lines.append("- Include clear rubrics for assignments and projects.")
    lines.append("- Provide space for differentiated support and extension activities.")

    return "\n".join(lines)

class TextSummaryRequest(BaseModel):
    text: str
    max_length: int = 150
    min_length: int = 50


class IBMCurriculumRequest(CurriculumRequest):
    """Alias model for clarity; same fields as CurriculumRequest."""

@app.get("/")
def home():
    return {"message": "CurricuForge Backend Running Successfully 🚀"}

@app.post("/generate")
def generate_curriculum(request: CurriculumRequest):
    try:
        # Create client here
        client = genai.Client(api_key=API_KEY)

        prompt = f"""
You are an expert curriculum designer.

Course Title: {request.courseTitle}
Course Level: {request.courseLevel}
Duration: {request.duration}
Target Audience: {request.audience}
Skills/Requirements: {request.requirements}
Description: {request.description}

Provide output in structured format with:

1. Course Overview
2. Course Objectives
3. Weekly Topic Plan (Week-wise)
4. Learning Outcomes (per week)
5. Recommended Tools/Technologies
6. Mini Projects / Assignments
7. Final Capstone Project
8. Academic Optimization Suggestions
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return {"output": response.text}

    except Exception as e:
        return {"error": str(e)}


@app.post("/huggingface/generate")
def generate_curriculum_hf(request: HFCurriculumRequest):
    """
    Curriculum generation using a lightweight, rule-based template.
    No Hugging Face tokens, no heavy models required.
    """
    try:
        text = build_template_curriculum(request)
        return {
            "output": text,
            "tool": "Template generator (no ML, no tokens)"
        }
    except Exception as e:
        return {"error": f"Hugging Face curriculum generation error: {str(e)}"}


@app.post("/ibm/generate")
def generate_curriculum_ibm(request: IBMCurriculumRequest):
    """
    Curriculum generation using IBM AI (watsonx / Watson NLU).
    Requires IBM_API_KEY and IBM_API_URL to be set in .env.
    """
    if not IBM_API_KEY or not IBM_API_URL:
        return {
            "error": "IBM AI not configured. Please set IBM_API_KEY and IBM_API_URL in your .env file."
        }

    prompt = f"""
You are an expert curriculum designer.

Course Title: {request.courseTitle}
Course Level: {request.courseLevel}
Duration: {request.duration}
Target Audience: {request.audience}
Skills/Requirements: {request.requirements}
Description: {request.description}

Provide output in structured format with:

1. Course Overview
2. Course Objectives
3. Weekly Topic Plan (Week-wise)
4. Learning Outcomes (per week)
5. Recommended Tools/Technologies
6. Mini Projects / Assignments
7. Final Capstone Project
8. Academic Optimization Suggestions
"""

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {IBM_API_KEY}",
        }

        # NOTE: The exact payload shape depends on your IBM service (watsonx, etc.).
        # This is a generic example you can adapt to your deployment.
        payload = {
            "input": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.4,
            },
        }

        resp = requests.post(IBM_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        # Try common response formats; adjust as needed to your IBM endpoint
        text = None
        if isinstance(data, dict):
            if "generated_text" in data:
                text = data["generated_text"]
            elif "results" in data and isinstance(data["results"], list) and data["results"]:
                # e.g. {"results": [{"generated_text": "..."}]}
                first = data["results"][0]
                if isinstance(first, dict) and "generated_text" in first:
                    text = first["generated_text"]
        if text is None:
            # Fallback: use raw text/JSON
            text = resp.text

        return {
            "output": text,
            "tool": "IBM AI (via IBM_API_URL)",
        }
    except Exception as e:
        return {"error": f"IBM AI error: {str(e)}"}

# Hugging Face - Text Summarization Endpoint
@app.post("/huggingface/summarize")
def summarize_text(request: TextSummaryRequest):
    """
    Summarize text using Hugging Face Transformers (BART model)
    """
    try:
        # Prefer local summarizer, but fall back to Hugging Face Inference API if configured
        text = request.text
        if len(text.split()) > 1024:
            text = " ".join(text.split()[:1024])

        if summarizer:
            summary = summarizer(text, max_length=request.max_length, min_length=request.min_length, do_sample=False)
            result_text = summary[0]['summary_text']
            source = "Hugging Face (local model)"
        elif hf_inference_available:
            try:
                hf_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
                hf_resp = requests.post(hf_url, headers={"Authorization": f"Bearer {HF_API_KEY}"}, json={"inputs": text, "options": {"wait_for_model": True}})
                hf_resp.raise_for_status()
                hf_json = hf_resp.json()
                # response is often a list of summary candidates
                if isinstance(hf_json, list) and 'summary_text' in hf_json[0]:
                    result_text = hf_json[0]['summary_text']
                elif isinstance(hf_json, dict) and 'summary_text' in hf_json:
                    result_text = hf_json['summary_text']
                else:
                    # fallback: use raw text
                    result_text = hf_resp.text
                source = "Hugging Face (inference API)"
            except Exception as e:
                return {"error": f"Hugging Face Inference API error: {str(e)}"}
        else:
            return {"error": "No Hugging Face summarization option available (local model not loaded and HF_API_KEY not set)."}

        return {
            "tool": source,
            "original_text": request.text[:200] + "..." if len(request.text) > 200 else request.text,
            "summary": result_text
        }
    except Exception as e:
        return {"error": f"Hugging Face Error: {str(e)}"}

# Health check endpoint
@app.get("/health")
def health_check():
    """Check which AI services are available"""
    return {
        "status": "Running",
        "gemini": "✅ Available" if API_KEY else "❌ Not configured",
        "huggingface_summarizer": "✅ Available" if summarizer or hf_inference_available else "❌ Not available",
        "huggingface_curriculum": "✅ Available (template-based, no ML)",
        # Backwards‑compatible keys for frontend display
        "huggingface": "✅ Available" if summarizer or hf_inference_available else "❌ Not available",
        "ibm_watson": "✅ Available" if IBM_API_KEY and IBM_API_URL else "❌ Not configured",
    }
