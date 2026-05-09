
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Student Engagement Intelligence System",
    layout="wide"
)

st.title("🎓 Student Engagement Intelligence System")
st.markdown("### LMS + Behavior → Learning → Placement")

# -----------------------------
# LOAD DATA
# -----------------------------
DATA_URL = "https://raw.githubusercontent.com/pragyanaischool/VTU_Internship_DataSets/refs/heads/main/student_data_engament_Project_8.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    return df

df = load_data()

st.success("Dataset Loaded Successfully ✅")

# -----------------------------
# DATA PREVIEW
# -----------------------------
with st.expander("📂 View Dataset"):
    st.dataframe(df)

# -----------------------------
# CLEAN COLUMN NAMES
# -----------------------------
df.columns = df.columns.str.strip()

# -----------------------------
# CREATE ADVANCED METRICS
# -----------------------------

# Engagement Score
df["Engagement_Score"] = (
    df["Attendance_%"] * 0.2 +
    df["Login_Frequency"] * 5 +
    df["Time_Spent_Hours"] * 2 +
    df["Videos_Watched"] * 0.3 +
    df["Quizzes_Attempted"] * 1.5 +
    df["Doubts_Raised"] * 2
)

# Learning Effectiveness
df["Learning_Effectiveness"] = (
    df["Avg_Quiz_Score"] *
    df["Video_Completion_%"] / 100
)

# Interaction Score
df["Interaction_Score"] = (
    df["Doubts_Raised"] +
    df["Peer_Discussion_Count"] +
    df["Hackathons_Attended"] +
    df["Workshops_Attended"]
)

# Placement Readiness
df["Placement_Readiness"] = (
    df["Engagement_Score"] * 0.4 +
    df["Learning_Effectiveness"] * 0.4 +
    df["Interaction_Score"] * 0.2
)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

department = st.sidebar.multiselect(
    "Select Department",
    options=df["Department"].unique(),
    default=df["Department"].unique()
)

college = st.sidebar.multiselect(
    "Select College",
    options=df["College"].unique(),
    default=df["College"].unique()
)

filtered_df = df[
    (df["Department"].isin(department)) &
    (df["College"].isin(college))
]

# -----------------------------
# KPIs
# -----------------------------
st.subheader("📊 Overall Analytics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Attendance",
        f"{filtered_df['Attendance_%'].mean():.2f}%"
    )

with col2:
    st.metric(
        "Average Quiz Score",
        f"{filtered_df['Avg_Quiz_Score'].mean():.2f}"
    )

with col3:
    placement_rate = (
        filtered_df["Placement_Status"]
        .value_counts(normalize=True)
        .get("Placed", 0) * 100
    )

    st.metric(
        "Placement Rate",
        f"{placement_rate:.2f}%"
    )

with col4:
    st.metric(
        "Avg Engagement Score",
        f"{filtered_df['Engagement_Score'].mean():.2f}"
    )

# -----------------------------
# ENGAGEMENT OVERVIEW
# -----------------------------
st.subheader("🔥 Engagement Overview")

fig1, ax1 = plt.subplots(figsize=(8, 4))

ax1.scatter(
    filtered_df["Attendance_%"],
    filtered_df["Avg_Quiz_Score"]
)

ax1.set_xlabel("Attendance %")
ax1.set_ylabel("Quiz Score")
ax1.set_title("Attendance vs Quiz Score")

st.pyplot(fig1)

# -----------------------------
# LOGIN FREQUENCY
# -----------------------------
st.subheader("💻 Login Frequency vs Placement")

login_bins = pd.cut(
    filtered_df["Login_Frequency"],
    bins=[0, 2, 4, 7],
    labels=["Low", "Medium", "High"]
)

login_analysis = pd.crosstab(
    login_bins,
    filtered_df["Placement_Status"]
)

st.dataframe(login_analysis)

fig2, ax2 = plt.subplots(figsize=(8, 4))

login_analysis.plot(
    kind="bar",
    ax=ax2
)

ax2.set_title("Login Frequency vs Placement")
ax2.set_ylabel("Count")

st.pyplot(fig2)

