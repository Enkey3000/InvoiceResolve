"""Rule-bound reconciliation agent with explicit evidence and approval states."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass

from invoice_resolve.data import Invoice, PurchaseOrder, Receipt


@dataclass(frozen=True)
class Resolution:
    invoice_id: str
    po_id: str
    status: str
    action: str
    evidence: dict[str, object]
    approval_required: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class InvoiceAgent:
    """Reconcile a three-way evidence chain without making payments."""

    def __init__(self, tolerance_cents: int = 25) -> None:
        if tolerance_cents < 0:
            raise ValueError("tolerance_cents must be non-negative")
        self.tolerance_cents = tolerance_cents

    def reconcile(
        self,
        purchase_orders: Iterable[PurchaseOrder],
        receipts: Iterable[Receipt],
        invoices: Iterable[Invoice],
    ) -> list[Resolution]:
        po_by_id = {po.po_id: po for po in purchase_orders}
        receipt_by_po = {receipt.po_id: receipt for receipt in receipts}
        resolutions: list[Resolution] = []
        seen_invoices: set[str] = set()
        for invoice in invoices:
            if invoice.invoice_id in seen_invoices:
                raise ValueEvidenceError(f"Duplicate invoice_id: {invoice.invoice_id}")
            seen_invoices.add(invoice.invoice_id)
            po = po_by_id.get(invoice.po_id)
            receipt = receipt_by_po.get(invoice.po_id)
            if po is None or receipt is None:
                evidence = {"missing_po": po is None, "missing_receipt": receipt is None}
                resolutions.append(
                    Resolution(
                        invoice.invoice_id,
                        invoice.po_id,
                        "blocked",
                        "hold_for_review",
                        evidence,
                        True,
                    )
                )
                continue
            evidence = {
                "po_quantity": po.quantity,
                "received_quantity": receipt.quantity_received,
                "billed_quantity": invoice.quantity_billed,
                "po_unit_price_cents": po.unit_price_cents,
                "billed_unit_price_cents": invoice.unit_price_cents,
                "freight_cents": invoice.freight_cents,
                "vendor_match": po.vendor_id == invoice.vendor_id,
            }
            quantity_ok = (
                invoice.quantity_billed <= receipt.quantity_received
                and invoice.quantity_billed <= po.quantity
            )
            price_delta = abs(invoice.unit_price_cents - po.unit_price_cents)
            price_ok = price_delta <= self.tolerance_cents
            vendor_ok = po.vendor_id == invoice.vendor_id
            freight_ok = invoice.freight_cents <= 1500
            if quantity_ok and price_ok and vendor_ok and freight_ok:
                status = "matched"
                action = "queue_for_approval"
            elif not vendor_ok or not quantity_ok:
                status = "disputed"
                action = "hold_for_review"
            else:
                status = "exception"
                action = "hold_for_review"
            resolutions.append(
                Resolution(
                    invoice.invoice_id,
                    invoice.po_id,
                    status,
                    action,
                    evidence,
                    True,
                )
            )
        return resolutions


class ValueEvidenceError(ValueError):
    """Raised when reconciliation evidence is structurally ambiguous."""
