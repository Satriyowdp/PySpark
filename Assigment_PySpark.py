# -*- coding: utf-8 -*-
"""Assigment_PySpark.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Mc2wWwtY3RAHugZPVIcZ8Rsxc4U6O3Kh
"""

!apt-get install openjdk-8-jdk-headless -qq > /dev/null
!pip install pyspark

from google.colab import drive
drive.mount('/content/drive')

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pyspark.sql.functions as F
from pyspark.sql.types import FloatType
import matplotlib.pyplot as plt

# Inisialisasi SparkSession
spark = SparkSession.builder \
    .appName("Airline Customer Analysis") \
    .getOrCreate()

# Step 1: ETL Data

# Baca File CSV
calendar_df = spark.read.csv("/content/drive/MyDrive/calendar.csv", header=True)
customer_flight_activity_df = spark.read.csv("/content/drive/MyDrive/customer_flight_activity.csv", header=True)
customer_loyalty_history_df = spark.read.csv("/content/drive/MyDrive/customer_loyalty_history.csv", header=True)

# Bersihkan customer_loyalty_history_df: Hapus baris duplikat (jika ada)
customer_loyalty_history_df = customer_loyalty_history_df.dropDuplicates()

# Step 2: Analisa Dataset dengan PySpark SQL

# Membuat Tampilan Sementara
calendar_df.createOrReplaceTempView("calendar")
customer_flight_activity_df.createOrReplaceTempView("customer_flight_activity")
customer_loyalty_history_df.createOrReplaceTempView("customer_loyalty_history")

# Analisis Menggunakan SQL Query
analysis_results_df = spark.sql("""
    SELECT
        clh.Country,
        clh.Province,
        clh.City,
        clh.Gender,
        clh.Education,
        clh.Salary,
        clh.Marital_Status,
        clh.Loyalty_Card,
        cfa.Year,
        cfa.Month,
        SUM(cfa.Total_Flights) AS Total_Flights,
        SUM(cfa.Distance) AS Total_Distance,
        SUM(cfa.Points_Accumulated) AS Total_Points_Accumulated,
        SUM(cfa.Points_Redeemed) AS Total_Points_Redeemed,
        SUM(cfa.Dollar_Cost_Points_Redeemed) AS Total_Dollar_Cost_Points_Redeemed
    FROM
        customer_loyalty_history clh
    JOIN
        customer_flight_activity cfa
    ON
        clh.Loyalty_Number = cfa.Loyalty_Number
    GROUP BY
        clh.Country, clh.Province, clh.City, clh.Gender, clh.Education,
        clh.Salary, clh.Marital_Status, clh.Loyalty_Card, cfa.Year, cfa.Month
""")

# Step 3: Menyimpan Hasil Analisa ke File
analysis_results_df.write.mode("overwrite").csv("Assignment-PySpark.csv", header=True)

# # Konversikan PySpark DataFrame ke Pandas DataFrame untuk memudahkan pembuatan plot
analysis_results_pandas = analysis_results_df.toPandas()

# Plot 1: Total Flights by Loyalty Card Status
plt.figure(figsize=(10, 6))
loyalty_card_flights = analysis_results_pandas.groupby('Loyalty_Card')['Total_Flights'].sum()
loyalty_card_flights.plot(kind='bar')
plt.title('Total Flights by Loyalty Card Status')
plt.xlabel('Loyalty Card Status')
plt.ylabel('Total Flights')
plt.xticks(rotation=45)

# Adding numeric labels
for i, value in enumerate(loyalty_card_flights):
    plt.text(i, value, str(value), ha='center', va='bottom')

plt.tight_layout()

# Menyimpan Plot
plt.savefig('loyalty_card_flights_plot.png')

# Show the plot
plt.show()

# Plot 2: Total Points Accumulated by Education Level
plt.figure(figsize=(10, 6))
education_points = analysis_results_pandas.groupby('Education')['Total_Points_Accumulated'].sum()
education_points.plot(kind='bar')
plt.title('Total Points Accumulated by Education Level')
plt.xlabel('Education Level')
plt.ylabel('Total Points Accumulated')
plt.xticks(rotation=45)

# Adding numeric labels
for i, value in enumerate(education_points):
    plt.text(i, value, str(value), ha='center', va='bottom')

plt.tight_layout()

# Menyimpan Plot
plt.savefig('education_points_plot.png')

# Show the plot
plt.show()

# Plot 3: Total Distance by Gender
plt.figure(figsize=(10, 6))
gender_distance = analysis_results_pandas.groupby('Gender')['Total_Distance'].sum()
gender_distance.plot(kind='bar')
plt.title('Total Distance by Gender')
plt.xlabel('Gender')
plt.ylabel('Total Distance (km)')
plt.xticks(rotation=0)

# Adding numeric labels
for i, value in enumerate(gender_distance):
    plt.text(i, value, str(value), ha='center', va='bottom')

plt.tight_layout()

# Menyimpan Plot
plt.savefig('gender_distance_plot.png')

# Show the plot
plt.show()

# Menghentikan SparkSession
spark.stop()