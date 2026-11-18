"""Command-line entry points for the InvoiceResolve demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from invoice_resolve.agent import InvoiceAgent
from invoice_resolve.data import generate_records, write_records
from invoice_resolve.loaders import load_invoices, load_purchase_orders, load_receipts
from invoice_resolve.reports import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="invoice-resolve",
        description="Run a local, auditable three-way invoice reconciliation demo.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="generate synthetic procurement records")
    generate.add_argument("--output-dir", type=Path, default=Path("data/sample"))
    generate.add_argument("--seed", type=int, default=89)

    reconcile = commands.add_parser("reconcile", help="reconcile invoices against POs and receipts")
    reconcile.add_argument("--input-dir", type=Path, default=Path("data/sample"))
    reconcile.add_argument("--output-dir", type=Path, default=Path("build/reports"))
    reconcile.add_argument("--tolerance-cents", type=int, default=25)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "generate":
            purchase_orders, receipts, invoices = generate_records(seed=args.seed)
            write_records(purchase_orders, receipts, invoices, args.output_dir)
            print(
                f"Wrote {len(purchase_orders)} POs, {len(receipts)} receipts, "
                f"and {len(invoices)} invoices to {args.output_dir}"
            )
            print("These records are fictional and must not be used for real payments.")
            return 0

        purchase_orders = load_purchase_orders(args.input_dir / "purchase_orders.csv")
        receipts = load_receipts(args.input_dir / "receipts.csv")
        invoices = load_invoices(args.input_dir / "invoices.csv")
        resolutions = InvoiceAgent(tolerance_cents=args.tolerance_cents).reconcile(
            purchase_orders,
            receipts,
            invoices,
        )
        metrics_path, queue_path = write_reports(resolutions, args.output_dir)
        counts: dict[str, int] = {}
        for item in resolutions:
            counts[item.status] = counts.get(item.status, 0) + 1
        print(
            json.dumps(
                {
                    "invoice_count": len(resolutions),
                    "status_counts": counts,
                    "approval_required": sum(item.approval_required for item in resolutions),
                },
                indent=2,
            )
        )
        print(f"Metrics: {metrics_path}")
        print(f"Approval queue: {queue_path}")
        print(
            "No payment or vendor action was performed. A human approver must authorize "
            "matched or exceptional items."
        )
    except (OSError, TypeError, ValueError) as exc:
        print(f"invoice-resolve: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
