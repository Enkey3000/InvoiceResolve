import pytest

from invoice_resolve.data import generate_records, write_records
from invoice_resolve.loaders import load_invoices, load_purchase_orders, load_receipts


def test_generated_records_are_deterministic():
    assert generate_records(seed=89) == generate_records(seed=89)


def test_csv_round_trip(tmp_path):
    purchase_orders, receipts, invoices = generate_records()
    write_records(purchase_orders, receipts, invoices, tmp_path)
    assert load_purchase_orders(tmp_path / "purchase_orders.csv") == purchase_orders
    assert load_receipts(tmp_path / "receipts.csv") == receipts
    assert load_invoices(tmp_path / "invoices.csv") == invoices


def test_loader_rejects_duplicate_po(tmp_path):
    path = tmp_path / "purchase_orders.csv"
    path.write_text(
        "po_id,vendor_id,item,quantity,unit_price_cents\n"
        "PO-1,V1,paper,10,100\n"
        "PO-1,V1,paper,10,100\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate po_id"):
        load_purchase_orders(path)
