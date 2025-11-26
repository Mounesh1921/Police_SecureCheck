🚓 SecureCheck: A Python–SQL Digital Ledger for Police Traffic Stop Logs

SecureCheck is an end-to-end data engineering and analytics project designed to streamline the process of managing, storing, and analyzing police traffic stop records.
This system automates data ingestion from CSV files, cleans and structures the dataset, stores it securely in a MySQL database, and presents interactive analytics using a Streamlit dashboard.

📌 Project Overview

Police departments often maintain large volumes of traffic stop logs, which include details such as vehicle number, driver demographics, violations, search outcomes, and arrest status.
Manual processing of such datasets is time-consuming, error-prone, and limits data-driven decision-making.

SecureCheck solves this problem by:

Automating data loading and preprocessing using Python

Creating a structured SQL database for long-term storage

Building a visually rich dashboard for real-time traffic analytics

Supporting search, filtering, reporting, and vehicle-risk analysis

Enabling officers and administrators to monitor trends and patterns

🏗️ Project Architecture

The project is structured into the following major components:

1. Data Loading & Cleaning (Python – Pandas)

The script Data_Load.py performs:

Reading the traffic stop dataset from GitHub

Removing columns consisting entirely of null values

Handling missing values (e.g., filling missing search_type with mode)

Ensuring correct data types before insertion

Establishing a MySQL connection using the appropriate authentication plugin

Creating the traffic_stops table

Safely inserting all records into the database

This step ensures the dataset is clean, standardized, and ready for analysis.

2. Database Design (MySQL)

A table named traffic_stops is created to store 16 key attributes:

Stop date & time

Country information

Driver gender, age, race

Violation types

Search conducted & search type

Arrest status

Stop duration

Drug-related flags

Vehicle number

The design uses a mix of TEXT, VARCHAR, INT, and DATE/TIME data types, optimized for analytic queries.

3. SecureCheck Dashboard (Streamlit + SQL + Plotly)

The Streamlit.py file implements a complete dashboard with:

🔎 Sidebar Filters

Vehicle number

Violation type

Gender

Driver race

Country

Date range

All filters dynamically update the metrics and charts.

📊 KPI Metrics

Total traffic logs

Total violations recorded

High-risk vehicles (≥4 stops)

📁 Data Download Options

All analytical tables can be exported as CSV.

📈 Dashboard Analytics Modules

The dashboard includes six analytical sections:

1️⃣ Vehicle-Based Analytics

Top 10 vehicles in drug-related stops

Most frequently searched vehicles

2️⃣ Time & Duration Analysis

Traffic stops by hour of day

Average stop duration by violation

3️⃣ Demographic Analysis

Arrests by age groups

Gender distribution by country

4️⃣ Violation Analysis

Violations associated with highest searches/arrests

5️⃣ Location-Based Insights

Drug-related stop trends by country

6️⃣ Advanced Analytics

Yearly breakdown of stops and arrests

Violation trends by driver age & race

Time period analysis (year, month, hour)

High-search & high-arrest violation types

Demographics grouped by country

🧰 Technologies Used
Component	Technology
Backend Data Processing	Python, Pandas
Database	MySQL, SQL
Dashboard	Streamlit
Visualization	Plotly Express
Data Source	CSV from GitHub
📦 How It Works

Load dataset → Clean → Insert into SQL using Data_Load.py

Dashboard fetches data with optimized SQL queries

User applies filters from sidebar

Dashboard updates charts + metrics live

CSV downloads available for reporting

🎯 Key Features

✔️ Automated Data Cleaning
✔️ MySQL Table Creation + Data Insertion
✔️ Real-Time Dashboard Analytics
✔️ Search & Filter Functionality
✔️ High-Risk Vehicle Detection
✔️ Country, Gender, Race & Violation Analysis
✔️ Exportable CSV Reports
✔️ User-friendly UI with gradient themes
