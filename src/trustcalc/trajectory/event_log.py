"""
Append-only EventLog for recording events and deriving simple trajectory features.

Events are JSON-like dictionaries and are written to a JSONL file for persistence.
The EventLog also supports an in-memory buffer for quick tests.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import tempfile


class EventLog:
    def __init__(self, path: Optional[str] = None, buffer_only: bool = False) -> None:
        self.buffer_only = buffer_only
        if path is None and not buffer_only:
            # default file inside outputs/
            self.path = Path("outputs/eventlog.jsonl")
        elif path is None:
            self.path = None
        else:
            self.path = Path(path)
        self._buffer: List[Dict] = []
        if self.path and not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Dict) -> None:
        self._buffer.append(event)
        if not self.buffer_only and self.path is not None:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")

    def get_recent(self, entity: str, n: int = 10) -> List[Dict]:
        rv = [e for e in self._buffer if e.get("entity") == entity]
        return rv[-n:]

    def all(self) -> List[Dict]:
        return list(self._buffer)

    def load_from_file(self, path: Optional[str] = None) -> None:
        if path is None and self.path is None:
            raise RuntimeError("no path configured for event log")
        p = Path(path) if path else self.path
        if p is None or not p.exists():
            return
        self._buffer = []
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    self._buffer.append(json.loads(line))
                except Exception:
                    continue

    def recent_feature_summary(self, entity: str, window: int = 10) -> Dict:
        """Compute a few small trajectory-derived features from recent events for an entity."""
        events = self.get_recent(entity, n=window)
        success = 0
        failure = 0
        anomalies = 0
        escalations = 0
        for e in events:
            res = e.get("result")
            if res == "success":
                success += 1
            elif res == "failure":
                failure += 1
            if e.get("anomaly"):
                anomalies += 1
            if e.get("escalation"):
                escalations += 1
        total = max(1, len(events))
        return {
            "recent_success_rate": success / total,
            "recent_failure_rate": failure / total,
            "recent_anomaly_count": anomalies,
            "recent_escalation_count": escalations,
            "observed_events": len(events),
        }


__all__ = ["EventLog"]
