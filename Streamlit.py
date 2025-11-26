import streamlit as st
import pandas as pd
import pymysql 
from datetime import datetime, date, timedelta
import plotly.express as px

# -----------------------------
# PAGE CONFIGURATION & STYLE
# -----------------------------
st.set_page_config(page_title="🚓 SecureCheck Dashboard", layout="wide")

page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #1e293b, #334155);
    color: white;
}
[data-testid="stSidebar"] {
    background: #0f172a;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)
st.title("🚓 SecureCheck Traffic Stop Dashboard")

# -----------------------------
# DATABASE FUNCTION
# -----------------------------
def get_data(query, params=None):
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="7654321",
        database="SecureCheck",
        port=3306
    )
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔎 Filters")

vehicle_options = get_data("SELECT DISTINCT vehicle_number FROM traffic_stops")['vehicle_number'].tolist()
selected_vehicles = st.sidebar.multiselect("Select Vehicle(s)", options=vehicle_options)

violation_options = get_data("SELECT DISTINCT violation FROM traffic_stops")['violation'].tolist()
selected_violations = st.sidebar.multiselect("Select Violation(s)", options=violation_options)

gender_options = ["Male", "Female", "Other"]
selected_genders = st.sidebar.multiselect("Select Gender(s)", options=gender_options)

race_options = get_data("SELECT DISTINCT driver_race FROM traffic_stops")['driver_race'].tolist()
selected_races = st.sidebar.multiselect("Select Race(s)", options=race_options)

country_options = get_data("SELECT DISTINCT country_name FROM traffic_stops")['country_name'].tolist()
selected_countries = st.sidebar.multiselect("Select Country(s)", options=country_options)

# Date range filter
# Default date range from 2020 to today
start_default = date(2020, 1, 1)
end_default = date.today()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(start_default, end_default)
)

start_date = datetime.combine(date_range[0], datetime.min.time())
end_date = datetime.combine(date_range[1], datetime.max.time())


# -----------------------------
# BUILD FILTER SQL
# -----------------------------
filters = ["stop_date BETWEEN %s AND %s"]
params = [start_date, end_date]

if selected_vehicles:
    filters.append("vehicle_number IN (%s)" % ",".join(["%s"]*len(selected_vehicles)))
    params.extend(selected_vehicles)

if selected_violations:
    filters.append("violation IN (%s)" % ",".join(["%s"]*len(selected_violations)))
    params.extend(selected_violations)

if selected_genders:
    filters.append("driver_gender IN (%s)" % ",".join(["%s"]*len(selected_genders)))
    params.extend(selected_genders)

if selected_races:
    filters.append("driver_race IN (%s)" % ",".join(["%s"]*len(selected_races)))
    params.extend(selected_races)

if selected_countries:
    filters.append("country_name IN (%s)" % ",".join(["%s"]*len(selected_countries)))
    params.extend(selected_countries)

filter_sql = "WHERE " + " AND ".join(filters)

# -----------------------------
# KPI CARDS
# -----------------------------
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)

total_logs = get_data(f"SELECT COUNT(*) AS c FROM traffic_stops {filter_sql}", params)['c'][0]
col1.metric("Total Logs", total_logs)

total_violations = get_data(f"SELECT COUNT(*) AS c FROM traffic_stops {filter_sql} AND violation IS NOT NULL AND violation != ''", params)['c'][0]
col2.metric("Total Violations", total_violations)

high_risk = get_data(f"""
SELECT COUNT(*) AS c 
FROM (
    SELECT vehicle_number 
    FROM traffic_stops
    {filter_sql}
    GROUP BY vehicle_number
    HAVING COUNT(*) >= 4
) AS t
""", params)['c'][0]
col3.metric("High-Risk Vehicles", high_risk)

st.write("---")

# -----------------------------
# TABS FOR ANALYTICS
# -----------------------------
tabs = st.tabs([
    "Vehicle Analytics", "Time & Duration", "Demographics", 
    "Violations", "Location-Based", "Advanced Analytics"
])

