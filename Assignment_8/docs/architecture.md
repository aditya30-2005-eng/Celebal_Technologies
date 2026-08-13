# Architecture

The E-Commerce Order Analytics System is a staged data pipeline built with
Python, Pandas, and SQLite. It moves data through four explicit stages:
synthesis, cleansing, persistence, and reporting. Each stage is owned by a
dedicated module and produces an artefact consumed by the next stage.

```
                     +---------------------+
                     |   Config (config.py)|
                     | paths, ratios, vocab|
                     +----------+----------+
                                |
         +-----------+----------+-----------+-----------+
         |           |                      |           |
         v           v                      v           v
   generate_data clean_data          build_database  report_cli
   (Faker/random)  (pandas)          (sqlite3)       (sqlite3)
         |           |                      |           |
         |   issue reports                 |           |
         v           v                      v           v
   data/raw/     data/cleaned/        database/     output/
   *.csv         *.csv                ecommerce.db  reports | csv | txt
```

## Stage 1 - Data Generation

`scripts/generate_data.py` uses `Faker` and a seeded `random.Random` instance
to build four related datasets: customers, products, orders, and order items.
The generator is deliberately polluted with the following classes of dirty
data so that the subsequent cleaning stage has realistic work to do:

- NULL and empty-string values
- Duplicate rows and duplicate identifiers
- Orphan foreign keys (customer, order, product references)
- Future order dates and alternate date formats (`dd-mm-yyyy`, `mm/dd/yyyy`)
- Mixed-case text, leading/trailing whitespace, and zero-padded identifiers
- Invalid email addresses
- Missing product prices
- Discounts above 100% or below 0%
- Zero and negative quantities
- Invalid statuses and categories
- Random unicode and wrong-datatype values

## Stage 2 - Data Cleaning

`scripts/clean_data.py` reads each raw CSV and repairs the dirty data:

- `clean_customers()` normalises names, lowers and validates emails, dedups,
  and parses joined dates.
- `clean_products()` normalises names and categories, dedups by product id,
  and coerces numeric price/stock values.
- `clean_orders()` parses and clamps dates, validates status, and enforces
  customer foreign keys.
- `clean_order_items()` repairs quantities, clamps discounts, validates order
  and product references, and computes the line total.

An `IssueTracker` accumulates every repair decision and writes a structured
cleaning report. Email validation, referential integrity, and dataset-level
validation summaries are emitted alongside.

## Stage 3 - Database Build

`scripts/build_database.py` executes `sql/schema.sql` which creates the four
tables with primary/foreign keys, check constraints, unique constraints,
defaults, indexes, and `ON DELETE CASCADE` / `ON UPDATE CASCADE` rules. The
cleaned CSVs are loaded with `INSERT` statements and every table count is
verified against the source files. `sql/views.sql` then creates convenience
views used across the reporting layer.

## Stage 4 - Reporting

`scripts/report_cli.py` exposes a command-line interface. Each report maps
to an SQL file under `sql/basic`, `sql/intermediate`, or `sql/advanced`.
Filters (customer id, category, date range) are injected as parameterised
`WHERE` conditions. Results render as aligned plain-text tables and may be
exported to CSV or TXT.

## Orchestration

`run_pipeline.py` sequences the four stages and `scripts/run_sql_queries.py`
executes every SQL analytics file, logging a summary of rows returned per
query.

## Design Principles

- **Configuration first.** Sizes, ratios, paths, and domain vocabularies live
  in `config.py`; scripts contain no magic numbers.
- **Modular and testable.** Cleaner and generator methods accept explicit
  paths and sizes so integration tests can isolate their behaviour.
- **Parameters over string interpolation.** Report filters use SQL bind
  parameters, avoiding injection and type coercions at the boundary.
- **Logging throughout.** Each stage writes to `logs/project.log` using the
  standard `logging` module rather than `print()`.

