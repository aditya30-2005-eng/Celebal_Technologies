# Pipeline

```
python run_pipeline.py
```

This single command triggers the entire end-to-end workflow:

```
 Generate Data    ──►  Clean Data    ──►  Build Database  ──►  Run SQL Queries
(generate_data.py)    (clean_data.py)     (build_database.py)  (run_sql_queries.py)
       │                     │                    │                     │
       v                     v                    v                     v
  data/raw/*.csv        data/cleaned/*.csv    database/ecommerce.db   stdout / logs
                         reports/*.txt
```

## Step-by-step

### 1. Generate Raw Data

**Script:** `scripts/generate_data.py`

Produces four CSV files under `data/raw/`:

| File              | Rows   | Content                              |
|-------------------|--------|--------------------------------------|
| customers.csv     | ~824   | Name, email, region, city, join date |
| products.csv      | ~515   | Name, category, brand, price, stock  |
| orders.csv        | 3500   | Customer ref, date, status, payment  |
| order_items.csv   | 12000  | Order ref, product ref, qty, price   |

The generator injects approximately 5% NULLs, 3% duplicates, 2% invalid FKs,
and assorted formatting issues.

### 2. Clean Data

**Script:** `scripts/clean_data.py`

Reads the raw CSVs, applies entity-specific cleaning rules, and writes:

| Artefact               | Path                           |
|------------------------|--------------------------------|
| Cleaned customers      | `data/cleaned/customers_clean.csv`  |
| Cleaned products       | `data/cleaned/products_clean.csv`   |
| Cleaned orders         | `data/cleaned/orders_clean.csv`     |
| Cleaned order items    | `data/cleaned/order_items_clean.csv`|
| Cleaning report        | `reports/cleaning_report.txt`       |
| Email validation       | `reports/email_report.txt`          |
| Referential integrity  | `reports/referential_integrity_report.txt` |
| Validation summary     | `reports/validation_report.txt`     |

### 3. Build Database

**Script:** `scripts/build_database.py`

1. Executes `sql/schema.sql` to create tables and indexes.
2. Loads cleaned CSVs into the tables.
3. Executes `sql/views.sql` to create analytical views.
4. Verifies that each table contains exactly the number of rows expected.

**Output:** `database/ecommerce.db`

### 4. Run SQL Analytics

**Script:** `scripts/run_sql_queries.py`

Iterates over every `.sql` file in `sql/basic`, `sql/intermediate`, and
`sql/advanced`, executes each one against the database, and logs a summary
of rows returned. Any query that fails is reported with its error message.

