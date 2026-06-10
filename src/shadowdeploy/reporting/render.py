"""Renderers for the promotion report: JSON (machine) and Markdown (human)."""
from __future__ import annotations

import json

from .report import PromotionReport


def to_dict(report: PromotionReport) -> dict:
    m = report.metrics
    return {
        "verdict": report.verdict.value,
        "reasons": list(report.reasons),
        "metrics": {
            "total": m.total,
            "matched": m.matched,
            "match_pct": m.match_pct,
            "mean_prod_latency_ms": m.mean_prod_latency_ms,
            "mean_shadow_latency_ms": m.mean_shadow_latency_ms,
            "latency_delta_ms": m.latency_delta_ms,
            "prod_error_rate": m.prod_error_rate,
            "shadow_error_rate": m.shadow_error_rate,
            "error_rate_delta": m.error_rate_delta,
            "category_counts": m.category_counts,
        },
    }


def to_json(report: PromotionReport, *, indent: int = 2) -> str:
    return json.dumps(to_dict(report), indent=indent, sort_keys=True)


def to_markdown(report: PromotionReport) -> str:
    m = report.metrics
    lines = [
        "# ShadowDeploy — Promotion Report",
        "",
        f"**Verdict:** `{report.verdict.value.upper()}`",
        "",
        "## Reasons",
    ]
    for r in report.reasons:
        lines.append(f"- {r}")
    lines += [
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total compared | {m.total} |",
        f"| Matched | {m.matched} |",
        f"| Match % | {m.match_pct} |",
        f"| Mean prod latency (ms) | {m.mean_prod_latency_ms} |",
        f"| Mean shadow latency (ms) | {m.mean_shadow_latency_ms} |",
        f"| Latency delta (ms) | {m.latency_delta_ms} |",
        f"| Prod error rate | {m.prod_error_rate} |",
        f"| Shadow error rate | {m.shadow_error_rate} |",
        f"| Error-rate delta | {m.error_rate_delta} |",
        "",
        "## Divergence categories",
        "",
    ]
    if m.category_counts:
        lines.append("| Category | Count |")
        lines.append("|---|---|")
        for cat in sorted(m.category_counts):
            lines.append(f"| {cat} | {m.category_counts[cat]} |")
    else:
        lines.append("_No divergences._")
    lines += [
        "",
        "> Shadow responses were never served to clients. "
        "This verdict is advisory; a human approves promotion.",
        "",
    ]
    return "\n".join(lines)