# -----------------------------
# TAB 1: Vehicle-Based Analytics
# -----------------------------
with tabs[0]:
    st.subheader("🚗 Vehicle-Based Analytics")
    
    # Top 10 vehicles in drug-related stops
    df_drug = get_data(f"""
    SELECT vehicle_number, COUNT(*) AS drug_stop_count
    FROM traffic_stops
    {filter_sql} AND drugs_related_stop = 1
    GROUP BY vehicle_number
    ORDER BY drug_stop_count DESC
    LIMIT 10
    """, params)
    st.write("**Top 10 Vehicles Involved in Drug-Related Stops**")
    st.dataframe(df_drug)
    st.download_button("Download CSV", convert_df_to_csv(df_drug), file_name="drug_stops.csv")
    fig_drug = px.bar(df_drug, x='vehicle_number', y='drug_stop_count', text='drug_stop_count', title="Drug-Related Stops")
    st.plotly_chart(fig_drug, use_container_width=True)

    # Most frequently searched vehicles
    df_search = get_data(f"""
    SELECT vehicle_number, COUNT(*) AS search_count
    FROM traffic_stops
    {filter_sql} AND search_conducted = 1
    GROUP BY vehicle_number
    ORDER BY search_count DESC
    LIMIT 10
    """, params)
    st.write("**Most Frequently Searched Vehicles**")
    st.dataframe(df_search)
    st.download_button("Download CSV", convert_df_to_csv(df_search), file_name="frequent_searches.csv")
    fig_search = px.bar(df_search, x='vehicle_number', y='search_count', text='search_count', title="Most Frequently Searched Vehicles")
    st.plotly_chart(fig_search, use_container_width=True)

# -----------------------------
# TAB 2: Time & Duration Analytics
# -----------------------------
with tabs[1]:
    st.subheader("🕒 Time & Duration Analytics")
    
    # Traffic stops by hour
    df_time = get_data(f"""
    SELECT HOUR(stop_time) AS hour_of_day, COUNT(*) AS stop_count
    FROM traffic_stops
    {filter_sql}
    GROUP BY hour_of_day
    ORDER BY stop_count DESC
    """, params)
    st.write("**Traffic Stops by Hour of the Day**")
    st.dataframe(df_time)
    fig_time = px.bar(df_time, x='hour_of_day', y='stop_count', text='stop_count', title="Traffic Stops by Hour")
    st.plotly_chart(fig_time, use_container_width=True)

    # Average stop duration by violation
    df_duration = get_data(f"""
    SELECT violation, ROUND(AVG(stop_duration),2) AS avg_duration
    FROM traffic_stops
    {filter_sql}
    GROUP BY violation
    ORDER BY avg_duration DESC
    """, params)
    st.write("**Average Stop Duration by Violation**")
    st.dataframe(df_duration)
    fig_duration = px.bar(df_duration, x='violation', y='avg_duration', text='avg_duration', title="Average Stop Duration")
    st.plotly_chart(fig_duration, use_container_width=True)

    # -------------------------------------------
    # NEW ANALYTIC → Are Night Stops More Likely to Lead to Arrests?
    # -------------------------------------------
    st.subheader("🌙 Night-Time vs Day-Time Arrest Rates")

    df_night_arrest = get_data(f"""
    SELECT
        CASE
            WHEN HOUR(stop_time) BETWEEN 20 AND 23 THEN 'Night (8 PM–11 PM)'
            WHEN HOUR(stop_time) BETWEEN 0 AND 5 THEN 'Night (12 AM–5 AM)'
            ELSE 'Daytime (6 AM–7 PM)'
        END AS time_period,
        COUNT(*) AS total_stops,
        SUM(is_arrested) AS total_arrests,
        ROUND(SUM(is_arrested) / COUNT(*) * 100, 2) AS arrest_rate_percent
    FROM traffic_stops
    {filter_sql}
    GROUP BY time_period
    ORDER BY arrest_rate_percent DESC;
    """, params)

    st.write("**Arrest Rate by Time of Day**")
    st.dataframe(df_night_arrest)

    # Chart
    fig_night_arrest = px.bar(
        df_night_arrest,
        x="time_period",
        y="arrest_rate_percent",
        text="arrest_rate_percent",
        title="Arrest Rate (%) by Time of Day",
    )
    st.plotly_chart(fig_night_arrest, use_container_width=True)

    # Interpretation highlight
    if not df_night_arrest.empty:
        highest = df_night_arrest.iloc[0]
        st.success(
            f"🔎 **Highest Arrest Rate:** {highest['time_period']} "
            f"({highest['arrest_rate_percent']}% arrest rate)"
        )


