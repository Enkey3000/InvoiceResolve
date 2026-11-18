"""Synthetic invoice, purchase-order, and receipt generation."""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PurchaseOrder:
    po_id: str
    vendor_id: str
    item: str
    quantity: int
    unit_price_cents: int


@dataclass(frozen=True)
class Receipt:
    receipt_id: str
    po_id: str
    quantity_received: int


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    po_id: str
    vendor_id: str
    quantity_billed: int
    unit_price_cents: int
    freight_cents: int


def generate_records(
    seed: int = 89, count: int = 24
) -> tuple[list[PurchaseOrder], list[Receipt], list[Invoice]]:
    rng = random.Random(seed)
    items = ("paper", "toner", "cleaning-kit", "cables", "gloves")
    purchase_orders: list[PurchaseOrder] = []
    receipts: list[Receipt] = []
    invoices: list[Invoice] = []
    for index in range(count):
        po_id = f"PO-{index + 1:04d}"
        vendor_id = f"VEN-{rng.randint(1, 4):03d}"
        quantity = rng.randint(4, 20)
        unit_price = rng.randint(250, 4500)
        item = items[index % len(items)]
        purchase_orders.append(PurchaseOrder(po_id, vendor_id, item, quantity, unit_price))
        received = quantity
        if index % 7 == 6:
            received = max(0, quantity - rng.randint(1, 3))
        receipts.append(Receipt(f"RCPT-{index + 1:04d}", po_id, received))
        billed_quantity = quantity
        billed_price = unit_price
        freight = 0
        if index % 5 == 4:
            billed_quantity = quantity + rng.randint(1, 3)
        if index % 9 == 8:
            billed_price += rng.randint(50, 300)
        if index % 11 == 10:
            freight = rng.randint(500, 1500)
        invoices.append(
            Invoice(
                f"INV-{index + 1:04d}",
                po_id,
                vendor_id,
                billed_quantity,
                billed_price,
                freight,
            )
        )
    return purchase_orders, receipts, invoices


def _write(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_records(
    purchase_orders: list[PurchaseOrder],
    receipts: list[Receipt],
    invoices: list[Invoice],
    output_dir: Path,
) -> None:
    _write(
        output_dir / "purchase_orders.csv",
        ("po_id", "vendor_id", "item", "quantity", "unit_price_cents"),
        [record.__dict__ for record in purchase_orders],
    )
    _write(
        output_dir / "receipts.csv",
        ("receipt_id", "po_id", "quantity_received"),
        [record.__dict__ for record in receipts],
    )
    _write(
        output_dir / "invoices.csv",
        (
            "invoice_id",
            "po_id",
            "vendor_id",
            "quantity_billed",
            "unit_price_cents",
            "freight_cents",
        ),
        [record.__dict__ for record in invoices],
    )
