# app.py
import streamlit as st
from pathlib import Path
from main import load_resume, get_job_result, get_gap_analysis
import tempfile

# Page config

st.set_page_config(
    page_title="Job Fit Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styling

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0a0a0f;
    color: #e8e8f0;
}

.stApp { background-color: #0a0a0f; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* Cards */
.card {
    background: #12121e;
    border: 1px solid #1e1e30;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #5a5a8a;
    margin-bottom: 0.75rem;
}

/* Verdict badge */
.verdict-strong {
    display: inline-block;
    background: #0d2b1a;
    color: #4ade80;
    border: 1px solid #166534;
    border-radius: 6px;
    padding: 0.35rem 0.9rem;
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.verdict-caution {
    display: inline-block;
    background: #2b1f0a;
    color: #fbbf24;
    border: 1px solid #92400e;
    border-radius: 6px;
    padding: 0.35rem 0.9rem;
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.verdict-skip {
    display: inline-block;
    background: #2b0a0a;
    color: #f87171;
    border: 1px solid #991b1b;
    border-radius: 6px;
    padding: 0.35rem 0.9rem;
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* Tag pills */
.tag-match {
    display: inline-block;
    background: #0d2b1a;
    color: #4ade80;
    border: 1px solid #166534;
    border-radius: 4px;
    padding: 0.2rem 0.6rem;
    font-size: 0.75rem;
    margin: 0.2rem;
}
.tag-gap {
    display: inline-block;
    background: #2b0a0a;
    color: #f87171;
    border: 1px solid #991b1b;
    border-radius: 4px;
    padding: 0.2rem 0.6rem;
    font-size: 0.75rem;
    margin: 0.2rem;
}
.tag-partial {
    display: inline-block;
    background: #2b1f0a;
    color: #fbbf24;
    border: 1px solid #92400e;
    border-radius: 4px;
    padding: 0.2rem 0.6rem;
    font-size: 0.75rem;
    margin: 0.2rem;
}

/* Text area */
.stTextArea textarea {
    background-color: #12121e !important;
    border: 1px solid #1e1e30 !important;
    color: #e8e8f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    border-radius: 8px !important;
}
.stTextArea textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 1px #4f46e5 !important;
}

/* Button */
.stButton > button {
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    padding: 0.6rem 1.5rem;
    width: 100%;
    transition: background 0.2s;
}
.stButton > button:hover {
    background: #4338ca;
    border: none;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #12121e;
    border: 1px dashed #2e2e4e;
    border-radius: 10px;
    padding: 1rem;
}

/* Hide sidebar toggle */
[data-testid="collapsedControl"] { display: none; }

/* Divider */
hr { border-color: #1e1e2e; }
</style>
""", unsafe_allow_html=True)

# Session state

if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_name" not in st.session_state:
    st.session_state.resume_name = None

# Header

st.markdown("<h1 style='font-family:Syne;font-size:2rem;margin-bottom:0'>Job Fit Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#5a5a8a;font-size:0.85rem;margin-top:0.25rem'>Upload your resume, paste a job posting, get an instant gap analysis.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Resume upload row

col_upload, col_status = st.columns([2, 1])

with col_upload:
    st.markdown("<div class='card-header'>Resume</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload resume",
        type=["pdf", "docx"],
        label_visibility="collapsed"
    )
    if uploaded_file and st.session_state.resume_text is None:
        with st.spinner("Reading resume..."):
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            try:
                st.session_state.resume_text = load_resume(tmp_path)
                st.session_state.resume_name = uploaded_file.name
            except Exception as e:
                st.error(f"Failed to read resume: {e}")

with col_status:
    if st.session_state.resume_text:
        st.markdown(f"""
        <div class='card'>
            <div class='card-header'>Status</div>
            <span style='color:#4ade80;font-size:0.8rem'>● {st.session_state.resume_name}</span><br>
            <span style='color:#5a5a8a;font-size:0.75rem'>{len(st.session_state.resume_text.split())} words extracted</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Clear Resume"):
            st.session_state.resume_text = None
            st.session_state.resume_name = None
            st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# Job posting input

if not st.session_state.resume_text:
    st.markdown("""
    <div class='card' style='text-align:center;padding:3rem'>
        <div style='font-size:2rem;margin-bottom:1rem'>📄</div>
        <div style='font-family:Syne;font-size:1rem;color:#e8e8f0;margin-bottom:0.5rem'>Upload your resume above to get started</div>
        <div style='color:#5a5a8a;font-size:0.8rem'>PDF or DOCX — stays loaded for the session</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div class='card-header'>Job Posting</div>", unsafe_allow_html=True)
    job_posting = st.text_area(
        "Job Posting",
        height=250,
        placeholder="Paste the full job posting here...",
        label_visibility="collapsed"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze = st.button("Analyze Fit →")

    if analyze:
        if not job_posting.strip():
            st.warning("Paste a job posting first.")
        else:
            with st.spinner("Parsing posting..."):
                job = get_job_result(job_posting)

            if not job:
                st.error("Failed to parse job posting.")
            else:
                with st.spinner("Running gap analysis..."):
                    gap = get_gap_analysis(st.session_state.resume_text, job)

                if gap:
                    st.markdown("<hr>", unsafe_allow_html=True)

                    # region Results

                    # Header row
                    col_title, col_verdict = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"<h2 style='font-family:Syne;margin-bottom:0'>{job.job_title}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:#5a5a8a;font-size:0.8rem;margin-top:0.2rem'>{job.work_arrangement} · {job.experience_req or 'Exp not specified'}</p>", unsafe_allow_html=True)
                    with col_verdict:
                        verdict_class = {
                            "Strong Apply": "verdict-strong",
                            "Apply with caveats": "verdict-caution",
                            "Skip": "verdict-skip"
                        }.get(gap.recommendation, "verdict-caution")
                        st.markdown(f"<div style='text-align:right;margin-top:0.5rem'><span class='{verdict_class}'>{gap.recommendation}</span></div>", unsafe_allow_html=True)

                    st.markdown("<hr>", unsafe_allow_html=True)

                    # A Quick Look
                    st.markdown("<div class='card-header'>A Quick Look</div>", unsafe_allow_html=True)
                    st.markdown(f"**Summary:** {job.job_summary}")
                    st.markdown(f"**Required Skills:** {', '.join(job.required_skills)}")
                    if job.preferred_skills:
                        st.markdown(f"**Preferred Skills:** {', '.join(job.preferred_skills)}")
                    if job.salary_range:
                        st.markdown(f"**Salary:** \\${job.salary_range.min_salary:,} – \\${job.salary_range.max_salary:,}")

                    st.markdown("<hr>", unsafe_allow_html=True)

                    # Overall assessment
                    st.markdown(f"""
                    <div class='card'>
                        <div class='card-header'>Overall Assessment</div>
                        <p style='color:#c8c8e0;font-size:0.85rem;line-height:1.6;margin:0'>{gap.overall_fit}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Three columns
                    c1, c2, c3 = st.columns(3)

                    with c1:
                        tags = "".join([f"<span class='tag-match'>{s}</span>" for s in gap.strong_matches])
                        st.markdown(f"""
                        <div class='card'>
                            <div class='card-header'>✓ Strong Matches ({len(gap.strong_matches)})</div>
                            {tags}
                        </div>
                        """, unsafe_allow_html=True)

                    with c2:
                        tags = "".join([f"<span class='tag-partial'>{s}</span>" for s in (gap.partial_matches or [])])
                        st.markdown(f"""
                        <div class='card'>
                            <div class='card-header'>~ Partial Matches ({len(gap.partial_matches or [])})</div>
                            {tags}
                        </div>
                        """, unsafe_allow_html=True)

                    with c3:
                        tags = "".join([f"<span class='tag-gap'>{s}</span>" for s in gap.gaps])
                        st.markdown(f"""
                        <div class='card'>
                            <div class='card-header'>✗ Gaps ({len(gap.gaps)})</div>
                            {tags}
                        </div>
                        """, unsafe_allow_html=True)

                    # endregion