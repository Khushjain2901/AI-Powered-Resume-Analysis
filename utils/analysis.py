from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Set


CANONICAL_SECTIONS = [
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
    "publications",
]

# Map of common aliases to canonical section names
SECTION_ALIASES = {
    "professional summary": "summary",
    "profile": "summary",
    "objective": "summary",
    "work experience": "experience",
    "employment": "experience",
    "work history": "experience",
    "professional experience": "experience",
    "education": "education",
    "academics": "education",
    "skills": "skills",
    "technical skills": "skills",
    "projects": "projects",
    "personal projects": "projects",
    "certifications": "certifications",
    "licenses": "certifications",
    "publications": "publications",
}


def simple_tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z\-\+\#/0-9]*", text.lower())


ROLE_PRESETS: Dict[str, Set[str]] = {
    # Data / AI
    "data scientist": {
        "python","pandas","numpy","sklearn","tensorflow","pytorch","sql","statistics","ml","classification","regression","nlp","feature engineering","model deployment","experiment tracking","tableau","powerbi","aws","gcp","azure","airflow","mlflow"
    },
    "data analyst": {
        "sql","excel","powerbi","tableau","python","pandas","visualization","dashboard","a/b testing","forecasting","etl","reporting","statistics","segmentation","ga4","lookerstudio"
    },
    # Engineering
    "software engineer": {
        "java","python","javascript","react","node","api","rest","graphql","docker","kubernetes","git","ci/cd","unit testing","microservices","sql","nosql","design patterns","testing"
    },
    "frontend developer": {
        "javascript","typescript","react","next.js","redux","html","css","tailwind","vite","webpack","accessibility","lighthouse","jest","cypress"
    },
    "backend developer": {
        "node","express","java","spring","python","django","flask","fastapi","rest","graphql","sql","postgres","mysql","redis","docker","kubernetes","microservices","auth","queue","rabbitmq","kafka"
    },
    "devops engineer": {
        "docker","kubernetes","terraform","ansible","aws","gcp","azure","ci/cd","github actions","gitlab ci","monitoring","prometheus","grafana","helm","istio","argocd"
    },
    "cloud architect": {
        "aws","gcp","azure","iam","vpc","load balancer","scalability","cost optimization","serverless","lambda","cloudformation","terraform","kubernetes","disaster recovery"
    },
    # Product / Design / Biz
    "product manager": {
        "roadmap","stakeholders","requirements","user research","kpi","okrs","backlog","prioritization","go to market","a/b testing","analytics","jira","wireframes","specs"
    },
    "ux designer": {
        "ux research","wireframing","prototyping","figma","usability testing","information architecture","heuristic evaluation","design system","accessibility","persona","journey map"
    },
    "business analyst": {
        "requirements","process mapping","sql","excel","dashboards","stakeholder management","gap analysis","kpi","user stories","confluence","jira"
    },
    "marketing manager": {
        "seo","sem","content strategy","campaigns","google ads","facebook ads","analytics","crm","a/b testing","email marketing","automation","brand strategy","roi"
    },
    # Security / QA
    "cybersecurity analyst": {
        "siem","splunk","wazuh","ids/ips","vulnerability management","threat hunting","incident response","nmap","wireshark","linux","mitre att&ck","risk assessment"
    },
    "qa engineer": {
        "test cases","test plans","manual testing","automation","selenium","cypress","jest","pytest","ci/cd","regression","integration","performance testing"
    },
    # Other example from screenshots
    "housekeeper": {
        "cleaning","sanitizing","laundry","organization","time management","attention to detail","inventory","safety procedures","guest service","housekeeping","vacuuming","mopping","disinfection"
    },
}


def role_keywords_for(job_role: str | None, job_desc: str | None, resume_text: str) -> Set[str]:
    role_text = (job_role or "").lower()
    # Try preset match by substring
    for key, vocab in ROLE_PRESETS.items():
        if key in role_text:
            return vocab
    # Use JD-driven extraction fallback
    if job_desc:
        tokens = [t for t in simple_tokenize(job_desc) if len(t) >= 3]
        common = Counter(tokens).most_common(60)
        return set([w for w, _ in common])
    # Last resort: resume-driven
    return set([w for w, _ in Counter(simple_tokenize(resume_text)).most_common(40)])


DOMAIN_PRESETS: Dict[str, Set[str]] = {
    "data scientist": {"regression","classification","nlp","feature engineering","model deployment","experiment tracking","ml"},
    "data analyst": {"a/b testing","forecasting","etl","segmentation","reporting"},
    "frontend developer": {"accessibility","lighthouse","performance","ux"},
    "backend developer": {"microservices","queue","auth","caching"},
    "devops engineer": {"monitoring","observability","infrastructure as code","sre","blue/green"},
    "cloud architect": {"disaster recovery","cost optimization","scalability","multi region"},
    "product manager": {"roadmap","prioritization","okrs","kpi","go to market"},
    "ux designer": {"usability testing","journey map","persona","heuristic evaluation"},
    "business analyst": {"gap analysis","process mapping","requirements"},
    "marketing manager": {"campaigns","roi","funnel","brand strategy"},
    "cybersecurity analyst": {"threat hunting","incident response","risk assessment"},
    "qa engineer": {"test plans","regression","performance testing"},
    "housekeeper": {"cleaning","sanitizing","housekeeping","laundry","organization","safety procedures","guest service","disinfection","vacuuming","mopping"},
}


