FEEDBACK_PROMPT_TEMPLATE = (
    "You are an expert resume reviewer and ATS. Analyze the provided resume text.\n"
    "Target role: {role}. Job description (optional): {job_desc}.\n"
    "Key role keywords: {keywords}.\n"
    "Return STRICT JSON with keys: sections (object with summary, experience, education, skills, projects ...),\n"
    "scores (object numeric 0-100 per section), improved_resume (string).\n"
    "Be concise and focus on: missing skills/keywords, formatting & clarity, vague language, \n"
    "and tailoring experience to the role with quantified outcomes.\n\n"
    "RESUME:<<<\n{resume_text}\n>>>"
)

ACHIEVEMENT_REWRITE_PROMPT = (
    "You are an expert resume coach. Rewrite vague resume bullets to be quantified and specific.\n"
    "Return STRICT JSON with an array 'suggestions', each item: {{original: str, suggestion: str}}.\n"
    "Context: Target role: {role}. Job description (optional): {job_desc}.\n"
    "Focus on making each bullet action-oriented and include realistic metrics inferred from context.\n\n"
    "BULLETS:<<<\n{bullets}\n>>>"
)



