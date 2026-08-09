# Changelog

All notable changes to the E-Commerce Order Analytics System are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-01-01

### Added

- Synthetic data generator for customers, products, orders, and order items
  with intentional dirty-data injection (NULLs, duplicates, invalid emails,
  future dates, wrong formats, negative quantities, invalid references, and more).
- Data cleaning pipeline with email validation, referential integrity checks,
  deduplication, date normalisation, and per-entity cleaning reports.
- SQLite database schema with primary/foreign keys, check constraints,
  unique constraints, defaults, indexes, and cascade rules.
- SQL analytics library organised into `basic`, `intermediate`, and `advanced`
  tiers covering revenue, returns, churn, RFM, cohort retention, window
  functions, CTEs, self-joins, and segmentation.
- Database views: `customer_summary`, `product_summary`, `monthly_revenue`,
  and `top_products`.
- CLI reporting tool with revenue, products, retention, cohort, churn,
  segmentation, RFM, monthly, and yearly reports, date/category/customer
  filters, and CSV/TXT export.
- Pytest suite covering data generation, cleaning, database integrity,
  CLI behaviour, edge cases, and query performance.
- Architecture, ER diagram, pipeline, folder structure, business rules,
  data dictionary, SQL explanation, and sample report documentation.

