"""Validated CSV loaders for purchase orders, receipts, and invoices."""

from __future__ import annotations

import csv
from pathlib import Path

from invoice_resolve.data import Invoice, PurchaseOrder, Receipt


def _rows(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path.name} is missing columns: {', '.join(sorted(missing))}")
        return list(reader)


def _positive_int(row: dict[str, str], field: str) -> int:
    try:
        value = int(row[field])
    except (KeyError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if value < 0:
        raise ValueError(f"{field} must be non-negative")
    return value


def load_purchase_orders(path: Path) -> list[PurchaseOrder]:
    rows = _rows(path, {"po_id", "vendor_id", "item", "quantity", "unit_price_cents"})
    records: list[PurchaseOrder] = []
    ids: set[str] = set()
    for row in rows:
        po_id = row["po_id"].strip()
        if not po_id or po_id in ids:
            raise ValueError(f"Empty or duplicate po_id: {po_id!r}")
        records.append(
            PurchaseOrder(
                po_id,
                row["vendor_id"].strip(),
                row["item"].strip(),
                _positive_int(row, "quantity"),
                _positive_int(row, "unit_price_cents"),
            )
        )
        ids.add(po_id)
    return records


def load_receipts(path: Path) -> list[Receipt]:
    rows = _rows(path, {"receipt_id", "po_id", "quantity_received"})
    records: list[Receipt] = []
    ids: set[str] = set()
    for row in rows:
        receipt_id = row["receipt_id"].strip()
        po_id = row["po_id"].strip()
        if not receipt_id or receipt_id in ids:
            raise ValueError(f"Empty or duplicate receipt_id: {receipt_id!r}")
        records.append(Receipt(receipt_id, po_id, _positive_int(row, "quantity_received")))
        ids.add(receipt_id)
    return records


def load_invoices(path: Path) -> list[Invoice]:
    rows = _rows(
        path,
        {
            "invoice_id",
            "po_id",
            "vendor_id",
            "quantity_billed",
            "unit_price_cents",
            "freight_cents",
        },
    )
    records: list[Invoice] = []
    ids: set[str] = set()
    for row in rows:
        invoice_id = row["invoice_id"].strip()
        if not invoice_id or invoice_id in ids:
            raise ValueError(f"Empty or duplicate invoice_id: {invoice_id!r}")
        records.append(
            Invoice(
                invoice_id,
                row["po_id"].strip(),
                row["vendor_id"].strip(),
                _positive_int(row, "quantity_billed"),
                _positive_int(row, "unit_price_cents"),
                _positive_int(row, "freight_cents"),
            )
        )
        ids.add(invoice_id)
    return records
