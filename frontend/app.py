import streamlit as st
import requests


# PAGE CONFIG
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.main {
    background-color: #0f1117;
    color: white;
}

.block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    color: white;
}

.card {
    background-color: #161a25;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #2a2f3a;
    margin-bottom: 15px;
}

textarea {
    background-color: #0f1117 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# HEADER
st.title(" AI Code Reviewer Dashboard")

# SIDEBAR

with st.sidebar:
    st.header("⚙️ Settings")

    st.markdown("###  Features")
    st.markdown("""
    - Bug Detection  
    - Security Review  
    - Performance Analysis  
    - Code Quality Review  
    """)

# MAIN INPUT
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(" Input Code for Review")

    # TEXT INPUT
    code_input = st.text_area(
        " Paste your code here",
        height=300,
        placeholder="Paste Python / JS / Java / C++ / SQL code here..."
    )

    # FILE UPLOAD
    uploaded_file = st.file_uploader(
        "📁 Or upload a code file",
        type=["py", "js", "java", "cpp", "txt", "ts", "html", "css"]
    )

    file_content = ""

    if uploaded_file is not None:
        try:
            file_content = uploaded_file.read().decode("utf-8")
            st.code(file_content, language="python")
        except Exception:
            st.error("Failed to read file")

    # SAFE MERGE
    final_code = "\n\n".join(filter(None, [code_input, file_content]))

    # ANALYZE BUTTON
    analyze = st.button(" Analyze Code", use_container_width=True)

    if analyze:

        if not final_code.strip():
            st.warning("Please paste or upload code first")
            st.stop()

        # SAFE REVIEW EXTRACTION
        review = data.get("review", {});

        #  CRITICAL SAFETY CHECKS
        if isinstance(review, str):
            st.error(" Backend returned invalid string format")
            st.stop()

        if not isinstance(review, dict):
            st.error(" Invalid response from backend")
            st.stop()

        # OUTPUT HEADER
        st.markdown("## 📊 Review Result")

        # SUMMARY
        st.markdown("##  Summary")
        st.info(review.get("summary", "No summary provided"))

        # CRITICAL ISSUES
    
        st.markdown("##  Critical Issues")
        critical = review.get("critical_issues", [])

        if critical:
            for item in critical:
                st.error(item)
        else:
            st.success("No critical issues found")

        # MEDIUM ISSUES
        st.markdown("##  Medium Issues")
        medium = review.get("medium_issues", [])

        if medium:
            for item in medium:
                st.warning(item)
        else:
            st.success("No medium issues found")

        # SUGGESTIONS
        st.markdown("##  Suggestions")
        suggestions = review.get("suggestions", [])

        if suggestions:
            for item in suggestions:
                st.info(item)
        else:
            st.info("No suggestions")

        # VERDICT
        verdict = review.get("verdict", "UNKNOWN")

        if verdict == "APPROVE":
            st.markdown(f"### 🟢 Final Verdict: {verdict}")
        elif verdict == "REJECT":
            st.markdown(f"### 🔴 Final Verdict: {verdict}")
        else:
            st.markdown(f"### 🟡 Final Verdict: {verdict}")

