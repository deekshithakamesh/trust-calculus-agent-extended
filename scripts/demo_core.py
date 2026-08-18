"""Demo script for the core Trust→Authority components.

Creates a TrustStore, EventLog, two mock tools, ingests a few evidence events
(benign then malicious), then runs the AuthorityEngine to show decisions and
explainability output. Writes outputs/demo-run/summary.json and events.jsonl.
"""
from trustcalc.trust.model import TrustStore
from trustcalc.trust.evidence import Evidence, map_strength_to_weight
from trustcalc.trajectory.event_log import EventLog
from trustcalc.authority.engine import AuthorityEngine
import json
from pathlib import Path


def run_demo():
    out_dir = Path("outputs/demo-run")
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = TrustStore()
    el = EventLog(path=str(out_dir / "events.jsonl"))
    ae = AuthorityEngine()

    tool_a = "tool-A"
    action_read = "read-public"
    action_write = "write-db"

    # benign interactions
    ev1 = Evidence(source="monitor-1", type="success", strength=0.9)
    ev1.weight = map_strength_to_weight(ev1.strength)
    ts.record_evidence(tool_a, action_read, ev1)
    el.append({"entity": tool_a, "action": action_read, "result": "success", "evidence": ev1.to_dict()})

    # check trust
    before = ts.get_trust_state(tool_a, action_read)
    dec = ae.decide(subject=tool_a, action=action_read, expected=before["expected"], confidence=before["confidence"], risk="low")

    print("After benign evidence:")
    print(json.dumps({"trust": before, "decision": dec.decision, "reason": dec.reason}, indent=2))

    # attacker tries privileged write after behaving
    ev2 = Evidence(source="attacker-1", type="success", strength=0.95)
    ev2.weight = map_strength_to_weight(ev2.strength)
    # attacker recommendations may be recorded as recommendation evidence for other tools
    ts.record_evidence(tool_a, action_write, ev2)
    el.append({"entity": tool_a, "action": action_write, "result": "success", "evidence": ev2.to_dict()})

    after = ts.get_trust_state(tool_a, action_write)
    dec2 = ae.decide(subject=tool_a, action=action_write, expected=after["expected"], confidence=after["confidence"], risk="very_high", provenance_warnings=["recommendation_from_unvetted_source"]) 

    print("After attacker evidence (attempted write):")
    print(json.dumps({"trust": after, "decision": dec2.decision, "reason": dec2.reason}, indent=2))

    # Write summary
    summary = {"before": before, "before_decision": dec.decision, "after": after, "after_decision": dec2.decision}
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    run_demo()
