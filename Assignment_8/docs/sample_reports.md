# Sample Reports

The following are representative outputs of the CLI reporting tool against
the reference SQLite database.

## Revenue by Category

```bash
python scripts/report_cli.py --report revenue
```

```
Revenue by Category
========================================================================================================================
      category  order_count  item_count    revenue  avg_line_value
          Toys          781         957 3124021.12         3264.39
        Sports          740         898 2945262.12         3279.80
         Books          738         869 2786217.85         3206.23
      Clothing          764         903 2774897.20         3072.98
```

## Top Products (filtered by category)

```bash
python scripts/report_cli.py --report products --category Electronics
```

```
Top Products
========================================================================================================================
 product_id        product_name    category     brand  units_sold   revenue  revenue_rank
        169          4K Monitor Electronics  Novatech         149 119895.30             1
        231       Standing Desk Electronics  Urbanfit          82  70345.48             2
         21         Dress Shirt Electronics      Apex          74  65435.86             3
```

## Customer Retention

```bash
python scripts/report_cli.py --report retention
```

```
Customer Retention
========================================================================================================================
cohort_month  total_customers  month_offset  active_customers  retention_pct
     2022-08               28             0                28         100.00
     2022-08               28             2                 3          10.71
     2022-08               28             3                 1           3.57
```

## RFM Analysis

```bash
python scripts/report_cli.py --report rfm
```

```
RFM Analysis
========================================================================================================================
 customer_id                  name  recency_days  frequency  monetary  r_score  f_score  m_score rfm_cell  rfm_total
         210         David Jimenez            76          6  94521.09        5        5        5      555         15
         577             Mark Hill            73          6  55146.25        5        5        5      555         15
         746   Raymond Christensen            69          6  74025.69        5        5        5      555         15
```

## Monthly Revenue

```bash
python scripts/report_cli.py --report monthly
```

```
Monthly Revenue
========================================================================================================================
year month month_key  order_count   revenue
2022    08   2022-08           28 384021.64
2022    09   2022-09           45 455907.86
2022    10   2022-10           48 546316.40
```

## Exporting

```bash
python scripts/report_cli.py --report revenue --export csv
python scripts/report_cli.py --report rfm --export txt
python scripts/report_cli.py --report monthly --start-date 2023-01-01 --end-date 2023-06-30
```

Exports are written to `output/csv/` and `output/txt/` with a timestamp
suffix so that repeated runs do not overwrite earlier results.

