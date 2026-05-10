import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="PragyanAI Engagement Intelligence",
    page_icon="🧠",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.stApp{
    background-color:#0f172a;
    color:white;
}

[data-testid="stSidebar"]{
    background-color:#111827;
}

.metric-card{
    background:#1e293b;
    padding:20px;
    border-radius:12px;
    border:1px solid #334155;
}

h1,h2,h3,h4{
    color:white !important;
}

.insight-box{
    background:#1e293b;
    padding:15px;
    border-left:5px solid #3b82f6;
    border-radius:10px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():

    df = pd.read_csv("data.csv")

    # clean column names
    df.columns = df.columns.str.strip()

    # rename columns safely
    rename_map = {}

    for col in df.columns:
        low = col.lower().strip()

        if "attendance" in low:
            rename_map[col] = "Attendance_%"

        elif "quiz" in low and "score" in low:
            rename_map[col] = "Avg_Quiz_Score"

        elif "placement" in low:
            rename_map[col] = "Placement_Status"

        elif "login" in low:
            rename_map[col] = "Login_Frequency"

        elif "time" in low and "spent" in low:
            rename_map[col] = "Time_Spent_Hours"

        elif "video" in low and "completion" in low:
            rename_map[col] = "Video_Completion_%"

        elif "doubt" in low and "raised" in low:
            rename_map[col] = "Doubts_Raised"

        elif "cgpa" in low:
            rename_map[col] = "CGPA"

        elif "department" in low:
            rename_map[col] = "Department"

        elif "college" in low:
            rename_map[col] = "College"

        elif "student" in low and "id" in low:
            rename_map[col] = "Student_ID"

    df.rename(columns=rename_map, inplace=True)

    # required columns
    required_cols = [
        "Attendance_%",
        "Avg_Quiz_Score",
        "Placement_Status",
        "Login_Frequency",
        "Time_Spent_Hours",
        "Video_Completion_%",
        "Doubts_Raised"
    ]

    # create missing columns
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0

    # numeric conversion
    numeric_cols = [
        "Attendance_%",
        "Avg_Quiz_Score",
        "Login_Frequency",
        "Time_Spent_Hours",
        "Video_Completion_%",
        "Doubts_Raised"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # =====================================================
    # CALCULATED METRICS
    # =====================================================

    def normalize(series):
        return ((series - series.min()) /
                (series.max() - series.min() + 1e-9)) * 100

    df["Engagement_Score"] = (
        normalize(df["Attendance_%"]) * 0.25 +
        normalize(df["Login_Frequency"]) * 0.20 +
        normalize(df["Time_Spent_Hours"]) * 0.20 +
        normalize(df["Video_Completion_%"]) * 0.20 +
        normalize(df["Doubts_Raised"]) * 0.15
    ).round(1)

    df["Learning_Effectiveness"] = (
        df["Avg_Quiz_Score"] *
        df["Video_Completion_%"] / 100
    ).round(1)

    df["Placement_Readiness"] = (
        df["Engagement_Score"] * 0.5 +
        df["Learning_Effectiveness"] * 0.5
    ).round(1)

    # =====================================================
    # RISK LEVEL
    # =====================================================

    def risk(row):

        if row["Attendance_%"] < 50 and row["Avg_Quiz_Score"] < 50:
            return "High Risk"

        elif row["Engagement_Score"] < 60:
            return "Medium Risk"

        else:
            return "Low Risk"

    df["Risk_Level"] = df.apply(risk, axis=1)

    return df


# =========================================================
# LOAD
# =========================================================
try:
    df = load_data()

except FileNotFoundError:
    st.error("data.csv file not found")
    st.stop()

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🧠 PragyanAI")

if "Department" in df.columns:

    departments = ["All"] + sorted(
        df["Department"].astype(str).unique().tolist()
    )

    selected_department = st.sidebar.selectbox(
        "Select Department",
        departments
    )

else:
    selected_department = "All"

# filter data
fdf = df.copy()

if selected_department != "All":
    fdf = fdf[fdf["Department"] == selected_department]

# =========================================================
# HEADER
# =========================================================
st.title("🧠 PragyanAI Engagement Intelligence")
st.markdown("""
Track student engagement, learning effectiveness,
risk levels, and placement readiness using analytics.
""")

# =========================================================
# KPIs
# =========================================================
total_students = len(fdf)

placed_students = (
    fdf["Placement_Status"]
    .astype(str)
    .str.lower()
    .eq("placed")
    .sum()
)

placement_rate = round(
    (placed_students / total_students) * 100,
    1
) if total_students > 0 else 0

avg_engagement = round(
    fdf["Engagement_Score"].mean(),
    1
)

avg_quiz = round(
    fdf["Avg_Quiz_Score"].mean(),
    1
)

high_risk = (
    fdf["Risk_Level"] == "High Risk"
).sum()

# KPI ROW
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Students", total_students)
c2.metric("Placement Rate", f"{placement_rate}%")
c3.metric("Avg Engagement", avg_engagement)
c4.metric("Avg Quiz", avg_quiz)
c5.metric("High Risk", high_risk)

st.markdown("---")

# =========================================================
# TABS
# =========================================================
tabs = st.tabs([
    "📊 Engagement",
    "📚 Learning",
    "🎯 Placement",
    "⚠️ Risk",
    "🏆 Leaderboard",
    "📁 Raw Data"
])

# =========================================================
# TAB 1
# =========================================================
with tabs[0]:

    st.subheader("Student Engagement Analysis")

    fig1 = px.histogram(
        fdf,
        x="Engagement_Score",
        nbins=20,
        color="Risk_Level",
        title="Engagement Score Distribution"
    )

    fig1.update_layout(
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    💡 Higher engagement strongly improves placement readiness.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Attendance vs Quiz Score")

    fig2 = px.scatter(
        fdf,
        x="Attendance_%",
        y="Avg_Quiz_Score",
        color="Placement_Status",
        size="Engagement_Score",
        hover_data=["Risk_Level"]
    )

    fig2.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# TAB 2
# =========================================================
with tabs[1]:

    st.subheader("Learning Effectiveness")

    fig3 = px.scatter(
        fdf,
        x="Video_Completion_%",
        y="Learning_Effectiveness",
        color="Risk_Level",
        size="Avg_Quiz_Score"
    )

    fig3.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Quiz Performance")

    fig4 = px.box(
        fdf,
        x="Placement_Status",
        y="Avg_Quiz_Score",
        color="Placement_Status"
    )

    fig4.update_layout(
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig4, use_container_width=True)

# =========================================================
# TAB 3
# =========================================================
with tabs[2]:

    st.subheader("Placement Readiness")

    fig5 = px.scatter(
        fdf,
        x="Engagement_Score",
        y="Placement_Readiness",
        color="Placement_Status",
        size="Avg_Quiz_Score",
        hover_data=["Risk_Level"]
    )

    fig5.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig5, use_container_width=True)

# =========================================================
# TAB 4
# =========================================================
with tabs[3]:

    st.subheader("Risk Analysis")

    risk_counts = fdf["Risk_Level"].value_counts()

    fig6 = px.pie(
        names=risk_counts.index,
        values=risk_counts.values,
        hole=0.5
    )

    fig6.update_layout(
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("---")

    st.subheader("🔴 High Risk Students")

    high_risk_df = fdf[
        fdf["Risk_Level"] == "High Risk"
    ].copy()

    safe_cols = [
        "Student_ID",
        "College",
        "Department",
        "CGPA",
        "Attendance_%",
        "Avg_Quiz_Score",
        "Engagement_Score",
        "Placement_Readiness",
        "Placement_Status",
    ]

    available_cols = [
        col for col in safe_cols
        if col in high_risk_df.columns
    ]

    if len(high_risk_df) > 0:

        st.dataframe(
            high_risk_df[available_cols].sort_values(
                by="Engagement_Score",
                ascending=True
            ),
            use_container_width=True,
            height=400
        )

    else:
        st.success("No high-risk students found.")

# =========================================================
# TAB 5
# =========================================================
with tabs[4]:

    st.subheader("🏆 Top Students")

    leaderboard = fdf.sort_values(
        by="Placement_Readiness",
        ascending=False
    ).head(10)

    leaderboard.index = np.arange(1, len(leaderboard) + 1)

    safe_cols = [
        "Student_ID",
        "Department",
        "CGPA",
        "Engagement_Score",
        "Learning_Effectiveness",
        "Placement_Readiness",
        "Placement_Status"
    ]

    available_cols = [
        c for c in safe_cols
        if c in leaderboard.columns
    ]

    st.dataframe(
        leaderboard[available_cols],
        use_container_width=True,
        height=450
    )

# =========================================================
# TAB 6
# =========================================================
with tabs[5]:

    st.subheader("Dataset Explorer")

    search = st.text_input("Search Student")

    temp_df = fdf.copy()

    if search:

        if "Student_ID" in temp_df.columns:

            temp_df = temp_df[
                temp_df["Student_ID"]
                .astype(str)
                .str.contains(search, case=False)
            ]

    st.dataframe(
        temp_df,
        use_container_width=True,
        height=500
    )

    st.download_button(
        "⬇ Download CSV",
        temp_df.to_csv(index=False),
        "filtered_data.csv",
        "text/csv"
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown("""
<center>

### 🧠 PragyanAI Engagement Intelligence

Predict • Analyze • Improve • Place

</center>
""", unsafe_allow_html=True)
