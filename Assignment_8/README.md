# E-Commerce Order Analytics System

An end-to-end analytics pipeline for e-commerce order data. The project
generates synthetic (intentionally messy) transactional datasets, cleans
them with a set of rules, loads them into a SQLite database, and then runs
a collection of analytical SQL queries and a CLI reporting tool to explore
revenue, retention, RFM, segmentation, cohorts, churn, and more.

Built as part of the Celebal Technologies internship assignment. Written
with Python, Pandas, SQLite, and SQL.

---

## What it does

The whole thing is a simple four-stage pipeline:

```
Generate data  -->  Clean data  -->  Build database  -->  Run reports / SQL
```

Why synthetic data? Real e-commerce data is messy, and a lot of cleaning
logic is easier to demonstrate when you control exactly how the mess looks.
The generator writes customers, products, orders, and order items with a
deliberate amount of dirty data: NULLs, duplicates, bad emails, future
dates, wrong date formats, negative quantities, orphaned references, and a
few other spacing/case issues. The cleaning stage fixes each one and keeps
a report of what was repaired.

Once the data is clean it gets loaded into a SQLite database with primary
keys, foreign keys, check constraints, indexes, and a few views. From there
the project provides:

- 30+ analytical SQL queries split into `basic`, `intermediate`, and
  `advanced` tiers (window functions, CTEs, self-joins, cohort retention,
  RFM, CLV, segmentation, churn).
- A command-line reporting tool that runs some of those queries with
  optional filters and CSV/TXT export.

---

## Project layout

```
.
├── config.py                 # paths, dataset sizes, clean ratios, vocab
├── run_pipeline.py           # runs all four stages in order
├── scripts/                  # the actual pipeline modules
│   ├── generate_data.py      # synthetic dirty data
│   ├── clean_data.py         # cleaning rules + issue reports
│   ├── build_database.py     # schema + views + row verification
│   ├── run_sql_queries.py    # executes every sql/ file
│   └── report_cli.py         # CLI reports
├── sql/
│   ├── schema.sql, views.sql
│   ├── basic/                # 5 queries
│   ├── intermediate/         # 3 queries
│   └── advanced/             # 27 queries
├── data/raw, data/cleaned    # generated + cleaned CSV files
├── database/                 # ecommerce.db (created at runtime)
├── reports/                  # cleaning / validation reports
├── output/                   # CLI exports and sample outputs
├── logs/                     # project.log
├── tests/                    # pytest suite
└── docs/                     # architecture, schema, query notes
```

See [docs/folder_structure.md](docs/folder_structure.md) for the full tree
and [docs/architecture.md](docs/architecture.md) for more on how the stages
fit together.

---

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

`requirements.txt` is just:

```
pandas>=2.2.0
numpy>=1.26.0
faker>=25.0.0
pytest>=8.0.0
```

Python 3.10 or newer is expected.

---

## Quick start

Everything runs from the project root:

```bash
python run_pipeline.py
```

That single command generates the raw CSVs, cleans them, builds
`database/ecommerce.db`, and runs every SQL query. After it finishes you
can try the CLI:

```bash
python scripts/report_cli.py --report revenue
python scripts/report_cli.py --report rfm
python scripts/report_cli.py --report retention
```

Or run the stages one at a time if you want to see each step:

```bash
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/build_database.py
python scripts/run_sql_queries.py
```

---

## CLI reports

The reporting tool reads from `database/ecommerce.db`, so it needs the
pipeline to have been run at least once.

### Daily / weekly / monthly order summary

The assignment requires a Python + SQLite command-line reporting tool that
accepts a `daily`, `weekly`, or `monthly` report type plus a start and end
date, and prints an order summary with total orders, total revenue, unique
customers, top 3 products, and a previous-period comparison with the
percentage change.

```bash
python scripts/report_cli.py --report daily --start-date 2026-01-01 --end-date 2026-01-01
python scripts/report_cli.py --report weekly --start-date 2026-01-01 --end-date 2026-01-07
python scripts/report_cli.py --report monthly --start-date 2026-01-01 --end-date 2026-01-31
```

Example output (weekly):

```
========================================
E-COMMERCE ORDER SUMMARY
========================================

Period: Weekly
Start Date: 2026-01-01
End Date:   2026-01-07

Total Orders:      13
Total Revenue:     133281.28
Unique Customers:  13

Top 3 Products:
1. Stapler (10106.32)
2. Building Blocks (9547.92)
3. Leather Belt (8777.82)

Previous Period:
Previous Revenue: 188498.0
Revenue Change:   -55216.72
Percentage Change:
-29.29%

========================================
```

The summary reports are computed directly from the database using only the
standard library's `sqlite3` module. Empty periods print zero totals and
`N/A (no previous-period revenue)` when there is nothing to compare against.

### Analytical reports

```bash
python scripts/report_cli.py --report revenue          # revenue by category
python scripts/report_cli.py --report products         # top products
python scripts/report_cli.py --report monthly_revenue  # revenue by month
python scripts/report_cli.py --report yearly           # year-over-year revenue
python scripts/report_cli.py --report retention        # retention matrix
python scripts/report_cli.py --report cohort           # cohort activity
python scripts/report_cli.py --report churn            # churn detection
python scripts/report_cli.py --report segmentation     # RFM segments
python scripts/report_cli.py --report rfm              # RFM scores
```

> Note: the assignment reserves the `monthly` name for the summary report.
> The original revenue-by-month analytical report is still available under
> the name `monthly_revenue`.

