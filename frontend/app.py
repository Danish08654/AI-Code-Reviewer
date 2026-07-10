import streamlit as st
import json
import time
import io
from datetime import datetime
from groq import Groq

# PAGE CONFIG

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* ── Top banner ── */
.banner {
    background: linear-gradient(135deg, #1a2332 0%, #0d1117 60%, #1a1a2e 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple), var(--accent-green));
}
.banner h1 {
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
}
.banner p {
    color: var(--text-muted);
    font-size: 0.92rem;
    margin: 0;
}

/* ── Metric pills ── */
.metrics-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
.metric-pill {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 20px;
    flex: 1;
    min-width: 110px;
}
.metric-pill .val {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent-blue);
    font-family: 'JetBrains Mono', monospace;
}
.metric-pill .lbl {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
}

/* ── Cards ── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.card-title {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Issue items ── */
.issue-item {
    background: var(--bg-secondary);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    border-left: 3px solid transparent;
    line-height: 1.55;
}
.issue-critical { border-left-color: var(--accent-red); }
.issue-medium   { border-left-color: var(--accent-yellow); }
.issue-info     { border-left-color: var(--accent-blue); }

/* ── Badge ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.badge-red    { background: rgba(248,81,73,0.15); color: var(--accent-red);    border: 1px solid rgba(248,81,73,0.3); }
.badge-yellow { background: rgba(210,153,34,0.15); color: var(--accent-yellow); border: 1px solid rgba(210,153,34,0.3); }
.badge-green  { background: rgba(63,185,80,0.15); color: var(--accent-green);  border: 1px solid rgba(63,185,80,0.3); }
.badge-blue   { background: rgba(88,166,255,0.15); color: var(--accent-blue);  border: 1px solid rgba(88,166,255,0.3); }

/* ── Verdict banner ── */
.verdict-approve {
    background: linear-gradient(135deg, rgba(63,185,80,0.15), rgba(63,185,80,0.05));
    border: 1px solid rgba(63,185,80,0.4);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.verdict-reject {
    background: linear-gradient(135deg, rgba(248,81,73,0.15), rgba(248,81,73,0.05));
    border: 1px solid rgba(248,81,73,0.4);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.verdict-review {
    background: linear-gradient(135deg, rgba(210,153,34,0.15), rgba(210,153,34,0.05));
    border: 1px solid rgba(210,153,34,0.4);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.verdict-text { font-size: 1.3rem; font-weight: 700; margin: 0; }

/* ── Score ring ── */
.score-circle {
    width: 90px; height: 90px;
    border-radius: 50%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    margin: 0 auto 12px;
}

/* ── Sidebar tweaks ── */
section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li { color: var(--text-primary) !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1f6feb, #388bfd);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.92rem;
    padding: 10px 20px;
    transition: all 0.2s;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #388bfd, #58a6ff);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(88,166,255,0.3);
}

/* ── Text area ── */
.stTextArea textarea {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 2px rgba(88,166,255,0.2) !important;
}

/* ── File uploader ── */
.stFileUploader {
    background: var(--bg-secondary);
    border: 1px dashed var(--border);
    border-radius: 10px;
    padding: 8px;
}
.stFileUploader label { color: var(--text-muted) !important; }

/* ── Progress / spinner ── */
.stSpinner > div { border-top-color: var(--accent-blue) !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px;
    font-size: 0.85rem;
}
.stDownloadButton > button:hover {
    border-color: var(--accent-blue) !important;
    color: var(--accent-blue) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-secondary);
    border-radius: 10px;
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--text-muted);
    border-radius: 7px;
    font-size: 0.85rem;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}
</style>
""", unsafe_allow_html=True)


# HELPERS

def get_groq_client():
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        return Groq(api_key=api_key)
    except Exception:
        st.error(" GROQ_API_KEY not found in Streamlit secrets. Add it under Settings → Secrets.")
        st.stop()


def detect_language(code: str, filename: str = "") -> str:
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".java": "Java", ".cpp": "C++", ".c": "C", ".cs": "C#",
        ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
        ".html": "HTML", ".css": "CSS", ".sql": "SQL",
        ".kt": "Kotlin", ".swift": "Swift"
    }
    for ext, lang in ext_map.items():
        if filename.endswith(ext):
            return lang
    hints = {
        
    }
    for hint, lang in hints.items():
        if hint in code[:500]:
            return lang
    return "Unknown"


def count_lines(code: str) -> int:
    return len([l for l in code.splitlines() if l.strip()])


REVIEW_PROMPT = """You are a senior software engineer conducting a thorough code review.
Analyze the provided code and return ONLY a valid JSON object — no markdown, no backticks, no preamble.

Return exactly this structure:
{{
  "summary": "2-3 sentence overview of the code quality",
  "language": "{language}",
  "quality_score": <integer 0-100>,
  "security_score": <integer 0-100>,
  "performance_score": <integer 0-100>,
  "maintainability_score": <integer 0-100>,
  "critical_issues": ["issue1", "issue2"],
  "medium_issues": ["issue1", "issue2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "security_findings": ["finding1", "finding2"],
  "performance_findings": ["finding1", "finding2"],
  "best_practices": ["practice1", "practice2"],
  "verdict": "APPROVE" | "NEEDS REVIEW" | "REJECT"
}}

Rules:
- critical_issues: security vulnerabilities, crashes, data loss risks
- medium_issues: bugs, logic errors, bad patterns
- suggestions: style, readability, maintainability improvements
- security_findings: XSS, SQLi, hardcoded secrets, unsafe deserialization, etc.
- performance_findings: O(n²) loops, memory leaks, blocking calls, etc.
- best_practices: idiomatic improvements and missing conventions
- verdict: APPROVE if quality_score >= 75 and no critical_issues, REJECT if critical_issues exist or score < 40, else NEEDS REVIEW
- Be concrete and actionable — reference line numbers or variable names where possible
- Return ONLY the JSON, nothing else

Code to review ({language}):
```
{code}
```"""


def analyze_code(client: Groq, code: str, language: str, model: str) -> dict:
    prompt = REVIEW_PROMPT.format(language=language, code=code[:8000])
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )
    raw = response.choices[0].message.content.strip()
    # Strip any accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return json.loads(raw.strip())


def build_report(review: dict, code: str, language: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# AI Code Review Report",
        f"Generated: {now}",
        f"Language: {language}  |  Lines: {count_lines(code)}",
        "",
        f"## Summary",
        review.get("summary", "N/A"),
        "",
        f"## Scores",
        f"- Quality:        {review.get('quality_score', 'N/A')}/100",
        f"- Security:       {review.get('security_score', 'N/A')}/100",
        f"- Performance:    {review.get('performance_score', 'N/A')}/100",
        f"- Maintainability:{review.get('maintainability_score', 'N/A')}/100",
        "",
        f"## Verdict: {review.get('verdict', 'UNKNOWN')}",
        "",
        "## Critical Issues",
    ]
    for i in review.get("critical_issues", []):
        lines.append(f"  - {i}")
    lines += ["", "## Medium Issues"]
    for i in review.get("medium_issues", []):
        lines.append(f"  - {i}")
    lines += ["", "## Security Findings"]
    for i in review.get("security_findings", []):
        lines.append(f"  - {i}")
    lines += ["", "## Performance Findings"]
    for i in review.get("performance_findings", []):
        lines.append(f"  - {i}")
    lines += ["", "## Suggestions & Best Practices"]
    for i in review.get("suggestions", []) + review.get("best_practices", []):
        lines.append(f"  - {i}")
    lines += ["", "---", "Generated by AI Code Reviewer (Groq + Streamlit)"]
    return "\n".join(lines)


def score_color(score: int) -> str:
    if score >= 75: return "#3fb950"
    if score >= 50: return "#d29922"
    return "#f85149"


def render_score_ring(label: str, score: int):
    color = score_color(score)
    st.markdown(f"""
    <div style="text-align:center; padding: 8px;">
        <div style="
            width:80px; height:80px; border-radius:50%;
            border: 3px solid {color};
            display:flex; flex-direction:column;
            align-items:center; justify-content:center;
            margin: 0 auto 8px;
            background: rgba(0,0,0,0.2);
        ">
            <span style="font-family:'JetBrains Mono',monospace; font-size:1.2rem; font-weight:700; color:{color};">{score}</span>
        </div>
        <span style="font-size:0.72rem; color:#8b949e; text-transform:uppercase; letter-spacing:0.08em;">{label}</span>
    </div>
    """, unsafe_allow_html=True)


def render_issue_list(items: list, cls: str, empty_msg: str = "None found ✓"):
    if not items:
        st.markdown(f'<div class="issue-item issue-info" style="color:#3fb950;">{empty_msg}</div>', unsafe_allow_html=True)
        return
    for item in items:
        st.markdown(f'<div class="issue-item {cls}">{item}</div>', unsafe_allow_html=True)


# SIDEBAR

with st.sidebar:
    st.markdown('<div style="padding: 8px 0 16px;">', unsafe_allow_html=True)
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    model_choice = st.selectbox(
        " LLM Model",
        options=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ],
        index=0,
        help="Larger models give more thorough reviews"
    )

    st.markdown("---")
    st.markdown("###  Review Scope")
    check_security   = st.checkbox("Security Analysis",     value=True)
    check_perf       = st.checkbox("Performance Analysis",  value=True)
    check_quality    = st.checkbox("Code Quality",          value=True)
    check_practices  = st.checkbox("Best Practices",        value=True)

    st.markdown("---")
    st.markdown("###  About")
    st.markdown("""
    <div style="font-size:0.82rem; color:#8b949e; line-height:1.6;">
    Supports: Python · JS · TS · Java · C++ · C · Go · Rust · Ruby · PHP · HTML · CSS · SQL
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# HEADER BANNER
st.markdown("""
<div class="banner">
    <h1> AI Code Reviewer</h1>
</div>
""", unsafe_allow_html=True)


# MAIN LAYOUT
left_col, right_col = st.columns([5, 4], gap="large")

with left_col:
    # Input tabs
    tab_paste, tab_upload = st.tabs(["✏️  Paste Code", "📁  Upload File"])

    with tab_paste:
        code_input = st.text_area(
            "Paste your code below",
            height=340,
            placeholder="# Paste Python, JavaScript, Java, C++, SQL, or any code here...",
            label_visibility="collapsed"
        )

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload a source file",
            type=["py", "js", "ts", "java", "cpp", "c", "cs", "go", "rs",
                  "rb", "php", "html", "css", "sql", "kt", "swift", "txt"],
            label_visibility="collapsed"
        )
        file_content = ""
        file_name    = ""
        if uploaded_file:
            try:
                file_content = uploaded_file.read().decode("utf-8")
                file_name    = uploaded_file.name
                lang_hint    = detect_language(file_content, file_name)
                st.markdown(
                    f'<span class="badge badge-blue">{file_name}</span> '
                    f'<span class="badge badge-blue">{lang_hint}</span> '
                    f'<span class="badge badge-green">{count_lines(file_content)} lines</span>',
                    unsafe_allow_html=True
                )
                st.code(file_content[:2000] + ("..." if len(file_content) > 2000 else ""), language="python")
            except Exception as e:
                st.error(f"Failed to read file: {e}")

    # Merge inputs
    final_code = "\n\n".join(filter(None, [code_input, file_content])).strip()

    # Quick stats bar
    if final_code:
        lang_detected = detect_language(final_code, file_name)
        n_lines = count_lines(final_code)
        n_chars = len(final_code)
        st.markdown(f"""
        <div style="display:flex; gap:10px; margin: 10px 0; flex-wrap:wrap;">
            <span class="badge badge-blue">🔤 {lang_detected}</span>
            <span class="badge badge-blue">📝 {n_lines} lines</span>
            <span class="badge badge-blue">💾 {n_chars:,} chars</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    analyze_btn = st.button("  Analyze Code", use_container_width=True)


# ANALYSIS
if analyze_btn:
    if not final_code:
        with left_col:
            st.warning("  Please paste or upload some code first.")
        st.stop()

    client   = get_groq_client()
    language = detect_language(final_code, file_name)

    with left_col:
        with st.spinner("  Analyzing your code with Groq…"):
            t0 = time.time()
            try:
                review = analyze_code(client, final_code, language, model_choice)
            except json.JSONDecodeError as e:
                st.error(f"❌  Failed to parse AI response as JSON: {e}")
                st.stop()
            except Exception as e:
                st.error(f"❌  Groq API error: {e}")
                st.stop()
            elapsed = time.time() - t0

    if not isinstance(review, dict):
        with left_col:
            st.error("❌  Unexpected response format from AI.")
        st.stop()

    # ── Store in session ──
    st.session_state["review"]   = review
    st.session_state["code"]     = final_code
    st.session_state["language"] = language
    st.session_state["elapsed"]  = elapsed

# RESULTS PANEL

if "review" in st.session_state:
    review   = st.session_state["review"]
    code     = st.session_state["code"]
    language = st.session_state["language"]
    elapsed  = st.session_state["elapsed"]

    with right_col:
        # ── Timing chip ──
        st.markdown(f'<div style="text-align:right; margin-bottom:10px;"><span class="badge badge-green">⚡ {elapsed:.2f}s</span></div>', unsafe_allow_html=True)

        # ── Verdict ──
        verdict = review.get("verdict", "UNKNOWN")
        verdict_cls = {
            "APPROVE":      ("verdict-approve", "🟢", "#3fb950"),
            "NEEDS REVIEW": ("verdict-review",  "🟡", "#d29922"),
            "REJECT":       ("verdict-reject",  "🔴", "#f85149"),
        }.get(verdict, ("verdict-review", "🟡", "#d29922"))

        st.markdown(f"""
        <div class="{verdict_cls[0]}">
            <p class="verdict-text" style="color:{verdict_cls[2]};">{verdict_cls[1]} {verdict}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

        # ── Score rings ──
        st.markdown('<div class="card"><div class="card-title" style="color:#8b949e;">📊 SCORES</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: render_score_ring("Quality",       review.get("quality_score", 0))
        with c2: render_score_ring("Security",      review.get("security_score", 0))
        with c3: render_score_ring("Performance",   review.get("performance_score", 0))
        with c4: render_score_ring("Maintain.",     review.get("maintainability_score", 0))
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Summary ──
        st.markdown(f"""
        <div class="card">
            <div class="card-title" style="color:#8b949e;">📝 SUMMARY</div>
            <p style="font-size:0.9rem; line-height:1.65; color:#c9d1d9; margin:0;">{review.get("summary", "")}</p>
        </div>
        """, unsafe_allow_html=True)

        # ── Issues tabs ──
        t1, t2, t3, t4, t5 = st.tabs(["🔴 Critical", "🟡 Medium", "🔒 Security", "⚡ Perf", "💡 Tips"])

        with t1:
            n = len(review.get("critical_issues", []))
            st.markdown(f'<span class="badge badge-red">{n} issue{"s" if n!=1 else ""}</span><br><br>', unsafe_allow_html=True)
            render_issue_list(review.get("critical_issues", []), "issue-critical")

        with t2:
            n = len(review.get("medium_issues", []))
            st.markdown(f'<span class="badge badge-yellow">{n} issue{"s" if n!=1 else ""}</span><br><br>', unsafe_allow_html=True)
            render_issue_list(review.get("medium_issues", []), "issue-medium")

        with t3:
            findings = review.get("security_findings", [])
            n = len(findings)
            st.markdown(f'<span class="badge badge-red">{n} finding{"s" if n!=1 else ""}</span><br><br>', unsafe_allow_html=True)
            render_issue_list(findings, "issue-critical", "No security issues detected ✓")

        with t4:
            findings = review.get("performance_findings", [])
            n = len(findings)
            st.markdown(f'<span class="badge badge-yellow">{n} finding{"s" if n!=1 else ""}</span><br><br>', unsafe_allow_html=True)
            render_issue_list(findings, "issue-medium", "No performance concerns ✓")

        with t5:
            all_tips = review.get("suggestions", []) + review.get("best_practices", [])
            n = len(all_tips)
            st.markdown(f'<span class="badge badge-blue">{n} tip{"s" if n!=1 else ""}</span><br><br>', unsafe_allow_html=True)
            render_issue_list(all_tips, "issue-info", "Code follows best practices ✓")

        # ── Download ──
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        report_text = build_report(review, code, language)
        report_bytes = io.BytesIO(report_text.encode("utf-8"))
        fname = f"code_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        st.download_button(
            label="⬇️  Download Full Report",
            data=report_bytes,
            file_name=fname,
            mime="text/plain",
            use_container_width=True
        )
