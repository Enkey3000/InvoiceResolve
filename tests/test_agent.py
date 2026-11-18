import csv

import pytest

from invoice_resolve.agent import InvoiceAgent
from invoice_resolve.data import Invoice, PurchaseOrder, Receipt, generate_records
from invoice_resolve.reports import write_reports


def test_agent_produces_mutually_exclusive_statuses():
    purchase_orders, receipts, invoices = generate_records(seed=89)
    resolutions = InvoiceAgent().reconcile(purchase_orders, receipts, invoices)
    assert len(resolutions) == len(invoices)
    assert {item.status for item in resolutions} <= {"matched", "exception", "disputed", "blocked"}


def test_agent_routes_exact_three_way_match_for_approval():
    po = PurchaseOrder("PO-1", "VEN-1", "paper", 10, 1000)
    receipt = Receipt("RCPT-1", "PO-1", 10)
    invoice = Invoice("INV-1", "PO-1", "VEN-1", 10, 1000, 0)
    resolution = InvoiceAgent().reconcile([po], [receipt], [invoice])[0]
    assert resolution.status == "matched"
    assert resolution.action == "queue_for_approval"
    assert resolution.approval_required


def test_agent_flags_quantity_mismatch():
    po = PurchaseOrder("PO-1", "VEN-1", "paper", 10, 1000)
    receipt = Receipt("RCPT-1", "PO-1", 8)
    invoice = Invoice("INV-1", "PO-1", "VEN-1", 10, 1000, 0)
    resolution = InvoiceAgent().reconcile([po], [receipt], [invoice])[0]
    assert resolution.status == "disputed"
    assert resolution.approval_required


def test_agent_blocks_missing_evidence():
    invoice = Invoice("INV-1", "PO-MISSING", "VEN-1", 10, 1000, 0)
    resolution = InvoiceAgent().reconcile([], [], [invoice])[0]
    assert resolution.status == "blocked"
    assert resolution.action == "hold_for_review"


def test_negative_tolerance_is_rejected():
    with pytest.raises(ValueError, match="tolerance_cents"):
        InvoiceAgent(tolerance_cents=-1)


def test_reports_write_queue(tmp_path):
    purchase_orders, receipts, invoices = generate_records()
    resolutions = InvoiceAgent().reconcile(purchase_orders, receipts, invoices)
    metrics_path, queue_path = write_reports(resolutions, tmp_path)
    assert metrics_path.is_file()
    with queue_path.open(newline="", encoding="utf-8") as file:
        assert len(list(csv.DictReader(file))) == len(resolutions)
