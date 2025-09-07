# AI Resume Reviewer & ATS Simulator

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. (Optional) Set API keys for richer feedback:

- `OPENAI_API_KEY` for OpenAI GPT models
- `ANTHROPIC_API_KEY` for Claude models

You can set them as environment variables or put them in a `.env` file in the project root (auto-loaded on app start).

Create `.env` (or copy from `.env.example`) and add:

```env
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

PowerShell example (temporary for the current session):

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:ANTHROPIC_API_KEY = "..."
```

## Run

```bash
streamlit run app.py
```

Open the URL printed in the terminal.

## Features

- Upload PDF/TXT or paste resume text
- Enter target job role and optional job description
- LLM-powered structured feedback with section scores and improved resume suggestion
- ATS simulation: keyword coverage, section detection, compatibility score
- Recruiter 6-second scan highlights
- Visual insights: keyword density, section balance, readability
- Achievement quantification helper for vague bullets

## Privacy

This app does not persist resumes. Content is processed in-memory during the session. If API keys are set, text is sent to the provider for processing.
