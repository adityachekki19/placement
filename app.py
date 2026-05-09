import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Student Engagement Intelligence System",
    layout="wide"
)

st.title("🎓 Student Engagement Intelligence System")
st.markdown("### LMS + Behavior → Learning → Placement")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/pragyanaischool/VTU_Internship_DataSets/refs/heads/main/student_data_engament_Project_8.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("%", "Percent")
        .str.replace("-", "_")
    )

    return df

df = load_data()

# ---------------------------------------------------
# SHOW DATASET COLUMNS
# ---------------------------------------------------
with st.expander("📌 Dataset Columns"):
    st.write(df.columns.tolist())

# ---------------------------------------------------
# REQUIRED COLUMN MAPPING
# ---------------------------------------------------
# Safe handling if columns differ

column_map = {}

for col in df.columns:

    lower = col.lower()

    if "attendance" in lower:
        column_map["attendance"] = col

    elif "quiz" in lower and "score" in lower:
        column_map["quiz_score"] = col

    elif "video" in lower and "completion" in lower:
        column_map["video_completion"] = col

    elif "login" in lower:
        column_map["login_frequency"] = col

    elif "time" in lower and "spent" in lower:
        column_map["time_spent"] = col

    elif "videos" in lower and "watched" in lower:
        column_map["videos_watched"] = col

    elif "quizzes" in lower and "attempted" in lower:
        column_map["quizzes_attempted"] = col

    elif "doubts" in lower and "raised" in lower:
        column_map["doubts_raised"] = col

    elif "peer" in lower:
        column_map["peer_discussion"] = col

    elif "hackathons" in lower:
        column_map["hackathons"] = col

    elif "workshops" in lower:
        column_map["workshops"] = col

    elif "placement" in lower and "status" in lower:
        column_map["placement_status"] = col

# ---------------------------------------------------
# CHECK IMPORTANT COLUMNS
# ---------------------------------------------------
required = [
    "attendance",
    "quiz_score",
    "video_completion",
    "login_frequency",
    "time_spent",
]

missing = [c for c in required if c not in column_map]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# ---------------------------------------------------
# CREATE ADVANCED METRICS
# ---------------------------------------------------

attendance_col = column_map["attendance"]
quiz_col = column_map["quiz_score"]
video_col = column_map["video_completion"]
login_col = column_map["login_frequency"]
time_col = column_map["time_spent"]

videos_col = column_map.get("videos_watched")
quiz_attempt_col = column_map.get("quizzes_attempted")
doubts_col = column_map.get("doubts_raised")
peer_col = column_map.get("peer_discussion")
hackathon_col = column_map.get("hackathons")
workshop_col = column_map.get("workshops")
placement_col = column_map.get("placement_status")

# Fill missing optional columns
optional_cols = [
    videos_col,
    quiz_attempt_col,
    doubts_col,
    peer_col,
    hackathon_col,
    workshop_col
]

for col in optional_cols:
    if col and df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(0)

# Engagement Score
df["Engagement_Score"] = (
    df[attendance_col] * 0.2 +
    df[login_col] * 5 +
    df[time_col] * 2
)

if videos_col:
    df["Engagement_Score"] += df[videos_col] * 0.3

if quiz_attempt_col:
    df["Engagement_Score"] += df[quiz_attempt_col] * 1.5

if doubts_col:
    df["Engagement_Score"] += df[doubts_col] * 2

# Learning Effectiveness
df["Learning_Effectiveness"] = (
    df[quiz_col] *
    df[video_col] / 100
)

# Interaction Score
df["Interaction_Score"] = 0

if doubts_col:
    df["Interaction_Score"] += df[doubts_col]

if peer_col:
    df["Interaction_Score"] += df[peer_col]

if hackathon_col:
    df["Interaction_Score"] += df[hackathon_col]

if workshop_col:
    df["Interaction_Score"] += df[workshop_col]

# Placement Readiness
df["Placement_Readiness"] = (
    df["Engagement_Score"] * 0.4 +
    df["Learning_Effectiveness"] * 0.4 +
    df["Interaction_Score"] * 0.2
)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.header("🔍 Filters")

if "Department" in df.columns:
    departments = st.sidebar.multiselect(
        "Select Department",
        df["Department"].unique(),
        default=df["Department"].unique()
    )

    df = df[df["Department"].isin(departments)]

if "College" in df.columns:
    colleges = st.sidebar.multiselect(
        "Select College",
        df["College"].unique(),
        default=df["College"].unique()
    )

    df = df[df["College"].isin(colleges)]

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------
st.subheader("📊 Overall KPIs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Attendance",
        f"{df[attendance_col].mean():.2f}"
    )

with col2:
    st.metric(
        "Average Quiz Score",
        f"{df[quiz_col].mean():.2f}"
    )

with col3:
    st.metric(
        "Avg Engagement",
        f"{df['Engagement_Score'].mean():.2f}"
    )

with col4:
    st.metric(
        "Placement Readiness",
        f"{df['Placement_Readiness'].mean():.2f}"
    )

# ---------------------------------------------------
# ATTENDANCE VS QUIZ
# ---------------------------------------------------
st.subheader("📈 Attendance vs Quiz Performance")

