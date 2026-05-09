import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Student Engagement Intelligence System",
    layout="wide"
)

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------
st.title("🎓 Student Engagement Intelligence System")
st.markdown("""
This dashboard analyzes:

✅ Student Attendance  
✅ Learning Activity  
✅ Quiz Performance  
✅ Doubt Solving Behavior  
✅ Event Participation  
✅ Placement Readiness  

The goal is to understand how engagement impacts placement success.
""")

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/pragyanaischool/VTU_Internship_DataSets/refs/heads/main/student_data_engament_Project_8.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # Clean columns
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("%", "Percent")
        .str.replace("-", "_")
    )

    return df

df = load_data()

# -------------------------------------------------------
# SHOW DATA
# -------------------------------------------------------
with st.expander("📂 View Dataset"):
    st.dataframe(df)

# -------------------------------------------------------
# AUTO DETECT COLUMNS
# -------------------------------------------------------
def find_column(keyword_list):
    for col in df.columns:
        name = col.lower()

        if all(word in name for word in keyword_list):
            return col

    return None

attendance_col = find_column(["attendance"])
quiz_col = find_column(["quiz", "score"])
video_col = find_column(["video", "completion"])
login_col = find_column(["login"])
time_col = find_column(["time", "spent"])
videos_col = find_column(["videos", "watched"])
doubt_col = find_column(["doubts", "raised"])
placement_col = find_column(["placement"])
peer_col = find_column(["peer"])
hackathon_col = find_column(["hackathons"])
workshop_col = find_column(["workshops"])

# -------------------------------------------------------
# CREATE ANALYTICS METRICS
# -------------------------------------------------------

# Fill missing values
df = df.fillna(0)

# Engagement Score
df["Engagement_Score"] = (
    df[attendance_col] * 0.3 +
    df[login_col] * 5 +
    df[time_col] * 2 +
    df[videos_col] * 0.5 +
    df[doubt_col] * 3
)

# Learning Score
df["Learning_Score"] = (
    df[quiz_col] *
    df[video_col] / 100
)

# Interaction Score
df["Interaction_Score"] = (
    df[doubt_col] +
    df[peer_col] +
    df[hackathon_col] +
    df[workshop_col]
)

# Placement Readiness
df["Placement_Readiness"] = (
    df["Engagement_Score"] * 0.4 +
    df["Learning_Score"] * 0.4 +
    df["Interaction_Score"] * 0.2
)

# -------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------
st.sidebar.header("🔍 Filter Students")

if "Department" in df.columns:

    dept = st.sidebar.multiselect(
        "Select Department",
        df["Department"].unique(),
        default=df["Department"].unique()
    )

    df = df[df["Department"].isin(dept)]

