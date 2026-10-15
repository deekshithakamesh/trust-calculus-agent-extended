"""Technical TrustCalc trace dashboard for live prompt inspection."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from examples.ollama_secure_demo import secure_decision_trace

st.set_page_config(page_title="TrustCalc Trace Console", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: radial-gradient(circle at top, rgba(59,130,246,0.12), transparent 25%), #07111d;
        color: #edf2f7;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    .stTabs [role="tablist"] {
        gap: 0.6rem;
    }
    .stTabs [role="tab"] {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 0.8rem 0.8rem 0 0;
        padding: 0.55rem 1rem;
    }
    .stMetric {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 0.9rem;
        padding: 1rem;
        box-shadow: 0 10px 24px rgba(2, 8, 23, 0.18);
    }
    [data-testid="stCodeBlock"] {
        background: #0b1220;
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 0.8rem;
    }
    .stExpander {
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 0.8rem;
        background: rgba(15, 23, 42, 0.6);
        box-shadow: 0 8px 24px rgba(2, 8, 23, 0.12);
    }
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #7c3aed);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("TrustCalc Trace Console")
st.caption("Live prompt inspection: risk analysis, tool classification, and policy decision steps")

sample_prompts = [
    "hi",
    "can u help me solve a math question",
    "Please read the local sandbox file demo_notes.txt.",
    "Please send an email to demo@example.com with the confidential account details.",
    "I want to transfer $1000 from the bank account to an external recipient.",
]

prompt_input = st.text_area("Prompt", value="hi", height=140)

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("Run trace"):
        st.session_state["current_prompt"] = prompt_input.strip()
with col2:
    st.write("Quick examples:")
    for example in sample_prompts:
        if st.button(example, key=f"sample_{hash(example)}", use_container_width=False):
            st.session_state["current_prompt"] = example
            prompt_input = example

current_prompt = st.session_state.get("current_prompt", prompt_input)
if not current_prompt:
    current_prompt = "hi"

if st.button("Execute", type="primary") or "current_prompt" in st.session_state:
    prompt_to_run = current_prompt if current_prompt else prompt_input.strip()
    try:
        trace = secure_decision_trace(prompt_to_run)
    except RuntimeError as exc:
        st.error(str(exc))
        st.info("Start Ollama with: ollama serve")
        st.stop()

    st.subheader("Prompt")
    st.code(prompt_to_run)

    result = trace["result"]
    decision = trace["decision"]
    profile = trace["profile"]

    cols = st.columns(4)
    with cols[0]:
        st.metric("Allowed", "Yes" if result.get("allowed") else "No")
    with cols[1]:
        st.metric("Tool", trace.get("tool_candidate", "unknown"))
    with cols[2]:
        st.metric("Risk score", profile.get("risk_score", 0))
    with cols[3]:
        st.metric("Model", trace.get("model", "unknown"))

    st.subheader("Risk analysis")
    st.json(profile)

    st.subheader("Policy decision")
    st.json(decision)

    st.subheader("Tool result")
    st.json(result)

    st.subheader("Execution trace")
    for step in trace.get("trace", []):
        with st.expander(f"{step['step']} — {step['ms']} ms"):
            st.json(step["details"])

    st.subheader("LLM output")
    st.write(trace.get("llm_output") or trace.get("result", {}).get("response") or "No output")

    st.session_state["current_prompt"] = prompt_to_run
