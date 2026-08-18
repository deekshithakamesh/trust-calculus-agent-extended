"""
Streamlit UI for Trust Calculus experiments

Usage:
  1. Install Streamlit: pip install streamlit
  2. From the repo root run:
       PYTHONPATH=src .venv/bin/python -m streamlit run scripts/streamlit_ui.py

The app runs a simple end-to-end demo using the FormattingChannel, PolicyEnforcer,
and EvaluationRunner, and shows the encoded message, policy decision, and
numeric leakage metrics. Results can be downloaded as JSON.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

try:
    import streamlit as st
except Exception as exc:  # pragma: no cover - runtime helper
    raise RuntimeError(
        "streamlit is not installed. Install with: pip install streamlit"
    ) from exc

# Ensure project src/ is importable when run from repo root
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# Imports from the project
from trustcalc.policy.engine import PolicyEngine
from trustcalc.gateway.enforcement import PolicyEnforcer
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.core.labels import make_secret, make_public
from trustcalc.sidechannels.channels.formatting_channel import (
    FormattingChannel,
    FormattingStrategy,
)
from trustcalc.evaluation.runner import EvaluationRunner

# ---------------------------------------------------------------------------
# Streamlit layout
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Trust Calculus — Demo UI", layout="wide")
st.title("Trust Calculus — End-to-end Demo")
st.caption("Encode a secret into a carrier using a formatting covert channel, run gateway enforcement, and show leakage metrics.")

with st.sidebar:
    st.header("Experiment configuration")
    secret = st.text_input("Secret to embed", value="TOP_SECRET_DATA")
    message = st.text_area(
        "Carrier message",
        value=(
            "This is a public carrier message that has many words for encoding "
            "purposes so we can hide bits inside formatting. Add more words to increase capacity."
        ),
        height=160,
    )

    strategy = st.selectbox(
        "Formatting strategy",
        options=[s.value for s in FormattingStrategy],
        index=0,
    )

    destination = st.selectbox("Destination label", ["public", "secret"], index=0)

    duration_seconds = st.number_input("Duration (seconds)", value=2.0, min_value=0.1)

    mitigation_before = st.slider("Mitigation before (example)", 0.0, 1.0, 1.0)
    mitigation_after = st.slider("Mitigation after (example)", 0.0, 1.0, 0.2)

    run_button = st.button("Run experiment")

# ---------------------------------------------------------------------------
# Backend wiring
# ---------------------------------------------------------------------------
engine = PolicyEngine()
enforcer = PolicyEnforcer(policy_engine=engine)
runner = EvaluationRunner()
channel = FormattingChannel()
channel.strategy = FormattingStrategy(strategy)

# Helper to run the experiment
def run_experiment(secret: str, message: str, destination_label_name: str) -> dict[str, Any]:
    source_label = make_secret()
    destination_label = make_public() if destination_label_name == "public" else source_label

    context = ExecutionContext(user_id="web-user", labels={"source": source_label, "destination": destination_label})

    decision = enforcer.authorize(object(), {}, context)

    encoded = channel.encode(secret, message)
    transmitted_bits = channel.encoder.bit_length(secret)
    # decode what is recoverable from the encoded message
    recovered = channel.decode(encoded)
    recovered_bits = channel.encoder.bit_length(recovered)

    result: dict[str, Any] = {
        "decision": decision.to_dict(),
        "blocked": decision.denied,
        "encoded": encoded,
        "transmitted_bits": transmitted_bits,
        "recovered": recovered,
        "recovered_bits": recovered_bits,
    }

    if not decision.denied:
        exp = runner.run_experiment(
            attack_name=f"formatting-channel-{destination_label_name}",
            transmitted_bits=transmitted_bits,
            recovered_bits=recovered_bits,
            duration_seconds=duration_seconds,
            mitigation_before=mitigation_before,
            mitigation_after=mitigation_after,
        )
        result["experiment"] = exp

    return result

# ---------------------------------------------------------------------------
# Run and display
# ---------------------------------------------------------------------------
if run_button:
    with st.spinner("Running experiment..."):
        try:
            channel.strategy = FormattingStrategy(strategy)
            out = run_experiment(secret, message, destination)
        except Exception as exc:
            st.exception(exc)
            st.stop()

    # Show policy decision
    st.subheader("Policy decision")
    decision = out.get("decision", {})
    st.json(decision)

    st.subheader("Encoded message (full)")
    st.code(out["encoded"])

    cols = st.columns(4)
    cols[0].metric("Transmitted bits", out["transmitted_bits"])
    cols[1].metric("Recovered bits", out["recovered_bits"])
    leak = (out["recovered_bits"] / out["transmitted_bits"]) if out["transmitted_bits"] else 0.0
    cols[2].metric("Bit leakage", f"{leak:.3f}")
    cols[3].metric("Blocked", str(out["blocked"]))

    if "experiment" in out:
        st.subheader("Experiment metrics")
        st.json(out["experiment"]) 

    # Offer download
    st.subheader("Download result")
    st.download_button(
        "Download result as JSON",
        data=json.dumps(out, indent=2),
        file_name="trustcalc_experiment_result.json",
        mime="application/json",
    )

else:
    st.info("Configure experiment in the sidebar and click 'Run experiment' to execute.")