# -------------------------------------------------------
# KPI SECTION
# -------------------------------------------------------
st.header("📊 Overall Performance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Attendance",
        f"{df[attendance_col].mean():.2f}%"
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

# -------------------------------------------------------
# ATTENDANCE ANALYSIS
# -------------------------------------------------------
st.header("📌 Attendance vs Quiz Performance")

st.markdown("""
### Insight
Students with higher attendance usually score better in quizzes.

👉 Consistency is one of the strongest predictors of placement success.
""")

fig1, ax1 = plt.subplots(figsize=(8, 4))

ax1.scatter(
    df[attendance_col],
    df[quiz_col]
)

ax1.set_xlabel("Attendance %")
ax1.set_ylabel("Quiz Score")
ax1.set_title("Attendance vs Quiz Score")

st.pyplot(fig1)

# -------------------------------------------------------
# LOGIN ANALYSIS
# -------------------------------------------------------
st.header("💻 Login Activity Analysis")

st.markdown("""
### Insight
Students who regularly use the LMS platform show better engagement.

👉 Habit formation improves learning outcomes.
""")

fig2, ax2 = plt.subplots(figsize=(8, 4))

ax2.scatter(
    df[login_col],
    df["Engagement_Score"]
)

ax2.set_xlabel("Login Frequency")
ax2.set_ylabel("Engagement Score")
ax2.set_title("Login Frequency vs Engagement")

st.pyplot(fig2)

# -------------------------------------------------------
# TIME SPENT ANALYSIS
# -------------------------------------------------------
st.header("⏰ Time Spent Analysis")

st.markdown("""
### Insight
Students spending more productive learning time become more placement ready.

⚠️ Too little time leads to weak learning.
""")

fig3, ax3 = plt.subplots(figsize=(8, 4))

ax3.scatter(
    df[time_col],
    df["Placement_Readiness"]
)

ax3.set_xlabel("Time Spent")
ax3.set_ylabel("Placement Readiness")
ax3.set_title("Time Spent vs Placement Readiness")

st.pyplot(fig3)

# -------------------------------------------------------
# VIDEO COMPLETION
# -------------------------------------------------------
st.header("🎥 Video Learning Analysis")

st.markdown("""
### Insight
Completing videos fully improves conceptual understanding.

Watching alone is not enough —
students must complete and practice.
""")

fig4, ax4 = plt.subplots(figsize=(8, 4))

ax4.hist(
    df[video_col],
    bins=10
)

ax4.set_xlabel("Video Completion %")
ax4.set_ylabel("Number of Students")
ax4.set_title("Video Completion Distribution")

st.pyplot(fig4)

# -------------------------------------------------------
# DOUBT ANALYSIS
# -------------------------------------------------------
st.header("❓ Doubt Solving Behavior")

st.markdown("""
### Insight
Students asking doubts learn faster and perform better.

👉 Asking doubts = Growth mindset
""")

fig5, ax5 = plt.subplots(figsize=(8, 4))

ax5.scatter(
    df[doubt_col],
    df[quiz_col]
)

ax5.set_xlabel("Doubts Raised")
ax5.set_ylabel("Quiz Score")
ax5.set_title("Doubt Solving vs Quiz Score")

st.pyplot(fig5)

# -------------------------------------------------------
# EVENT PARTICIPATION
# -------------------------------------------------------
st.header("🏆 Event Participation")

st.markdown("""
### Insight
Hackathons and workshops improve practical skills and confidence.
""")

event_data = pd.Series({
    "Hackathons": df[hackathon_col].sum(),
    "Workshops": df[workshop_col].sum()
})

fig6, ax6 = plt.subplots(figsize=(6, 4))

event_data.plot(
    kind="bar",
    ax=ax6
)

ax6.set_title("Events Participation")

st.pyplot(fig6)

# -------------------------------------------------------
# HIGH RISK STUDENTS
# -------------------------------------------------------
st.header("⚠️ Risk Detection System")

st.markdown("""
Students with:
- Low Attendance
- Low Quiz Scores
- Low Engagement

are at high risk of poor placements or dropout.
""")

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
        quiz_col,
        "Engagement_Score"
    ])

    st.dataframe(risk_students[show_cols])

else:
    st.success("✅ No High Risk Students Found")

# -------------------------------------------------------
# STUDENT SEGMENTATION
# -------------------------------------------------------
st.header("🧠 Student Segmentation")

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

df["Student_Type"] = np.select(
    conditions,
    choices,
    default="Passive Learners"
)

segment_count = df["Student_Type"].value_counts()

fig7, ax7 = plt.subplots(figsize=(7, 4))

segment_count.plot(
    kind="bar",
    ax=ax7
)

ax7.set_title("Student Segmentation")

st.pyplot(fig7)

# -------------------------------------------------------
# LEADERBOARD
# -------------------------------------------------------
st.header("🏅 Top Engaged Students")

top_students = df.sort_values(
    by="Engagement_Score",
    ascending=False
).head(10)

leaderboard_cols = []

if "Student_ID" in df.columns:
    leaderboard_cols.append("Student_ID")

if "Department" in df.columns:
    leaderboard_cols.append("Department")

leaderboard_cols.extend([
    "Engagement_Score",
    "Placement_Readiness"
])

st.dataframe(top_students[leaderboard_cols])

# -------------------------------------------------------
# FINAL INSIGHT
# -------------------------------------------------------
st.header("🚀 Final Master Insight")

st.success("""
❌ Watching videos alone is NOT learning.

✅ Real learning happens when students:
- Watch
- Practice
- Ask doubts
- Participate
- Apply skills

Engagement is one of the strongest predictors of placement success.
""")

# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------
st.markdown("---")
st.markdown("### PragyanAI Engagement Intelligence Engine")