# -----------------------------
# TIME SPENT ANALYSIS
# -----------------------------
st.subheader("⏰ Time Spent vs Placement")

fig3, ax3 = plt.subplots(figsize=(8, 4))

ax3.scatter(
    filtered_df["Time_Spent_Hours"],
    filtered_df["Placement_Readiness"]
)

ax3.set_xlabel("Time Spent Hours")
ax3.set_ylabel("Placement Readiness")
ax3.set_title("Time Spent vs Placement Readiness")

st.pyplot(fig3)

# -----------------------------
# VIDEO COMPLETION
# -----------------------------
st.subheader("🎥 Video Completion Analysis")

fig4, ax4 = plt.subplots(figsize=(8, 4))

ax4.hist(
    filtered_df["Video_Completion_%"],
    bins=10
)

ax4.set_title("Video Completion Distribution")
ax4.set_xlabel("Completion %")

st.pyplot(fig4)

# -----------------------------
# DOUBT ANALYSIS
# -----------------------------
st.subheader("❓ Doubt Behavior Impact")

fig5, ax5 = plt.subplots(figsize=(8, 4))

ax5.scatter(
    filtered_df["Doubts_Raised"],
    filtered_df["Avg_Quiz_Score"]
)

ax5.set_xlabel("Doubts Raised")
ax5.set_ylabel("Quiz Score")
ax5.set_title("Doubts Raised vs Quiz Score")

st.pyplot(fig5)

# -----------------------------
# EVENT PARTICIPATION
# -----------------------------
st.subheader("🏆 Event Participation")

event_data = filtered_df[
    [
        "Hackathons_Attended",
        "Workshops_Attended",
        "Live_Sessions_Joined"
    ]
].sum()

fig6, ax6 = plt.subplots(figsize=(8, 4))

event_data.plot(
    kind="bar",
    ax=ax6
)

ax6.set_title("Events Participation")

st.pyplot(fig6)

# -----------------------------
# RISK DETECTION
# -----------------------------
st.subheader("⚠️ Risk Detection")

risk_students = filtered_df[
    (filtered_df["Attendance_%"] < 60) &
    (filtered_df["Avg_Quiz_Score"] < 50)
]

st.write("### High Risk Students")

st.dataframe(
    risk_students[
        [
            "Student_ID",
            "Department",
            "Attendance_%",
            "Avg_Quiz_Score",
            "Placement_Status"
        ]
    ]
)

# -----------------------------
# SEGMENTATION
# -----------------------------
st.subheader("🧠 Student Segmentation")

conditions = [
    (
        (filtered_df["Engagement_Score"] > 120) &
        (filtered_df["Avg_Quiz_Score"] > 75)
    ),

    (
        (filtered_df["Videos_Watched"] > 20) &
        (filtered_df["Doubts_Raised"] < 2)
    ),

    (
        (filtered_df["Login_Frequency"] > 5) &
        (filtered_df["Avg_Quiz_Score"] < 50)
    )
]

choices = [
    "High Performers",
    "Passive Learners",
    "Active But Confused"
]

filtered_df["Segment"] = np.select(
    conditions,
    choices,
    default="Disengaged Students"
)

segment_count = filtered_df["Segment"].value_counts()

fig7, ax7 = plt.subplots(figsize=(8, 4))

segment_count.plot(
    kind="bar",
    ax=ax7
)

ax7.set_title("Student Segmentation")

st.pyplot(fig7)

# -----------------------------
# LEADERBOARD
# -----------------------------
st.subheader("🏅 Top Engaged Students")

top_students = filtered_df.sort_values(
    by="Engagement_Score",
    ascending=False
).head(10)

st.dataframe(
    top_students[
        [
            "Student_ID",
            "Department",
            "Engagement_Score",
            "Placement_Readiness"
        ]
    ]
)

# -----------------------------
# FINAL INSIGHT
# -----------------------------
st.subheader("🚀 Final Master Insight")

st.info(
    """
    ❌ Watching videos alone is NOT learning.

    ✅ Real learning =
    Watching + Practicing + Asking Doubts + Applying Skills

    Engagement is one of the strongest predictors of placement success.
    """
)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("Developed for PragyanAI Engagement Intelligence Engine")
