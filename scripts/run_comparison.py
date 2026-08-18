"""
Run a comparison of Trust Calculus enforcement vs a no-policy baseline across attack modules.
Produces:
 - outputs/comparison_summary.csv
 - outputs/comparison_summary.json
 - outputs/avg_leakage_by_attack.png
 - outputs/leakage_boxplot.png

Usage:
  PYTHONPATH=src .venv/bin/python scripts/run_comparison.py

Notes:
 - This is a best-effort runner. Some attacks may not expose consistent metadata; the script extracts numeric metrics where available.
"""

from __future__ import annotations

import importlib
import inspect
import json
import os
import sys
from dataclasses import is_dataclass
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Ensure src on path
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from trustcalc.policy.engine import PolicyEngine
from trustcalc.gateway.enforcement import PolicyEnforcer
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.core.labels import make_secret, make_public
from trustcalc.evaluation.runner import EvaluationRunner
from trustcalc.attacks.base import Attack

ATTACKS_DIR = os.path.join(SRC, 'trustcalc', 'attacks')
OUTPUT_DIR = os.path.join(ROOT, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

engine = PolicyEngine()
enforcer = PolicyEnforcer(policy_engine=engine)
runner = EvaluationRunner()

# discover attack modules (py files excluding base and __init__)
modules = []
for fname in sorted(os.listdir(ATTACKS_DIR)):
    if not fname.endswith('.py'):
        continue
    if fname in ('__init__.py', 'base.py'):
        continue
    modules.append(fname[:-3])

records = []

for mod_name in modules:
    mod_path = f'trustcalc.attacks.{mod_name}'
    try:
        mod = importlib.import_module(mod_path)
    except Exception as e:
        print(f"Failed to import {mod_path}: {e}")
        continue

    # find Attack subclasses in module
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        if obj is Attack:
            continue
        try:
            if issubclass(obj, Attack):
                cls = obj
            else:
                continue
        except Exception:
            continue

        print(f"Running attack class: {cls.__name__}")

        # try to construct an instance
        try:
            attack = cls(name=cls.__name__)
        except TypeError:
            try:
                attack = cls()
            except Exception as e:
                print(f"Could not instantiate {cls.__name__}: {e}")
                continue

        # attempt to set a default secret if attribute exists
        try:
            if hasattr(attack, 'secret'):
                setattr(attack, 'secret', 'TOP_SECRET_DATA')
        except Exception:
            pass

        # baseline: no policy (run attack directly)
        baseline_result = None
        try:
            baseline_result = attack.run('public_carrier')
        except Exception as e:
            print(f"Baseline run failed for {cls.__name__}: {e}")

        # trust-calculus: enforce information flow (secret -> public)
        source_label = make_secret()
        dest_public = make_public()
        context_public = ExecutionContext(user_id='runner', labels={'source': source_label, 'destination': dest_public})

        decision = enforcer.authorize(object(), {}, context_public)
        trust_result = None
        blocked = False
        if decision.denied:
            blocked = True
        else:
            try:
                trust_result = attack.run('public_carrier')
            except Exception as e:
                print(f"Trust run failed for {cls.__name__}: {e}")

        # heuristics to extract numeric metrics
        def extract_metrics(result: Any, attack_obj: Any) -> dict[str, Any]:
            if result is None:
                return {'leakage': np.nan, 'capacity': np.nan, 'recovered_bits': np.nan}

            # AttackResult dataclass: has attributes leakage and metadata
            leakage = getattr(result, 'leakage', np.nan)
            metadata = getattr(result, 'metadata', {}) or {}

            capacity = metadata.get('capacity')
            if capacity is None:
                capacity = metadata.get('encoded_capacity')
            if capacity is None:
                # try to infer from channel/encoder if present
                ch = getattr(attack_obj, 'channel', None)
                sec = getattr(attack_obj, 'secret', None)
                if ch is not None and sec is not None and hasattr(getattr(ch, 'encoder', None), 'bit_length'):
                    try:
                        capacity = ch.encoder.bit_length(sec)
                    except Exception:
                        capacity = np.nan

            # recovered bits: try metadata
            recovered_bits = metadata.get('recovered_bits') or metadata.get('recovered')
            if isinstance(recovered_bits, str):
                # if recovered string, compute bit length heuristically
                enc = getattr(attack_obj, 'channel', None)
                if enc is not None and hasattr(getattr(enc, 'encoder', None), 'bit_length'):
                    try:
                        recovered_bits = enc.encoder.bit_length(recovered_bits)
                    except Exception:
                        recovered_bits = np.nan
                else:
                    recovered_bits = np.nan

            # fallback: use leakage as number of recovered bits when it seems integer
            if (recovered_bits is None or (isinstance(recovered_bits, float) and np.isnan(recovered_bits))) and isinstance(leakage, (int, float)):
                try:
                    recovered_bits = int(leakage)
                except Exception:
                    recovered_bits = np.nan

            return {'leakage': leakage, 'capacity': capacity, 'recovered_bits': recovered_bits}

        b_metrics = extract_metrics(baseline_result, attack)
        t_metrics = extract_metrics(trust_result, attack)

        rec = {
            'attack': cls.__name__,
            'baseline_leakage': b_metrics['leakage'],
            'baseline_capacity': b_metrics['capacity'],
            'baseline_recovered_bits': b_metrics['recovered_bits'],
            'trust_leakage': t_metrics['leakage'],
            'trust_capacity': t_metrics['capacity'],
            'trust_recovered_bits': t_metrics['recovered_bits'],
            'trust_blocked': blocked,
        }

        records.append(rec)

# create DataFrame
df = pd.DataFrame(records)

# compute derived columns
for col in ['baseline_leakage', 'trust_leakage', 'baseline_recovered_bits', 'trust_recovered_bits', 'baseline_capacity', 'trust_capacity']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# normalized leakage fraction where possible
# use recovered_bits / capacity when both present
df['baseline_leakage_frac'] = df.apply(lambda r: (r['baseline_recovered_bits'] / r['baseline_capacity']) if pd.notna(r['baseline_recovered_bits']) and pd.notna(r['baseline_capacity']) and r['baseline_capacity']>0 else r['baseline_leakage'] if pd.notna(r['baseline_leakage']) else np.nan, axis=1)

df['trust_leakage_frac'] = df.apply(lambda r: (r['trust_recovered_bits'] / r['trust_capacity']) if pd.notna(r['trust_recovered_bits']) and pd.notna(r['trust_capacity']) and r['trust_capacity']>0 else r['trust_leakage'] if pd.notna(r['trust_leakage']) else np.nan, axis=1)

# summary stats
summary = {}
summary['attacks'] = df['attack'].tolist()
summary['avg_baseline_leakage'] = float(df['baseline_leakage_frac'].mean()) if not df['baseline_leakage_frac'].isna().all() else None
summary['avg_trust_leakage'] = float(df['trust_leakage_frac'].mean()) if not df['trust_leakage_frac'].isna().all() else None
summary['blocked_count'] = int(df['trust_blocked'].sum()) if 'trust_blocked' in df.columns else 0
summary['attack_count'] = len(df)

# save CSV and JSON
csv_path = os.path.join(OUTPUT_DIR, 'comparison_summary.csv')
df.to_csv(csv_path, index=False)
json_path = os.path.join(OUTPUT_DIR, 'comparison_summary.json')
with open(json_path, 'w') as fh:
    json.dump(summary, fh, indent=2)

# Plot average leakage per attack (bar chart)
fig_path = os.path.join(OUTPUT_DIR, 'avg_leakage_by_attack.png')
plt.figure(figsize=(10,6))
indices = np.arange(len(df))
width = 0.35

baseline_vals = df['baseline_leakage_frac'].fillna(0)
trust_vals = df['trust_leakage_frac'].fillna(0)

plt.bar(indices - width/2, baseline_vals, width, label='Baseline')
plt.bar(indices + width/2, trust_vals, width, label='Trust Calculus')
plt.xticks(indices, df['attack'], rotation=45, ha='right')
plt.ylabel('Leakage fraction')
plt.title('Average leakage fraction by attack: Baseline vs Trust Calculus')
plt.legend()
plt.tight_layout()
plt.savefig(fig_path)

# Boxplot of leakage distributions (where available)
box_path = os.path.join(OUTPUT_DIR, 'leakage_boxplot.png')
plt.figure(figsize=(8,6))
# matplotlib may not accept labels in some versions; set xticks explicitly after plotting
box = plt.boxplot([baseline_vals.dropna().values, trust_vals.dropna().values])
plt.xticks([1, 2], ['Baseline', 'Trust Calculus'])
plt.ylabel('Leakage fraction')
plt.title('Leakage fraction distribution')
plt.tight_layout()
plt.savefig(box_path)

print('Outputs written to:', OUTPUT_DIR)
print('Summary:', json.dumps(summary, indent=2))
