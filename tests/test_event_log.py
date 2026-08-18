import tempfile
import os
from trustcalc.trajectory.event_log import EventLog


def test_event_log_append_and_recent():
    # use buffer_only to avoid filesystem in CI
    el = EventLog(buffer_only=True)
    ev1 = {"entity": "tool-A", "action": "read", "result": "success"}
    ev2 = {"entity": "tool-A", "action": "read", "result": "failure", "anomaly": True}
    el.append(ev1)
    el.append(ev2)
    recent = el.get_recent("tool-A", n=5)
    assert len(recent) == 2
    summary = el.recent_feature_summary("tool-A", window=5)
    assert summary["observed_events"] == 2
