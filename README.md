# CurricuForge Backend - AI Integrations

This backend integrates:
- Gemini (Google) for curriculum generation
- Hugging Face for text summarization
- IBM AI (e.g. watsonx) for curriculum generation

Use environment variables (see `.env.example`) to configure API keys.

Quick start

1. Copy `.env.example` to `.env` and fill your keys.
2. Create a virtual environment and install requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Run the FastAPI app locally:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Endpoints

- `GET /` — health message
- `GET /health` — shows status of Gemini, Hugging Face, and IBM services
- `POST /generate` — uses Gemini to generate curriculum (requires `GEMINI_API_KEY`)
- `POST /huggingface/generate` — rule‑based curriculum generator (no ML, no tokens)
- `POST /huggingface/summarize` — summarizes text; prefers local `transformers` pipeline, falls back to Hugging Face Inference API if `HF_API_KEY` is available
- `POST /ibm/generate` — curriculum generation using IBM AI (requires `IBM_API_KEY` and `IBM_API_URL`)

Notes
- Never commit `.env` or your API keys to source control.
- If you plan to self-host models or run heavy inference locally, ensure you have the proper hardware and install `torch`/`transformers` accordingly.
- For self-hosting Hugging Face models, consider using Hugging Face Inference Endpoints or a local container setup.# CurricuForge Backend - AI Integrations

This backend includes example integrations for Gemini (Google GenAI), Hugging Face, and IBM Watson NLU.

Setup

1. Copy `.env.example` to `.env` and fill in keys:

```
GEMINI_API_KEY=
HF_API_KEY=
IBM_API_KEY=
IBM_API_URL=
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the FastAPI app (from the `backend` folder):

```bash
uvicorn main:app --reload --port 8000
```

Endpoints

- `GET /` - health message
- `POST /generate` - Gemini curriculum generation (requires `GEMINI_API_KEY`)
- `POST /huggingface/summarize` - summarize text using Hugging Face pipeline
- `POST /ibm/analyze` - analyze text with IBM Watson NLU (requires `IBM_API_KEY` and `IBM_API_URL`)

Security

Never commit your `.env` file with real API keys. Use environment variables or a secret manager in production.
