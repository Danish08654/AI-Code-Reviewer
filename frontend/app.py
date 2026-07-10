import streamlit as st
import json, time, io
from datetime import datetime
from groq import Groq

st.set_page_config(page_title="Code Reviewer", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .block-container { background: #0f172a !important; font-family: 'Inter', sans-serif; }
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div
    { background: #1e293b !important; border-right: 1px solid #334155 !important; }
#MainMenu, footer, header { visibility: hidden; }
p, label, span, div { color: #cbd5e1; }
h1, h2, h3 { color: #f1f5f9; }

.stTextArea textarea { background: #1e293b !important; color: #f1f5f9 !important; border: 1px solid #334155 !important; border-radius: 8px !important; font-size: 0.85rem !important; }
.stButton > button { background: #3b82f6 !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px !important; }
.stButton > button:hover { background: #2563eb !important; }
.stDownloadButton > button { background: #1e293b !important; color: #cbd5e1 !important; border: 1px solid #334155 !important; border-radius: 8px !important; }
.stSelectbox > div > div { background: #1e293b !important; border-color: #334155 !important; color: #f1f5f9 !important; }
[data-testid="stFileUploadDropzone"] { background: #1e293b !important; border: 1px dashed #334155 !important; border-radius: 8px !important; }
.stTabs [data-baseweb="tab-list"] { background: #1e293b !important; border-radius: 8px !important; padding: 3px !important; gap: 2px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #94a3b8 !important; border-radius: 6px !important; font-size: 0.85rem !important; }
.stTabs [aria-selected="true"] { background: #0f172a !important; color: #f1f5f9 !important; }
hr { border-color: #334155 !important; }

.card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; }
.issue { border-left: 3px solid #475569; border-radius: 6px; padding: 10px 14px; margin-bottom: 6px; font-size: 0.84rem; color: #cbd5e1; line-height: 1.6; background: #0f172a; }
.red    { border-left-color: #ef4444; }
.yellow { border-left-color: #f59e0b; }
.blue   { border-left-color: #3b82f6; }
.green  { border-left-color: #22c55e; color: #22c55e; }
.verdict { text-align: center; border-radius: 10px; padding: 14px; font-weight: 700; font-size: 1.05rem; margin-bottom: 14px; }
</style>
""", unsafe_allow_html=True)

# ── helpers ──
def client():
    try: return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except: st.error("Add GROQ_API_KEY to Streamlit Secrets."); st.stop()

def lang(code, name=""):
    exts = {".py":"Python",".js":"JavaScript",".ts":"TypeScript",".java":"Java",
            ".cpp":"C++",".go":"Go",".rs":"Rust",".html":"HTML",".css":"CSS",".sql":"SQL"}
    for e, l in exts.items():
        if name.endswith(e): return l
    for k, l in {"def ":"Python","function ":"JS","public class":"Java","SELECT ":"SQL","<html":"HTML"}.items():
        if k in code[:300]: return l
    return "Code"

def run_review(groq, code, language, model):
    prompt = f"""Review this {language} code. Return ONLY JSON, no markdown.
{{
  "summary": "brief overview",
  "quality_score": 0-100, "security_score": 0-100,
  "performance_score": 0-100, "maintainability_score": 0-100,
  "critical_issues": [], "medium_issues": [],
  "security_findings": [], "performance_findings": [],
  "suggestions": [],
  "verdict": "APPROVE or NEEDS REVIEW or REJECT"
}}
Verdict: APPROVE if quality>=75 and no critical issues. REJECT if critical issues or score<40.

```{code[:7000]}```"""
    raw = groq.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2, max_tokens=1500
    ).choices[0].message.content.strip()
    if "```" in raw: raw = raw.split("```")[1].lstrip("json")
    return json.loads(raw.strip().rstrip("`"))

def score_color(s): return "#22c55e" if s>=75 else "#f59e0b" if s>=50 else "#ef4444"

def score_ring(label, score):
    c = score_color(score)
    st.markdown(f"""
    <div style="text-align:center">
      <div style="width:68px;height:68px;border-radius:50%;border:2.5px solid {c};
           display:flex;align-items:center;justify-content:center;margin:0 auto 4px;
           color:{c};font-weight:700;font-size:1.1rem;">{score}</div>
      <div style="font-size:0.65rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em">{label}</div>
    </div>""", unsafe_allow_html=True)

def show_issues(items, cls, empty="All clear ✓"):
    if not items: st.markdown(f'<div class="issue green">{empty}</div>', unsafe_allow_html=True); return
    for i in items: st.markdown(f'<div class="issue {cls}">{i}</div>', unsafe_allow_html=True)

# ── sidebar ──
with st.sidebar:
    st.markdown("### Settings")
    st.divider()
    model = st.selectbox("Model", [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ])
    st.divider()
    st.caption("Supports Python · JS · TS · Java · C++ · Go · Rust · SQL · HTML")

# ── main ──
st.markdown("## 🤖 AI Code Reviewer")
st.caption("Paste or upload code to get an instant AI-powered review.")
st.divider()

left, right = st.columns([1, 1], gap="large")

with left:
    tab1, tab2 = st.tabs(["Paste Code", "Upload File"])
    with tab1:
        code_in = st.text_area("", height=300, placeholder="Paste your code here…")
    with tab2:
        up = st.file_uploader("", type=["py","js","ts","java","cpp","go","rs","html","css","sql","txt","rb","php"])
        fcode, fname = "", ""
        if up:
            try:
                fcode, fname = up.read().decode(), up.name
                st.code(fcode[:1200] + ("…" if len(fcode) > 1200 else ""))
            except: st.error("Could not read file.")

    final = "\n\n".join(filter(None, [code_in, fcode])).strip()
    if final:
        language = lang(final, fname)
        st.caption(f"Detected: **{language}** · {len([l for l in final.splitlines() if l.strip()])} lines")

    st.markdown("<br>", unsafe_allow_html=True)
    go = st.button("Analyze Code →", use_container_width=True)

# ── run ──
if go:
    if not final: st.warning("Please add some code first."); st.stop()
    groq = client()
    language = lang(final, fname)
    with st.spinner("Reviewing…"):
        t0 = time.time()
        try: rev = run_review(groq, final, language, model)
        except json.JSONDecodeError: st.error("Couldn't parse AI response. Try again."); st.stop()
        except Exception as e: st.error(f"Error: {e}"); st.stop()
    if not isinstance(rev, dict): st.error("Unexpected response."); st.stop()
    st.session_state.update(rev=rev, code=final, lang=language, elapsed=time.time()-t0)

# ── results ──
if "rev" in st.session_state:
    rev, code, language, elapsed = (
        st.session_state["rev"], st.session_state["code"],
        st.session_state["lang"], st.session_state["elapsed"]
    )
    with right:
        verdict = rev.get("verdict", "UNKNOWN")
        colors = {"APPROVE": ("#22c55e","rgba(34,197,94,.1)","rgba(34,197,94,.3)"),
                  "NEEDS REVIEW": ("#f59e0b","rgba(245,158,11,.1)","rgba(245,158,11,.3)"),
                  "REJECT": ("#ef4444","rgba(239,68,68,.1)","rgba(239,68,68,.3)")}
        tc, bg, bc = colors.get(verdict, colors["NEEDS REVIEW"])
        st.markdown(f'<div class="verdict" style="color:{tc};background:{bg};border:1px solid {bc};">'
                    f'{verdict}</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        for col, label, key in zip([c1,c2,c3,c4],
            ["Quality","Security","Perf","Maintain"],
            ["quality_score","security_score","performance_score","maintainability_score"]):
            with col: score_ring(label, rev.get(key, 0))

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="card"><p style="font-size:.875rem;line-height:1.65;margin:0;">'
                    f'{rev.get("summary","")}</p></div>', unsafe_allow_html=True)

        t1,t2,t3,t4,t5 = st.tabs(["Critical","Medium","Security","Performance","Tips"])
        with t1: show_issues(rev.get("critical_issues",[]),     "red")
        with t2: show_issues(rev.get("medium_issues",[]),       "yellow")
        with t3: show_issues(rev.get("security_findings",[]),   "red")
        with t4: show_issues(rev.get("performance_findings",[]),"yellow")
        with t5: show_issues(rev.get("suggestions",[]),         "blue")

        st.markdown("<br>", unsafe_allow_html=True)
        report = "\n".join([
            f"Code Review — {datetime.now():%Y-%m-%d %H:%M}",
            f"Language: {language} | Verdict: {verdict}",
            f"Scores — Quality:{rev.get('quality_score')} Security:{rev.get('security_score')} Perf:{rev.get('performance_score')} Maintain:{rev.get('maintainability_score')}",
            f"\nSummary\n{rev.get('summary','')}",
            *[f"\n{h}\n" + "\n".join(f"- {i}" for i in rev.get(k,[]) or ["None"])
              for h, k in [("Critical Issues","critical_issues"),("Medium Issues","medium_issues"),
                           ("Security","security_findings"),("Performance","performance_findings"),
                           ("Suggestions","suggestions")]]
        ])
        st.download_button("Download Report", io.BytesIO(report.encode()),
            file_name=f"review_{datetime.now():%Y%m%d_%H%M}.txt",
            mime="text/plain", use_container_width=True)
        st.caption(f"Reviewed in {elapsed:.1f}s · {model}")
