import streamlit as st
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv

from image_describer import describe_image
from video_describer import describe_video

# Load .env
load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediaIntel | AI Analysis Platform",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Corporate CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --navy:      #0B1220;
    --navy-mid:  #111B2E;
    --navy-card: #162035;
    --border:    #1E2E45;
    --accent:    #0EA5E9;
    --accent-dim:#0C3F5C;
    --success:   #10B981;
    --text-1:    #F1F5F9;
    --text-2:    #94A3B8;
    --text-3:    #4B6278;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--navy) !important;
    color: var(--text-1) !important;
}

/* ── Main container ── */
.main .block-container {
    padding: 2.5rem 2rem 4rem !important;
    max-width: 760px !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Logo bar ── */
.corp-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 2.5rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--border);
}
.corp-logo {
    width: 32px; height: 32px;
    background: var(--accent);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}
.corp-name {
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: var(--text-1);
}
.corp-name span { color: var(--accent); }
.corp-badge {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    color: var(--accent);
    background: var(--accent-dim);
    padding: 3px 10px;
    border-radius: 2px;
    text-transform: uppercase;
}

/* ── Page title ── */
.page-title {
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--text-1);
    margin: 0 0 0.35rem;
    letter-spacing: -0.02em;
}
.page-sub {
    font-size: 0.9rem;
    color: var(--text-2);
    margin-bottom: 2rem;
    font-weight: 300;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: var(--navy-card) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 6px !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileUploader"] label {
    color: var(--text-2) !important;
    font-size: 0.85rem !important;
}
[data-testid="stFileUploadDropzone"] {
    background: transparent !important;
    border: none !important;
}

/* ── Upload label override ── */
.upload-label {
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 0.4rem;
    display: block;
}

/* ── Info card ── */
.info-card {
    background: var(--navy-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 4px;
    padding: 1rem 1.25rem;
    margin: 1.25rem 0;
    font-size: 0.85rem;
    color: var(--text-2);
}
.info-card strong { color: var(--text-1); font-weight: 500; }

/* ── Stat row ── */
.stat-row {
    display: flex;
    gap: 1px;
    margin: 1.25rem 0;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
}
.stat-cell {
    flex: 1;
    background: var(--navy-card);
    padding: 0.85rem 1rem;
    text-align: center;
}
.stat-cell .val {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--accent);
}
.stat-cell .lbl {
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-top: 2px;
}

/* ── Primary button ── */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 0.55rem 1.5rem !important;
    transition: background 0.15s, opacity 0.15s !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: #0284c7 !important;
    opacity: 0.95 !important;
}

/* ── Result box ── */
.result-box {
    background: var(--navy-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.5rem;
    margin-top: 1.25rem;
}
.result-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--success);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.result-label::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    background: var(--success);
    border-radius: 50%;
}
.result-text {
    font-size: 0.92rem;
    line-height: 1.7;
    color: var(--text-1);
    font-weight: 300;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--navy-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.82rem !important;
    color: var(--text-2) !important;
    letter-spacing: 0.04em !important;
}

/* ── Error / warning ── */
.stAlert { border-radius: 4px !important; font-size: 0.85rem !important; }

/* ── Image ── */
[data-testid="stImage"] img {
    border-radius: 4px !important;
    border: 1px solid var(--border) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header bar ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="corp-header">
    <div class="corp-logo"></div>
    <div class="corp-name">Media<span>Intel</span></div>
    <div class="corp-badge">AI Platform v2.1</div>
</div>
""", unsafe_allow_html=True)

# ── Page title ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-title">Media Analysis</div>
<div class="page-sub">Upload an image or video file to generate an AI-powered content description.</div>
""", unsafe_allow_html=True)

# ── Capability stats ───────────────────────────────────────────────────────────
st.markdown("""
<div class="stat-row">
    <div class="stat-cell"><div class="val">LLaVA</div><div class="lbl">Vision Model</div></div>
    <div class="stat-cell"><div class="val">6</div><div class="lbl">Formats Supported</div></div>
    <div class="stat-cell"><div class="val">4</div><div class="lbl">Max Frames (Video)</div></div>
    <div class="stat-cell"><div class="val">Groq</div><div class="lbl">Inference Backend</div></div>
</div>
""", unsafe_allow_html=True)

# ── API key check ──────────────────────────────────────────────────────────────
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found — add it to your .env file and restart.")
    st.stop()

# ── File uploader ──────────────────────────────────────────────────────────────
st.markdown('<span class="upload-label">Select File</span>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="upload",
    type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
    label_visibility="collapsed"
)

# ── Processing ─────────────────────────────────────────────────────────────────
if uploaded_file:
    file_type = uploaded_file.type
    suffix = Path(uploaded_file.name).suffix
    file_size_kb = round(uploaded_file.size / 1024, 1)

    # File metadata card
    st.markdown(f"""
    <div class="info-card">
        <strong>{uploaded_file.name}</strong>&nbsp;&nbsp;·&nbsp;&nbsp;
        {file_type}&nbsp;&nbsp;·&nbsp;&nbsp;{file_size_kb} KB
    </div>
    """, unsafe_allow_html=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = Path(tmp.name)

    try:
        # ── IMAGE ──────────────────────────────────────────────────────────────
        if file_type.startswith("image"):
            st.image(uploaded_file, use_column_width=True)
            st.markdown("")

            if st.button("▶  Run Image Analysis"):
                with st.spinner("Processing image through vision model…"):
                    result = describe_image(
                        image_path=tmp_path,
                        api_key=api_key,
                        model="auto"
                    )
                st.markdown(f"""
                <div class="result-box">
                    <div class="result-label">Analysis Complete</div>
                    <div class="result-text">{result}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── VIDEO ──────────────────────────────────────────────────────────────
        elif file_type.startswith("video"):
            st.video(uploaded_file)
            st.markdown("")

            if st.button("▶  Run Video Analysis"):
                with st.spinner("Extracting frames and running inference…"):
                    result = describe_video(
                        video_path=tmp_path,
                        api_key=api_key,
                        model="auto",
                        max_frames=4
                    )

                st.markdown(f"""
                <div class="result-box">
                    <div class="result-label">Summary</div>
                    <div class="result-text">{result["description"]}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("Frame-by-frame breakdown"):
                    for i, frame in enumerate(result["frame_descriptions"], 1):
                        st.markdown(f"**Frame {i}** — {frame}")

        else:
            st.error("Unsupported file type. Please upload JPG, PNG, MP4, MOV, or AVI.")

    except Exception as e:
        st.error(f"Analysis failed: {e}")

    finally:
        if tmp_path.exists():
            tmp_path.unlink()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; font-size:0.72rem; color:#4B6278; letter-spacing:0.08em; font-family:'DM Mono',monospace;">
    MEDIAINTEL PLATFORM &nbsp;·&nbsp; POWERED BY GROQ &nbsp;·&nbsp; CONFIDENTIAL
</div>
""", unsafe_allow_html=True)