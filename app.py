import ipaddress
import re
from urllib.parse import urlsplit

import streamlit as st
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

MODEL_NAME = "CrabInHoney/urlbert-tiny-v4-phishing-classifier"

st.set_page_config(
    page_title="PhishGuard AI | URL Scanner",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Lightweight custom styling: a polished, standard dashboard look built on Streamlit.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
      --pg-bg: #08111f;
      --pg-panel: #101c2d;
      --pg-panel-2: #132238;
      --pg-border: #23344b;
      --pg-text: #eff5ff;
      --pg-muted: #9db0c9;
      --pg-teal: #41d6c3;
      --pg-red: #ff657a;
      --pg-yellow: #f3c969;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: radial-gradient(ellipse at 70% -20%, #17304b 0%, var(--pg-bg) 55%); color: var(--pg-text); }
    [data-testid="stHeader"] { background: rgba(8,17,31,0.75); }
    [data-testid="stSidebar"] { background: #0b1727; border-right: 1px solid var(--pg-border); }
    [data-testid="stSidebar"] * { color: var(--pg-text); }
    .block-container { max-width: 1240px; padding-top: 2.1rem; padding-bottom: 3rem; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.035em; color: var(--pg-text); }
    h1 { font-size: 2.7rem !important; line-height: 1.1 !important; }
    h2 { font-size: 1.45rem !important; }
    p, label, li { color: var(--pg-text); }
    .pg-brand { display:flex; align-items:center; gap:12px; margin-bottom: 1.1rem; }
    .pg-logo { display:flex; align-items:center; justify-content:center; width:46px; height:46px; border-radius:14px; background:linear-gradient(135deg,#1b827b,#1d526b); border:1px solid #38b8ac; font-size:23px; box-shadow:0 0 30px rgba(65,214,195,.13); }
    .pg-brand-name { font-family:'Space Grotesk',sans-serif; font-size:1.12rem; font-weight:700; line-height:1.15; }
    .pg-brand-sub { font-size:.77rem; color:var(--pg-muted); margin-top:4px; }
    .pg-kicker { color:var(--pg-teal); text-transform:uppercase; font-size:.72rem; letter-spacing:.16em; font-weight:700; margin-bottom:.65rem; }
    .pg-subtitle { color:var(--pg-muted); font-size:1.02rem; max-width:760px; line-height:1.65; }
    .pg-panel { background:linear-gradient(145deg,rgba(19,34,56,.96),rgba(13,25,42,.97)); border:1px solid var(--pg-border); border-radius:18px; padding:22px 24px; }
    .pg-label { color:var(--pg-muted); font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; font-weight:700; margin-bottom:9px; }
    .pg-verdict { border-radius:16px; padding:19px 21px; margin: 8px 0 18px 0; border:1px solid; }
    .pg-verdict-danger { background:rgba(255,101,122,.09); border-color:rgba(255,101,122,.45); }
    .pg-verdict-safe { background:rgba(65,214,195,.08); border-color:rgba(65,214,195,.38); }
    .pg-verdict-title { font-family:'Space Grotesk',sans-serif; font-size:1.22rem; font-weight:700; margin-bottom:5px; }
    .pg-verdict-desc { color:var(--pg-muted); font-size:.9rem; line-height:1.5; }
    .pg-mini { color:var(--pg-muted); font-size:.83rem; line-height:1.55; }
    .pg-rule { border:0; border-top:1px solid var(--pg-border); margin:1.2rem 0; }
    .pg-step { display:flex; gap:11px; align-items:flex-start; margin:.9rem 0; }
    .pg-step-num { display:flex; width:26px; height:26px; flex:0 0 26px; align-items:center; justify-content:center; border-radius:9px; background:#183c4b; color:var(--pg-teal); font-weight:700; font-size:.8rem; }
    .pg-footer { color:#8195af; font-size:.78rem; border-top:1px solid var(--pg-border); margin-top:2rem; padding-top:1.2rem; }
    div[data-testid="stTextInput"] input { background:#091525 !important; border:1px solid #2c405b !important; color:#eff5ff !important; border-radius:11px !important; min-height:48px; }
    div[data-testid="stTextInput"] input:focus { border-color:var(--pg-teal) !important; box-shadow:0 0 0 1px var(--pg-teal) !important; }
    div[data-testid="stButton"] > button[kind="primary"], div[data-testid="stFormSubmitButton"] > button { background:linear-gradient(90deg,#24a99c,#2cbdaf) !important; color:#04151b !important; font-weight:700 !important; border:0 !important; min-height:46px; border-radius:11px !important; }
    div[data-testid="stButton"] > button { border-radius:10px; border:1px solid #30445f; background:#132238; color:#eaf2ff; }
    div[data-testid="stButton"] > button:hover { border-color:var(--pg-teal); color:white; }
    div[data-testid="stProgressBar"] > div > div { background:var(--pg-teal); }
    [data-testid="stMetric"] { background:#101c2d; border:1px solid var(--pg-border); padding:14px 16px; border-radius:13px; }
    [data-testid="stMetricLabel"] { color:var(--pg-muted) !important; }
    [data-testid="stMetricValue"] { color:var(--pg-text) !important; }
    a { color:var(--pg-teal) !important; }
    .stAlert { border-radius:12px; }
    code { color:#7ce7dc !important; }
    @media (max-width: 700px) { h1 { font-size:2rem !important; } .block-container { padding-left:1rem; padding-right:1rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def normalize_url(raw_url: str) -> str:
    """Trim input and add HTTPS when the user enters only a domain/path."""
    url = raw_url.strip()
    if not url:
        raise ValueError("Enter a URL or domain name first.")
    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = "https://" + url
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Enter a valid web address, such as example.com or https://example.com/path.")
    return url


def get_warning_signs(url: str) -> list[str]:
    """Simple teaching checks. These are not an explanation of the AI model."""
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    flags = []

    if len(url) > 75:
        flags.append("Long URL — more than 75 characters")
    if "@" in parsed.netloc:
        flags.append("Contains '@' in the address — this can obscure the intended destination")
    try:
        ipaddress.ip_address(host)
        flags.append("Uses an IP address instead of a regular domain name")
    except ValueError:
        pass
    if "xn--" in host.lower():
        flags.append("Contains punycode, used for some internationalized domain names")
    if host.count("-") >= 2:
        flags.append("Several hyphens in the hostname")
    if len(host.split(".")) >= 4:
        flags.append("Many hostname sections or subdomains")
    if re.search(r"(login|verify|password|account|billing|update|secure)", url, re.I):
        flags.append("Contains a credential-themed word (not suspicious by itself)")
    if parsed.scheme.lower() != "https":
        flags.append("Does not use HTTPS — a weak signal only")
    return flags


def friendly_class(label: str) -> str:
    label_upper = str(label).upper()
    label_text = str(label).lower()
    # The model card maps LABEL_0 to good/non-phishing and LABEL_1 to fish/phishing.
    if label_upper in {"LABEL_1", "1"} or any(x in label_text for x in ("phish", "fish", "malicious")):
        return "Likely phishing"
    if label_upper in {"LABEL_0", "0"} or any(x in label_text for x in ("good", "benign", "legitimate", "non-phishing")):
        return "Likely legitimate"
    return f"Model class {label}"


@st.cache_resource(show_spinner=False)
def load_classifier():
    """Download and cache the small pretrained model once per app session."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    device = 0 if torch.cuda.is_available() else -1
    classifier = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        device=device,
        top_k=None,
    )
    return classifier, ("GPU" if device >= 0 else "CPU")


def run_classification(classifier, url: str) -> list[dict]:
    output = classifier(url)
    # Transformers versions may return either a list of dictionaries or a nested list.
    if output and isinstance(output[0], list):
        output = output[0]
    if not output or not all("label" in item and "score" in item for item in output):
        raise RuntimeError("The model returned an unexpected response format. Please check the installed Transformers version.")
    return sorted(output, key=lambda item: float(item["score"]), reverse=True)


# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div class="pg-brand">
          <div class="pg-logo">🛡️</div>
          <div><div class="pg-brand-name">PhishGuard AI</div><div class="pg-brand-sub">URL threat analysis</div></div>
        </div>
        <hr class="pg-rule" />
        <div class="pg-kicker">About this demo</div>
        <div class="pg-mini">A classroom demonstration of AI as a cybersecurity defender. Paste a URL as text; the app does not visit or open that site.</div>
        <hr class="pg-rule" />
        <div class="pg-kicker">How it works</div>
        <div class="pg-step"><div class="pg-step-num">1</div><div><b>Input</b><div class="pg-mini">Enter a URL or domain.</div></div></div>
        <div class="pg-step"><div class="pg-step-num">2</div><div><b>AI analysis</b><div class="pg-mini">A pretrained URL classifier scores the text.</div></div></div>
        <div class="pg-step"><div class="pg-step-num">3</div><div><b>Review</b><div class="pg-mini">Compare the model result with separate URL warning checks.</div></div></div>
        <hr class="pg-rule" />
        <div class="pg-kicker">Model</div>
        <div class="pg-mini"><b>URLBERT-Tiny v4</b><br/>Runs on your computer after the initial model download.</div>
        <div class="pg-mini" style="margin-top:8px;"><a href="https://huggingface.co/CrabInHoney/urlbert-tiny-v4-phishing-classifier" target="_blank">View model card ↗</a></div>
        <hr class="pg-rule" />
        <div class="pg-mini">Educational prototype only. A score is not a safety guarantee and must not be the sole basis for security decisions.</div>
        """,
        unsafe_allow_html=True,
    )

# Main header
st.markdown('<div class="pg-kicker">AI • Cybersecurity • Live demonstration</div>', unsafe_allow_html=True)
st.title("Phishing URL Classifier")
st.markdown(
    '<div class="pg-subtitle">Inspect a suspicious link with a pretrained AI model. See the predicted category, the model scores, and a separate checklist of common URL warning signs.</div>',
    unsafe_allow_html=True,
)
st.write("")

# Local status strip
status_cols = st.columns([1, 1, 1.6])
with status_cols[0]:
    st.markdown('<div class="pg-panel"><div class="pg-label">Mode</div><b>Local AI analysis</b><div class="pg-mini">No website is opened</div></div>', unsafe_allow_html=True)
with status_cols[1]:
    st.markdown('<div class="pg-panel"><div class="pg-label">Model size</div><b>Lightweight BERT</b><div class="pg-mini">CPU supported</div></div>', unsafe_allow_html=True)
with status_cols[2]:
    st.markdown('<div class="pg-panel"><div class="pg-label">Important</div><b>Assistive, not definitive</b><div class="pg-mini">Always verify suspicious messages and domains independently.</div></div>', unsafe_allow_html=True)

st.write("")
st.markdown("## Analyze a URL")
st.markdown('<div class="pg-mini">Try one of the prepared examples, or paste a URL from your own safe test material.</div>', unsafe_allow_html=True)

sample_cols = st.columns([1, 1, 2.2])
with sample_cols[0]:
    if st.button("Use legitimate example", use_container_width=True):
        st.session_state["url_input"] = "https://huggingface.co/"
        st.rerun()
with sample_cols[1]:
    if st.button("Use phishing example", use_container_width=True):
        st.session_state["url_input"] = "http://hu991ngface.com.ru/"
        st.rerun()
with sample_cols[2]:
    st.markdown('<div class="pg-mini" style="padding:10px 2px;">The sample phishing URL is a model-card example. Do not visit it.</div>', unsafe_allow_html=True)

with st.form("url_analysis_form", clear_on_submit=False):
    input_cols = st.columns([5, 1.2])
    with input_cols[0]:
        raw_url = st.text_input(
            "URL or domain",
            key="url_input",
            placeholder="e.g. https://example.com/login",
            help="The app analyzes the address as text only. It does not fetch the website.",
        )
    with input_cols[1]:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        analyze_clicked = st.form_submit_button("Analyze URL", type="primary", use_container_width=True)

if analyze_clicked:
    try:
        normalized_url = normalize_url(raw_url)
        with st.spinner("Loading the AI model and analyzing the URL… The first run downloads the model."):
            classifier, runtime_device = load_classifier()
            predictions = run_classification(classifier, normalized_url)
        best = predictions[0]
        best_name = friendly_class(best["label"])
        is_phishing = best_name == "Likely phishing"
        score_percent = float(best["score"]) * 100
        warnings = get_warning_signs(normalized_url)

        st.markdown('<hr class="pg-rule" />', unsafe_allow_html=True)
        st.markdown("## Analysis result")
        st.markdown(f'<div class="pg-label">Inspected URL</div>', unsafe_allow_html=True)
        st.code(normalized_url, language=None)

        verdict_class = "pg-verdict-danger" if is_phishing else "pg-verdict-safe"
        verdict_symbol = "⚠️" if is_phishing else "✓"
        verdict_description = (
            "The model classified this address as phishing-like. Treat it as suspicious and verify it through a trusted channel."
            if is_phishing else
            "The model classified this address as legitimate-like. This does not prove the site is safe; phishing links can still evade detection."
        )
        st.markdown(
            f'<div class="pg-verdict {verdict_class}"><div class="pg-verdict-title">{verdict_symbol} &nbsp; {best_name}</div><div class="pg-verdict-desc">{verdict_description}</div></div>',
            unsafe_allow_html=True,
        )

        metric_cols = st.columns(3)
        metric_cols[0].metric("Top class score", f"{score_percent:.1f}%")
        metric_cols[1].metric("URL length", f"{len(normalized_url)} chars")
        metric_cols[2].metric("Runtime", runtime_device)

        st.markdown("### Model class scores")
        st.markdown('<div class="pg-mini">These are scores produced by the classifier. They should not be interpreted as a guarantee or as perfectly calibrated real-world probabilities.</div>', unsafe_allow_html=True)
        for pred in predictions:
            label = friendly_class(pred["label"])
            pct = max(0.0, min(1.0, float(pred["score"])))
            score_cols = st.columns([1.7, 4.3, 0.8])
            with score_cols[0]:
                st.markdown(f"**{label}**")
            with score_cols[1]:
                st.progress(pct)
            with score_cols[2]:
                st.markdown(f"**{pct * 100:.1f}%**")

        st.markdown("### URL warning-sign checks")
        st.markdown('<div class="pg-mini">These are simple rules displayed for teaching. They are separate from the AI model and do not explain the model’s internal reasoning.</div>', unsafe_allow_html=True)
        if warnings:
            for item in warnings:
                st.warning(item, icon="⚠️")
        else:
            st.success("The simple checklist did not find common warning signs. This is not proof that the address is safe.", icon="✓")

        with st.expander("How to explain this result to the class"):
            st.markdown(
                "1. **Input:** The analyst provides a URL as text. The app does not visit it.\n"
                "2. **AI processing:** A pretrained transformer model scores the URL against patterns learned during training.\n"
                "3. **Output:** The app shows each class score and the highest-scoring category.\n"
                "4. **Human review:** Separate URL checks surface common warning signs, but they are not a true explanation of the model.\n"
                "5. **Limitations:** False positives and false negatives are possible. The result is one signal, not a security guarantee."
            )
    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error("The model could not be loaded or run. Check your internet connection for the first model download, then try again.")
        with st.expander("Technical details"):
            st.code(f"{type(exc).__name__}: {exc}")

st.markdown(
    '<div class="pg-footer">PhishGuard AI · Academic demonstration · Model: <a href="https://huggingface.co/CrabInHoney/urlbert-tiny-v4-phishing-classifier" target="_blank">CrabInHoney URLBERT-Tiny v4</a><br/>Never click or open a suspicious address just to test it here. The app classifies text only.</div>',
    unsafe_allow_html=True,
)
