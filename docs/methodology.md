# Agentic reconciliation methodology

## Synthetic case study

InvoiceResolve demonstrates a narrow autonomous workflow for comparing a purchase
order, goods receipt, and invoice. It generates fictional procurement records, then
runs evidence checks and assigns a resolution status. The workflow never issues a
payment, modifies an invoice, or contacts a vendor.

## Agent behavior

The agent loads three records and maps them by PO ID. It checks that all evidence
exists, that the vendor matches, that billed quantity does not exceed PO quantity or
receipt quantity, that unit price is within a configurable tolerance, and that freight
is below a conservative demonstration cap.

Statuses are:

- `matched`: quantity, price, vendor, and freight checks pass
- `exception`: no disputed quantity/vendor mismatch, but another check fails
- `disputed`: vendor or quantity evidence conflicts
- `blocked`: PO or receipt evidence is missing

Every item has an explicit action and approval state. Even exact matches require
human approval in this demo.

## Limitations

- The synthetic records do not represent real vendor behavior or accounting policy.
- The tolerance and freight rules are illustrative constants, not tax or procurement
  rules.
- The workflow does not calculate tax, discounts, partial goods, currency conversion,
  contract terms, or payment terms.
- CSV inputs omit provenance, revision history, approvals, document images, and
  signed attestations.
- The agent is deterministic; it does not use an LLM or make claims from unstructured
  documents.

## Responsible deployment

Before production use, integrate authorized ERP and AP systems; preserve immutable
source-document links; apply legal accounting and tax rules; test currency, tax,
partial receipt, credit memo, duplicate, and three-way mismatch scenarios; log every
tool call; require dual approval for exceptions; and enforce separation of duties.