fig1, ax1 = plt.subplots(figsize=(8, 4))

ax1.scatter(
    df[attendance_col],
    df[quiz_col]
)

ax1.set_xlabel("Attendance")
ax1.set_ylabel("Quiz Score")
ax1.set_title("Attendance vs Quiz Score")

st.pyplot(fig1)

# ---------------------------------------------------
# LOGIN VS ENGAGEMENT
# ---------------------------------------------------
st.subheader("💻 Login Frequency vs Engagement")

fig2, ax2 = plt.subplots(figsize=(8, 4))

ax2.scatter(
    df[login_col],
    df["Engagement_Score"]
)

ax2.set_xlabel("Login Frequency")
ax2.set_ylabel("Engagement Score")
ax2.set_title("Login Frequency vs Engagement")

st.pyplot(fig2)

# ---------------------------------------------------
# TIME SPENT ANALYSIS
# ---------------------------------------------------
st.subheader("⏰ Time Spent vs Placement Readiness")

fig3, ax3 = plt.subplots(figsize=(8, 4))

ax3.scatter(
    df[time_col],
    df["Placement_Readiness"]
)

ax3.set_xlabel("Time Spent")
ax3.set_ylabel("Placement Readiness")
ax3.set_title("Time Spent vs Placement Readiness")

st.pyplot(fig3)

# ---------------------------------------------------
# VIDEO COMPLETION
# ---------------------------------------------------
st.subheader("🎥 Video Completion Distribution")

fig4, ax4 = plt.subplots(figsize=(8, 4))

ax4.hist(
    df[video_col],
    bins=10
)

ax4.set_xlabel("Video Completion %")
ax4.set_ylabel("Students")

st.pyplot(fig4)

# ---------------------------------------------------
# DOUBT ANALYSIS
# ---------------------------------------------------
if doubts_col:

    st.subheader("❓ Doubt Analysis")

    fig5, ax5 = plt.subplots(figsize=(8, 4))

    ax5.scatter(
        df[doubts_col],
        df[quiz_col]
    )

    ax5.set_xlabel("Doubts Raised")
    ax5.set_ylabel("Quiz Score")

    st.pyplot(fig5)

# ---------------------------------------------------
# EVENT ANALYSIS
# ---------------------------------------------------
if hackathon_col and workshop_col:

    st.subheader("🏆 Event Participation")

    event_data = pd.Series({
        "Hackathons": df[hackathon_col].sum(),
        "Workshops": df[workshop_col].sum()
    })

    fig6, ax6 = plt.subplots(figsize=(8, 4))

    event_data.plot(
        kind="bar",
        ax=ax6
    )

    ax6.set_title("Events Participation")

    st.pyplot(fig6)

# ---------------------------------------------------
# RISK DETECTION
# ---------------------------------------------------
st.subheader("⚠️ High Risk Students")

risk_students = df[
    (df[attendance_col] < 60) &
    (df[quiz_col] < 50)
]

if len(risk_students) > 0:

    show_cols = []

    if "Student_ID" in df.columns:
        show_cols.append("Student_ID")

    if "Department" in df.columns:
        show_cols.append("Department")

    show_cols.extend([
        attendance_col,
        quiz_col
    ])

    st.dataframe(risk_students[show_cols])

else:
    st.success("No High Risk Students Found")

# ---------------------------------------------------
# STUDENT SEGMENTATION
# ---------------------------------------------------
st.subheader("🧠 Student Segmentation")

conditions = [
    (
        (df["Engagement_Score"] > 120) &
        (df[quiz_col] > 75)
    ),

    (
        (df["Engagement_Score"] > 80) &
        (df[quiz_col] < 50)
    ),

    (
        (df["Engagement_Score"] < 60)
    )
]

choices = [
    "High Performers",
    "Active But Confused",
    "Disengaged Students"
]

df["Segment"] = np.select(
    conditions,
    choices,
    default="Passive Learners"
)

segment_counts = df["Segment"].value_counts()

fig7, ax7 = plt.subplots(figsize=(8, 4))

segment_counts.plot(
    kind="bar",
    ax=ax7
)

ax7.set_title("Student Segmentation")

st.pyplot(fig7)

# ---------------------------------------------------
# LEADERBOARD
# ---------------------------------------------------
st.subheader("🏅 Top Engaged Students")

top_students = df.sort_values(
    by="Engagement_Score",
    ascending=False
).head(10)

display_cols = []

if "Student_ID" in df.columns:
    display_cols.append("Student_ID")

if "Department" in df.columns:
    display_cols.append("Department")

display_cols.extend([
    "Engagement_Score",
    "Placement_Readiness"
])

st.dataframe(top_students[display_cols])

# ---------------------------------------------------
# FINAL INSIGHT
# ---------------------------------------------------
st.subheader("🚀 Final Master Insight")

st.info(
    """
    ❌ Watching videos alone is NOT learning.

    ✅ Real Learning =
    Watching + Practicing + Asking Doubts + Applying Skills

    Engagement is one of the strongest predictors
    of placement success.
    """
)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.markdown("Developed for PragyanAI Engagement Intelligence Engine")
