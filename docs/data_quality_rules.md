# Data Quality Rules — Procurement Spend Analytics

**Module:** `app/ingest/load_data.py`  
**Last Updated:** 2026-05-06

This document defines the data quality rules enforced during ingestion of the procurement spend dataset. Rules are grouped by category and map directly to validation logic in the pipeline.

---

## 1. Schema Rules

### DQ-001 — Required Columns Present
- **Description:** The ingested CSV must contain all 16 expected columns.
- **Expected Columns:** `po_id`, `po_date`, `supplier_id`, `supplier_name`, `category`, `subcategory`, `department`, `country`, `amount_usd`, `currency`, `payment_terms`, `status`, `invoice_id`, `invoice_date`, `quantity`, `unit_price`
- **Action on Failure:** Raise `ValueError` — pipeline halts immediately.
- **Implemented In:** `validate_columns()`

---

## 2. Type & Format Rules

### DQ-002 — Numeric Columns Must Be Castable to Float
- **Columns:** `amount_usd`, `quantity`, `unit_price`
- **Rule:** Values must be parseable as numeric after stripping whitespace. Non-parseable values are coerced to `NaN`.
- **Action:** Coerce invalid values to `NaN`; downstream flag rules will detect missing amounts.
- **Implemented In:** `cast_types()`

### DQ-003 — Date Columns Must Be Parseable
- **Columns:** `po_date`, `invoice_date`
- **Rule:** Values must be parseable as dates. Invalid/unparseable dates are coerced to `NaT`.
- **Action:** Coerce to `NaT`; records with `NaT` in `po_date` should be reviewed.
- **Implemented In:** `cast_types()`

### DQ-004 — String Columns Must Not Be Empty Strings
- **Columns:** All columns except numeric and date columns.
- **Rule:** Empty strings (after whitespace trimming) are replaced with `pd.NA`.
- **Action:** Replace with `pd.NA`.
- **Implemented In:** `cast_types()`

---

## 3. Completeness Rules

### DQ-005 — `amount_usd` Must Not Be Null
- **Column:** `amount_usd`
- **Rule:** Every PO must have a spend amount in USD.
- **Flag:** `flag_missing_amount = True` when `amount_usd` is `NaN`.
- **Severity:** High — records without spend amounts must be excluded from all spend aggregations.
- **Threshold:** > 0 missing records triggers investigation.
- **Implemented In:** `flag_anomalies()`

### DQ-006 — Supplier Identity Must Be Present
- **Columns:** `supplier_id`, `supplier_name`
- **Rule:** Both `supplier_id` and `supplier_name` must be present on every PO.
- **Flag:** `flag_missing_supplier = True` when either is `NaN`.
- **Severity:** High — unidentified suppliers cannot be included in supplier-level reporting.
- **Implemented In:** `flag_anomalies()`

### DQ-007 — `invoice_id` and `invoice_date` Are Conditionally Required
- **Columns:** `invoice_id`, `invoice_date`
- **Rule:** Records with `status = Paid` or `status = Approved` must have both `invoice_id` and `invoice_date` populated.
- **Flag:** `flag_pending_no_invoice` captures `Pending` POs without invoice data.
- **Severity:** Medium — acceptable for `Pending` status; unacceptable for `Paid`/`Approved`.
- **Note:** 26% of records currently have missing invoice fields; correlation with `Pending` status should be validated before reporting.
- **Implemented In:** `flag_anomalies()`

---

## 4. Validity Rules

### DQ-008 — `quantity` Must Not Be Zero
- **Column:** `quantity`
- **Rule:** Any PO with `quantity = 0` while `quantity` is not null indicates a likely data entry error.
- **Flag:** `flag_zero_quantity = True`
- **Severity:** Medium — zero-quantity POs with non-zero `amount_usd` are financially inconsistent.
- **Implemented In:** `flag_anomalies()`

### DQ-009 — `status` Must Be a Known Value
- **Column:** `status`
- **Allowed Values:** `Paid`, `Pending`, `Approved`, `Cancelled`
- **Rule:** Any value outside the allowed set should be treated as invalid.
- **Action:** Log a warning; consider rejecting or quarantining unknown status values.
- **Severity:** Medium
- **Note:** Not yet implemented in pipeline — recommended for next iteration.

### DQ-010 — `amount_usd` Must Be Positive
- **Column:** `amount_usd`
- **Rule:** Spend amounts must be greater than zero. Negative values indicate credits or errors.
- **Action:** Flag records with `amount_usd <= 0` for review.
- **Severity:** High
- **Note:** Not yet implemented in pipeline — recommended for next iteration.

### DQ-011 — `unit_price` × `quantity` Should Reconcile with `amount_usd`
- **Columns:** `amount_usd`, `unit_price`, `quantity`
- **Rule:** `unit_price * quantity` should approximate `amount_usd` within a configurable tolerance (e.g., ±1%).
- **Severity:** Medium — discrepancies may indicate currency conversion, discounts, or data entry errors.
- **Note:** Not yet implemented in pipeline — recommended for next iteration.

---

## 5. Consistency Rules

### DQ-012 — Cancelled POs Should Not Have Paid Invoices
- **Columns:** `status`, `invoice_id`
- **Rule:** Records with `status = Cancelled` should not have a linked `invoice_id`.
- **Flag:** `flag_cancelled = True` for all cancelled records (used to filter from spend reports).
- **Severity:** Low — warrants review but not necessarily blocking.
- **Implemented In:** `flag_anomalies()`

---

## 6. Flag Summary Reference

| Flag Column | Rule(s) | Severity |
|---|---|---|
| `flag_missing_amount` | DQ-005 | High |
| `flag_missing_supplier` | DQ-006 | High |
| `flag_zero_quantity` | DQ-008 | Medium |
| `flag_cancelled` | DQ-012 | Low |
| `flag_pending_no_invoice` | DQ-007 | Medium |

---

## 7. Remediation Guidelines

| Severity | Action |
|---|---|
| **High** | Exclude from all aggregations and reports until resolved. Alert data owner. |
| **Medium** | Include in reports with a footnote; escalate to source system owner within 5 business days. |
| **Low** | Log and monitor; no immediate reporting exclusion required. |

---

## 8. Future Enhancements

- [ ] Implement DQ-009 (`status` allowed values check)
- [ ] Implement DQ-010 (non-positive `amount_usd` check)
- [ ] Implement DQ-011 (`unit_price × quantity` reconciliation)
- [ ] Add `po_date` must not be in the future rule
- [ ] Add cross-field rule: `invoice_date` must be >= `po_date`
