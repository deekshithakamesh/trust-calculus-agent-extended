from trustcalc.attacks.asb import (
    DirectPromptInjectionAttack,
    MemoryPoisoningAttack,
    MixedASBAttack,
    ObservationPromptInjectionAttack,
    PlanOfThoughtBackdoorAttack,
)


def test_direct_prompt_injection_blocked_by_default():
    attack = DirectPromptInjectionAttack(name="dpi")

    result = attack.run("target")

    assert result.category == "direct_prompt_injection"
    assert result.blocked is True
    assert result.success is False
    assert result.leakage == 0.0


def test_observation_prompt_injection_rejects_untrusted_signal():
    attack = ObservationPromptInjectionAttack(name="opi")

    result = attack.run("target", observation="malicious", allowed_observations=("safe",))

    assert result.blocked is True
    assert result.success is False
    assert "Observation injection blocked." in result.message


def test_memory_poisoning_and_backdoor_are_detected():
    memory_attack = MemoryPoisoningAttack(name="mp")
    memory_result = memory_attack.run(
        "target",
        memory="malicious memory",
        allowed_memory_items=("safe memory",),
    )
    assert memory_result.blocked is True

    backdoor = PlanOfThoughtBackdoorAttack(name="pot")
    backdoor_result = backdoor.run("target", prompt="PLAN_EXECUTE step=run_admin_tool")
    assert backdoor_result.success is True
    assert backdoor_result.blocked is False


def test_mixed_attack_requires_both_channels_to_be_safe():
    attack = MixedASBAttack(name="mixed")

    result = attack.run(
        "target",
        direct_blocked=True,
        observation_blocked=True,
    )

    assert result.blocked is True
    assert result.success is False
