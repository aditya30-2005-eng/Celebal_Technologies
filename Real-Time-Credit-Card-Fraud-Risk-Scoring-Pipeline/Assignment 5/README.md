# Week 5 - PySpark Assignment

## Name
Aditya Kumar Singh

## Internship
Celebal Technologies Internship

## Technology Used
- Python
- PySpark
- Apache Spark
- VS Code

---

# Question 1

### What are the limitations of MapReduce and why is Spark better?

MapReduce stores intermediate data on disk after every step, so it is slower for large datasets. It is also not suitable for iterative tasks like Machine Learning because data is read and written many times.

Spark performs most operations in memory, which makes it much faster. It also supports SQL, Machine Learning, Streaming, and Graph processing in one framework.

---

# Question 2

### What is In-Memory Computing?

In-memory computing means Spark processes data in RAM instead of reading and writing to disk after every operation. This improves the speed of data processing and makes Spark much faster than MapReduce.

---

# Question 3

Removed duplicate rows using the `dropDuplicates()` function.

---

# Question 4

Filtered records where the region is **West** and calculated the average salary using the `groupBy()` and `avg()` functions.

---

# Question 5

### Difference between `na.drop()` and `na.fill()`

- `na.drop()` removes rows that contain null values.
- `na.fill()` replaces null values with a specified value instead of removing the row.

---

# Question 6

Counted the total number of records for each region using `groupBy()` and `count()`.

---

# Question 7

### What is Immutability in Spark?

Spark DataFrames are immutable, which means the original DataFrame is never modified. Every transformation creates a new DataFrame.

---

# Question 8

Filtered users whose age is between 18 and 30 and whose subscription type is **Premium**.

---

# Question 9

### Why should null values be handled before aggregation?

Null values can affect calculations like average, sum, and count. Handling them before aggregation helps produce accurate and reliable results.

---

# Question 10

Renamed the **salary** column to **income** using `withColumnRenamed()`.

---

# Question 11

### What is Shuffle in Spark?

Shuffle is the process of moving data between different partitions during operations like `groupBy()` and `join()`. It helps combine related data but can increase execution time.

---

# Question 12

Removed records where the email was null or the username was empty.

---

# Question 13

Calculated the minimum, maximum, and average salary using aggregation functions.

---

# Question 14

### Risk of using `inferSchema=True`

When data contains mixed or inconsistent formats, Spark may detect the wrong data type automatically. For important projects, defining the schema manually is a better approach.

---

# Question 15

Created a simple PySpark pipeline that:
- Removed duplicate records.
- Replaced null salary values with 0.
- Grouped the data by region.
- Calculated the total salary for each region.

---

# Conclusion

In this assignment, I learned how to create PySpark DataFrames, remove duplicate records, filter data, handle null values, perform aggregation, rename columns, and build a simple data processing pipeline using Apache Spark.

## Insights

- Spark DataFrames make data processing simple and efficient.
- Removing duplicates and handling null values improves data quality.
- Filtering helps extract only the required records.
- Aggregation functions provide useful summaries of the data.
- GroupBy allows analysis based on categories like region.
- Spark performs these operations efficiently using distributed processing.
