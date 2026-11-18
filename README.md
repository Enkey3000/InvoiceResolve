# InvoiceResolve

**A local, auditable agent-style workflow for three-way invoice reconciliation.**

InvoiceResolve compares synthetic purchase orders, receipts, and invoices. It
produces an evidence record, a resolution status, and an approval queue. The demo
does not submit payments, change vendor records, or contact external systems.

> **Scope:** All records, prices, vendors, and reconciliation outcomes are synthetic.
> This project is a software pattern, not an accounting or accounts-payable system.

## Executive summary and case study

A fictional procurement team receives invoices after issuing purchase orders and
recording receipts. Manual three-way review is repetitive and slow. InvoiceResolve
demonstrates an agentic pipeline that gathers evidence, applies rule-bound checks,
and hands every item to an approval state. Exact matches are not paid automatically:
the workflow intentionally requires explicit human authorization.

## Quick start (PowerShell)

Requires Python 3.10 or later.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
invoice-resolve generate --output-dir data/sample --seed 89
invoice-resolve reconcile --input-dir data/sample --output-dir build/reports
python -m pytest
ruff check .
```

Run from source without the console script:

```powershell
$env:PYTHONPATH = "src"
python -m invoice_resolve.cli reconcile --input-dir data/sample --output-dir build/reports
```

The reconciliation writes `build/reports/evaluation.json` and
`build/reports/approval_queue.csv`.

## Data contract

`purchase_orders.csv`:

- PO ID, vendor ID, item, quantity, and unit price cents

`receipts.csv`:

- Receipt ID, PO ID, and quantity received

`invoices.csv`:

- Invoice ID, PO ID, vendor ID, billed quantity, unit price cents, and freight cents

The loaders reject missing columns, duplicate IDs, negative values, and malformed
integers.

## Five assumptions and solutions

1. **PO, receipt, and invoice share stable identifiers.** Map evidence by PO ID and
   reject ambiguous duplicate evidence.
2. **Small price variations may be acceptable.** Apply a configurable cents tolerance.
3. **Quantity should be controlled by both PO and receipt.** Reject billed quantities
   exceeding either evidence source.
4. **Missing or conflicting evidence needs stopping.** Return `blocked` or `disputed`
   and require review.
5. **An agent should not execute money movement.** Emit approval actions only and
   preserve the evidence trail.

## Foreseeable questions

**Is this an autonomous payment system?** No. It has no ERP, bank, or vendor access.

**Why require approval for matched invoices?** Separation of duties and synthetic
safety policy keep the demo from making financial decisions.

**What tools can the agent use?** The demo currently uses CSV loaders, deterministic
reconciliation rules, and report writers.

**How is the result audited?** Every output carries invoice ID, PO ID, status, action,
approval state, and source evidence values.

**Can it process real AP documents?** Not without an approved integration,
document-extraction layer, accounting policy engine, and security review.

## Automation, optimization, and potential cost savings

- **Automation:** Batch reconcile authorized records and surface only exceptions.
- **Optimization:** Tune tolerance and routing rules using approved historical outcomes.
- **Potential savings:** Review preparation and exception triage could reduce AP
  handling time. This project makes no measured productivity or cost claim.

## Project layout

```text
InvoiceResolve/
├── .github/workflows/ci.yml
├── data/sample/
├── docs/methodology.md
├── reports/
├── src/invoice_resolve/
├── tests/
├── pyproject.toml
└── README.md
```

## License

MIT. See [LICENSE](LICENSE).
