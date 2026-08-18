from trustcalc.trust.provenance import ProvenanceGraph, ProvenanceNode, discount_correlated_evidence
from trustcalc.trust.trajectory import TrajectoryEvent, analyze_trajectory


def test_provenance_graph_tracks_causal_links():
    graph = ProvenanceGraph()
    root = graph.add_node("root", "startup")
    child = graph.add_node("child", "tool_call", parents=[root.id])

    assert child.parent_ids == (root.id,)
    assert root.id in graph.nodes
    assert child.id in graph.nodes


def test_discount_correlated_evidence_reduces_weight():
    evidence = [
        {"source": "source-a", "weight": 1.0},
        {"source": "source-b", "weight": 0.9},
    ]

    discounted = discount_correlated_evidence(evidence, shared_sources={"source-a", "source-b"})

    assert len(discounted) == 2
    assert all(item["weight"] <= 1.0 for item in discounted)
    assert discounted[0]["weight"] < 1.0


def test_trajectory_anomaly_detection_flags_repeated_actions():
    events = [
        TrajectoryEvent(actor="tool-a", action="file_read", outcome="success", timestamp=1.0),
        TrajectoryEvent(actor="tool-a", action="file_read", outcome="success", timestamp=2.0),
        TrajectoryEvent(actor="tool-a", action="file_read", outcome="success", timestamp=3.0),
        TrajectoryEvent(actor="tool-a", action="file_read", outcome="success", timestamp=4.0),
        TrajectoryEvent(actor="tool-a", action="file_read", outcome="success", timestamp=5.0),
        TrajectoryEvent(actor="tool-a", action="file_read", outcome="success", timestamp=6.0),
        TrajectoryEvent(actor="tool-a", action="database_write", outcome="attack", timestamp=7.0),
    ]

    summary = analyze_trajectory(events)

    assert summary["anomaly_detected"] is True
    assert summary["risk_score"] > 0.5
