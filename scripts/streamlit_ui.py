"""Chat-style TrustCalc demo UI with conversation memory.

This version keeps a running conversation history so the assistant behaves more like
an actual AI agent while still enforcing the TrustCalc policy boundary.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from examples.ollama_secure_demo import LLM_PROVIDER, secure_decision_trace

st.set_page_config(page_title="Assistant", page_icon="✦", layout="wide")

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
        background: radial-gradient(circle at top, rgba(59,130,246,0.14), transparent 30%), #06121d;
        color: #edf5ff;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1000px;
    }
    div[data-testid="stChatMessage"] {
        background: rgba(12, 22, 36, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 22px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 10px 28px rgba(2, 8, 23, 0.18);
    }
    div[data-testid="stChatMessage"] p {
        margin: 0;
        line-height: 1.7;
        color: #edf2f7;
        font-size: 1.06rem;
    }
    [data-testid="stChatInput"] {
        background: rgba(12, 22, 36, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 0.2rem 0.5rem;
        box-shadow: 0 12px 30px rgba(2, 8, 23, 0.22);
    }
    .stTextInput input {
        background: transparent;
        color: #f8fafc;
    }
    .stChatMessage [data-testid="stChatMessageContent"] {
        background: transparent;
    }
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #7c3aed);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. I can help with thoughtful guidance and keep the conversation focused on the task at hand."}
    ]

st.markdown("<div style='font-size: 2.2rem; font-weight: 600; margin-bottom: 0.2rem;'>Assistant</div>", unsafe_allow_html=True)
st.caption("How can I help you today?")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Message")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        result = secure_decision_trace(prompt)
    except RuntimeError as exc:
        st.error(str(exc))
        if LLM_PROVIDER == "openai":
            st.info("Set OPENAI_API_KEY and run with TRUSTCALC_LLM_PROVIDER=openai")
        else:
            st.info("Start Ollama with: ollama serve")
        st.stop()

    allowed = bool(result["result"].get("allowed", False))
    if allowed:
        assistant_reply = result["result"].get("response") or result.get("llm_output") or "I can help with that."
    else:
        assistant_reply = "I can’t help with that request."

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.rerun()
