"""Command-line interface for ShadowDeploy.

Subcommands:
  emit-iac   Generate Terraform or CDK for the harness from a config file.
  estimate   Print the estimated added cost of shadowing.
  report     Run a recorded fixture of prod/shadow exchanges and emit a report.

Config is a JSON file matching the load_config schema. The CLI never touches
AWS; emit-iac produces text, estimate does arithmetic, report works on recorded
captures.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .core.config import load_config
from .core.cost import estimate_cost
from .core.models import CapturedExchange, IaCTool
from .handlers.compare_handler import compare_batch
from .iac.cdk_emitter import emit_cdk
from .iac.terraform_emitter import emit_terraform
from .reporting.render import to_json, to_markdown
from .reporting.report import build_report


def _load_config_file(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return load_config(json.load(fh))


def _cmd_emit_iac(args) -> int:
    config = _load_config_file(args.config)
    if config.iac_tool is IaCTool.CDK:
        out = emit_cdk(config, environment=args.environment)
    else:
        out = emit_terraform(config, environment=args.environment)
    print(out)
    return 0


def _cmd_estimate(args) -> int:
    config = _load_config_file(args.config)
    est = estimate_cost(config, args.monthly_requests, monthly_budget=args.budget)
    print(json.dumps(est.__dict__, indent=2, default=list))
    return 0


def _cmd_report(args) -> int:
    config = _load_config_file(args.config)
    with open(args.captures, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    captures = [CapturedExchange(**c) for c in raw]
    results = compare_batch(captures, config)
    if not results:
        print("no comparable pairs", file=sys.stderr)
        return 2
    report = build_report(results)
    if args.format == "markdown":
        print(to_markdown(report))
    else:
        print(to_json(report))
    return 0 if report.verdict.value != "block" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shadowdeploy")
    sub = parser.add_subparsers(dest="command", required=True)

    p_iac = sub.add_parser("emit-iac", help="generate Terraform/CDK")
    p_iac.add_argument("--config", required=True)
    p_iac.add_argument("--environment", default="dev")
    p_iac.set_defaults(func=_cmd_emit_iac)

    p_est = sub.add_parser("estimate", help="estimate added cost")
    p_est.add_argument("--config", required=True)
    p_est.add_argument("--monthly-requests", type=int, required=True, dest="monthly_requests")
    p_est.add_argument("--budget", type=float, default=100.0)
    p_est.set_defaults(func=_cmd_estimate)

    p_rep = sub.add_parser("report", help="build a promotion report from captures")
    p_rep.add_argument("--config", required=True)
    p_rep.add_argument("--captures", required=True)
    p_rep.add_argument("--format", choices=["json", "markdown"], default="json")
    p_rep.set_defaults(func=_cmd_report)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
