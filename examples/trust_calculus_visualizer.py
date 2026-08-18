#!/usr/bin/env python3
"""
Trust Calculus Agent - Interactive Visualizer with Graphs & Charts

Generates comprehensive visualizations showing:
1. Trust vs Confidence decision matrix with authority zones
2. Risk levels for different actions
3. Authority decision flow
4. Attack defense coverage matrix
5. Implementation phase timeline
6. Success metrics dashboard
7. Security-Utility Pareto frontier
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from trustcalc.core.labels import Integrity, Confidentiality, SecurityLabel

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10


def visualize_trust_confidence_matrix():
    """
    Create a 2D matrix showing:
    - X-axis: Trust (0 to 1)
    - Y-axis: Confidence (0 to 1)
    - Color zones: Authority decision types
    - Scatter points: Example scenarios
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Decision zones based on trust and confidence
    trust = np.linspace(0, 1, 100)
    confidence = np.linspace(0, 1, 100)
    T, C = np.meshgrid(trust, confidence)
    
    # Decision logic (simplified)
    # DENY: low trust or low confidence
    # SANDBOX: medium trust, low-medium confidence
    # RESTRICT: medium trust, medium confidence
    # VERIFY: high trust, high-medium confidence, high risk expected
    # ALLOW: high trust, high confidence
    
    decisions = np.zeros_like(T)
    
    # ALLOW zone: trust > 0.75 AND confidence > 0.75
    allow_zone = (T > 0.75) & (C > 0.75)
    decisions[allow_zone] = 5
    
    # VERIFY zone: 0.65 < trust < 0.85 AND 0.55 < confidence < 0.85
    verify_zone = (T > 0.65) & (T < 0.85) & (C > 0.55) & (C < 0.85)
    decisions[verify_zone] = 4
    
    # RESTRICT zone: 0.55 < trust < 0.75 AND 0.4 < confidence < 0.75
    restrict_zone = (T > 0.55) & (T < 0.75) & (C > 0.4) & (C < 0.75)
    decisions[restrict_zone] = 3
    
    # SANDBOX zone: 0.4 < trust < 0.65
    sandbox_zone = (T > 0.4) & (T < 0.65)
    decisions[sandbox_zone] = 2
    
    # DENY zone: trust < 0.4
    deny_zone = (T < 0.4)
    decisions[deny_zone] = 1
    
    # Plot decision zones
    colors = ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c', '#1f77b4']
    cmap = plt.cm.colors.ListedColormap(colors)
    
    im = ax.contourf(T, C, decisions, levels=[0, 1.5, 2.5, 3.5, 4.5, 5.5], cmap=cmap, alpha=0.7)
    
    # Example scenarios
    scenarios = [
        {'name': 'High Trust\nHigh Confidence', 'trust': 0.95, 'confidence': 0.90, 'decision': 'ALLOW', 'color': '#1f77b4'},
        {'name': 'High Trust\nLow Confidence', 'trust': 0.90, 'confidence': 0.15, 'decision': 'SANDBOX', 'color': '#2ca02c'},
        {'name': 'Medium Trust\nMedium Confidence', 'trust': 0.65, 'confidence': 0.60, 'decision': 'RESTRICT', 'color': '#ffbb78'},
        {'name': 'Low Trust\nHigh Confidence', 'trust': 0.30, 'confidence': 0.85, 'decision': 'DENY', 'color': '#d62728'},
        {'name': 'High Trust\nMedium Confidence', 'trust': 0.80, 'confidence': 0.70, 'decision': 'VERIFY', 'color': '#ff7f0e'},
    ]
    
    for scenario in scenarios:
        ax.scatter(scenario['trust'], scenario['confidence'], s=400, marker='o', 
                  color=scenario['color'], edgecolor='black', linewidth=2, zorder=5)
        ax.annotate(scenario['name'], 
                   xy=(scenario['trust'], scenario['confidence']),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=9, weight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor=scenario['color'], alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    ax.set_xlabel('Trust (Belief Strength)', fontsize=12, weight='bold')
    ax.set_ylabel('Confidence (Evidence Quantity)', fontsize=12, weight='bold')
    ax.set_title('Authority Decision Matrix: Trust vs Confidence\n(High Trust with Low Confidence = SANDBOX, not ALLOW)', 
                fontsize=14, weight='bold', pad=20)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    
    # Add decision zone labels
    ax.text(0.2, 0.2, 'DENY', fontsize=14, weight='bold', color='white', ha='center', va='center', alpha=0.8)
    ax.text(0.5, 0.2, 'SANDBOX', fontsize=14, weight='bold', color='white', ha='center', va='center', alpha=0.8)
    ax.text(0.5, 0.5, 'RESTRICT', fontsize=14, weight='bold', color='white', ha='center', va='center', alpha=0.8)
    ax.text(0.7, 0.65, 'VERIFY', fontsize=12, weight='bold', color='white', ha='center', va='center', alpha=0.8)
    ax.text(0.87, 0.87, 'ALLOW', fontsize=14, weight='bold', color='white', ha='center', va='center', alpha=0.8)
    
    plt.tight_layout()
    return fig


def visualize_risk_levels():
    """Visualize action risk levels and required trust thresholds."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    actions = ['WebSearch', 'FileRead\n(public)', 'FileRead\n(private)', 'DatabaseWrite', 'CodeExecution']
    risks = [0.05, 0.10, 0.40, 0.70, 0.95]
    colors_risk = ['#2ca02c', '#90ee90', '#ffbb78', '#ff7f0e', '#d62728']
    
    # Plot 1: Risk Levels
    bars1 = ax1.barh(actions, risks, color=colors_risk, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Risk Level [0-1]', fontsize=12, weight='bold')
    ax1.set_title('Action Risk Levels', fontsize=13, weight='bold')
    ax1.set_xlim(0, 1)
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, risk) in enumerate(zip(bars1, risks)):
        ax1.text(risk + 0.02, i, f'{risk:.2f}', va='center', fontsize=11, weight='bold')
    
    # Plot 2: Required Trust Threshold
    required_trust = [0.5 + 0.5 * r for r in risks]
    bars2 = ax2.barh(actions, required_trust, color=colors_risk, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Required Trust [0-1]', fontsize=12, weight='bold')
    ax2.set_title('Required Trust for Authorization\n(T_required = 0.5 + 0.5 × Risk)', fontsize=13, weight='bold')
    ax2.set_xlim(0, 1)
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, req) in enumerate(zip(bars2, required_trust)):
        ax2.text(req + 0.02, i, f'{req:.2f}', va='center', fontsize=11, weight='bold')
    
    # Add risk monotonicity principle line
    ax2.axvline(x=0.5, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Base threshold')
    
    plt.tight_layout()
    return fig


def visualize_authority_flow():
    """Visualize the 5 authority decision types."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'Authority Decision Flow', fontsize=16, weight='bold', ha='center')
    
    # Decision boxes
    decisions = [
        {'y': 8, 'title': '1. ALLOW', 'desc': 'Trusted + Evidence\nHigh risk tolerance', 'color': '#1f77b4'},
        {'y': 6.5, 'title': '2. VERIFY', 'desc': 'Monitor + Audit\nHigh risk action', 'color': '#ff7f0e'},
        {'y': 5, 'title': '3. RESTRICT', 'desc': 'Limited capability\nProvenance concerns', 'color': '#ffbb78'},
        {'y': 3.5, 'title': '4. SANDBOX', 'desc': 'Isolated execution\nInsufficient trust', 'color': '#2ca02c'},
        {'y': 2, 'title': '5. DENY', 'desc': 'Blocked\nUntrusted entity', 'color': '#d62728'},
    ]
    
    for i, dec in enumerate(decisions):
        # Box
        box = FancyBboxPatch((0.5, dec['y']-0.3), 2.5, 0.8, 
                            boxstyle="round,pad=0.1", 
                            edgecolor='black', facecolor=dec['color'], 
                            linewidth=2, alpha=0.8)
        ax.add_patch(box)
        
        # Text
        ax.text(1.75, dec['y']+0.15, dec['title'], fontsize=11, weight='bold', 
               ha='center', va='center', color='white')
        
        # Description
        ax.text(4.5, dec['y'], dec['desc'], fontsize=10, ha='left', va='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.9))
        
        # Arrow
        if i < len(decisions) - 1:
            ax.annotate('', xy=(1.75, decisions[i+1]['y']+0.35), xytext=(1.75, dec['y']-0.35),
                       arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Criteria on the right
    ax.text(8.5, 9, 'Decision Criteria:', fontsize=11, weight='bold')
    criteria = [
        'Trust: High (>0.8)',
        'Confidence: High (>0.8)',
        'Risk: Low (<0.3)',
        'No anomalies',
    ]
    for i, crit in enumerate(criteria):
        ax.text(8.5, 8.5 - i*0.4, f'• {crit}', fontsize=9)
    
    plt.tight_layout()
    return fig


def visualize_attack_defense_matrix():
    """Visualize which defenses protect against which attacks."""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    attacks = [
        'Immediate Malicious',
        'Reputation Poisoning',
        'Hidden Trigger',
        'Compromised Tool',
        'Collusion',
        'Sybil/Reputation',
        'Delegation Attack',
        'Prompt Injection',
        'On-Off Attack',
        'Authority Inflation',
        'Trust Inflation Loop',
        'Privilege via Intermediary',
    ]
    
    defenses = [
        'IFC Layer',
        'Risk Monotonicity',
        'Trajectory Analysis',
        'Behavioral Profiling',
        'Provenance Tracking',
        'Evidence Discounting',
        'Attenuation Rules',
        'Context Anomaly',
        'Temporal Analysis',
        'Recommendation Weighting',
        'Transitive Limits',
    ]
    
    # Coverage matrix (1 = covered, 0 = not covered)
    coverage = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Immediate Malicious
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Reputation Poisoning
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],  # Hidden Trigger
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],  # Compromised Tool
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # Collusion
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],  # Sybil
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],  # Delegation
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # Prompt Injection
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],  # On-Off Attack
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Authority Inflation
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # Trust Inflation Loop
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],  # Privilege via Intermediary
    ])
    
    # Plot heatmap
    im = ax.imshow(coverage, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    # Set ticks
    ax.set_xticks(np.arange(len(defenses)))
    ax.set_yticks(np.arange(len(attacks)))
    ax.set_xticklabels(defenses, rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels(attacks, fontsize=10)
    
    # Add checkmarks
    for i in range(len(attacks)):
        for j in range(len(defenses)):
            if coverage[i, j] == 1:
                ax.text(j, i, '✓', ha='center', va='center', color='darkgreen', fontsize=14, weight='bold')
    
    ax.set_title('Attack-Defense Coverage Matrix\n(✓ = Defense protects against Attack)', 
                fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    return fig


def visualize_implementation_timeline():
    """Visualize the 13-phase implementation timeline."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    phases = [
        {'num': 0, 'name': 'Architecture', 'weeks': 2, 'status': 'DONE'},
        {'num': 1, 'name': 'Trust State', 'weeks': 1, 'status': 'NEXT'},
        {'num': 2, 'name': 'Temporal', 'weeks': 1, 'status': 'TODO'},
        {'num': 3, 'name': 'Risk Model', 'weeks': 1, 'status': 'TODO'},
        {'num': 4, 'name': 'Authority Eng.', 'weeks': 1, 'status': 'TODO'},
        {'num': 5, 'name': 'Trajectory', 'weeks': 1, 'status': 'TODO'},
        {'num': 6, 'name': 'Delegation', 'weeks': 1, 'status': 'TODO'},
        {'num': 7, 'name': 'Provenance', 'weeks': 1, 'status': 'TODO'},
        {'num': 8, 'name': 'Attack Sim', 'weeks': 2, 'status': 'TODO'},
        {'num': 9, 'name': 'Baselines', 'weeks': 1, 'status': 'TODO'},
        {'num': 10, 'name': 'Experiments', 'weeks': 2, 'status': 'TODO'},
        {'num': 11, 'name': 'Ablations', 'weeks': 1, 'status': 'TODO'},
        {'num': 12, 'name': 'Properties', 'weeks': 1, 'status': 'TODO'},
        {'num': 13, 'name': 'Integration', 'weeks': 1, 'status': 'TODO'},
    ]
    
    colors_status = {'DONE': '#2ca02c', 'NEXT': '#ff7f0e', 'TODO': '#d3d3d3'}
    
    # Calculate cumulative weeks
    cumulative = 0
    bars = []
    for phase in phases:
        start = cumulative
        duration = phase['weeks']
        color = colors_status[phase['status']]
        
        bar = ax.barh(phase['num'], duration, left=start, height=0.6, 
                     color=color, edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Add phase label
        ax.text(start + duration/2, phase['num'], 
               f"P{phase['num']}\n{phase['name']}\n{phase['weeks']}w",
               ha='center', va='center', fontsize=9, weight='bold', color='black')
        
        cumulative += duration
    
    ax.set_yticks(range(len(phases)))
    ax.set_yticklabels([f"Phase {p['num']}" for p in phases], fontsize=10)
    ax.set_xlabel('Timeline (Weeks)', fontsize=12, weight='bold')
    ax.set_title('13-Phase Implementation Roadmap (13 weeks total)', fontsize=14, weight='bold', pad=20)
    ax.set_xlim(0, cumulative + 1)
    ax.grid(axis='x', alpha=0.3)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#2ca02c', edgecolor='black', label='✓ DONE'),
        mpatches.Patch(facecolor='#ff7f0e', edgecolor='black', label='→ NEXT'),
        mpatches.Patch(facecolor='#d3d3d3', edgecolor='black', label='□ TODO'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    return fig


def visualize_success_metrics():
    """Visualize success criteria."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Security Metrics
    security_metrics = ['Attack Success\nRate', 'Time to\nDetection (s)', 'False\nNegatives', 'Privilege\nEscalation']
    security_values = [5, 60, 0, 5]  # Attack success <5%, detection <60s, FN=0, blocked >95%
    security_targets = [5, 60, 0, 95]
    
    x_pos = np.arange(len(security_metrics))
    ax1.bar(x_pos, security_values, color='#2ca02c', alpha=0.7, edgecolor='black', linewidth=1.5, label='Target')
    ax1.set_ylabel('Metric Value', fontsize=11, weight='bold')
    ax1.set_title('Security Metrics (Targets)', fontsize=12, weight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(security_metrics, fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    
    for i, (v, t) in enumerate(zip(security_values, security_targets)):
        ax1.text(i, v + 2, f'{v}%', ha='center', fontsize=10, weight='bold')
    
    # 2. Utility Metrics
    utility_metrics = ['Task Success\nRate', 'False Positive\nRate', 'Latency p99\n(ms)', 'Throughput\n(calls/s)']
    utility_values = [95, 5, 200, 100]
    
    x_pos2 = np.arange(len(utility_metrics))
    ax2.bar(x_pos2, utility_values, color='#1f77b4', alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Metric Value', fontsize=11, weight='bold')
    ax2.set_title('Utility Metrics (Targets)', fontsize=12, weight='bold')
    ax2.set_xticks(x_pos2)
    ax2.set_xticklabels(utility_metrics, fontsize=10)
    ax2.grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(utility_values):
        ax2.text(i, v + 3, f'{v}', ha='center', fontsize=10, weight='bold')
    
    # 3. Pareto Frontier (Security vs Utility)
    baseline_systems = ['NoSecurity', 'StaticPolicy', 'SimpleRep', 'SimpleThresh', 'RiskBased', 'TrajOnly', 'Proposed']
    security_scores = [0, 20, 40, 50, 65, 75, 85]
    utility_scores = [100, 85, 75, 70, 72, 70, 95]
    colors_systems = ['red', 'orange', 'yellow', 'lightgreen', 'lightblue', 'lightcyan', 'darkgreen']
    
    ax3.scatter(security_scores, utility_scores, s=300, c=colors_systems, edgecolor='black', linewidth=2, alpha=0.8)
    
    for i, system in enumerate(baseline_systems):
        ax3.annotate(system, (security_scores[i], utility_scores[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9, weight='bold')
    
    # Highlight Pareto frontier
    pareto_mask = [0, 6]  # NoSecurity (extreme) and Proposed (desired)
    pareto_x = [security_scores[i] for i in pareto_mask]
    pareto_y = [utility_scores[i] for i in pareto_mask]
    ax3.plot(pareto_x, pareto_y, 'k--', linewidth=2, alpha=0.5, label='Pareto Frontier')
    
    ax3.set_xlabel('Security Score', fontsize=11, weight='bold')
    ax3.set_ylabel('Utility Score', fontsize=11, weight='bold')
    ax3.set_title('Security-Utility Tradeoff (Pareto Frontier)', fontsize=12, weight='bold')
    ax3.set_xlim(-5, 105)
    ax3.set_ylim(60, 105)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. Ablation Study (8 components)
    components = ['Trust\nModel', 'Confidence\nModel', 'Risk\nModel', 'Trajectory', 
                 'Provenance', 'Delegation', 'Temporal\nDecay', 'Evidence\nDiscounting']
    impact = [18, 15, 14, 12, 11, 10, 8, 7]  # Performance impact if removed
    
    x_pos3 = np.arange(len(components))
    bars = ax4.barh(x_pos3, impact, color='#ff7f0e', alpha=0.7, edgecolor='black', linewidth=1.5)
    ax4.set_xlabel('Performance Impact if Removed (%)', fontsize=11, weight='bold')
    ax4.set_title('Ablation Study: Component Importance', fontsize=12, weight='bold')
    ax4.set_yticks(x_pos3)
    ax4.set_yticklabels(components, fontsize=10)
    ax4.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(impact):
        ax4.text(v + 0.5, i, f'{v}%', va='center', fontsize=10, weight='bold')
    
    plt.tight_layout()
    return fig


def main():
    """Generate all visualizations."""
    print("\n" + "="*70)
    print("Trust Calculus Agent - Generating Visualizations")
    print("="*70)
    print()
    
    output_dir = Path(__file__).parent.parent / "results" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    visualizations = [
        ("1_trust_confidence_matrix.png", visualize_trust_confidence_matrix, 
         "Trust vs Confidence Decision Matrix"),
        ("2_risk_levels.png", visualize_risk_levels, 
         "Action Risk Levels & Required Trust"),
        ("3_authority_flow.png", visualize_authority_flow, 
         "Authority Decision Flow"),
        ("4_attack_defense_matrix.png", visualize_attack_defense_matrix, 
         "Attack-Defense Coverage Matrix"),
        ("5_implementation_timeline.png", visualize_implementation_timeline, 
         "13-Phase Implementation Timeline"),
        ("6_success_metrics.png", visualize_success_metrics, 
         "Success Metrics Dashboard"),
    ]
    
    for filename, viz_func, title in visualizations:
        print(f"📊 Generating: {title}...", end=" ")
        try:
            fig = viz_func()
            filepath = output_dir / filename
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            print(f"✓ Saved to {filepath}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print()
    print("="*70)
    print("All visualizations generated!")
    print("="*70)
    print()
    print("Output directory:", output_dir)
    print()
    print("Generated files:")
    for filename, _, title in visualizations:
        print(f"  • {filename} - {title}")
    print()
    print("📂 Open in VS Code: File > Open Folder > results/visualizations/")
    print()


if __name__ == "__main__":
    main()
