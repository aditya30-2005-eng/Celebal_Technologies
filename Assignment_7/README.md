# Superstore Data Cleaning and Delta Lake Assignment

## Objective

Clean the Superstore dataset with Pandas and perform a Delta Lake customer merge.

## Folder Structure

```
Assignment_7/
├── assignment.ipynb                 # Pandas data loading, exploration & cleaning
├── Superstore.csv                   # Raw dataset
├── cleaned_superstore.csv           # Cleaned output
├── README.md
└── delta-lake-assignment/
    ├── data/                        # customer_master.csv, customer_incremental.csv
    ├── notebooks/                   # delta_scd_assignment.ipynb
    ├── delta_output/                # merged_customers.csv + Delta table
    └── screenshots/                 # data_loading, data_cleaning, scd1, scd2, validation, final_output
```

## Files

- `assignment.ipynb` – Pandas exploration & cleaning (load, head, tail, shape, columns, dtypes, info, describe, missing values, filters, dedupe, total_amount, cleaned CSV)
- `delta-lake-assignment/notebooks/delta_scd_assignment.ipynb` – Delta Lake merge using DeltaTable.merge() (update existing, insert new customers)

## How to Run

1. Open `assignment.ipynb` in Jupyter Notebook or VS Code.
2. Run all cells from top to bottom.
3. Open `delta-lake-assignment/notebooks/delta_scd_assignment.ipynb`.
4. Run all cells from top to bottom.
5. Outputs are written to `cleaned_superstore.csv` and `delta-lake-assignment/delta_output/`.

