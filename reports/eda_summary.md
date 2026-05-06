# Procurement Spend Analytics — EDA Summary

**Dataset:** `data/raw/procurement_spend_raw.csv`  
**Analysis Date:** 2026-05-06  
**Pipeline:** `app/ingest/load_data.py`

---

## 1. Dataset Overview

| Metric | Value |
|---|---|
| Total Records | 50 |
| Total Columns (raw) | 16 |
| Total Columns (after flags) | 21 |
| Date Range | 2024-01-05 → 2024-05-28 |
| Total Spend (USD) | $669,120.50 |

---

## 2. Spend Distribution

| Statistic | Amount (USD) |
|---|---|
| Mean | $13,940.01 |
| Median | $9,550.00 |
| Std Dev | $13,592.31 |
| Min | $870.00 |
| 25th Percentile | $4,950.00 |
| 75th Percentile | $16,500.00 |
| Max | $62,000.00 |

> The distribution is right-skewed — a few large POs significantly pull the mean above the median.

---

## 3. Spend by Category

| Category | PO Count |
|---|---|
| IT | 16 |
| Facilities | 7 |
| HR | 6 |
| Office | 5 |
| Marketing | 5 |
| Logistics | 4 |
| Legal | 3 |
| Security | 2 |
| Operations | 2 |

**IT dominates** with 32% of all purchase orders.

---

## 4. Spend by Department

| Department | PO Count |
|---|---|
| Operations | 13 |
| IT | 12 |
| HR | 7 |
| Legal | 5 |
| Marketing | 5 |
| Engineering | 4 |
| Admin | 4 |

---

## 5. PO Status Distribution

| Status | Count |
|---|---|
| Paid | 37 (74%) |
| Pending | 7 (14%) |
| Approved | 4 (8%) |
| Cancelled | 2 (4%) |

---

## 6. Geographic Distribution

| Country | PO Count |
|---|---|
| USA | 36 (72%) |
| UK | 3 |
| Germany | 3 |
| Canada | 2 |
| India | 2 |
| Australia | 2 |
| Singapore | 2 |

US-based transactions make up nearly three-quarters of all POs.

---

## 7. Top 5 Suppliers by Total Spend

| Supplier | Total Spend (USD) |
|---|---|
| TechParts Ltd | $98,500.00 |
| BuildRight Co | $75,250.00 |
| Acme Corp | $68,000.00 |
| AutoParts | $63,700.00 |
| DataSolutions | $52,000.00 |

Top 5 suppliers account for ~53% of total spend.

---

## 8. Missing Value Summary

| Column | Missing Count | Missing % |
|---|---|---|
| invoice_id | 13 | 26.0% |
| invoice_date | 13 | 26.0% |
| quantity | 3 | 6.0% |
| amount_usd | 2 | 4.0% |
| unit_price | 2 | 4.0% |
| supplier_id | 1 | 2.0% |

> `invoice_id` and `invoice_date` have the highest missingness (26%), largely attributable to Pending POs that have not yet been invoiced.

---

## 9. Data Quality Flag Summary

| Flag | Count | % of Records |
|---|---|---|
| `flag_missing_amount` | 2 | 4.0% |
| `flag_missing_supplier` | 1 | 2.0% |
| `flag_zero_quantity` | 0 | 0.0% |
| `flag_cancelled` | 2 | 4.0% |
| `flag_pending_no_invoice` | 7 | 14.0% |

---

## 10. Key Findings & Recommendations

1. **Invoice gaps:** 26% of records lack invoice data — align with AP team to confirm whether these are expected for pending POs or represent gaps.
2. **IT spend concentration:** IT category represents 32% of POs; consider category-level budget controls and vendor consolidation.
3. **Supplier concentration risk:** Top 5 suppliers hold 53% of spend — evaluate dual-sourcing strategy for critical categories.
4. **Missing amount_usd:** 2 records have no spend amount; these must be investigated before any spend reporting is published.
5. **Pending without invoice:** 7 POs are in `Pending` status with no linked invoice — flag for follow-up with procurement operations team.