# -----------------------------
# TAB 3: Demographics
# -----------------------------
with tabs[2]:
    st.subheader("🧍 Demographic-Based Analytics")
    
    # Arrests by age group
    df_age = get_data(f"""
    SELECT 
        CASE
            WHEN driver_age < 18 THEN 'Under 18'
            WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
            WHEN driver_age BETWEEN 26 AND 35 THEN '26-35'
            WHEN driver_age BETWEEN 36 AND 45 THEN '36-45'
            WHEN driver_age BETWEEN 46 AND 60 THEN '46-60'
            ELSE '60+'
        END AS driver_age_group,
        COUNT(*) AS arrests
    FROM traffic_stops
    {filter_sql} AND is_arrested = 1
    GROUP BY driver_age_group
    ORDER BY arrests DESC
    LIMIT 10
    """, params)
    st.write("**Driver Age Group with Highest Arrest Rate**")
    st.dataframe(df_age)
    fig_age = px.bar(df_age, x='driver_age_group', y='arrests', text='arrests', title="Arrests by Age Group")
    st.plotly_chart(fig_age, use_container_width=True)

    # Gender distribution by country
    df_gender_country = get_data(f"""
    SELECT country_name AS country, driver_gender, COUNT(*) AS stop_count
    FROM traffic_stops
    {filter_sql}
    GROUP BY country, driver_gender
    ORDER BY stop_count DESC
    """, params)
    st.write("**Gender Distribution of Drivers Stopped by Country**")
    st.dataframe(df_gender_country)
    fig_gender_country = px.bar(df_gender_country, x='country', y='stop_count', color='driver_gender', barmode='stack', title="Gender Distribution by Country")
    st.plotly_chart(fig_gender_country, use_container_width=True)

    # -------------------------------------------
    # NEW ANALYTIC → Race and Gender Highest Search Rate
    # -------------------------------------------
    st.subheader("🔍 Race × Gender Search Rate Analysis")

    df_race_gender = get_data(f"""
    SELECT 
        driver_race,
        driver_gender,
        COUNT(*) AS total_stops,
        SUM(search_conducted) AS total_searches,
        ROUND(SUM(search_conducted) / COUNT(*) * 100, 2) AS search_rate_percent
    FROM traffic_stops
    {filter_sql}
    GROUP BY driver_race, driver_gender
    ORDER BY search_rate_percent DESC
    """, params)

    st.write("**Search Rate by Race & Gender Combination**")
    st.dataframe(df_race_gender)

    # Highlight the highest search-rate combination
    if not df_race_gender.empty:
        top = df_race_gender.iloc[0]
        st.success(
            f"👑 **Highest Search Rate:** {top['driver_race']} - {top['driver_gender']} "
            f"({top['search_rate_percent']}%)"
        )

    # Bar chart
    fig_race_gender = px.bar(
        df_race_gender,
        x="driver_race",
        y="search_rate_percent",
        color="driver_gender",
        text="search_rate_percent",
        barmode="group",
        title="Search Rate (%) by Race & Gender"
    )
    st.plotly_chart(fig_race_gender, use_container_width=True)



# -----------------------------
# TAB 4: Violation-Based Analytics
# -----------------------------
with tabs[3]:
    st.subheader("⚖️ Violation-Based Analytics")
    
    # Violations vs Searches & Arrests
    df_violation_search_arrest = get_data(f"""
    SELECT violation, 
           SUM(search_conducted) AS total_searches,
           SUM(is_arrested) AS total_arrests
    FROM traffic_stops
    {filter_sql}
    GROUP BY violation
    ORDER BY total_searches DESC, total_arrests DESC
    LIMIT 10
    """, params)
    st.write("**Violations Most Associated with Searches or Arrests**")
    st.dataframe(df_violation_search_arrest)
    fig_violation = px.bar(df_violation_search_arrest, x='violation', y=['total_searches','total_arrests'], barmode='group', title="Violations vs Searches & Arrests")
    st.plotly_chart(fig_violation, use_container_width=True)

    # -------------------------------------------
    # NEW ANALYTIC → Top Violations Among Younger Drivers (<25)
    # -------------------------------------------
    st.subheader("🧑‍🧒 Top Violations Among Younger Drivers (<25 Years)")

    df_young_violations = get_data(f"""
    SELECT 
        violation, 
        COUNT(*) AS violation_count
    FROM traffic_stops
    {filter_sql} AND driver_age < 25
    GROUP BY violation
    ORDER BY violation_count DESC
    LIMIT 10;
    """, params)

    st.write("**Most Common Violations for Drivers Under 25**")
    st.dataframe(df_young_violations)

    # Chart
    fig_young_violations = px.bar(
        df_young_violations,
        x="violation",
        y="violation_count",
        text="violation_count",
        title="Top Violations Among Younger Drivers (<25)"
    )
    st.plotly_chart(fig_young_violations, use_container_width=True)


