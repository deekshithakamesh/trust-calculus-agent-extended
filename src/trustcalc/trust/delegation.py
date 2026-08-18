from __future__ import annotations

import math


def effective_authority(base_authority: float, delegation_depth: int = 0, attenuation: float = 0.3) -> float:
    """Reduce effective authority as delegation depth increases."""
    depth = max(int(delegation_depth), 0)
    authority = float(base_authority)
    return max(0.0, min(1.0, authority * math.exp(-(attenuation * depth))))
