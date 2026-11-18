"""Write reconciliation metrics and approval queue reports."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path

from invoice_resolve.agent import Resolution


def write_reports(resolutions: Iterable[Resolution], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    items = list(resolutions)
    counts: dict[str, int] = {}
    for item in items:
        counts[item.status] = counts.get(item.status, 0) + 1
    approval_count = sum(item.approval_required for item in items)
    metrics = {
        "invoice_count": len(items),
        "status_counts": counts,
        "approval_required": approval_count,
        "approval_rate": round(approval_count / len(items), 4) if items else 0.0,
    }
    metrics_path = output_dir / "evaluation.json"
    queue_path = output_dir / "approval_queue.csv"
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    fields = (
        "invoice_id",
        "po_id",
        "status",
        "action",
        "approval_required",
        "evidence",
    )
    with queue_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "invoice_id": item.invoice_id,
                    "po_id": item.po_id,
                    "status": item.status,
                    "action": item.action,
                    "approval_required": item.approval_required,
                    "evidence": json.dumps(item.evidence, sort_keys=True),
                }
            )
    return metrics_path, queue_path