# -----------------------------
# TAB 5: Location-Based Analytics
# -----------------------------
with tabs[4]:
    st.subheader("🌍 Location-Based Analytics")
    
    # Drug-related stops by country
    df_country_drug = get_data(f"""
    SELECT country_name AS country, COUNT(*) AS drug_stop_count
    FROM traffic_stops
    {filter_sql} AND drugs_related_stop = 1
    GROUP BY country
    ORDER BY drug_stop_count DESC
    LIMIT 10
    """, params)
    st.write("**Countries Reporting Highest Rate of Drug-Related Stops**")
    st.dataframe(df_country_drug)
    fig_country_drug = px.bar(df_country_drug, x='country', y='drug_stop_count', text='drug_stop_count', title="Drug-Related Stops by Country")
    st.plotly_chart(fig_country_drug, use_container_width=True)

    # -------------------------------------------
    # NEW ANALYTIC → Arrest Rate by Country & Violation
    # -------------------------------------------
    st.subheader("🚨 Arrest Rate by Country and Violation")

    df_country_violation_arrest = get_data(f"""
    SELECT
        country_name AS country,
        violation,
        COUNT(*) AS total_stops,
        SUM(is_arrested) AS total_arrests,
        ROUND(SUM(is_arrested)/COUNT(*)*100, 2) AS arrest_rate_percent
    FROM traffic_stops
    {filter_sql}
    GROUP BY country, violation
    ORDER BY arrest_rate_percent DESC;
    """, params)

    st.write("**Arrest Rate (%) by Country & Violation**")
    st.dataframe(df_country_violation_arrest)

    # Bar Chart
    fig_country_violation_arrest = px.bar(
        df_country_violation_arrest,
        x="country",
        y="arrest_rate_percent",
        color="violation",
        text="arrest_rate_percent",
        title="Arrest Rate (%) by Country and Violation",
        barmode="group"
    )
    st.plotly_chart(fig_country_violation_arrest, use_container_width=True)

    # -------------------------------------------
    # NEW ANALYTIC → Country with Most Search-Conducted Stops
    # -------------------------------------------
    st.subheader("🔍 Country with the Most Search-Conducted Stops")

    df_country_search = get_data(f"""
    SELECT 
        country_name AS country,
        COUNT(*) AS total_search_stops
    FROM traffic_stops
    {filter_sql} AND search_conducted = 1
    GROUP BY country
    ORDER BY total_search_stops DESC;
    """, params)

    st.write("**Total Search-Conducted Stops by Country**")
    st.dataframe(df_country_search)

    # Highlight the top country
    if not df_country_search.empty:
        top_country = df_country_search.iloc[0]
        st.success(
            f"🏆 **Highest Search-Conducted Stops:** {top_country['country']} "
            f"({top_country['total_search_stops']} searches)"
        )

    # Chart
    fig_country_search = px.bar(
        df_country_search,
        x="country",
        y="total_search_stops",
        text="total_search_stops",
        title="Search-Conducted Stops by Country"
    )
    st.plotly_chart(fig_country_search, use_container_width=True)


