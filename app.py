import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from predict import load_model, predict
import tempfile
import os
import time
from datetime import datetime

os.environ["QT_QPA_PLATFORM"] = "offscreen"

st.set_page_config(
    page_title="HazardEye — Spill & Dustbin Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-base:      #07080d;
    --bg-surface:   #0e101a;
    --bg-card:      #13161f;
    --bg-hover:     #1a1e2b;
    --border:       rgba(255,255,255,0.08);
    --border-glow:  rgba(99,179,237,0.4);
    --accent:       #63b3ed;
    --accent-dim:   rgba(99,179,237,0.12);
    --danger:       #fc8181;
    --danger-dim:   rgba(252,129,129,0.12);
    --success:      #68d391;
    --success-dim:  rgba(104,211,145,0.12);
    --warning:      #f6ad55;
    --text-primary:   #e2e8f0;
    --text-secondary: #718096;
    --text-muted:     #4a5568;
    --mono: 'Space Mono', monospace;
    --sans: 'Outfit', sans-serif;
}

html, body, [class*="css"] { font-family: var(--sans); color: var(--text-primary); }

.stApp {
    background: var(--bg-base);
    background-image:
        radial-gradient(ellipse 80% 40% at 20% 0%,  rgba(99,179,237,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(252,129,129,0.04) 0%, transparent 60%);
}

section[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.8rem 2.2rem 3rem !important; max-width: 1400px !important; }

div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.5rem 1.8rem !important;
}

.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 1.5rem; border-bottom: 1px solid var(--border); margin-bottom: 1.8rem;
}
.brand-row { display: flex; align-items: center; gap: 0.8rem; }
.brand-icon {
    width: 42px; height: 42px; background: var(--accent-dim);
    border: 1px solid var(--border-glow); border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 1.3rem;
}
.brand-name { font-family: var(--mono); font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.brand-sub  { font-size: 0.7rem; color: var(--text-muted); letter-spacing: 1.5px; text-transform: uppercase; }
.status-pill {
    display: flex; align-items: center; gap: 0.5rem;
    background: var(--success-dim); border: 1px solid rgba(104,211,145,0.3);
    border-radius: 999px; padding: 0.32rem 0.9rem;
    font-size: 0.73rem; color: var(--success); font-family: var(--mono);
}
.status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--success); animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.4; transform:scale(0.75); }
}

.sec-label {
    font-family: var(--mono); font-size: 0.66rem; font-weight: 700;
    letter-spacing: 2.5px; text-transform: uppercase; color: var(--accent);
    display: flex; align-items: center; gap: 0.5rem;
    margin-bottom: 1rem; padding-bottom: 0.6rem; border-bottom: 1px solid var(--border);
}

[data-testid="stFileUploader"] {
    background: rgba(99,179,237,0.03) !important;
    border: 1.5px dashed rgba(99,179,237,0.22) !important;
    border-radius: 12px !important; transition: all 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--border-glow) !important;
    background: var(--accent-dim) !important;
}
[data-testid="stImage"] img {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important; width: 100% !important;
}
div[data-testid="stRadio"] > div { gap: 1rem; margin-bottom: 1rem; }
div[data-testid="stRadio"] label {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    font-family: var(--mono) !important;
}

.placeholder {
    background: rgba(255,255,255,0.015); border: 1.5px dashed rgba(255,255,255,0.06);
    border-radius: 12px; height: 280px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: var(--text-muted); font-size: 0.85rem; gap: 0.5rem; margin-top: 0.5rem;
}
.placeholder-icon { font-size: 2.6rem; opacity: 0.3; }

.meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.9rem; }
.meta-tile { background: var(--bg-hover); border: 1px solid var(--border); border-radius: 8px; padding: 0.55rem 0.8rem; }
.meta-key  { font-size: 0.62rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; }
.meta-val  { font-family: var(--mono); font-size: 0.72rem; color: var(--text-secondary); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.result-hazard, .result-clear {
    border-radius: 12px; padding: 1.2rem 1.4rem;
    display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1rem;
    animation: slideIn 0.3s ease;
}
.result-hazard { background: var(--danger-dim); border: 1px solid rgba(252,129,129,0.3); border-left: 4px solid var(--danger); }
.result-clear  { background: var(--success-dim); border: 1px solid rgba(104,211,145,0.3); border-left: 4px solid var(--success); }
@keyframes slideIn { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
.res-icon  { font-size: 1.8rem; line-height: 1; margin-top: 2px; }
.res-title { font-family: var(--mono); font-size: 0.9rem; font-weight: 700; margin-bottom: 0.25rem; }
.result-hazard .res-title { color: var(--danger); }
.result-clear  .res-title { color: var(--success); }
.res-desc { font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5; }

.chip-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
.chip { display: inline-flex; align-items: center; gap: 0.35rem; border-radius: 7px; padding: 0.35rem 0.7rem; font-family: var(--mono); font-size: 0.68rem; font-weight: 700; }
.chip-on  { background: var(--success-dim); border: 1px solid rgba(104,211,145,0.35); color: var(--success); }
.chip-off { background: rgba(255,255,255,0.03); border: 1px solid var(--border); color: var(--text-muted); text-decoration: line-through; }

.m-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1rem; }
.m-tile { background: var(--bg-hover); border: 1px solid var(--border); border-radius: 10px; padding: 0.8rem 0.9rem; text-align: center; }
.m-num  { font-family: var(--mono); font-size: 1.55rem; font-weight: 700; line-height: 1; }
.m-lbl  { font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0.25rem; }
.c-danger  { color: var(--danger); }
.c-success { color: var(--success); }
.c-accent  { color: var(--accent); }
.c-warning { color: var(--warning); }

.risk-bar-wrap { background: var(--bg-hover); border: 1px solid var(--border); border-radius: 10px; padding: 0.8rem 1rem; }
.risk-bar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.45rem; }
.risk-bar-track  { height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.risk-bar-fill   { height: 100%; border-radius: 3px; transition: width 0.4s ease; }
.risk-note       { margin-top: 0.35rem; font-size: 0.67rem; color: var(--text-muted); }

.hist-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.6rem 0.75rem; border-radius: 8px; margin-bottom: 0.4rem;
    border: 1px solid var(--border); background: var(--bg-hover); transition: border-color 0.15s;
}
.hist-item:hover { border-color: rgba(99,179,237,0.3); }
.hist-name { font-family: var(--mono); font-size: 0.68rem; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 110px; }
.hist-time { font-size: 0.65rem; color: var(--text-muted); margin-top: 1px; }
.badge-h { background: var(--danger-dim); border: 1px solid rgba(252,129,129,0.35); color: var(--danger); border-radius: 5px; padding: 0.12rem 0.45rem; font-family: var(--mono); font-size: 0.62rem; font-weight: 700; white-space: nowrap; }
.badge-c { background: var(--success-dim); border: 1px solid rgba(104,211,145,0.35); color: var(--success); border-radius: 5px; padding: 0.12rem 0.45rem; font-family: var(--mono); font-size: 0.62rem; font-weight: 700; white-space: nowrap; }

