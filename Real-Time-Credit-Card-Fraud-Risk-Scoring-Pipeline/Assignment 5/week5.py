import os

os.environ["PYSPARK_PYTHON"] = r"C:\Python313\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Python313\python.exe"

from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("Week 5 Assignment") \
    .master("local[*]") \
    .getOrCreate()

# Sample Data

data = [
    (1, "Aditya", 22, "West", "Premium", 5000),
    (2, "Rahul", 25, "East", "Basic", 7000),
    (3, "Nisha", 28, "West", "Premium", 6000),
    (4, "Aman", 35, "North", "Premium", None),
    (5, "Priya", 22, "West", "Basic", 4500),
    (5, "Priya", 22, "West", "Basic", 4500)
]

columns = ["id", "name", "age", "region", "subscription", "salary"]

df = spark.createDataFrame(data, columns)

print("\nOriginal Data")
df.show()


# Question 3

print("\nQuestion 3 - Remove Duplicate Rows")

df1 = df.dropDuplicates()
df1.show()


# Question 4

print("\nQuestion 4 - West Region")

df1.filter(col("region") == "West").show()

print("Average Salary by Region")

df1.groupBy("region").agg(
    avg("salary").alias("Average Salary")
).show()


# Question 5

print("\nQuestion 5 - Handle Null Values")

print("Fill Null Salary with 0")

fill_df = df.na.fill({"salary": 0})
fill_df.show()

print("Drop Rows Having Null Values")

drop_df = df.na.drop()
drop_df.show()


# Question 6

print("\nQuestion 6 - Count Region Wise")

df.groupBy("region").count().show()


# Question 8

print("\nQuestion 8 - Premium Users Between Age 18 to 30")

df.filter(
    (col("age") >= 18) &
    (col("age") <= 30) &
    (col("subscription") == "Premium")
).show()


# Question 10

print("\nQuestion 10 - Rename Column")

rename_df = df.withColumnRenamed("salary", "income")
rename_df.show()

print("Schema After Renaming")
rename_df.printSchema()

print("\nCasting Age Column to Integer")

cast_df = rename_df.withColumn("age", col("age").cast("int"))

cast_df.printSchema()
cast_df.show()


# Question 12

print("\nQuestion 12 - Remove Null Email and Empty Username")

email_data = [
    ("Aditya", "aditya@gmail.com"),
    ("Rahul", None),
    ("", "abc@gmail.com"),
    ("Nisha", "nisha@gmail.com")
]

email_columns = ["username", "email"]

email_df = spark.createDataFrame(email_data, email_columns)

email_df.filter(
    col("email").isNotNull() &
    (trim(col("username")) != "")
).show()


# Question 13

print("\nQuestion 13 - Salary Statistics")

df.agg(
    min("salary").alias("Minimum Salary"),
    max("salary").alias("Maximum Salary"),
    avg("salary").alias("Average Salary")
).show()


# Question 15

print("\nQuestion 15 - Pipeline Example")

result = (
    df
    .dropDuplicates()
    .na.fill({"salary": 0})
    .groupBy("region")
    .sum("salary")
)

result.show()

spark.stop()
