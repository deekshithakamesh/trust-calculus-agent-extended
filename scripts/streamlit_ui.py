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

st.set_page_config(page_title="TrustCalc Safety Console", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. I can help with safe, local-only questions and keep the conversation focused within the approved scope."}
    ]

st.title("TrustCalc Safety Console")
st.caption("Local chatbot demo with policy-aware safety filtering")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("How can I help you today?")
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
    tool = result["tool_candidate"]
    if allowed:
        assistant_reply = (
            "I can help with that in a safe, local-only way."
            if tool == "chat"
            else "I can help with that within the local sandbox policy."
        )
    else:
        assistant_reply = "I’m not able to assist with that request. It would move outside the safe local boundary, and I’m designed to stay within the approved operating scope."

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.rerun()
