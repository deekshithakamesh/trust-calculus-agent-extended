from uuid import uuid4

from trustcalc.core.provenance import (
    OperationType,
    ProvenanceGraph,
    ProvenanceNode,
)


def test_origin():

    node = ProvenanceNode.origin(
        actor="user",
        description="Prompt",
    )

    assert node.operation == OperationType.ORIGIN


def test_graph():

    graph = ProvenanceGraph()

    root = ProvenanceNode.origin("user")

    graph.add(root)

    child = ProvenanceNode.derived(
        operation=OperationType.LLM_RESPONSE,
        parents=[root.id],
    )

    graph.add(child)

    assert graph.contains(root.id)

    lineage = graph.lineage(child.id)

    assert len(lineage) == 2


def test_explain():

    graph = ProvenanceGraph()

    root = ProvenanceNode.origin("user")

    graph.add(root)

    explanation = graph.explain(root.id)

    assert "origin" in explanation


def test_verify_integrity_healthy_lineage():

    graph = ProvenanceGraph()

    root = ProvenanceNode.origin("user")

    graph.add(root)

    child = ProvenanceNode.derived(
        operation=OperationType.LLM_RESPONSE,
        parents=[root.id],
    )

    graph.add(child)

    ok, problems = graph.verify_integrity(child.id)

    assert ok is True

    assert problems == []


def test_verify_integrity_missing_parent():

    graph = ProvenanceGraph()

    orphan = ProvenanceNode.derived(
        operation=OperationType.TRANSFORM,
        parents=[uuid4()],
    )

    graph.add(orphan)

    ok, problems = graph.verify_integrity(orphan.id)

    assert ok is False

    assert any("missing" in p for p in problems)


def test_verify_integrity_unknown_node():

    graph = ProvenanceGraph()

    ok, problems = graph.verify_integrity(uuid4())

    assert ok is False

    assert any("does not exist" in p for p in problems)


def test_verify_integrity_cycle_detection():

    graph = ProvenanceGraph()

    a = ProvenanceNode.origin("user")

    b = ProvenanceNode.derived(
        operation=OperationType.TRANSFORM,
        parents=[a.id],
    )

    graph.add(a)
    graph.add(b)

    # Introduce a cycle by bypassing the append-only API.
    graph._nodes[a.id] = ProvenanceNode.derived(
        operation=OperationType.TRANSFORM,
        parents=[b.id],
    )

    ok, problems = graph.verify_integrity(a.id)

    assert ok is False

    assert any("Cycle" in p for p in problems)
