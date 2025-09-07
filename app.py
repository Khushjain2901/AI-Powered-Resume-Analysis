import os
from io import BytesIO
from typing import Optional, Dict, Any

import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from utils.parser import extract_text_from_any
from utils.analysis import (
    compute_ats_score,
    analyze_recruiter_scan,
    analyze_visual_insights,
    suggest_quantified_achievements,
    role_keywords_for,
    categorize_keywords,
)
from utils.llm import LLMClient
from prompts import (
    FEEDBACK_PROMPT_TEMPLATE,
    ACHIEVEMENT_REWRITE_PROMPT,
)


st.set_page_config(page_title="AI Resume Reviewer", page_icon="📄", layout="wide")
load_dotenv(override=False)

# Map Streamlit secrets to environment variables in hosted deployments
try:
    if hasattr(st, "secrets"):
        if "OPENAI_API_KEY" in st.secrets and not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = str(st.secrets["OPENAI_API_KEY"]) or ""
        if "ANTHROPIC_API_KEY" in st.secrets and not os.getenv("ANTHROPIC_API_KEY"):
            os.environ["ANTHROPIC_API_KEY"] = str(st.secrets["ANTHROPIC_API_KEY"]) or ""
except Exception:
    pass

# Global vibrant styling
st.markdown(
    """
    <style>
    .app-hero {padding: 64px 28px; background: linear-gradient(120deg, #6a11cb 0%, #2575fc 100%); border-radius: 18px; color: #fff; margin-bottom: 28px; box-shadow: 0 10px 30px rgba(37,117,252,0.25);} 
    .app-hero h1 {margin: 0; font-size: 44px; font-weight: 800; letter-spacing: 0.3px;}
    .app-hero p {margin: 10px 0 0 0; font-size: 18px; opacity: 0.95;}
    .pill {display:inline-block; padding:6px 10px; border-radius:999px; background: rgba(255,255,255,0.2); margin-right:8px; font-size:12px}
    .card {background: #ffffff; border-radius: 14px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); border: 1px solid #eef0f5;}
    .card h3 {margin-top:0}
    .grid {display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px;}
    .feature {background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); border: 1px solid #eaeaea;}
    .feature h4 {margin:6px 0 4px 0}
    .mini-card {background:#fafafa;border:1px solid #eee;border-radius:10px;padding:12px;margin:8px 0}
    .muted {color:#6b7280;font-size:12px}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_llm_client(openai_key: Optional[str] = None, anthropic_key: Optional[str] = None) -> LLMClient:
    provider = None
    if (openai_key or os.getenv("OPENAI_API_KEY")):
        provider = "openai"
    elif (anthropic_key or os.getenv("ANTHROPIC_API_KEY")):
        provider = "anthropic"
    else:
        provider = "heuristic"
    return LLMClient(provider=provider, openai_api_key=openai_key, anthropic_api_key=anthropic_key)


def read_resume_input() -> Optional[str]:
    uploaded = st.file_uploader("Upload resume (PDF or TXT)", type=["pdf", "txt"])
    pasted = st.text_area("Or paste resume text", height=220, placeholder="Paste your resume text here…")

    resume_text = None
    if uploaded is not None:
        try:
            data = uploaded.read()
            resume_text = extract_text_from_any(BytesIO(data), uploaded.type or uploaded.name)
        except Exception as e:
            st.error(f"Failed to read uploaded file: {e}")

    if (resume_text is None or len(resume_text.strip()) == 0) and pasted.strip():
        resume_text = pasted

    return resume_text


def read_job_inputs() -> Dict[str, Optional[str]]:
    col1, col2 = st.columns(2)
    with col1:
        job_role = st.text_input("Target job role", placeholder="e.g., Data Scientist")
    with col2:
        job_desc = st.text_area("Optional: Job description", height=180, placeholder="Paste the JD to tailor analysis…")
    return {"job_role": job_role.strip() if job_role else None, "job_desc": job_desc.strip() if job_desc else None}


def run_review(resume_text: str, job_role: Optional[str], job_desc: Optional[str]) -> Dict[str, Any]:
    client = get_llm_client()
    role_keywords = role_keywords_for(job_role, job_desc, resume_text)

    ats = compute_ats_score(resume_text, role_keywords)
    recruiter = analyze_recruiter_scan(resume_text)
    visuals = analyze_visual_insights(resume_text, role_keywords)

    prompt = FEEDBACK_PROMPT_TEMPLATE.format(
        role=job_role or "(unspecified role)",
        job_desc=job_desc or "",
        keywords=", ".join(sorted(role_keywords))[:1500],
        resume_text=resume_text[:12000],
    )

    feedback = client.generate_structured_feedback(prompt)
    quantified_suggestions = suggest_quantified_achievements(resume_text)

    return {
        "ats": ats,
        "recruiter": recruiter,
        "visuals": visuals,
        "feedback": feedback,
        "quantified": quantified_suggestions,
    }


def main():
    # Hero Section
    st.markdown(
        """
        <div class="app-hero">
          <h1>AI-Powered Resume Analysis & Optimization</h1>
          <p>Personalized feedback, missing keywords, and ATS-focused suggestions to help you stand out.</p>
          <div style="margin-top: 12px;">
            <span class="pill">⚡ Instant</span>
            <span class="pill">🔒 Private</span>
            <span class="pill">🤖 AI-Powered</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("We do not store your data. This is a demo and may be inaccurate.")

    with st.expander("Privacy & Disclaimer", expanded=False):
        st.write(
            "This tool analyzes your resume text in-memory only during this session. "
            "We do not permanently store resumes. If you use external LLM APIs, your data "
            "may be sent to that provider for processing."
        )

    with st.sidebar:
        st.subheader("LLM Provider")
        provider_label = "OpenAI" if os.getenv("OPENAI_API_KEY") else ("Anthropic" if os.getenv("ANTHROPIC_API_KEY") else "Heuristic")
        st.text(f"Using: {provider_label}")
        st.divider()
        st.markdown("This app uses environment variables for API keys. Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`. You can also create a `.env` file in the project root.")

    # Upload/Enhance sections with cards
    st.markdown("<div class='card'><h3>📤 Upload Your Resume</h3>", unsafe_allow_html=True)
    resume_text = read_resume_input()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card' style='margin-top:16px'><h3>🎯 Enhance Your Analysis</h3>", unsafe_allow_html=True)
    job = read_job_inputs()
    st.markdown("</div>", unsafe_allow_html=True)

    # Feature highlights
    st.markdown("<div class='grid' style='margin:18px 0;'>", unsafe_allow_html=True)
    st.markdown("<div class='card feature'><h4>⚙️ ATS Optimized</h4><div>See coverage and section detection like an ATS.</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='card feature'><h4>🧠 Smart Feedback</h4><div>Section-wise tips with actionable improvements.</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='card feature'><h4>📊 Visual Insights</h4><div>Keyword density, balance, and readability.</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='card feature'><h4>🔢 Quantify Impact</h4><div>Turn vague bullets into metric-driven achievements.</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Review Resume", type="primary"):
        if not resume_text or len(resume_text.strip()) < 30:
            st.error("Please provide a valid resume (upload or paste text).")
            return

        with st.spinner("Analyzing resume…"):
            # Create client from environment-provided keys
            client = get_llm_client()
            # Inject into run_review by monkey-passing via local closure replacement
            def _run(resume_text_i, job_role_i, job_desc_i):
                role_keywords = role_keywords_for(job_role_i, job_desc_i, resume_text_i)
                ats = compute_ats_score(resume_text_i, role_keywords)
                recruiter = analyze_recruiter_scan(resume_text_i)
                visuals = analyze_visual_insights(resume_text_i, role_keywords)
                prompt = FEEDBACK_PROMPT_TEMPLATE.format(
                    role=job_role_i or "(unspecified role)",
                    job_desc=job_desc_i or "",
                    keywords=", ".join(sorted(role_keywords))[:1500],
                    resume_text=resume_text_i[:12000],
                )
                feedback = client.generate_structured_feedback(prompt)
                quantified_suggestions = suggest_quantified_achievements(resume_text_i)
                return {"ats": ats, "recruiter": recruiter, "visuals": visuals, "feedback": feedback, "quantified": quantified_suggestions}

            results = _run(resume_text, job.get("job_role"), job.get("job_desc"))

        # Layout results
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Structured Feedback",
            "ATS Simulation",
            "Recruiter 6-sec Scan",
            "Visual Insights",
            "Achievement Helper",
        ])

        # Compact KPI summary across tabs top
        with st.container():
            kpi_cols = st.columns(4)
            kpi_cols[0].metric("ATS Score", f"{results['ats']['score']} / 100")
            read = results["visuals"].get("readability", {})
            kpi_cols[1].metric("Word count", read.get("word_count", 0))
            kpi_cols[2].metric("Read time (min)", read.get("estimated_read_time_min", 0))
            missing = results["ats"].get("missing_keywords", [])
            kpi_cols[3].metric("Missing keywords", len(missing))

        with tab1:
            fb = results["feedback"] if isinstance(results["feedback"], dict) else {"sections": {"general": str(results["feedback"])}}
            st.subheader("Section-wise Feedback")
            for section, content in fb.get("sections", {}).items():
                with st.expander(section.capitalize(), expanded=False):
                    # Normalize content to display professionally
                    if isinstance(content, list):
                        # If list of dicts (e.g., experience entries), render mini cards
                        if content and isinstance(content[0], dict):
                            for entry in content:
                                title = entry.get("title") or entry.get("role") or entry.get("degree") or "Item"
                                org = entry.get("company") or entry.get("organization") or entry.get("institution") or entry.get("location")
                                dates = entry.get("dates") or entry.get("year") or ""
                                body_lines = []
                                # combine responsibilities or bullet-like details
                                if isinstance(entry.get("responsibilities"), list):
                                    body_lines.extend([str(x) for x in entry.get("responsibilities")])
                                for k in ("gpa","location","summary","highlights"):
                                    if entry.get(k):
                                        body_lines.append(f"{k.capitalize()}: {entry.get(k)}")
                                st.markdown(f"<div class='mini-card'><strong>{title}</strong>" + (f" · {org}" if org else "") + (f" <span class='muted'>({dates})</span>" if dates else "") + "</div>", unsafe_allow_html=True)
                                for bl in body_lines[:6]:
                                    st.markdown(f"- {bl}")
                        else:
                            for item in content:
                                st.markdown(f"- {item}")
                    elif isinstance(content, dict):
                        # Pretty print key points from dict instead of raw dict
                        for k, v in content.items():
                            if isinstance(v, list):
                                st.markdown(f"**{k.capitalize()}**")
                                for it in v[:8]:
                                    st.markdown(f"- {it}")
                            else:
                                st.markdown(f"**{k.capitalize()}**: {v}")
                    else:
                        st.write(content)
            if fb.get("scores"):
                st.subheader("Section Scores")
                scores_dict = fb["scores"]
                # Badges line
                try:
                    badge_html = []
                    for name, val in scores_dict.items():
                        v = int(val)
                        if v >= 80:
                            color = "#16a34a"
                            label = "Excellent"
                        elif v >= 60:
                            color = "#22c55e"
                            label = "Good"
                        elif v >= 40:
                            color = "#f59e0b"
                            label = "Fair"
                        elif v >= 20:
                            color = "#f97316"
                            label = "Needs Work"
                        else:
                            color = "#ef4444"
                            label = "Poor"
                        badge_html.append(f"<span class='pill' style='background:{color}33;color:{color};font-weight:600;margin-bottom:6px'>{name.capitalize()}: {v} • {label}</span>")
                    st.markdown(" ".join(badge_html), unsafe_allow_html=True)
                except Exception:
                    pass
                try:
                    df_scores = pd.DataFrame({"section": list(scores_dict.keys()), "score": list(scores_dict.values())})
                    df_scores = df_scores.sort_values("score", ascending=True)
                    fig_scores = px.bar(df_scores, x="score", y="section", orientation="h", range_x=[0,100], color="score", color_continuous_scale="Bluered_r", height=320, title="Scores by Section")
                    st.plotly_chart(fig_scores, use_container_width=True)
                except Exception:
                    st.json(scores_dict)
            if fb.get("improved_resume"):
                st.subheader("Suggested Improved Version")
                st.write(fb["improved_resume"])
                st.download_button("Download Improved Resume", data=fb["improved_resume"], file_name="improved_resume.txt")

        with tab2:
            st.subheader("ATS Keywords & Compatibility")
            st.progress(results['ats']['score'] / 100.0, text=f"Compatibility: {results['ats']['score']} / 100")
            missing = results["ats"].get("missing_keywords", [])
            if missing:
                st.write("Missing keywords (role-tailored):")
                cats = categorize_keywords(job.get("job_role"), set(missing))
                color_map = {"Soft skills": "#1e3a8a", "Tools/Tech": "#7c2d12", "Domain": "#155e75", "Other": "#6b21a8"}
                for title, items in cats.items():
                    if not items:
                        continue
                    st.markdown(f"**{title}**")
                    color = color_map.get(title, "#b10f2e")
                    chips = " ".join([f"<span class='pill' style='background:{color}22;color:{color}'>{k}</span>" for k in items[:24]])
                    st.markdown(chips, unsafe_allow_html=True)
            else:
                st.success("No critical keywords missing.")

            st.write("Detected sections:")
            sec = results["ats"].get("detected_sections", {})
            if not sec:
                # Recompute on the resume text to populate if missing
                recompute = analyze_visual_insights(resume_text, role_keywords_for(job.get("job_role"), job.get("job_desc"), resume_text))
                sec = recompute.get("section_balance", {})
            if sec:
                df_sec = pd.DataFrame({"section": list(sec.keys()), "weight": list(sec.values())})
                fig_sec = px.bar(df_sec, x="section", y="weight", color="section", title="Section Balance", height=300)
                st.plotly_chart(fig_sec, use_container_width=True)
            else:
                st.info("No sections detected.")

        with tab3:
            st.subheader("What stands out in 6 seconds")
            st.write(results["recruiter"]["highlights"]) 
            st.subheader("Likely ignored")
            st.write(results["recruiter"]["ignored"]) 

        with tab4:
            st.subheader("Keyword Density")
            kd = results["visuals"].get("keyword_density", {})
            if kd:
                df_kd = pd.DataFrame({"keyword": list(kd.keys()), "count": list(kd.values())})
                df_kd = df_kd.sort_values("count", ascending=False).head(20)
                fig_kd = px.bar(df_kd, x="keyword", y="count", color="count", title="Top Keywords", height=340)
                st.plotly_chart(fig_kd, use_container_width=True)
            else:
                st.info("No keywords to display.")

            st.subheader("Section Balance (approximate)")
            sb = results["visuals"].get("section_balance", {})
            if sb:
                df_sb = pd.DataFrame({"section": list(sb.keys()), "weight": list(sb.values())})
                fig_sb = px.pie(df_sb, names="section", values="weight", title="Sections Share", height=320)
                st.plotly_chart(fig_sb, use_container_width=True)
            else:
                st.info("No section data.")

            st.subheader("Readability")
            read = results["visuals"].get("readability", {})
            if read:
                cols = st.columns(3)
                cols[0].metric("Avg sentence length", read.get("avg_sentence_length", 0))
                cols[1].metric("Word count", read.get("word_count", 0))
                cols[2].metric("Est. read time (min)", read.get("estimated_read_time_min", 0))
            else:
                st.info("No readability metrics.")

        with tab5:
            st.subheader("Quantify vague achievements")
            # Try LLM-improved rewrites when API available
            improved_items = []
            if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
                def _orig(q):
                    if isinstance(q, dict):
                        return q.get("original") or q.get("text") or q.get("bullet") or str(q)
                    return str(q)
                bullets = "\n".join([f"- {_orig(q)}" for q in results.get("quantified", [])])
                prompt_q = ACHIEVEMENT_REWRITE_PROMPT.format(
                    role=job.get("job_role") or "(unspecified)",
                    job_desc=job.get("job_desc") or "",
                    bullets=bullets[:4000],
                )
                q_client = get_llm_client()
                q_resp = q_client.generate_quantified_rewrites(prompt_q)
                improved_items = q_resp.get("suggestions", [])

            # Merge heuristic and improved
            base_items = results.get("quantified", [])
            merged = improved_items if improved_items else base_items
            for item in merged:
                if isinstance(item, dict):
                    original = item.get("original") or item.get("text") or item.get("bullet") or ""
                    suggestion = item.get("suggestion") or ""
                else:
                    original = str(item)
                    suggestion = ""
                with st.expander((original or "Achievement")[:120] + ("…" if original and len(original) > 120 else "")):
                    st.write("Suggestion:")
                    st.write(suggestion or "Rewrite with action + metric. Example: 'Led a team of 8 to deliver X, achieving Y% improvement.'")


if __name__ == "__main__":
    main()



