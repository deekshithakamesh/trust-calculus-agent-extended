from trustcalc.policy.engine import PolicyEngine
from trustcalc.runtime.interpreter import Interpreter
from trustcalc.runtime.taint_tracker import TaintTracker


class DummyGateway:

    def authorize(
        self,
        **kwargs,
    ):

        from trustcalc.policy.decisions import Decision

        return Decision.allow()

    def execute(
        self,
        **kwargs,
    ):
        raise NotImplementedError

    def execute_llm(
        self,
        **kwargs,
    ):
        raise NotImplementedError


def test_reset():

    interpreter = Interpreter(

        taint_tracker=TaintTracker(),

        policy_engine=PolicyEngine(),

        gateway=DummyGateway(),
    )

    interpreter.execution_log.append({})

    interpreter.reset()

    assert interpreter.history() == []

def test_validate_plan():

    interpreter = Interpreter(

        taint_tracker=TaintTracker(),

        policy_engine=PolicyEngine(),

        gateway=DummyGateway(),
    )

    assert interpreter.validate_plan(
        [
            {
                "type": "llm",
                "prompt": "hello",
            }
        ]
    )


def test_statistics():

    interpreter = Interpreter(

        taint_tracker=TaintTracker(),

        policy_engine=PolicyEngine(),

        gateway=DummyGateway(),
    )

    interpreter.execution_log.extend(
        [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "failed"},
        ]
    )

    stats = interpreter.statistics()

    assert stats["completed"] == 2

    assert stats["failed"] == 1


def test_report():

    interpreter = Interpreter(

        taint_tracker=TaintTracker(),

        policy_engine=PolicyEngine(),

        gateway=DummyGateway(),
    )

    report = interpreter.report()

    assert "statistics" in report

    assert "history" in report