import streamlit as st
import json
import time
import io
from datetime import datetime
from groq import Groq

st.set_page_config(page_title="AI Code Reviewer", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap');

*, body { font-family: 'Inter', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .block-container { background: #0d1117 !important; }
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background: #161b22 !important; border-right: 1px solid #21262d !important; }
#MainMenu, footer, header { visibility: hidden; }

.banner { border: 1px solid #21262d; border-top: 2px solid #58a6ff; border-radius: 12px; padding: 22px 28px; margin-bottom: 20px; }
.banner h1 { font-size: 1.6rem; font-weight: 700; color: #e6edf3; margin: 0 0 4px; }
.banner p  { font-size: 0.85rem; color: #8b949e; margin: 0; }

.card { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; }
.clabel { font-size: 0.68rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: #8b949e; margin-bottom: 10px; }

.issue { background: #0d1117; border-left: 3px solid #30363d; border-radius: 6px; padding: 10px 14px; margin-bottom: 7px; font-size: 0.85rem; color: #c9d1d9; line-height: 1.55; }
.r { border-left-color: #f85149; } .y { border-left-color: #d29922; } .b { border-left-color: #58a6ff; } .g { border-left-color: #3fb950; color: #3fb950; }

.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.68rem; font-weight: 600; }
.br { background: rgba(248,81,73,.1);  color: #f85149; border: 1px solid rgba(248,81,73,.25); }
.by { background: rgba(210,153,34,.1); color: #d29922; border: 1px solid rgba(210,153,34,.25); }
.bg { background: rgba(63,185,80,.1);  color: #3fb950; border: 1px solid rgba(63,185,80,.25); }
.bb { background: rgba(88,166,255,.1); color: #58a6ff; border: 1px solid rgba(88,166,255,.25); }

.verdict { border-radius: 10px; padding: 14px; text-align: center; font-size: 1.05rem; font-weight: 700; margin-bottom: 12px; }
.vg { background: rgba(63,185,80,.1);  border: 1px solid rgba(63,185,80,.3);  color: #3fb950; }
.vy { background: rgba(210,153,34,.1); border: 1px solid rgba(210,153,34,.3); color: #d29922; }
.vr { background: rgba(248,81,73,.1);  border: 1px solid rgba(248,81,73,.3);  color: #f85149; }

.ring { width: 72px; height: 72px; border-radius: 50%; border: 3px solid; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-family: 'JetBrains Mono'; font-size: 1.1rem; font-weight: 700; background: rgba(0,0,0,.2); }
.rlabel { text-align: center; font-size: 0.65rem; color: #8b949e; text-transform: uppercase; letter-spacing: .08em; }

.stTextArea textarea { background: #161b22 !important; color: #e6edf3 !important; border: 1px solid #21262d !important; border-radius: 8px !important; font-family: 'JetBrains Mono' !important; font-size: 0.82rem !important; }
[data-testid="stFileUploadDropzone"] { background: #161b22 !important; border: 1px dashed #30363d !important; border-radius: 8px !important; }
.stButton > button { background: #1f6feb !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stButton > button:hover { background: #388bfd !important; }
.stDownloadButton > button { background: #161b22 !important; color: #e6edf3 !important; border: 1px solid #30363d !important; border-radius: 8px !important; }
.stSelectbox > div > div { background: #161b22 !important; border-color: #21262d !important; color: #e6edf3 !important; }
.stTabs [data-baseweb="tab-list"] { background: #161b22 !important; border-radius: 8px !important; padding: 3px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #8b949e !important; border-radius: 6px !important; }
.stTabs [aria-selected="true"] { background: #0d1117 !important; color: #e6edf3 !important; }
hr { border-color: #21262d !important; }
label, span, p { color: #c9d1d9; }
</style>
""", unsafe_allow_html=True)


def get_client():
    try: return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except: st.error("⚠️ GROQ_API_KEY not found in Secrets."); st.stop()

def detect_lang(code, fname=""):
    for ext, l in {".py":"Python",".js":"JavaScript",".ts":"TypeScript",".java":"Java",
                   ".cpp":"C++",".c":"C",".go":"Go",".rs":"Rust",".html":"HTML",
                   ".css":"CSS",".sql":"SQL",".rb":"Ruby",".php":"PHP"}.items():
        if fname.endswith(ext): return l
    for kw, l in {"def ":"Python","function ":"JavaScript","public class":"Java",
                  "#include":"C++","SELECT ":"SQL","<html":"HTML"}.items():
        if kw in code[:400]: return l
    return "Unknown"

def line_count(code): return len([l for l in code.splitlines() if l.strip()])

PROMPT = """Senior engineer code review. Return ONLY valid JSON, no markdown.
{{
  "summary": "2-3 sentences",
  "quality_score": 0-100, "security_score": 0-100,
  "performance_score": 0-100, "maintainability_score": 0-100,
  "critical_issues": [], "medium_issues": [], "suggestions": [],
  "security_findings": [], "performance_findings": [], "best_practices": [],
  "verdict": "APPROVE|NEEDS REVIEW|REJECT"
}}
APPROVE: quality>=75 & no critical. REJECT: critical exists or score<40.
Code ({lang}):
```{code}```"""

def analyze(client, code, lang, model):
    raw = client.chat.completions.create(
        model=model,
        messages=[{"role":"user","content":PROMPT.format(lang=lang, code=code[:8000])}],
        temperature=0.3, max_tokens=2048
    ).choices[0].message.content.strip()
    if raw.startswith("```"): raw = raw.split("```")[1].lstrip("json")
    return json.loads(raw.strip().rstrip("```"))

def report(rev, code, lang):
    lines = [f"# Code Review — {datetime.now():%Y-%m-%d %H:%M}\nLanguage: {lang} | Lines: {line_count(code)}\n",
             f"## Summary\n{rev.get('summary','')}\n",
             f"## Scores\nQuality:{rev.get('quality_score')} Security:{rev.get('security_score')} Perf:{rev.get('performance_score')} Maintain:{rev.get('maintainability_score')}\n",
             f"## Verdict: {rev.get('verdict')}\n"]
    for h, k in [("Critical","critical_issues"),("Medium","medium_issues"),("Security","security_findings"),
                  ("Performance","performance_findings"),("Tips","suggestions")]:
        items = rev.get(k,[]) + (rev.get("best_practices",[]) if k=="suggestions" else [])
        lines.append(f"## {h}\n" + "\n".join(f"- {i}" for i in items or ["None"]))
    return "\n".join(lines)

def ring(label, score):
    color = "#3fb950" if score>=75 else "#d29922" if score>=50 else "#f85149"
    st.markdown(f'<div class="ring" style="border-color:{color};color:{color};">{score}</div>'
                f'<div class="rlabel">{label}</div>', unsafe_allow_html=True)

def issues(items, cls, empty="None found ✓"):
    if not items: st.markdown(f'<div class="issue g">{empty}</div>', unsafe_allow_html=True); return
    for i in items: st.markdown(f'<div class="issue {cls}">{i}</div>', unsafe_allow_html=True)


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.divider()
    model = st.selectbox("Model", ["llama-3.3-70b-versatile","llama-3.1-8b-instant","mixtral-8x7b-32768","gemma2-9b-it"])
    st.divider()
    st.markdown("**Scope**")
    for s in ["Security","Performance","Code quality","Best practices"]: st.checkbox(s, value=True)
    st.divider()
    st.markdown('<p style="font-size:.78rem;color:#8b949e;">Powered by <b style="color:#58a6ff;">Groq</b><br>Python·JS·TS·Java·C++·Go·Rust·SQL·HTML</p>', unsafe_allow_html=True)


# ── HEADER ──
st.markdown( 🤖 AI Code Reviewer
unsafe_allow_html=True)

left, right = st.columns([5, 4], gap="large")

with left:
    t1, t2 = st.tabs(["✏️ Paste Code", "📁 Upload File"])
    with t1:
        code_input = st.text_area("Code", height=340, placeholder="# Paste code here…", label_visibility="collapsed")
    with t2:
        up = st.file_uploader("File", label_visibility="collapsed",
             type=["py","js","ts","java","cpp","c","go","rs","rb","php","html","css","sql","txt"])
        fcode, fname = "", ""
        if up:
            try:
                fcode = up.read().decode("utf-8"); fname = up.name
                st.markdown(f'<span class="badge bb">{fname}</span> <span class="badge bg">{line_count(fcode)} lines</span>', unsafe_allow_html=True)
                st.code(fcode[:1500] + ("…" if len(fcode)>1500 else ""))
            except Exception as e: st.error(f"Can't read file: {e}")

    final = "\n\n".join(filter(None,[code_input,fcode])).strip()
    if final:
        lang = detect_lang(final, fname)
        st.markdown(f'<div style="margin:8px 0;display:flex;gap:6px;">'
                    f'<span class="badge bb">🔤 {lang}</span>'
                    f'<span class="badge bb">📝 {line_count(final)} lines</span>'
                    f'<span class="badge bb">💾 {len(final):,} chars</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🔍 Analyze Code", use_container_width=True)


if run:
    if not final: st.warning("Paste or upload code first."); st.stop()
    client = get_client()
    lang   = detect_lang(final, fname)
    with left:
        with st.spinner("Analyzing…"):
            t0 = time.time()
            try: rev = analyze(client, final, lang, model)
            except json.JSONDecodeError as e: st.error(f"Parse error: {e}"); st.stop()
            except Exception as e: st.error(f"Groq error: {e}"); st.stop()
    if not isinstance(rev, dict): st.error("Bad response format."); st.stop()
    st.session_state.update(rev=rev, code=final, lang=lang, t=time.time()-t0)


if "rev" in st.session_state:
    rev  = st.session_state["rev"]
    code = st.session_state["code"]
    lang = st.session_state["lang"]
    secs = st.session_state["t"]

    with right:
        st.markdown(f'<div style="text-align:right;margin-bottom:8px;"><span class="badge bg">⚡ {secs:.2f}s</span></div>', unsafe_allow_html=True)

        verdict = rev.get("verdict","UNKNOWN")
        vcls = {"APPROVE":("vg","🟢"),"NEEDS REVIEW":("vy","🟡"),"REJECT":("vr","🔴")}.get(verdict,("vy","🟡"))
        st.markdown(f'<div class="verdict {vcls[0]}">{vcls[1]} {verdict}</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="clabel">📊 Scores</div>', unsafe_allow_html=True)
        for col, label, key in zip(st.columns(4), ["Quality","Security","Perf","Maintain"],
                                   ["quality_score","security_score","performance_score","maintainability_score"]):
            with col: ring(label, rev.get(key, 0))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f'<div class="card"><div class="clabel">📝 Summary</div>'
                    f'<p style="font-size:.875rem;line-height:1.65;color:#c9d1d9;margin:0;">{rev.get("summary","")}</p></div>',
                    unsafe_allow_html=True)

        ta, tb, tc, td, te = st.tabs(["🔴 Critical","🟡 Medium","🔒 Security","⚡ Perf","💡 Tips"])
        with ta: issues(rev.get("critical_issues",[]),     "r")
        with tb: issues(rev.get("medium_issues",[]),       "y")
        with tc: issues(rev.get("security_findings",[]),   "r", "No security issues ✓")
        with td: issues(rev.get("performance_findings",[]),"y", "No performance concerns ✓")
        with te: issues(rev.get("suggestions",[]) + rev.get("best_practices",[]), "b", "Follows best practices ✓")

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("⬇️ Download Report",
            data=io.BytesIO(report(rev,code,lang).encode()),
            file_name=f"review_{datetime.now():%Y%m%d_%H%M%S}.txt",
            mime="text/plain", use_container_width=True)
