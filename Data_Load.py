import pandas as pd
import mysql.connector

# ------------------------------
# STEP 1: LOAD & CLEAN CSV FILE
# ------------------------------

df = pd.read_csv(
    "https://raw.githubusercontent.com/Mounesh1921/SecureCheck-A-Python-SQL-Digital-Ledger-for-Police-Post-Logs/refs/heads/main/traffic_stops_with_vehicle_number.csv"
)

print(df)
print(df.isnull().sum())  # Check missing values

# Remove columns with all NULL values
df.dropna(axis=1, how='all', inplace=True)

# Fill missing search_type with mode
mode_search_type = df['search_type'].mode()[0]
df['search_type'].fillna(mode_search_type, inplace=True)

print(df)

# ------------------------------
# STEP 2: MYSQL CONNECTION (FIXED)
# ------------------------------

try:
    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="7654321",
        database="SecureCheck",
        auth_plugin='mysql_native_password'   # FIX for caching_sha2_password
    )

    if connection.is_connected():
        print("Connected to MySQL successfully!")

except mysql.connector.Error as e:
    print("MySQL Connection Error:", e)
    raise SystemExit

# Use real cursor AFTER successful connection
mycursor = connection.cursor()

# ------------------------------
# STEP 3: CREATE TABLE
# ------------------------------

mycursor.execute("""
CREATE TABLE IF NOT EXISTS traffic_stops (
    stop_date DATE,
    stop_time TIME,
    country_name TEXT,
    driver_gender VARCHAR(20),
    driver_age_raw INT,
    driver_age INT,
    driver_race VARCHAR(30),
    violation_raw TEXT,
    violation TEXT,
    search_conducted VARCHAR(10),
    search_type TEXT,
    stop_outcome TEXT,
    is_arrested VARCHAR(10),
    stop_duration TEXT,
    drugs_related_stop VARCHAR(10),
    vehicle_number VARCHAR(50)
)
""")
connection.commit()
print("Table Created successfully!")

# ------------------------------
# STEP 4: INSERT DATA SAFELY
# ------------------------------

sql = """
INSERT INTO traffic_stops (
    stop_date, stop_time, country_name, driver_gender, driver_age_raw, driver_age,
    driver_race, violation_raw, violation, search_conducted, search_type, stop_outcome,
    is_arrested, stop_duration, drugs_related_stop, vehicle_number
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

for _, row in df.iterrows():

    values = (
        str(row['stop_date']) if not pd.isna(row['stop_date']) else None,
        str(row['stop_time']) if not pd.isna(row['stop_time']) else None,
        row['country_name'],
        row['driver_gender'],
        int(row['driver_age_raw']) if not pd.isna(row['driver_age_raw']) else None,
        int(row['driver_age']) if not pd.isna(row['driver_age']) else None,
        row['driver_race'],
        row['violation_raw'],
        row['violation'],
        row['search_conducted'],
        row['search_type'],
        row['stop_outcome'],
        row['is_arrested'],
        row['stop_duration'],
        row['drugs_related_stop'],
        row['vehicle_number']
    )

    mycursor.execute(sql, values)

connection.commit()
print("Data inserted successfully!")

connection.close()