# -----------------------------
# TAB 6: Advanced Analytics
# -----------------------------
with tabs[5]:
    st.subheader("📊 Advanced Analytics")

    # 1️⃣ Yearly Breakdown of Stops & Arrests by Country
    st.markdown("**1️⃣ Yearly Breakdown of Stops & Arrests by Country**")
    df_yearly = get_data(f"""
    SELECT country_name AS country,
           YEAR(stop_date) AS year,
           COUNT(*) AS total_stops,
           SUM(is_arrested) AS total_arrests
    FROM traffic_stops
    {filter_sql}
    GROUP BY country, year
    ORDER BY country, year
    """, params)
    st.dataframe(df_yearly)
    fig_yearly = px.bar(df_yearly, x='year', y='total_stops', color='country', barmode='group', title="Yearly Stops by Country")
    st.plotly_chart(fig_yearly, use_container_width=True)

    # 2️⃣ Driver Violation Trends by Age & Race
    st.markdown("**2️⃣ Driver Violation Trends by Age & Race**")
    df_violation_trends = get_data(f"""
    SELECT driver_race,
           CASE
               WHEN driver_age < 18 THEN 'Under 18'
               WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
               WHEN driver_age BETWEEN 26 AND 35 THEN '26-35'
               WHEN driver_age BETWEEN 36 AND 45 THEN '36-45'
               WHEN driver_age BETWEEN 46 AND 60 THEN '46-60'
               ELSE '60+'
           END AS driver_age_group,
           violation,
           COUNT(*) AS violation_count
    FROM traffic_stops
    {filter_sql}
    GROUP BY driver_race, driver_age_group, violation
    ORDER BY violation_count DESC
    """, params)
    st.dataframe(df_violation_trends)
    fig_violation_trends = px.bar(df_violation_trends,
                                  x='driver_age_group',
                                  y='violation_count',
                                  color='driver_race',
                                  facet_col='violation',
                                  title="Driver Violation Trends by Age & Race")
    st.plotly_chart(fig_violation_trends, use_container_width=True)

    # 3️⃣ Time Period Analysis: Stops by Year, Month, Hour
    st.markdown("**3️⃣ Time Period Analysis of Stops (Year, Month, Hour)**")
    df_time_analysis = get_data(f"""
    SELECT YEAR(stop_date) AS year,
           MONTH(stop_date) AS month,
           HOUR(stop_time) AS hour,
           COUNT(*) AS stop_count
    FROM traffic_stops
    {filter_sql}
    GROUP BY year, month, hour
    ORDER BY year, month, hour
    """, params)
    st.dataframe(df_time_analysis)
    fig_time_analysis = px.line(df_time_analysis,
                                x='hour',
                                y='stop_count',
                                color='month',
                                line_group='year',
                                title="Stops by Hour for Each Month")
    st.plotly_chart(fig_time_analysis, use_container_width=True)

    # 4️⃣ Violations with High Search & Arrest Rates
    st.markdown("**4️⃣ Violations with High Search & Arrest Rates**")
    df_violation_high_rates = get_data(f"""
    SELECT violation,
           total_stops,
           total_searches,
           total_arrests,
           ROUND(total_searches/total_stops*100,2) AS search_rate,
           ROUND(total_arrests/total_stops*100,2) AS arrest_rate
    FROM (
        SELECT violation,
               COUNT(*) AS total_stops,
               SUM(search_conducted) AS total_searches,
               SUM(is_arrested) AS total_arrests
        FROM traffic_stops
        {filter_sql}
        GROUP BY violation
    ) AS t
    ORDER BY search_rate DESC, arrest_rate DESC
    LIMIT 10
    """, params)
    st.dataframe(df_violation_high_rates)
    fig_violation_high = px.bar(df_violation_high_rates,
                                x='violation',
                                y=['search_rate','arrest_rate'],
                                barmode='group',
                                title="Violations with High Search & Arrest Rates")
    st.plotly_chart(fig_violation_high, use_container_width=True)

    # 5️⃣ Driver Demographics by Country (Age, Gender, Race)
    st.markdown("**5️⃣ Driver Demographics by Country**")
    df_demographics_country = get_data(f"""
    SELECT country_name AS country,
           driver_gender,
           driver_race,
           CASE
               WHEN driver_age < 18 THEN 'Under 18'
               WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
               WHEN driver_age BETWEEN 26 AND 35 THEN '26-35'
               WHEN driver_age BETWEEN 36 AND 45 THEN '36-45'
               WHEN driver_age BETWEEN 46 AND 60 THEN '46-60'
               ELSE '60+'
           END AS driver_age_group,
           COUNT(*) AS count
    FROM traffic_stops
    {filter_sql}
    GROUP BY country, driver_gender, driver_race, driver_age_group
    ORDER BY count DESC
    """, params)
    st.dataframe(df_demographics_country)
    fig_demographics_country = px.sunburst(df_demographics_country,
                                           path=['country','driver_gender','driver_race','driver_age_group'],
                                           values='count',
                                           title="Driver Demographics by Country")
    st.plotly_chart(fig_demographics_country, use_container_width=True)

    # 6️⃣ Top 5 Violations by Arrest Rate
    st.markdown("**6️⃣ Top 5 Violations by Arrest Rate**")
    df_top_violations = get_data(f"""
    SELECT violation,
           COUNT(*) AS total_stops,
           SUM(is_arrested) AS total_arrests,
           ROUND(SUM(is_arrested)/COUNT(*)*100,2) AS arrest_rate_percent
    FROM traffic_stops
    {filter_sql}
    GROUP BY violation
    ORDER BY arrest_rate_percent DESC
    LIMIT 5
    """, params)
    st.dataframe(df_top_violations)
    fig_top_violations = px.bar(df_top_violations,
                                x='violation',
                                y='arrest_rate_percent',
                                text='arrest_rate_percent',
                                title="Top 5 Violations by Arrest Rate")
    st.plotly_chart(fig_top_violations, use_container_width=True)
