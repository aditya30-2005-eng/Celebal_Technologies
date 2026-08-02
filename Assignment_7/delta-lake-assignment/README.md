# Delta Lake Assignment

## Objective

Load customer master and incremental CSVs, handle nulls, remove duplicates, create a Delta table, and merge (update existing + insert new) customers using DeltaTable.merge().

## Folder Structure

```
delta-lake-assignment/
├── data/
│   ├── customer_master.csv
│   └── customer_incremental.csv
├── notebooks/
│   └── delta_scd_assignment.ipynb
├── delta_output/
│   ├── customer_master_delta/       # Delta table
│   └── merged_customers.csv
└── screenshots/
    ├── data_loading/
    ├── data_cleaning/
    ├── scd1/
    ├── scd2/
    ├── validation/
    └── final_output/
```

## Files

- `notebooks/delta_scd_assignment.ipynb` – main merge notebook
- `data/customer_master.csv` – existing customer records
- `data/customer_incremental.csv` – incremental updates / new records

## How to Run

1. Open `notebooks/delta_scd_assignment.ipynb` in Jupyter Notebook or VS Code.
2. Run all cells from top to bottom.
3. Results are written to `delta_output/`.