Filters:

```bash
python scripts/report_cli.py --report revenue --start-date 2023-01-01 --end-date 2023-06-30
python scripts/report_cli.py --report products --category Electronics
python scripts/report_cli.py --report rfm --customer-id 7
```

Not every report accepts every filter. Date filters need the underlying
query to use `o.order_date`, category needs a join to `products`, and
customer filtering is only supported on the customer-centric reports
(`rfm`, `segmentation`, `churn`). Using an unsupported filter prints an
error and exits with a non-zero code.

Export to a file:

```bash
python scripts/report_cli.py --report revenue --export csv
python scripts/report_cli.py --report rfm --export txt
```

CSV exports go to `output/csv/`, text exports to `output/txt/`. Files get a
timestamp suffix so repeated runs don't overwrite each other.

---

## SQL queries

All queries live under `sql/` and assume the schema from `sql/schema.sql`.
The `basic` tier covers simple revenue and ranking queries, `intermediate`
covers returns and never-delivered logic, and `advanced` shows window
functions, CTEs, self-joins, cohort retention, RFM, CLV, segmentation,
churn, and more. Every file is run by `scripts/run_sql_queries.py`, which
writes the result of each to `output/sample_outputs/<name>.csv`.

Assignment-specific queries:

- `sql/advanced/aov_by_segment.sql` — Average Order Value per RFM segment.
  Returns `segment`, `customer_count`, `total_orders`, `total_revenue`, and
  `average_order_value` (total revenue / total orders). It reuses the
  project's RFM segmentation logic.
- `sql/advanced/purchase_frequency_segmentation.sql` — classifies each
  customer as **One-Time**, **Occasional**, or **Loyal** based on order
  frequency. One-Time = 1 order, Occasional = 2–5 orders, Loyal = 6 or more
  orders.
- `sql/advanced/ntile.sql` — customer spending quartiles. Each customer is
  assigned a `quartile` (1–4) via `NTILE(4)` and a `quartile_label`
  (1 = Platinum, 2 = Gold, 3 = Silver, 4 = Bronze).
- `sql/advanced/self_join.sql` — frequently bought together. Returns
  `product_a`, `product_b`, and `times_bought_together` for product pairs
  bought in the same order. The `product_a < product_b` condition excludes
  same-product pairs and prevents A-B / B-A duplicates. No same-category
  restriction is applied, so cross-category pairs are included.

A short explanation of every query is in
[docs/sql_explanation.md](docs/sql_explanation.md).

---

## Screenshots

Real output from the project is captured under `output/screenshots/`:

| File | Shows |
|------|-------|
| `01_pipeline.png` | Pipeline execution log |
| `02_revenue_report.png` | SQL report: revenue by category |
| `03_top_customers.png` | SQL report: top 10 customers |
| `04_cohort_retention.png` | SQL report: cohort / retention |
| `05_cli_summary.png` | CLI weekly order summary |

Regenerate them with:

```bash
python scripts/generate_screenshots.py
```

---

## Assignment column compatibility

The existing project uses a set of column names that differ slightly from
the official assignment's conceptual schema. To stay compatible without
breaking the existing SQL and CLI, the cleaning stage preserves the
original columns and adds assignment-compatible alias columns where the
assignment uses a different name. Each alias shares a single source of
truth with its original, so there is no duplicate or conflicting data.

| Dataset     | Existing column     | Assignment-compatible alias |
|-------------|---------------------|-----------------------------|
| customers   | `name`              | `customer_name`             |
| customers   | `joined_date`       | `registration_date`         |
| customers   | *(new)*             | `customer_type`             |
| products    | *(new)*             | `subcategory`               |
| products    | *(new)*             | `cost_price`                |
| orders      | `shipping_region`   | `region_code`               |
| order_items | `order_item_id`     | `item_id`                   |
| order_items | `discount`          | `discount_percent`          |

The new `customer_type`, `subcategory`, and `cost_price` columns carry
realistic values generated in `scripts/generate_data.py` and are cleaned
alongside the existing fields, so they appear in the cleaned CSVs and the
SQLite database.

## Tests

```bash
pytest -v
```

The test suite covers the generator (including that dirty data is actually
injected), the cleaning rules and line-total math, schema and referential
integrity, CLI parsing and filters, a set of edge cases, and basic
performance bounds on a few of the heavier queries.

---

## Documentation

| File | What it covers |
|------|----------------|
| [docs/architecture.md](docs/architecture.md) | How the stages fit together |
| [docs/er_diagram.md](docs/er_diagram.md) | Tables and relationships |
| [docs/pipeline.md](docs/pipeline.md) | Step-by-step pipeline walkthrough |
| [docs/data_dictionary.md](docs/data_dictionary.md) | Column definitions |
| [docs/business_rules.md](docs/business_rules.md) | Cleaning rules and assumptions |
| [docs/sql_explanation.md](docs/sql_explanation.md) | What each SQL query answers |
| [docs/sample_reports.md](docs/sample_reports.md) | Example CLI output |
| [docs/folder_structure.md](docs/folder_structure.md) | Repository tree |

---

## Notes and limitations

- The data is purely synthetic; it is fine for learning and demonstrating
  a pipeline, but it should not be treated as real business data.
- Only `--customer-id` on `rfm`, `segmentation`, and `churn` supports
  customer-level filtering right now. Adding it to the revenue reports
  would require a per-customer breakdown in those queries.

## License

MIT, see [LICENSE](LICENSE).