def categorize_keywords(job_role: str | None, keywords: Set[str]) -> Dict[str, List[str]]:
    role_text = (job_role or "").lower()
    soft = {"communication","leadership","collaboration","time management","attention to detail","customer service","problem solving","teamwork","stakeholder management","presentation"}
    tools = {"python","java","sql","excel","tableau","powerbi","docker","kubernetes","git","jira","react","node","tensorflow","pytorch","terraform","ansible","aws","gcp","azure","postgres","mysql","redis","kafka","figma","selenium","cypress"}

    # choose domain set if matches, else empty
    domain: Set[str] = set()
    for key, vocab in DOMAIN_PRESETS.items():
        if key in role_text:
            domain = vocab
            break

    cats = {"Soft skills": [], "Tools/Tech": [], "Domain": [], "Other": []}
    for k in sorted(keywords):
        if k in soft:
            cats["Soft skills"].append(k)
        elif k in tools:
            cats["Tools/Tech"].append(k)
        elif k in domain:
            cats["Domain"].append(k)
        else:
            cats["Other"].append(k)
    return cats


def detect_sections(text: str) -> Dict[str, int]:
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    section_lengths: Dict[str, int] = defaultdict(int)
    current = "summary"

    # Build patterns for aliases
    import re as _re
    alias_patterns = [(alias, _re.compile(rf"\b{_re.escape(alias)}\b", _re.IGNORECASE)) for alias in SECTION_ALIASES.keys()]

    for line in lines:
        lower = line.lower()
        # Consider short lines or lines with colon as potential headings
        is_heading = len(line) <= 120
        matched = None
        for alias, pat in alias_patterns:
            if pat.search(lower):
                matched = SECTION_ALIASES[alias]
                break
        if matched and is_heading:
            current = matched
        section_lengths[current] += max(1, len(line) // 60)

    # If detection is too sparse, fall back to keyword-based estimation
    non_other = {k: v for k, v in section_lengths.items() if k in CANONICAL_SECTIONS}
    if not non_other or sum(non_other.values()) < 3:
        tokens = simple_tokenize(text)
        counts = Counter(tokens)
        heuristics = {
            "summary": ["summary", "objective", "profile"],
            "experience": ["experience", "managed", "lead", "developed", "responsible", "achieved"],
            "education": ["bsc", "msc", "university", "degree", "gpa", "bachelor", "master"],
            "skills": ["skills", "python", "java", "sql", "excel", "communication"],
            "projects": ["project", "built", "implemented", "designed"],
            "certifications": ["certified", "certificate", "certification"],
            "publications": ["publication", "journal", "conference"],
        }
        fallback = {}
        for sec, kws in heuristics.items():
            fallback[sec] = sum(counts.get(k, 0) for k in kws)
        # Normalize small weights
        for k in list(fallback.keys()):
            if fallback[k] > 0:
                fallback[k] = max(1, fallback[k] // 2)
        return {k: v for k, v in fallback.items() if v > 0}

    return dict(non_other)


def compute_ats_score(resume_text: str, role_keywords: Set[str]) -> Dict[str, object]:
    tokens = simple_tokenize(resume_text)
    token_set = set(tokens)
    missing = sorted([k for k in role_keywords if k not in token_set])
    coverage = 1.0 - (len(missing) / max(1, len(role_keywords)))
    section_info = detect_sections(resume_text)
    score = int(60 * coverage + 40 * min(1.0, len(section_info) / 6.0))
    return {
        "score": max(0, min(100, score)),
        "missing_keywords": missing[:100],
        "detected_sections": section_info,
    }


def analyze_recruiter_scan(resume_text: str) -> Dict[str, str]:
    first_lines = [l.strip() for l in resume_text.splitlines()[:20] if l.strip()]
    highlights = "\n".join(first_lines[:8])
    ignored = "\n".join(first_lines[8:]) if len(first_lines) > 8 else "Short resume header; focus on punchy summary."
    return {"highlights": highlights or "No immediate highlights detected.", "ignored": ignored}


def analyze_visual_insights(resume_text: str, role_keywords: Set[str]) -> Dict[str, object]:
    tokens = simple_tokenize(resume_text)
    counter = Counter(tokens)
    keyword_counts = {k: counter.get(k, 0) for k in sorted(list(role_keywords))[:25]}
    sections = detect_sections(resume_text)
    words = len(tokens)
    sentences = max(1, resume_text.count('.') + resume_text.count('!') + resume_text.count('?'))
    avg_sentence_len = words / sentences
    readability = {
        "avg_sentence_length": round(avg_sentence_len, 2),
        "word_count": words,
        "estimated_read_time_min": round(words / 200.0, 2),
    }
    return {
        "keyword_density": keyword_counts,
        "section_balance": sections,
        "readability": readability,
    }


def suggest_quantified_achievements(resume_text: str) -> List[Dict[str, str]]:
    suggestions: List[Dict[str, str]] = []
    bullet_like = re.findall(r"(?:^|\n)[\-\u2022\*]\s+(.+)", resume_text)
    vague_patterns = ["responsible for", "worked on", "helped with", "assisted", "involved in"]
    for bullet in bullet_like[:60]:
        lower = bullet.lower()
        if any(pat in lower for pat in vague_patterns) and len(bullet.split()) >= 4:
            suggestions.append({
                "original": bullet.strip(),
                "suggestion": "Rewrite with action + metric. Example: 'Led a team of 8 to deliver X, achieving Y% improvement.'",
            })
    return suggestions[:20]



