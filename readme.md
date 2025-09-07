## AI‑Powered Resume Analysis (Streamlit)

An elegant Streamlit app to review resumes with ATS-style checks, section-wise AI feedback, visual insights, and quantified bullet suggestions.

- **Stack**: Streamlit, Plotly, Pandas
- **Optional AI Providers**: OpenAI or Anthropic (falls back to a heuristic mock if no keys are set)
- **Inputs**: PDF upload or pasted text; optional target job role and job description

### Features

- **ATS Compatibility Score**: Keyword coverage and section detection approximating an ATS scan.
- **Section‑wise Feedback**: Actionable suggestions per `summary`, `experience`, `education`, `skills`, etc.
- **Visual Insights**: Keyword density, section balance, and readability metrics.
- **Achievement Helper**: Rewrites vague bullets into quantified, action‑oriented statements.
- **Privacy‑first**: Processes data in‑memory during the session; no persistence.

---

## Quickstart

### Prerequisites

- Python 3.10+
- Windows, macOS, or Linux

### Setup

PowerShell (Windows):

```powershell
# Clone
git clone <your_fork_or_repo_url>
cd AI-Powered-Resume-Analysis

# (Recommended) Create venv
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# Install deps
pip install -r requirements.txt
```

macOS/Linux (bash/zsh):

```bash
# Clone
git clone <your_fork_or_repo_url>
cd AI-Powered-Resume-Analysis

# (Recommended) Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install deps
pip install -r requirements.txt
```

### Run locally

```bash
streamlit run app.py
```

Then open the URL printed in the terminal (typically `http://localhost:8501`).

---

## Configuration

Set one of the following environment variables to use real LLMs; otherwise the app uses a built‑in heuristic mock.

- `OPENAI_API_KEY`: Uses OpenAI `gpt-4o-mini` for structured JSON feedback
- `ANTHROPIC_API_KEY`: Uses Anthropic `claude-3-haiku-20240307`

You can place variables in a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=...
```

The app auto-detects provider priority: OpenAI → Anthropic → heuristic fallback.

---

## How it works (high level)

- `utils/parser.py`: Robust PDF/text extraction (pdfplumber → PyMuPDF → pdfminer.six fallback chain).
- `utils/analysis.py`: Keyword presets, ATS scoring, recruiter scan, visual insights, quantified suggestions.
- `utils/llm.py`: Provider‑aware client that returns strict JSON; falls back to heuristic JSON when no API key.
- `prompts.py`: Structured prompts for feedback and quantified bullet rewrites.
- `app.py`: Streamlit UI, tabs for feedback, ATS, visuals, and achievement helper.

Project entrypoint: `app.py`.

---

## Usage

1. Start the app and open the browser link.
2. Upload a resume (`.pdf` or `.txt`) or paste text.
3. (Optional) Enter a target role and job description for tailored analysis.
4. Click “Review Resume.”
5. Explore results across tabs: Structured Feedback, ATS Simulation, Recruiter Scan, Visual Insights, Achievement Helper.

Notes:

- Without API keys, the app still works with heuristic JSON for a realistic demo.
- With API keys, you’ll get richer, model‑generated structured feedback and rewrites.

---

## Deployment

Choose one of the common paths below.

### Streamlit Community Cloud

1. Push this repo to GitHub.
2. On Streamlit Cloud, deploy your repo and set Environment Variables (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).
3. No extra build steps are required; `requirements.txt` is provided.

### Hugging Face Spaces (Gradio/Streamlit runtime)

1. Create a new Space with “Streamlit”.
2. Upload repo files (or connect to GitHub).
3. Set Secrets for `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.

### Docker (optional)

Create `Dockerfile` similar to:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8501
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t resume-analyzer .
docker run -p 8501:8501 --env OPENAI_API_KEY=$OPENAI_API_KEY resume-analyzer
```

---

## Live Test of Deployment

Use this checklist right after deploying to confirm the app is healthy.

### 1) Smoke test the homepage

- Open the deployed URL in a browser.
- Verify the hero section shows “AI‑Powered Resume Analysis & Optimization”.
- Confirm sidebar displays the detected provider (OpenAI / Anthropic / Heuristic).

CLI curl check (expects the title text):

```bash
curl -sS <YOUR_DEPLOYED_URL> | grep -i "AI-Powered Resume Analysis"
```

Exit code 0 indicates the expected text is present.

### 2) Upload flow

- Upload a short PDF (or paste text) and click “Review Resume”.
- Expect: tabs render, ATS score appears, and metrics are populated.

### 3) Provider checks

- Without API keys: Results should still render with placeholder heuristic content.
- With `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`:
  - “Section‑wise Feedback” should feel richer and include `scores` and an `improved_resume` field.

### 4) Visualizations

- In “ATS Simulation” and “Visual Insights” tabs, confirm charts load without errors.

### 5) Error handling

- Try uploading a malformed PDF or empty input; expect an inline error message rather than a crash.

### 6) Logs (if available)

- Review platform logs (Cloud/Spaces/Docker) for startup messages and any exceptions.

If something breaks:

- Verify environment variables are set on the platform.
- Re‑install dependencies using the platform’s rebuild button.
- Test locally with the same Python version.

---

## Troubleshooting

- “Failed to read uploaded file”: The parser has multiple fallbacks; ensure the file isn’t encrypted and try a different extractor locally.
- Empty feedback with API keys set: Check quota/keys and platform egress rules.
- Charts not rendering: Make sure `plotly` is installed (listed in `requirements.txt`).

---

## Privacy & Disclaimer

This demo processes your resume in‑memory during the session. If you enable external LLM providers, content may be sent to that provider to generate feedback. Accuracy is not guaranteed; review and edit before use.

---

## License

Add your preferred license (e.g., MIT) here.
