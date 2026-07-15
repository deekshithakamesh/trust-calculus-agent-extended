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
