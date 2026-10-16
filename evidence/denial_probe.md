# Denial Feedback Probe

With fixed arguments and a PUBLIC destination, the two-label uniform-prior probe returns different allow/deny statuses for PUBLIC and SECRET sources. The status therefore carries 1.0 bit in this probe even though denial text is generic.

Caller-visible denial: `Tool call denied by policy.`

Capability name disclosed in denial: `False`.
Full capability reason retained in audit: `True`.

This result assumes the request is independent of the protected label. A destination or argument selected based on that label can also leak through whether a request is refused and is outside this probe's guarantee.
