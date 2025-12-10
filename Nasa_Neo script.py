import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------
# 1. Streamlit basic setup
# ----------------------------
st.set_page_config(
    page_title="NASA NEO Tracker",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# 2. Modern Custom CSS
# ----------------------------
st.markdown(
    """
<style>

/* ================= GLOBAL ================= */
.main {
    background: radial-gradient(circle at top left, #0f172a 0, #020617 45%, #000000 100%);
    color: #e5e7eb;
    font-family: "Inter", system-ui, sans-serif;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}

/* ================= SIDEBAR ================= */
section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.94);
    border-right: 1px solid rgba(148, 163, 184, 0.25);
    backdrop-filter: blur(18px);
}
.sidebar-header { padding-bottom: 0.5rem; }
.sidebar-title {
    font-weight: 700; font-size: 1.1rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.sidebar-subtitle {
    font-size: .78rem; opacity: .75;
    margin-bottom: .8rem;
}

/* ================= SIDEBAR BUTTONS ================= */
/* Default button */
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 999px;
    padding: .45rem .8rem;
    font-size: .84rem; font-weight: 500;
    text-align: left;

    background: linear-gradient(135deg, #111827, #0f172a);
    border: 1px solid rgba(148,163,184,0.55);
    color: #f1f5f9;

    box-shadow: 0 8px 15px rgba(0,0,0,0.4);
    transition: all .18s ease-in-out;
}

/* Hover = Cyan highlight */
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-color: #38bdf8;
    box-shadow: 0 0 0 2px rgba(56,189,248,.6);
    transform: translateY(-2px);
}

/* Active (clicked) = Orange highlight */
section[data-testid="stSidebar"] .stButton > button:active,
section[data-testid="stSidebar"] .stButton > button:focus-visible {
    background: linear-gradient(135deg, #fb923c, #f97316);
    border-color: #fdba74;
    color: #0f172a !important;
    box-shadow: 0 0 0 2px rgba(251,146,60,.75);
    transform: translateY(0px);
}

/* ================= MAIN BUTTONS ================= */
.block-container .stButton > button {
    border-radius: 999px;
    padding: .45rem 1.1rem;

    background: linear-gradient(135deg, #1f2937, #0f172a);
    border: 1px solid rgba(148,163,184,0.55);
    color: #f8fafc;

    transition: all .18s ease-in-out;
}

/* Hover = Purple glow */
.block-container .stButton > button:hover {
    background: linear-gradient(135deg, #312e81, #1e1b4b);
    border-color: #a855f7;
    box-shadow: 0 0 0 2px rgba(168,85,247,.6);
    transform: translateY(-2px);
}

/* Active = Teal highlight */
.block-container .stButton > button:active,
.block-container .stButton > button:focus-visible {
    background: linear-gradient(135deg, #14b8a6, #0d9488);
    color: #022c22 !important;
    border-color: #5eead4;
    box-shadow: 0 0 0 2px rgba(45,212,191,.7);
    transform: translateY(0px);
}

/* ================= HERO CARD ================= */
.hero-card {
    border-radius: 1.75rem;
    padding: 1.6rem 2.1rem;
    margin-top: .5rem;
    color: #f8fafc;

    background: radial-gradient(circle at top left, #0ea5e9 0, #1d4ed8 40%, #020617 100%);
    box-shadow: 0 25px 45px rgba(0,0,0,0.6);
}

/* ================= METRIC CARDS ================= */
.metric-card {
    border-radius: 1.35rem;
    padding: 1.2rem 1.3rem;

    background: radial-gradient(circle at top left, #0f172a 0, #1e293b 55%, #0f172a 100%);
    border: 1px solid rgba(148,163,184,0.35);

    transition: 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    border-color: #60a5fa;
    box-shadow: 0 18px 45px rgba(0,0,0,0.55);
}

</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------
# 3. Header (hero card)
# ----------------------------
st.markdown(
    """
    <div class="hero-card">
      <div class="hero-inner">
        <div class="hero-pill">🪐 2024 Near-Earth Objects · SQL-powered analytics</div>
        <div class="hero-title">NASA NEO Tracking & Insights Dashboard</div>
        <div class="hero-subtitle">
          Advanced monitoring of near-Earth objects with query-driven views on approach counts,
          relative velocities, miss distances, and hazard potential.
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# 4. DB helpers
# ----------------------------
def get_connection():
    """
    Create and return a new MySQL/TiDB connection using Streamlit secrets.
    """
    return mysql.connector.connect(
        host=st.secrets["host"],
        user=st.secrets["user"],
        password=st.secrets["password"],
        database=st.secrets["name"],
        port=st.secrets.get("port", 4000),
    )


def run_query(sql, params=None):
    """
    Run a SELECT query and return a pandas DataFrame.
    The connection is opened and closed inside this function.
    """
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql(sql, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Database query failed: {e}")
        return pd.DataFrame()
    finally:
        if conn is not None:
            conn.close()

# ----------------------------
# 5. Top metrics (overview)
# ----------------------------
try:
    total_asteroids_df = run_query(
        "SELECT COUNT(DISTINCT id) AS count FROM asteroids"
    )
    total_approaches_df = run_query(
        "SELECT COUNT(*) AS count FROM close_approach"
    )
    hazardous_count_df = run_query(
        "SELECT COUNT(*) AS count FROM asteroids WHERE is_potentially_hazardous_asteroid = 1"
    )

    total_asteroids = (
        int(total_asteroids_df.iloc[0]["count"])
        if not total_asteroids_df.empty
        else 0
    )
    total_approaches = (
        int(total_approaches_df.iloc[0]["count"])
        if not total_approaches_df.empty
        else 0
    )
    hazardous_count = (
        int(hazardous_count_df.iloc[0]["count"])
        if not hazardous_count_df.empty
        else 0
    )

except Exception as e:
    st.error(f"⚠️ Database connection failed: {e}")
    st.info("🔧 Please check your MySQL connection settings in st.secrets.")
    total_asteroids = total_approaches = hazardous_count = 0

hazard_percentage = (
    (hazardous_count / total_asteroids * 100) if total_asteroids > 0 else 0
)

# Modern metric cards
st.markdown(
    f"""
    <div class="metric-row">
      <div class="metric-card">
        <div class="metric-label">Total Objects Tracked</div>
        <div class="metric-value">🪐 {total_asteroids:,}</div>
        <div class="metric-tag">Unique asteroids observed in 2024</div>
      </div>

      <div class="metric-card">
        <div class="metric-label">Close Approaches Recorded</div>
        <div class="metric-value">🚀 {total_approaches:,}</div>
        <div class="metric-tag">Earth-approaching events in dataset</div>
      </div>

      <div class="metric-card">
        <div class="metric-label">Potentially Hazardous</div>
        <div class="metric-value">⚠️ {hazardous_count:,}</div>
        <div class="metric-tag">Objects flagged as PHAs</div>
      </div>

      <div class="metric-card">
        <div class="metric-label">Hazard Rate</div>
        <div class="metric-value">📊 {hazard_percentage:.1f}%</div>
        <div class="metric-tag">Share of tracked objects exceeding risk threshold</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# 6. Helper to run + show queries
# ----------------------------
def show_query(sql, show_chart=True):
    """
    Run the given SQL string, show results as a table,
    and optionally show a chart based on the data.
    """
    try:
        df = run_query(sql)

        if df.empty:
            st.warning("No data returned for this query.")
            return df

        st.dataframe(df, use_container_width=True, height=400)

        if show_chart and len(df) > 0:
            if (
                len(df.columns) == 2
                and df.columns[1] in ["count", "approach_count", "total"]
            ):
                fig = px.bar(
                    df.head(10),
                    x=df.columns[0],
                    y=df.columns[1],
                    title=f"Top 10 - {df.columns[1].replace('_', ' ').title()}",
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            elif len(df.columns) > 1 and "velocity" in df.columns[1].lower():
                fig = px.histogram(
                    df,
                    x=df.columns[1],
                    title=f"Distribution of {df.columns[1].replace('_', ' ').title()}",
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

        return df

    except Exception as e:
        st.error(f"❌ Query execution failed: {e}")
        return pd.DataFrame()

# ----------------------------
# 7. Query definitions
# ----------------------------
queries = {
    "1. Count asteroid approaches": """
        SELECT neo_reference_id, COUNT(*) AS approach_count
        FROM close_approach
        GROUP BY neo_reference_id
        ORDER BY approach_count DESC
    """,
    "2. Average velocity per asteroid": """
        SELECT neo_reference_id, AVG(relative_velocity_km_per_hour) AS avg_velocity
        FROM close_approach
        GROUP BY neo_reference_id
        ORDER BY avg_velocity DESC
    """,
    "3. Top 10 fastest asteroids": """
        SELECT neo_reference_id, MAX(relative_velocity_km_per_hour) AS max_velocity
        FROM close_approach
        GROUP BY neo_reference_id
        ORDER BY max_velocity DESC
        LIMIT 10
    """,
    "4. Hazardous asteroids > 3 approaches": """
        SELECT ca.neo_reference_id, COUNT(*) AS approach_count
        FROM close_approach ca
        JOIN asteroids a ON ca.neo_reference_id = a.id
        WHERE a.is_potentially_hazardous_asteroid = 1
        GROUP BY ca.neo_reference_id
        HAVING COUNT(*) > 3
    """,
    "5. Month with most approaches": """
        SELECT DATE_FORMAT(close_approach_date, '%Y-%m') AS month, COUNT(*) AS count
        FROM close_approach
        GROUP BY month
        ORDER BY count DESC
        LIMIT 1
    """,
    "6. Fastest ever approach": """
        SELECT neo_reference_id, MAX(relative_velocity_km_per_hour) AS fastest_speed
        FROM close_approach
        GROUP BY neo_reference_id
        ORDER BY fastest_speed DESC
        LIMIT 1
    """,
    "7. Sort by max estimated diameter": """
        SELECT id, name, estimated_diameter_max_km
        FROM asteroids
        ORDER BY estimated_diameter_max_km DESC
    """,
    "8. Closest approach getting nearer over time": """
        SELECT *
        FROM close_approach
        ORDER BY neo_reference_id, close_approach_date
    """,
    "9. Closest approach date & distance": """
        SELECT a.name,
               ca.close_approach_date,
               MIN(ca.miss_distance_km) AS closest_approach
        FROM close_approach ca
        JOIN asteroids a ON ca.neo_reference_id = a.id
        GROUP BY a.id, a.name, ca.close_approach_date
        ORDER BY closest_approach ASC
    """,
    "10. Velocity > 50,000 km/h": """
        SELECT DISTINCT a.name, ca.relative_velocity_km_per_hour
        FROM close_approach ca
        JOIN asteroids a ON ca.neo_reference_id = a.id
        WHERE ca.relative_velocity_km_per_hour > 50000
    """,
    "11. Approaches per month": """
        SELECT DATE_FORMAT(close_approach_date, '%Y-%m') AS month, COUNT(*) AS total
        FROM close_approach
        GROUP BY month
        ORDER BY total DESC
    """,
    "12. Brightest asteroid (lowest magnitude)": """
        SELECT id, name, absolute_magnitude_h
        FROM asteroids
        ORDER BY absolute_magnitude_h ASC
        LIMIT 1
    """,
    "13. Hazardous vs Non-hazardous count": """
        SELECT is_potentially_hazardous_asteroid, COUNT(*) AS count
        FROM asteroids
        GROUP BY is_potentially_hazardous_asteroid
    """,
    "14. Asteroids < 1 LD": """
        SELECT a.name,
               ca.close_approach_date,
               ca.miss_distance_lunar
        FROM close_approach ca
        JOIN asteroids a ON ca.neo_reference_id = a.id
        WHERE ca.miss_distance_lunar < 1
        ORDER BY ca.miss_distance_lunar
    """,
    "15. Asteroids < 0.05 AU": """
        SELECT a.name,
               ca.close_approach_date,
               ca.astronomical
        FROM close_approach ca
        JOIN asteroids a ON ca.neo_reference_id = a.id
        WHERE ca.astronomical < 0.05
        ORDER BY ca.astronomical
    """,
    "Bonus 1: Orbiting bodies (non-Earth)": """
        SELECT orbiting_body, COUNT(*) AS count
        FROM close_approach
        WHERE orbiting_body != 'Earth'
        GROUP BY orbiting_body
        ORDER BY count DESC
    """,
    "Bonus 2: Avg miss distance by hazard type": """
        SELECT a.is_potentially_hazardous_asteroid,
               AVG(ca.miss_distance_km) AS avg_miss_distance
        FROM close_approach ca
        JOIN asteroids a ON ca.neo_reference_id = a.id
        GROUP BY a.is_potentially_hazardous_asteroid
    """,
    "Bonus 3: Top 5 closest approaches": """
        SELECT a.name,
               ca.close_approach_date,
               ca.miss_distance_km
        FROM close_approach ca
        JOIN asteroids a ON ca.neo_reference_id = a.id
        ORDER BY ca.miss_distance_km ASC
        LIMIT 5
    """,
    "Bonus 4: Count of hazardous asteroids": """
        SELECT COUNT(DISTINCT id) AS hazardous_asteroid_count
        FROM asteroids
        WHERE is_potentially_hazardous_asteroid = 1
    """,
    "Bonus 5: Frequent <1 LD asteroids": """
        SELECT ca.neo_reference_id,
               a.name,
               COUNT(*) AS close_pass_count
        FROM close_approach ca
        JOIN asteroids a ON ca.neo_reference_id = a.id
        WHERE ca.miss_distance_lunar < 1
        GROUP BY ca.neo_reference_id, a.name
        HAVING COUNT(*) > 1
        ORDER BY close_pass_count DESC
    """,
}

# ----------------------------
# 8. Sidebar – query selection (modern text, same logic)
# ----------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-title">🛰 Query Selection</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-subtitle">Choose from our comprehensive set of asteroid analysis queries.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

query_categories = {
    "📈 Statistical Analysis": [
        "1. Count asteroid approaches",
        "2. Average velocity per asteroid",
        "3. Top 10 fastest asteroids",
        "11. Approaches per month",
    ],
    "⚠️ Hazard Assessment": [
        "4. Hazardous asteroids > 3 approaches",
        "13. Hazardous vs Non-hazardous count",
        "Bonus 4: Count of hazardous asteroids",
        "Bonus 2: Avg miss distance by hazard type",
    ],
    "🏃‍♂️ Speed & Motion": [
        "6. Fastest ever approach",
        "10. Velocity > 50,000 km/h",
    ],
    "📏 Distance & Size": [
        "7. Sort by max estimated diameter",
        "9. Closest approach date & distance",
        "14. Asteroids < 1 LD",
        "15. Asteroids < 0.05 AU",
        "Bonus 3: Top 5 closest approaches",
    ],
    "📅 Temporal Analysis": [
        "5. Month with most approaches",
        "8. Closest approach getting nearer over time",
    ],
    "🌟 Special Queries": [
        "12. Brightest asteroid (lowest magnitude)",
        "Bonus 1: Orbiting bodies (non-Earth)",
        "Bonus 5: Frequent <1 LD asteroids",
    ],
}

selected_query = None
for category, queries_list in query_categories.items():
    with st.sidebar.expander(category):
        for query_label in queries_list:
            if st.button(query_label, key=f"btn_{query_label}"):
                selected_query = query_label

if selected_query is None:
    selected_query = "1. Count asteroid approaches"

# ----------------------------
# 9. Show selected query (section style)
# ----------------------------
st.markdown(
    f"""
    <div class="section-heading">
      <span class="icon">🔍</span>
      <span>{selected_query}</span>
    </div>
    <div class="section-heading-sub">
      Results and visualizations for the selected NEO query.
    </div>
    """,
    unsafe_allow_html=True,
)

show_query(queries[selected_query])

# ----------------------------
# 10. Advanced Filters (modern section heading)
# ----------------------------
st.markdown(
    """
    <div class="section-heading">
      <span class="icon">🎛️</span>
      <span>Advanced Asteroid Approach Filters</span>
    </div>
    <div class="section-heading-sub">
      Customize your search parameters to find specific asteroid approaches.
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Date & Time Filters")
    selected_date = st.date_input("Select Close Approach Date (after)", datetime(2024, 1, 1))
    st.info("📊 Data Range: January 1, 2024 - December 31, 2024")

    st.subheader("🚀 Velocity Filters")
    min_velocity = st.slider("Minimum Relative Velocity (km/h)", 0.0, 100000.0, 0.0, 1000.0)
    max_velocity = st.slider("Maximum Relative Velocity (km/h)", 0.0, 100000.0, 50000.0, 1000.0)

    st.subheader("📏 Size Filters")
    min_diameter = st.slider("Minimum Estimated Diameter (km)", 0.0, 50.0, 0.0, 0.1)
    max_diameter = st.slider("Maximum Estimated Diameter (km)", 0.0, 50.0, 5.0, 0.1)

with col2:
    st.subheader("🌍 Distance Filters (Astronomical Units)")
    min_au = st.slider("Minimum AU", 0.0, 1.0, 0.0, 0.01)
    max_au = st.slider("Maximum AU", 0.0, 1.0, 0.05, 0.01)

    st.subheader("🌙 Distance Filters (Lunar Distance)")
    min_ld = st.slider("Minimum LD", 0.0, 100.0, 0.0, 1.0)
    max_ld = st.slider("Maximum LD", 0.0, 100.0, 10.0, 1.0)

    st.subheader("⚠️ Hazard Classification")
    hazardous = st.selectbox("Potentially Hazardous?", ["Both", "Yes", "No"])

filter_query = f"""
SELECT a.name,
       ca.close_approach_date,
       ca.relative_velocity_km_per_hour,
       ca.miss_distance_km,
       ca.miss_distance_lunar,
       a.estimated_diameter_min_km,
       a.estimated_diameter_max_km,
       a.is_potentially_hazardous_asteroid
FROM close_approach ca
JOIN asteroids a ON ca.neo_reference_id = a.id
WHERE DATE(ca.close_approach_date) >= DATE('{selected_date}')
  AND ca.astronomical BETWEEN {min_au} AND {max_au}
  AND ca.miss_distance_lunar BETWEEN {min_ld} AND {max_ld}
  AND ca.relative_velocity_km_per_hour BETWEEN {min_velocity} AND {max_velocity}
  AND a.estimated_diameter_max_km BETWEEN {min_diameter} AND {max_diameter}
"""

if hazardous == "Yes":
    filter_query += " AND a.is_potentially_hazardous_asteroid = 1"
elif hazardous == "No":
    filter_query += " AND a.is_potentially_hazardous_asteroid = 0"

st.markdown("#### 🎯 Filtered Results")
filtered_df = show_query(filter_query, show_chart=False)

if not filtered_df.empty:
    st.success(f"✅ Found {len(filtered_df)} asteroids matching your criteria")
else:
    st.warning("🔍 No asteroids found matching your criteria. Try adjusting the filters.")

# ----------------------------
# 11. Colab launch instructions
# ----------------------------
st.markdown(
    """
    ---
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 10px; color: white; margin-top: 2rem;">
        <h2>🚀 Launch Instructions for Google Colab</h2>
        <p>Follow these steps to run this dashboard in Google Colab:</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.code(
    """
# Step 1: Get your external IP (this will be your password)
!wget -q -O - ipv4.icanhazip.com

# Step 2: Install required packages (if not already installed)
!pip install streamlit plotly mysql-connector-python

# Step 3: Launch the app
!streamlit run "Nasa_Neo script.py" & npx localtunnel --port 8501
""",
    language="bash",
)

st.markdown(
    """
**📋 Then follow these steps:**
1. ✅ Enter `y` when prompted to proceed  
2. 🔗 Copy the generated link (e.g., `https://fruity-aliens-unite.loca.lt/`)  
3. 🌐 Paste it in your browser  
4. 🔑 Enter the IP address from Step 1 as the password  
5. 🎉 You'll be redirected to your enhanced Streamlit app!

**💡 Pro Tips:**
- Ensure your database is reachable from Colab and credentials are in `st.secrets`  
- The dashboard works best with a stable internet connection  
- Use the interactive filters to explore different aspects of asteroid data  
"""
)
