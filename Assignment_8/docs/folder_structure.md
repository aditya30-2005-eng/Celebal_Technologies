# Project Folder Structure

```
ecommerce-order-analytics/
|
|-- config.py                      # Central configuration (paths, sizes, ratios, vocab)
|-- run_pipeline.py                # One-command orchestration script
|-- requirements.txt               # Python dependencies
|-- .gitignore                     # Ignored files (venv, caches, DBs, outputs)
|-- LICENSE                        # MIT license
|-- CHANGELOG.md                   # Version history
|-- CONTRIBUTING.md                # Developer guidelines
|-- README.md                      # Project overview and usage
|
|-- scripts/
|   |-- __init__.py
|   |-- utils.py                   # Shared helpers (to_int, to_float, email validation, etc.)
|   |-- generate_data.py           # Synthetic dirty-data generator
|   |-- clean_data.py              # Data cleaning pipeline
|   |-- build_database.py          # SQLite schema execution and data loading
|   |-- report_cli.py              # CLI reporting tool
|   |-- run_sql_queries.py         # Execute all SQL analytics files
|
|-- sql/
|   |-- schema.sql                 # Table DDL with PK/FK/CHECK/UNIQUE/NOT NULL/INDEX/DEFAULT/CASCADE
|   |-- views.sql                  # Analytical views (customer_summary, product_summary, monthly_revenue, top_products)
|   |-- basic/
|   |   |-- revenue_by_category.sql
|   |   |-- revenue_by_customer.sql
|   |   |-- revenue_by_month.sql
|   |   |-- top_customers.sql
|   |   |-- top_products.sql
|   |-- intermediate/
|   |   |-- never_delivered.sql
|   |   |-- return_rate.sql
|   |   |-- products_returned_more_than_sold.sql
|   |-- advanced/
|   |   |-- running_total.sql
|   |   |-- moving_average.sql
|   |   |-- dense_rank.sql
|   |   |-- rank.sql
|   |   |-- row_number.sql
|   |   |-- lag.sql
|   |   |-- lead.sql
|   |   |-- window_functions.sql
|   |   |-- nested_cte.sql
|   |   |-- multi_level_cte.sql
|   |   |-- year_over_year.sql
|   |   |-- ntile.sql
|   |   |-- quartiles.sql
|   |   |-- first_last_value.sql
|   |   |-- cumulative_distribution.sql
|   |   |-- self_join.sql
|   |   |-- cohort_analysis.sql
|   |   |-- retention.sql
|   |   |-- customer_lifetime_value.sql
|   |   |-- rfm.sql
|   |   |-- segmentation.sql
|   |   |-- spend_tier.sql
|   |   |-- frequency_tier.sql
|   |   |-- repeat_customers.sql
|   |   |-- churn_detection.sql
|
|-- data/
|   |-- raw/                       # Generated CSVs (with intentional dirty data)
|   |-- cleaned/                   # Cleaned CSVs
|
|-- database/
|   |-- ecommerce.db               # SQLite database (generated at runtime)
|
|-- tests/
|   |-- __init__.py
|   |-- conftest.py                # Fixtures (generator, cleaner, built_database, etc.)
|   |-- test_generate_data.py      # Generator integrity and dirty-data presence
|   |-- test_clean_data.py         # Cleaning logic, issue tracker, line totals
|   |-- test_build_database.py     # Schema enforcement, FK integrity, views
|   |-- test_report_cli.py         # CLI parsing, date validation, filters, empty results
|   |-- test_edge_cases.py         # Future dates, discount>100, qty=0, missing FK, etc.
|   |-- test_performance.py        # Baseline performance bounds for complex queries
|
|-- logs/
|   |-- project.log                # Pipeline execution log
|
|-- reports/                       # Cleaning and validation reports
|
|-- output/
|   |-- csv/                       # CSV exports from the CLI
|   |-- txt/                       # Text exports from the CLI
|   |-- reports/                   # Additional output reports
|   |-- sample_outputs/
|   |-- screenshots/
|
|-- docs/
    |-- architecture.md            # System architecture and design principles
    |-- er_diagram.md              # Entity-relationship diagram and constraints
    |-- pipeline.md                # Stage-by-stage pipeline walkthrough
    |-- folder_structure.md        # This file
    |-- data_dictionary.md         # Column-level descriptions for each table
    |-- business_rules.md          # Business logic applied during cleaning
    |-- sql_explanation.md         # Purpose of every SQL query
    |-- sample_reports.md          # Example CLI output
```

