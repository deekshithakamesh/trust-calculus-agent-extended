Threat Model and Attacker Taxonomy (Draft)

Purpose
-------
Define adversary goals, capabilities, and a taxonomy of attacks that the experiment harness must implement. This document guides the attack simulator design and evaluation metrics so the system is tested against realistic, adaptive attackers.

High-level adversary goals
--------------------------
Primary attacker objective:
- Obtain unauthorized authority to perform a high-impact action (e.g., exfiltrate data, write to DB, transfer funds) while minimizing the probability of detection.

Secondary objectives:
- Manipulate trust values of targeted tools/agents (reputation poisoning / Sybil)
- Create or exploit delegation chains to extend authority
- Hide malicious behavior within long periods of benign behavior (hidden-trigger)
- Cause denial-of-service by triggering unnecessary verifications

Threat model assumptions
------------------------
- The attacker can control one or more tools or agents (full or partial control). A controlled entity may behave arbitrarily when compromised.
- The attacker can craft evidence via recommendations, messages, or interactions with other agents (reputation manipulation).
- The defender (trust calculus) controls the authority engine and can observe all tool interactions through the mocked runtime (no blind spots in controlled experiments).
- Network-level attacks and supply-chain attacks outside the controlled environment are out-of-scope for initial experiments.
- Human verification is modeled as an oracle that can be invoked with configurable false positive/negative rates.

Capabilities and primitives available to attacker
------------------------------------------------
- Run controlled tool instances that behave according to a programmed strategy.
- Create many pseudo-identities (Sybil) if experiment allows; cost model configurable.
- Provide recommendations or references to other tools/agents.
- Delay malicious behavior to build reputation.
- Collude with other attacker-controlled tools to amplify influence.
- Exploit delegation mechanisms to get an agent to delegate authority.

Attack categories (to implement in simulator)
---------------------------------------------
1. Immediate malicious tool
   - Behavior: always malicious; attempts high-risk actions immediately.
   - Purpose: baseline, trivial attack.

2. Slow reputation poisoning
   - Behavior: behave benignly for a long period, occasionally perform low-impact actions to appear reliable, then slowly recommend other attacker nodes to grow influence.
   - Purpose: test whether the calculus resists slow manipulation.

3. Hidden-trigger / delayed compromise
   - Behavior: obey rules until a trigger (sequence of events, time, or external signal) then perform malicious action.
   - Purpose: test trajectory-aware detection and recovery.

4. Colluding tools
   - Behavior: multiple controlled entities exchange recommendations and reinforce each other's evidence.
   - Purpose: test provenance discounting and correlated-evidence mitigation.

5. Sybil attack
   - Behavior: attacker creates many low-cost identities to flood the system with supporting evidence.
   - Purpose: test robust weighting and cost modeling.

6. Delegation attack
   - Behavior: attacker seeks to obtain higher-level agent delegation intentionally (e.g., by manipulating a more trusted agent to delegate).
   - Purpose: test authority attenuation and revocation propagation.

7. On-off attack (churn)
   - Behavior: alternate between good behavior and malicious bursts.
   - Purpose: test recovery, detection latency, and stability.

8. Recommendation poisoning
   - Behavior: attacker injects recommendations or endorsements for untrusted entities.
   - Purpose: test provenance graph analysis and discounting.

9. Context manipulation
   - Behavior: attacker subtly modifies context to make risky operations appear low-risk (e.g., subverting labels or contexts).
   - Purpose: ensure trust calculus uses robust context features.

10. Adaptive optimizer attacker
   - Behavior: uses feedback from the authority engine (allowed/denied) to adapt strategy via simple reinforcement or search, with the goal of maximizing authority gained per detection probability.
   - Purpose: stress-test the system for strategic manipulation.

Detection and attacker cost model
---------------------------------
- Introduce a cost to identity creation or recommendations to limit trivial Sybil attacks in some experiments; make cost configurable so we can study cost-vs-effectiveness curves.
- Track detection as any authority decision that is VERIFY/RESTRICT/DENY on an attacker action; measure time-to-detection and whether the attack eventually succeeds.

Metrics tied to threat model
---------------------------
- Attack Success Rate (fraction of runs where attacker performed a high-impact action)
- Time to Authority Gain (time until attacker obtains required authority)
- Detection Rate and Time to Detection
- Privilege Escalation Rate
- Trust Manipulation Success Rate (attacker increases expected trust or confidence of attacker-controlled entities beyond threshold)
- Collusion Amplification Factor (how many colluding nodes required to reach a target trust)

Experiment scenarios
--------------------
Construct reproducible scenarios that combine attacker strategy, initial conditions, cost model, and defender configuration (thresholds, decay half-life, provenance discount). Example scenarios:
- Fast-compromise: immediate malicious tool with low-cost Sybils disabled.
- Slow-poison: controlled tool behaves benignly for 1000 events then performs high-risk action.
- Delegation-grab: attacker convinces mid-trust agent to delegate for read/write; then escalates.
- Collusion-lab: 5 colluding tools attempt to raise trust of a new node via recommendations.

Notes
-----
This threat model is intentionally broad. The simulator will allow toggling attacker power (Sybil cost, collusion degree, visibility) so ablations and sensitivity studies are possible. The goal is to create realistic, adaptive adversaries that cannot trivially be defended by naive thresholding.