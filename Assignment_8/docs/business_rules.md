# Business Rules

This document lists the business logic applied during the cleaning stage and
the assumptions encoded in the analytical SQL queries.

## Cleaning Rules

### Customers

| Rule                            | Implementation                                 |
|---------------------------------|------------------------------------------------|
| Null customer id               | Row dropped                                     |
| Duplicate customer id          | Keep first occurrence                           |
| Duplicate email                 | Keep first occurrence                           |
| Invalid email                   | Row dropped (email must match RFC-style check)  |
| Whitespace / extra spaces       | `normalize_text()` trims and collapses spaces   |
| Mixed case name                 | Title-cased                                      |
| Empty name                      | Replaced with `Unknown Customer`                |
| Empty region / city             | Replaced with `Unknown`                         |
| Unparseable joined date         | Defaulted to `2020-01-01`                       |
| Future joined date              | Row dropped                                      |

### Products

| Rule                          | Implementation                                  |
|-------------------------------|-------------------------------------------------|
| Null product id               | Row dropped                                      |
| Duplicate product id          | Keep first occurrence                            |
| Mixed case name/category/brand | Title-cased                                     |
| Empty name                    | Replaced with `Unnamed Product`                  |
| Empty category                | Replaced with `Uncategorized`                    |
| Empty brand                   | Replaced with `Unknown`                          |
| Missing or non-numeric price   | Defaulted to `19.99`                             |
| Negative stock                | Clamped to `0`                                   |

### Orders

| Rule                          | Implementation                                  |
|-------------------------------|-------------------------------------------------|
| Null order id                | Row dropped                                      |
| Duplicate order id           | Keep first occurrence                            |
| Null customer id             | Row dropped                                      |
| Orphan customer reference    | Row dropped                                      |
| Future order date            | Clamped to today and recorded as an issue        |
| Alternate date formats       | Parsed (`%Y-%m-%d`, `%d-%m-%Y`, `%m/%d/%Y`, etc.) |
| Invalid status               | Replaced with `PENDING`                          |
| Empty payment method         | Replaced with `unknown`                          |
| Empty shipping region        | Replaced with `Unknown`                          |

### Order Items

| Rule                          | Implementation                                  |
|-------------------------------|-------------------------------------------------|
| Null line identifier          | Row dropped                                      |
| Null quantity                 | Defaulted to `1`                                 |
| Zero quantity                 | Replaced with `1`                                |
| Negative quantity             | Absolute value taken                             |
| Null unit price               | Defaulted to `0.0`                               |
| Discount over 100%            | Clamped to `0.0`                                 |
| Negative discount             | Clamped to `0.0`                                 |
| Orphan order reference        | Row dropped                                      |
| Orphan product reference      | Row dropped                                      |
| `line_total`                  | Computed as `quantity * unit_price * (1 - discount)` |

## Analytical Assumptions

- **Revenue** is the sum of `line_total` for non-cancelled orders
  (statuses other than `CANCELLED` and `REFUNDED`).
- **Return rate** is the share of a product's units that were ordered with
  status `RETURNED`.
- **Never delivered** means no order for the customer has reached
  `DELIVERED` status.
- **Recency** (RFM) is measured in days from the latest `order_date` in the
  dataset to the most recent purchase.
- **Churn** is determined by `days_inactive` (days since last order) with
  five bands: `Active`, `Slipping`, `At Risk`, `Churned`, and
  `Churned - Long Term`.
- **Cohorts** are defined by the calendar month (`YYYY-MM`) of a customer's
  first purchase; retention is measured across subsequent months.