.guide-row  { display: flex; align-items: flex-start; gap: 0.6rem; margin-bottom: 0.7rem; }
.guide-dot  { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.guide-title { font-size: 0.8rem; color: var(--text-primary); font-weight: 600; }
.guide-desc  { font-size: 0.75rem; color: var(--text-muted); margin-top: 1px; line-height: 1.4; }
.guide-note  { margin-top: 0.6rem; padding-top: 0.7rem; border-top: 1px solid var(--border); font-size: 0.72rem; color: var(--text-muted); line-height: 1.5; }

.sidebar-sec { font-family: var(--mono); font-size: 0.63rem; letter-spacing: 2px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.55rem; }
.tip-row { display: flex; gap: 0.5rem; margin-bottom: 0.55rem; font-size: 0.79rem; color: var(--text-secondary); }
.tip-dot { width: 5px; height: 5px; background: var(--accent); border-radius: 50%; margin-top: 6px; flex-shrink: 0; }

/* Notification toast styling */
.notif-toast {
    border-radius: 12px; padding: 1rem 1.2rem;
    display: flex; align-items: flex-start; gap: 0.8rem;
    margin-bottom: 0.8rem; animation: slideIn 0.3s ease;
    font-family: var(--sans);
}
.notif-toast.hazard {
    background: var(--danger-dim);
    border: 1px solid rgba(252,129,129,0.35);
    border-left: 4px solid var(--danger);
}
.notif-toast.clear {
    background: var(--success-dim);
    border: 1px solid rgba(104,211,145,0.35);
    border-left: 4px solid var(--success);
}
.notif-icon-sm { font-size: 1.2rem; line-height: 1; flex-shrink: 0; margin-top: 2px; }
.notif-title { font-family: var(--mono); font-size: 0.75rem; font-weight: 700; margin-bottom: 2px; }
.notif-toast.hazard .notif-title { color: var(--danger); }
.notif-toast.clear  .notif-title { color: var(--success); }
.notif-msg { font-size: 0.73rem; color: var(--text-secondary); line-height: 1.4; }
.voice-status {
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-family: var(--mono); font-size: 0.63rem; margin-top: 0.4rem;
    padding: 0.18rem 0.55rem; border-radius: 999px;
    background: rgba(99,179,237,0.12); color: var(--accent);
    border: 1px solid rgba(99,179,237,0.25);
}
.voice-dot-anim { display: inline-flex; gap: 2px; }
.voice-dot-anim span {
    width: 3px; height: 3px; border-radius: 50%;
    background: var(--accent); display: inline-block;
    animation: vbounce 0.8s infinite;
}
.voice-dot-anim span:nth-child(2) { animation-delay: 0.13s; }
.voice-dot-anim span:nth-child(3) { animation-delay: 0.26s; }
@keyframes vbounce { 0%,80%,100%{transform:scaleY(1)} 40%{transform:scaleY(1.8)} }

.stSpinner > div { border-top-color: var(--accent) !important; }
.stButton > button {
    background: var(--accent-dim) !important; border: 1px solid var(--border-glow) !important;
    color: var(--accent) !important; border-radius: 8px !important;
    font-family: var(--mono) !important; font-size: 0.75rem !important;
    padding: 0.4rem 1rem !important; transition: all 0.15s !important;
}
.stButton > button:hover { background: rgba(99,179,237,0.22) !important; border-color: var(--accent) !important; }
div[data-testid="stMetric"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; padding: 0.65rem 0.9rem !important; }
div[data-testid="stMetricValue"] { font-family: var(--mono) !important; color: var(--accent) !important; }
div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.7rem !important; }
hr { border-color: var(--border) !important; }
.stToggle label { color: var(--text-secondary) !important; font-size: 0.82rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Notification helper ────────────────────────────────────────────────────────
def trigger_alert(result: int, volume: float = 0.9, voice_enabled: bool = True,
                  browser_enabled: bool = True, alert_on_clear: bool = True):
    """
    Injects a JS snippet that:
      - Speaks the result via Web Speech API
      - Shows a browser push notification
    Only fires when conditions are met.
    """
    if result == 0 and not alert_on_clear:
        return

    if result == 1:
        voice_text   = "Warning! Hazard detected. Both a dustbin and a spill are present. Immediate attention is required."
        notif_title  = "HazardEye — Hazard Detected"
        notif_body   = "Both a dustbin and a spill were found. Immediate action needed."
    else:
        voice_text   = "All clear. No hazard detected. The area appears safe."
        notif_title  = "HazardEye — All Clear"
        notif_body   = "No concurrent dustbin and spill detected. Area is safe."

    voice_flag   = "true" if voice_enabled   else "false"
    browser_flag = "true" if browser_enabled else "false"

    js = f"""
    <script>
    (function() {{
        const voiceEnabled   = {voice_flag};
        const browserEnabled = {browser_flag};
        const volume         = {volume};

        // ── Voice ──
        if (voiceEnabled && window.speechSynthesis) {{
            window.speechSynthesis.cancel();
            const utt = new SpeechSynthesisUtterance("{voice_text}");
            utt.volume = volume;
            utt.rate   = 0.95;
            utt.pitch  = 1;
            // Prefer an English voice if available
            const voices = window.speechSynthesis.getVoices();
            const enVoice = voices.find(v => v.lang.startsWith('en'));
            if (enVoice) utt.voice = enVoice;
            window.speechSynthesis.speak(utt);
        }}

        // ── Browser notification ──
        if (browserEnabled && 'Notification' in window) {{
            function fire() {{
                new Notification("{notif_title}", {{ body: "{notif_body}" }});
            }}
            if (Notification.permission === 'granted') {{
                fire();
            }} else if (Notification.permission !== 'denied') {{
                Notification.requestPermission().then(p => {{
                    if (p === 'granted') fire();
                }});
            }}
        }}
    }})();
    </script>
    """
    components.html(js, height=0)


# ── Session state ──────────────────────────────────────────────────────────────
if "history"       not in st.session_state: st.session_state.history       = []
if "total_scans"   not in st.session_state: st.session_state.total_scans   = 0
if "total_hazards" not in st.session_state: st.session_state.total_hazards = 0


# ── Model ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return load_model()

with st.spinner("Initialising HazardEye model…"):
    model = get_model()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-sec">⚙ Configuration</div>', unsafe_allow_html=True)
    show_metadata = st.toggle("Show image metadata", value=True)
    show_history  = st.toggle("Show scan history",   value=True)
    st.markdown("---")

    st.markdown('<div class="sidebar-sec">🔔 Notifications</div>', unsafe_allow_html=True)
    voice_enabled   = st.toggle("Voice alerts",           value=True)
    browser_enabled = st.toggle("Browser notifications",  value=True)
    alert_on_clear  = st.toggle("Announce 'all clear'",   value=True)
    alert_volume    = st.slider(
        "Alert volume", 0.0, 1.0, 0.9, 0.05,
        format="%.0f%%",
        help="Controls how loud the voice alert is"
    )
    # Show a small live preview button
    if st.button("🔊 Test voice"):
        trigger_alert(
            result=1,
            volume=alert_volume,
            voice_enabled=voice_enabled,
            browser_enabled=False,   # don't spam browser notif on test
            alert_on_clear=True,
        )
    st.markdown("---")

    st.markdown('<div class="sidebar-sec">📋 Tips</div>', unsafe_allow_html=True)
    for tip in [
        "Upload a clear, well-lit image",
        "Ensure dustbin & spill are in frame",
        "Higher resolution = better detection",
        "JPG, PNG, BMP, WEBP supported",
        "Check history panel for past scans",
    ]:
        st.markdown(f'<div class="tip-row"><div class="tip-dot"></div><span>{tip}</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sidebar-sec">📊 Session stats</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.metric("Scans",   st.session_state.total_scans)
    with c2: st.metric("Hazards", st.session_state.total_hazards)

    if st.session_state.total_scans > 0:
        rate = st.session_state.total_hazards / st.session_state.total_scans
        st.progress(rate, text=f"Hazard rate: {round(rate*100)}%")

    if st.button("🗑  Clear history"):
        st.session_state.history       = []
        st.session_state.total_scans   = 0
        st.session_state.total_hazards = 0
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.68rem;color:var(--text-muted);text-align:center;font-family:\'Space Mono\',monospace;">HazardEye v2.0 · YOLOv8</div>',
        unsafe_allow_html=True,
    )


# ── Top bar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="brand-row">
    <div class="brand-icon">🔍</div>
    <div>
      <div class="brand-name">HazardEye</div>
      <div class="brand-sub">Spill &amp; Dustbin Detector</div>
    </div>
  </div>
  <div class="status-pill"><div class="status-dot"></div>MODEL READY</div>
</div>
""", unsafe_allow_html=True)


# ── Three columns ──────────────────────────────────────────────────────────────
col_upload, col_results, col_history = st.columns([5, 5, 3], gap="medium")


# ══════════════════════════════════════════════
# COLUMN 1 — Upload & Camera
# ══════════════════════════════════════════════
with col_upload:
    st.markdown('<div class="sec-label">📁 &nbsp;INPUT SOURCE</div>', unsafe_allow_html=True)

    input_type = st.radio(
        "Select Input Method",
        ["Upload File", "Use Camera"],
        horizontal=True,
        label_visibility="collapsed",
    )

    uploaded_file = None

    if input_type == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
            label_visibility="collapsed",
        )
    else:
        uploaded_file = st.camera_input("Take a snapshot", label_visibility="collapsed")

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, use_container_width=True)

        if show_metadata:
            w, h    = img.size
            size_kb = round(uploaded_file.size / 1024, 1)
            aspect  = f"{round(w/h, 2)}:1"
            fname   = getattr(uploaded_file, "name", "camera_shot.jpg")
            st.markdown(f"""
            <div class="meta-grid">
              <div class="meta-tile"><div class="meta-key">Source</div>
                <div class="meta-val" title="{fname}">{fname}</div></div>
              <div class="meta-tile"><div class="meta-key">Dimensions</div>
                <div class="meta-val">{w} × {h} px</div></div>
              <div class="meta-tile"><div class="meta-key">File size</div>
                <div class="meta-val">{size_kb} KB</div></div>
              <div class="meta-tile"><div class="meta-key">Aspect ratio</div>
                <div class="meta-val">{aspect}</div></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        placeholder_text = "Drop image here"     if input_type == "Upload File" else "Ready to capture"
        placeholder_icon = "🖼️"                  if input_type == "Upload File" else "📸"
        st.markdown(f"""
        <div class="placeholder">
          <span class="placeholder-icon">{placeholder_icon}</span>
          <span>{placeholder_text}</span>
          <span style="font-size:0.73rem;">Waiting for input...</span>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# COLUMN 2 — Results
# ══════════════════════════════════════════════
with col_results:
    st.markdown('<div class="sec-label">🎯 &nbsp;DETECTION RESULTS</div>', unsafe_allow_html=True)

    if uploaded_file is None:
        st.markdown("""
        <div class="placeholder">
          <span class="placeholder-icon">🧠</span>
          <span>Awaiting image input</span>
          <span style="font-size:0.73rem;">Results appear here after upload</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(tmp.name)
        tmp.close()

        with st.spinner("Running inference…"):
            t0      = time.time()
            result  = predict(model, tmp.name)
            elapsed = round((time.time() - t0) * 1000)

        os.unlink(tmp.name)

        is_hazard = (result == 1)

        # ── Update session state ──
        st.session_state.total_scans   += 1
        st.session_state.total_hazards += int(is_hazard)
        st.session_state.history.insert(0, {
            "name":       getattr(uploaded_file, "name", "camera_shot.jpg"),
            "result":     result,
            "time":       datetime.now().strftime("%H:%M:%S"),
            "elapsed_ms": elapsed,
        })
        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[:20]

        # ── 🔔 Fire voice + browser notification ──
        trigger_alert(
            result          = result,
            volume          = alert_volume,
            voice_enabled   = voice_enabled,
            browser_enabled = browser_enabled,
            alert_on_clear  = alert_on_clear,
        )

        # ── Result banner ──
        if is_hazard:
            st.markdown("""
            <div class="result-hazard">
              <div class="res-icon">🚨</div>
              <div>
                <div class="res-title">HAZARD DETECTED</div>
                <div class="res-desc">Both a dustbin and a spill were found. Immediate attention may be needed.</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="result-clear">
              <div class="res-icon">✅</div>
              <div>
                <div class="res-title">ALL CLEAR</div>
                <div class="res-desc">No concurrent dustbin + spill condition detected. The area appears safe.</div>
              </div>
            </div>""", unsafe_allow_html=True)

        # ── Voice status indicator ──
        if voice_enabled and (is_hazard or alert_on_clear):
            st.markdown("""
            <div class="notif-toast hazard" style="padding:0.6rem 0.9rem;margin-bottom:0.8rem;" id="voice-notif-row">
              <div class="notif-icon-sm">🔊</div>
              <div>
                <div class="notif-title">VOICE ALERT TRIGGERED</div>
                <div class="voice-status">
                  <div class="voice-dot-anim"><span></span><span></span><span></span></div>
                  Speaking alert…
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        if browser_enabled and (is_hazard or alert_on_clear):
            st.markdown("""
            <div class="notif-toast clear" style="padding:0.5rem 0.9rem;margin-bottom:0.8rem;">
              <div class="notif-icon-sm">🔔</div>
              <div>
                <div class="notif-title">BROWSER NOTIFICATION SENT</div>
                <div class="notif-msg">Check your OS notification tray.</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Detection chips ──
        d_chip = '<span class="chip chip-on">✔ DUSTBIN</span>'  if is_hazard else '<span class="chip chip-off">✘ DUSTBIN</span>'
        s_chip = '<span class="chip chip-on">✔ SPILL</span>'    if is_hazard else '<span class="chip chip-off">✘ SPILL</span>'
        st.markdown(f'<div class="chip-row">{d_chip}{s_chip}</div>', unsafe_allow_html=True)

        # ── Metric tiles ──
        sc = "c-danger" if is_hazard else "c-success"
        st.markdown(f"""
        <div class="m-grid">
          <div class="m-tile"><div class="m-num {sc}">{result}</div><div class="m-lbl">Prediction</div></div>
          <div class="m-tile"><div class="m-num c-accent">{elapsed}ms</div><div class="m-lbl">Inference time</div></div>
          <div class="m-tile"><div class="m-num c-accent">{st.session_state.total_scans}</div><div class="m-lbl">Session scans</div></div>
          <div class="m-tile"><div class="m-num c-warning">{st.session_state.total_hazards}</div><div class="m-lbl">Hazards found</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Risk bar ──
        if st.session_state.total_scans > 0:
            rate  = st.session_state.total_hazards / st.session_state.total_scans
            rlbl  = "HIGH" if rate > 0.6 else "MEDIUM" if rate > 0.3 else "LOW"
            rcol  = "var(--danger)" if rate > 0.6 else "var(--warning)" if rate > 0.3 else "var(--success)"
            st.markdown(f"""
            <div class="risk-bar-wrap">
              <div class="risk-bar-header">
                <span style="font-size:0.66rem;text-transform:uppercase;letter-spacing:1.5px;color:var(--text-muted);">Session risk level</span>
                <span style="font-family:var(--mono);font-size:0.73rem;font-weight:700;color:{rcol};">{rlbl}</span>
              </div>
              <div class="risk-bar-track">
                <div class="risk-bar-fill" style="width:{int(rate*100)}%;background:{rcol};"></div>
              </div>
              <div class="risk-note">{int(rate*100)}% of scans flagged as hazardous this session</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# COLUMN 3 — History + Guide
# ══════════════════════════════════════════════
with col_history:
    st.markdown('<div class="sec-label">🕒 &nbsp;SCAN HISTORY</div>', unsafe_allow_html=True)

    if not show_history:
        st.markdown('<div style="color:var(--text-muted);font-size:0.8rem;">History hidden — enable in sidebar.</div>', unsafe_allow_html=True)
    elif not st.session_state.history:
        st.markdown("""
        <div class="placeholder" style="height:180px;">
          <span class="placeholder-icon">📋</span>
          <span>No scans yet</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        for e in st.session_state.history:
            badge = '<span class="badge-h">HAZARD</span>' if e["result"] == 1 else '<span class="badge-c">CLEAR</span>'
            st.markdown(f"""
            <div class="hist-item">
              <div>
                <div class="hist-name" title="{e['name']}">{e['name']}</div>
                <div class="hist-time">{e['time']} · {e['elapsed_ms']}ms</div>
              </div>
              {badge}
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr style="margin:1.2rem 0;">', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">📖 &nbsp;LABEL GUIDE</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="guide-row">
      <div class="guide-dot" style="background:var(--success);"></div>
      <div><div class="guide-title">Class 0 — Dustbin</div>
           <div class="guide-desc">Waste receptacle detected in frame.</div></div>
    </div>
    <div class="guide-row">
      <div class="guide-dot" style="background:var(--danger);"></div>
      <div><div class="guide-title">Class 1 — Spill</div>
           <div class="guide-desc">Liquid or solid spill hazard detected.</div></div>
    </div>
    <div class="guide-note">
      Prediction = <span style="color:var(--danger);font-family:var(--mono);">1 (HAZARD)</span>
      only when <em>both</em> classes co-occur in the same image.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="margin:1.2rem 0;">', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">🔔 &nbsp;ALERT STATUS</div>', unsafe_allow_html=True)
    voice_icon   = "🟢" if voice_enabled   else "🔴"
    browser_icon = "🟢" if browser_enabled else "🔴"
    clear_icon   = "🟢" if alert_on_clear  else "🔴"
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;gap:0.4rem;font-size:0.75rem;color:var(--text-secondary);font-family:var(--mono);">
      <div>{voice_icon} Voice alerts &nbsp;·&nbsp; Vol {int(alert_volume*100)}%</div>
      <div>{browser_icon} Browser notifications</div>
      <div>{clear_icon} Announce all-clear</div>
    </div>
    """, unsafe_allow_html=True)