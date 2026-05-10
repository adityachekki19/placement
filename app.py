import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PragyanAI — Engagement Intelligence",
    page_icon="🧠",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
body {
    background-color: #0d1117;
}
.stApp {
    background: #0d1117;
    color: white;
}
.metric-box {
    background: #161b22;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #30363d;
}
.insight-box {
    background: #111827;
    border-left: 5px solid #3b82f6;
    padding: 14px;
    border-radius: 10px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────────────────────────
PLOT_BG = "#0d1117"
GRID = "#30363d"
FONT = "#ffffff"

# ─────────────────────────────────────────────────────────────
# PLOT LAYOUT
# ─────────────────────────────────────────────────────────────
def layout(title="", height=400):
    return dict(
        title=title,
        height=height,
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT),
        xaxis=dict(gridcolor=GRID),
        yaxis=dict(gridcolor=GRID),
    )

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():

    df = pd.read_csv("data.csv")

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("%", "Percent")
        .str.replace(r"[^A-Za-z0-9_]", "", regex=True)
    )

    # Rename automatically
    rename_map = {}

    for col in df.columns:

        c = col.lower()

        if "attendance" in c:
            rename_map[col] = "Attendance_%"

        elif "login" in c:
            rename_map[col] = "Login_Frequency"

        elif "time" in c and ("spent" in c or "hour" in c):
            rename_map[col] = "Time_Spent_Hours"

        elif "video" in c and ("completion" in c or "complete" in c):
            rename_map[col] = "Video_Completion_%"

        elif "quiz" in c and ("score" in c or "avg" in c):
            rename_map[col] = "Avg_Quiz_Score"

        elif "doubt" in c and "raised" in c:
            rename_map[col] = "Doubts_Raised"

        elif "placement" in c:
            rename_map[col] = "Placement_Status"

        elif "department" in c or "dept" in c:
            rename_map[col] = "Department"

        elif "cgpa" in c or "gpa" in c:
            rename_map[col] = "CGPA"

        elif "gender" in c:
            rename_map[col] = "Gender"

        elif "student" in c and "id" in c:
            rename_map[col] = "Student_ID"

    df.rename(columns=rename_map, inplace=True)

    # Required columns
    required = {
        "Attendance_%": 0,
        "Login_Frequency": 0,
        "Time_Spent_Hours": 0,
        "Video_Completion_%": 0,
        "Avg_Quiz_Score": 0,
        "Doubts_Raised": 0,
        "Placement_Status": "Not Placed",
        "Department": "Unknown",
        "CGPA": 0,
        "Gender": "Unknown",
    }

    for col, default in required.items():
        if col not in df.columns:
            df[col] = default

    # Convert numeric
    numeric_cols = [
        "Attendance_%",
        "Login_Frequency",
        "Time_Spent_Hours",
        "Video_Completion_%",
        "Avg_Quiz_Score",
        "Doubts_Raised",
        "CGPA",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Optional columns
    optional_cols = [
        "Peer_Discussion_Count",
        "Hackathons_Attended",
        "Workshops_Attended",
        "Live_Sessions_Joined",
    ]

    for col in optional_cols:
        if col not in df.columns:
            df[col] = 0

    # Normalize
    def normalize(x):
        return ((x - x.min()) / (x.max() - x.min() + 1e-9)) * 100

    # Scores
    df["Engagement_Score"] = (
        normalize(df["Attendance_%"]) * 0.20 +
        normalize(df["Login_Frequency"]) * 0.15 +
        normalize(df["Time_Spent_Hours"]) * 0.15 +
        normalize(df["Video_Completion_%"]) * 0.20 +
        normalize(df["Avg_Quiz_Score"]) * 0.20 +
        normalize(df["Doubts_Raised"]) * 0.10
    ).round(1)

    df["Learning_Effectiveness"] = (
        (df["Avg_Quiz_Score"] / 100) *
        (df["Video_Completion_%"] / 100) * 100
    ).round(1)

    df["Placement_Readiness"] = (
        df["Engagement_Score"] * 0.5 +
        df["Learning_Effectiveness"] * 0.5
    ).round(1)

    # Segments
    def segment(row):
        if row["Engagement_Score"] >= 75:
            return "High Performer 🏆"
        elif row["Engagement_Score"] >= 50:
            return "Average Learner 📘"
        else:
            return "Disengaged ⚠️"

    df["Segment"] = df.apply(segment, axis=1)

    # Risk
    def risk(row):
        if row["Attendance_%"] < 60 and row["Avg_Quiz_Score"] < 50:
            return "High Risk"
        elif row["Engagement_Score"] < 50:
            return "Medium Risk"
        else:
            return "Low Risk"

    df["Risk_Level"] = df.apply(risk, axis=1)

    return df

# ─────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────
try:
    df = load_data()

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
st.sidebar.title("🧠 PragyanAI")

departments = ["All"] + sorted(df["Department"].astype(str).unique())

selected_dept = st.sidebar.selectbox(
    "Department",
    departments
)

if selected_dept != "All":
    df = df[df["Department"] == selected_dept]

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.title("🧠 PragyanAI Engagement Intelligence Dashboard")

st.markdown("""
<div class="insight-box">
Tracks student engagement, learning effectiveness,
placement readiness and risk analysis.
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# KPI SECTION
# ─────────────────────────────────────────────────────────────
total_students = len(df)

placed = (
    df["Placement_Status"]
    .astype(str)
    .str.lower()
    .eq("placed")
    .sum()
)

placement_rate = round((placed / total_students) * 100, 1)

avg_engagement = round(df["Engagement_Score"].mean(), 1)

avg_quiz = round(df["Avg_Quiz_Score"].mean(), 1)

high_risk = (df["Risk_Level"] == "High Risk").sum()

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Students", total_students)
c2.metric("Placed", placed)
c3.metric("Placement %", f"{placement_rate}%")
c4.metric("Avg Engagement", avg_engagement)
c5.metric("High Risk", high_risk)

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Engagement",
    "📚 Learning",
    "⚠️ Risk",
    "🏅 Leaderboard",
    "📈 Analytics"
])

# ─────────────────────────────────────────────────────────────
# TAB 1
# ─────────────────────────────────────────────────────────────
with tabs[0]:

    st.subheader("Attendance vs Engagement")

    fig1 = px.scatter(
        df,
        x="Attendance_%",
        y="Engagement_Score",
        color="Placement_Status",
        size="Avg_Quiz_Score",
        hover_data=["Department", "CGPA"],
    )

    fig1.update_layout(**layout(height=450))

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Engagement Distribution")

    fig2 = px.histogram(
        df,
        x="Engagement_Score",
        nbins=20,
        color="Placement_Status"
    )

    fig2.update_layout(**layout(height=400))

    st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 2
# ─────────────────────────────────────────────────────────────
with tabs[1]:

    st.subheader("Video Completion vs Quiz Score")

    fig3 = px.scatter(
        df,
        x="Video_Completion_%",
        y="Avg_Quiz_Score",
        color="Segment",
        size="Engagement_Score",
        hover_data=["Department"]
    )

    fig3.update_layout(**layout(height=450))

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Learning Effectiveness")

    fig4 = px.box(
        df,
        x="Placement_Status",
        y="Learning_Effectiveness",
        color="Placement_Status"
    )

    fig4.update_layout(**layout(height=400))

    st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 3
# ─────────────────────────────────────────────────────────────
with tabs[2]:

    st.subheader("Risk Level Distribution")

    risk_counts = df["Risk_Level"].value_counts()

    fig5 = px.pie(
        names=risk_counts.index,
        values=risk_counts.values,
        hole=0.5
    )

    fig5.update_layout(**layout(height=450))

    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("High Risk Students")

    high_risk_df = df[df["Risk_Level"] == "High Risk"]

    st.dataframe(
        high_risk_df[
            [
                "Student_ID",
                "Department",
                "Attendance_%",
                "Avg_Quiz_Score",
                "Engagement_Score"
            ]
        ],
        use_container_width=True
    )

# ─────────────────────────────────────────────────────────────
# TAB 4
# ─────────────────────────────────────────────────────────────
with tabs[3]:

    st.subheader("Top Students")

    top_students = df.sort_values(
        "Placement_Readiness",
        ascending=False
    ).head(10)

    st.dataframe(
        top_students[
            [
                "Student_ID",
                "Department",
                "CGPA",
                "Engagement_Score",
                "Placement_Readiness",
                "Segment"
            ]
        ],
        use_container_width=True
    )

    fig6 = px.bar(
        top_students,
        x="Student_ID",
        y="Placement_Readiness",
        color="Segment"
    )

    fig6.update_layout(**layout(height=450))

    st.plotly_chart(fig6, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 5
# ─────────────────────────────────────────────────────────────
with tabs[4]:

    st.subheader("Correlation Matrix")

    corr_cols = [
        "Attendance_%",
        "Login_Frequency",
        "Time_Spent_Hours",
        "Video_Completion_%",
        "Avg_Quiz_Score",
        "Engagement_Score",
        "Learning_Effectiveness",
        "Placement_Readiness",
    ]

    corr = df[corr_cols].corr()

    fig7 = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues"
    )

    fig7.update_layout(**layout(height=600))

    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Raw Dataset")

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        data=df.to_csv(index=False),
        file_name="filtered_data.csv",
        mime="text/csv"
    )

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")

st.markdown("""
<center>
<h4>🧠 PragyanAI Engagement Intelligence</h4>
<p>
Tracks engagement → Predicts placement → Detects risk
</p>
</center>
""", unsafe_allow_html=True)
