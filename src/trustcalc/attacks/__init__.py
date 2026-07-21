"""
trustcalc.attacks
=================

Attack implementations for evaluating the Trust Calculus framework.

Exports
-------
- Base attack interfaces
- Prompt injection attacks
- Jailbreak attacks
- Privilege escalation attacks
- Data exfiltration attacks
- Covert channel attacks
"""

from .base import Attack, AttackResult
from .prompt_injection import PromptInjectionAttack
from .jailbreak import JailbreakAttack
from .privilege_escalation import PrivilegeEscalationAttack
from .data_exfiltration import DataExfiltrationAttack
from .formatting_attack import FormattingAttack
from .whitespace_attack import WhitespaceAttack
from .synonym_attack import SynonymAttack
from .timing_attack import TimingAttack

__all__ = [
    "Attack",
    "AttackResult",
    "PromptInjectionAttack",
    "JailbreakAttack",
    "PrivilegeEscalationAttack",
    "DataExfiltrationAttack",
    "FormattingAttack",
    "WhitespaceAttack",
    "SynonymAttack",
    "TimingAttack",
]