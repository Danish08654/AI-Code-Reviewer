import streamlit as st
import json
import time
import io
from datetime import datetime
from groq import Groq

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

/* Dark background everywhere */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
.block-container, [data-testid="stVerticalBlock"] {
    background: #0d1117 !important;
}
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div {
    background: #161b22 !important;
    border-right: 1px solid #21262d !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* Typography */
h1, h2, h3, h4, p, label, span, div { color: #e6edf3; }

/* Banner */
.banner {
    background: linear-gradient(135deg, #161b22, #0d1117);
    border: 1px solid #21262d;
    border-top: 2px solid #58a6ff;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 20px;
}
.banner h1 { font-size: 1.75rem; font-weight: 700; margin: 0 0 4px; color: #e6edf3; }
.banner p  { font-size: 0.875rem; color: #8b949e; margin: 0; }

/* Cards */
.card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.card-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 10px;
}

/* Issue rows */
.issue {
    background: #0d1117;
    border-left: 3px solid #30363d;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.875rem;
    color: #c9d1d9;
    line-height: 1.55;
}
.issue-red    { border-left-color: #f85149; }
.issue-yellow { border-left-color: #d29922; }
.issue-blue   { border-left-color: #58a6ff; }
.issue-green  { border-left-color: #3fb950; color: #3fb950; }

/* Badges */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
}
.badge-red    { background: rgba(248,81,73,.12);  color: #f85149;  border: 1px solid rgba(248,81,73,.25); }
.badge-yellow { background: rgba(210,153,34,.12); color: #d29922;  border: 1px solid rgba(210,153,34,.25); }
.badge-green  { background: rgba(63,185,80,.12);  color: #3fb950;  border: 1px solid rgba(63,185,80,.25); }
.badge-blue   { background: rgba(88,166,255,.12); color: #58a6ff;  border: 1px solid rgba(88,166,255,.25); }

/* Verdict */
.verdict {
    border-radius: 10px;
    padding: 16px 22px;
    text-align: center;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 14px;
}
.verdict-green  { background: rgba(63,185,80,.1);  border: 1px solid rgba(63,185,80,.3);  color: #3fb950; }
.verdict-yellow { background: rgba(210,153,34,.1); border: 1px solid rgba(210,153,34,.3); color: #d29922; }
.verdict-red    { background: rgba(248,81,73,.1);  border: 1px solid rgba(248,81,73,.3);  color: #f85149; }

/* Score rings */
.ring-wrap { text-align: center; padding: 6px; }
.ring {
    width: 76px; height: 76px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.15rem; font-weight: 700;
    border: 3px solid;
    background: rgba(0,0,0,.2);
}
.ring-label { font-size: 0.68rem; color: #8b949e; text-transform: uppercase; letter-spacing: .08em; }

/* Inputs */
.stTextArea textarea {
    background: #161b22 !important;
    color: #e6edf3 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
}
.stTextArea textarea:focus { border-color: #58a6ff !important; }

[data-testid="stFileUploadDropzone"] {
    background: #161b22 !important;
    border: 1px dashed #30363d !important;
    border-radius: 8px !important;
}

/* Buttons */
.stButton > button {
    background: #1f6feb !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px !important;
}
.stButton > button:hover { background: #388bfd !important; }

.stDownloadButton > button {
    background: #161b22 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}
.stDownloadButton > button:hover { border-color: #58a6ff !important; color: #58a6ff !important; }

/* Selectbox */
.stSelectbox > div > div { background: #161b22 !important; border-color: #21262d !important; color: #e6edf3 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #161b22 !important; border-radius: 8px !important; padding: 3px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #8b949e !important; border-radius: 6px !important; }
.stTabs [aria-selected="true"] { background: #0d1117 !important; color: #e6edf3 !important; }

/* Misc */
hr { border-color: #21262d !important; }
.stCheckbox span, .stSelectbox label, section[data-testid="stSidebar"] label { color: #c9d1d9 !important; }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──

def get_groq_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        st.error("⚠️ GROQ_API_KEY not found. Add it under Settings → Secrets.")
        st.stop()


def detect_language(code: str, filename: str = "") -> str:
    for ext, lang in {".py":"Python",".js":"JavaScript",".ts":"TypeScript",".java":"Java",
                      ".cpp":"C++",".c":"C",".cs":"C#",".go":"Go",".rs":"Rust",".rb":"Ruby",
                      ".php":"PHP",".html":"HTML",".css":"CSS",".sql":"SQL",".kt":"Kotlin",".swift":"Swift"}.items():
        if filename.endswith(ext): return lang
    for hint, lang in {"def ":"Python","import ":"Python","function ":"JavaScript",
                       "const ":"JavaScript","public class":"Java","#include":"C++",
                       "SELECT ":"SQL","<html":"HTML"}.items():
        if hint in code[:500]: return lang
    return "Unknown"


def count_lines(code: str) -> int:
    return len([l for l in code.splitlines() if l.strip()])


REVIEW_PROMPT = """You are a senior software engineer. Analyze the code and return ONLY valid JSON — no markdown, no backticks.

{{
  "summary": "2-3 sentence overview",
  "quality_score": <0-100>,
  "security_score": <0-100>,
  "performance_score": <0-100>,
  "maintainability_score": <0-100>,
  "critical_issues": ["..."],
  "medium_issues": ["..."],
  "suggestions": ["..."],
  "security_findings": ["..."],
  "performance_findings": ["..."],
  "best_practices": ["..."],
  "verdict": "APPROVE" | "NEEDS REVIEW" | "REJECT"
}}

verdict rules: APPROVE if quality>=75 and no critical_issues; REJECT if critical_issues or score<40; else NEEDS REVIEW.
Be specific — reference variable/function names and line numbers where possible.

Code ({language}):
```
{code}
```"""


def analyze_code(client, code: str, language: str, model: str) -> dict:
    raw = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": REVIEW_PROMPT.format(language=language, code=code[:8000])}],
        temperature=0.3,
        max_tokens=2048,
    ).choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip().rstrip("```"))


def build_report(review: dict, code: str, language: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sections = [
        f"# AI Code Review Report\nGenerated: {now}\nLanguage: {language} | Lines: {count_lines(code)}\n",
        f"## Summary\n{review.get('summary','N/A')}\n",
        f"## Scores\n- Quality: {review.get('quality_score','?')}/100\n- Security: {review.get('security_score','?')}/100\n- Performance: {review.get('performance_score','?')}/100\n- Maintainability: {review.get('maintainability_score','?')}/100\n",
        f"## Verdict: {review.get('verdict','UNKNOWN')}\n",
    ]
    for title, key in [("Critical Issues","critical_issues"),("Medium Issues","medium_issues"),
                       ("Security Findings","security_findings"),("Performance Findings","performance_findings"),
                       ("Suggestions & Best Practices","suggestions")]:
        items = review.get(key, [])
        if title == "Suggestions & Best Practices":
            items += review.get("best_practices", [])
        sections.append(f"## {title}\n" + ("\n".join(f"  - {i}" for i in items) or "  None") + "\n")
    sections.append("---\nGenerated by AI Code Reviewer (Groq + Streamlit)")
    return "\n".join(sections)


def score_ring(label: str, score: int):
    color = "#3fb950" if score >= 75 else "#d29922" if score >= 50 else "#f85149"
    st.markdown(f"""
    <div class="ring-wrap">
        <div class="ring" style="border-color:{color}; color:{color};">{score}</div>
        <div class="ring-label">{label}</div>
    </div>""", unsafe_allow_html=True)


def issue_list(items: list, cls: str, empty: str = "None found ✓"):
    if not items:
        st.markdown(f'<div class="issue issue-green">{empty}</div>', unsafe_allow_html=True)
        return
    for item in items:
        st.markdown(f'<div class="issue {cls}">{item}</div>', unsafe_allow_html=True)


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.divider()
    model = st.selectbox("Model", [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ], help="Larger = more thorough, slower")
    st.divider()
    st.markdown("**Review scope**")
    st.checkbox("Security",      value=True)
    st.checkbox("Performance",   value=True)
    st.checkbox("Code quality",  value=True)
    st.checkbox("Best practices",value=True)
    st.divider()
    st.markdown('<p style="font-size:.8rem;color:#8b949e;">Powered by <b style="color:#58a6ff;">Groq</b><br>Python · JS · TS · Java · C++ · Go · Rust · SQL · HTML</p>', unsafe_allow_html=True)


# ── HEADER ──
st.markdown("""
<div class="banner">
    <h1>🤖 AI Code Reviewer</h1>
    <p>Bug detection · Security audit · Performance analysis · Quality scoring</p>
</div>
""", unsafe_allow_html=True)


# ── LAYOUT ──
left, right = st.columns([5, 4], gap="large")

with left:
    tab1, tab2 = st.tabs(["✏️ Paste Code", "📁 Upload File"])

    with tab1:
        code_input = st.text_area("Code", height=340,
            placeholder="# Paste your code here...",
            label_visibility="collapsed")

    with tab2:
        uploaded = st.file_uploader("File", label_visibility="collapsed",
            type=["py","js","ts","java","cpp","c","cs","go","rs","rb","php","html","css","sql","kt","swift","txt"])
        file_code, file_name = "", ""
        if uploaded:
            try:
                file_code = uploaded.read().decode("utf-8")
                file_name = uploaded.name
                lang_hint = detect_language(file_code, file_name)
                st.markdown(
                    f'<span class="badge badge-blue">{file_name}</span> '
                    f'<span class="badge badge-blue">{lang_hint}</span> '
                    f'<span class="badge badge-green">{count_lines(file_code)} lines</span>',
                    unsafe_allow_html=True)
                st.code(file_code[:2000] + ("…" if len(file_code) > 2000 else ""))
            except Exception as e:
                st.error(f"Could not read file: {e}")

    final_code = "\n\n".join(filter(None, [code_input, file_code])).strip()

    if final_code:
        lang = detect_language(final_code, file_name)
        st.markdown(
            f'<div style="margin:10px 0;display:flex;gap:8px;flex-wrap:wrap;">'
            f'<span class="badge badge-blue">🔤 {lang}</span>'
            f'<span class="badge badge-blue">📝 {count_lines(final_code)} lines</span>'
            f'<span class="badge badge-blue">💾 {len(final_code):,} chars</span></div>',
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🔍 Analyze Code", use_container_width=True)


# ── RUN ANALYSIS ──
if run:
    if not final_code:
        with left: st.warning("Please paste or upload some code first.")
        st.stop()

    client   = get_groq_client()
    language = detect_language(final_code, file_name)

    with left:
        with st.spinner("Analyzing with Groq…"):
            t0 = time.time()
            try:
                review = analyze_code(client, final_code, language, model)
            except json.JSONDecodeError as e:
                st.error(f"Failed to parse response: {e}"); st.stop()
            except Exception as e:
                st.error(f"Groq error: {e}"); st.stop()

    if not isinstance(review, dict):
        with left: st.error("Unexpected response format."); st.stop()

    st.session_state.update(review=review, code=final_code, language=language, elapsed=time.time()-t0)


# ── RESULTS ──
if "review" in st.session_state:
    rev  = st.session_state["review"]
    code = st.session_state["code"]
    lang = st.session_state["language"]
    secs = st.session_state["elapsed"]

    with right:
        # Timing
        st.markdown(f'<div style="text-align:right;margin-bottom:8px;"><span class="badge badge-green">⚡ {secs:.2f}s</span></div>', unsafe_allow_html=True)

        # Verdict
        verdict = rev.get("verdict", "UNKNOWN")
        vcls = {"APPROVE": ("verdict-green","🟢"), "NEEDS REVIEW": ("verdict-yellow","🟡"), "REJECT": ("verdict-red","🔴")}.get(verdict, ("verdict-yellow","🟡"))
        st.markdown(f'<div class="verdict {vcls[0]}">{vcls[1]} {verdict}</div>', unsafe_allow_html=True)

        # Scores
        st.markdown('<div class="card"><div class="card-label">📊 Scores</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: score_ring("Quality",     rev.get("quality_score", 0))
        with c2: score_ring("Security",    rev.get("security_score", 0))
        with c3: score_ring("Perf",        rev.get("performance_score", 0))
        with c4: score_ring("Maintain",    rev.get("maintainability_score", 0))
        st.markdown("</div>", unsafe_allow_html=True)

        # Summary
        st.markdown(f'<div class="card"><div class="card-label">📝 Summary</div><p style="font-size:.875rem;line-height:1.65;color:#c9d1d9;margin:0;">{rev.get("summary","")}</p></div>', unsafe_allow_html=True)

        # Tabs
        t1, t2, t3, t4, t5 = st.tabs(["🔴 Critical", "🟡 Medium", "🔒 Security", "⚡ Perf", "💡 Tips"])
        with t1: issue_list(rev.get("critical_issues",[]), "issue-red")
        with t2: issue_list(rev.get("medium_issues",[]),   "issue-yellow")
        with t3: issue_list(rev.get("security_findings",[]), "issue-red",    "No security issues ✓")
        with t4: issue_list(rev.get("performance_findings",[]), "issue-yellow", "No performance concerns ✓")
        with t5: issue_list(rev.get("suggestions",[]) + rev.get("best_practices",[]), "issue-blue", "Code follows best practices ✓")

        # Download
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download Report",
            data=io.BytesIO(build_report(rev, code, lang).encode()),
            file_name=f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
