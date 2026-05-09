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
Analyze how student engagement impacts:
- Learning
- Skills
- Placement Success
""")

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------
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

# -------------------------------------------------------
# SHOW DATA
# -------------------------------------------------------
with st.expander("📂 View Dataset"):
    st.dataframe(df)

with st.expander("📌 Dataset Columns"):
    st.write(df.columns.tolist())

# -------------------------------------------------------
# SAFE COLUMN FINDER
# -------------------------------------------------------
def get_column(possible_names):

    for name in possible_names:

        for col in df.columns:

            if name.lower() in col.lower():
                return col

    return None

# -------------------------------------------------------
# COLUMN DETECTION
# -------------------------------------------------------
attendance_col = get_column(["attendance"])
quiz_col = get_column(["quiz_score", "quiz"])
video_col = get_column(["video_completion"])
login_col = get_column(["login"])
time_col = get_column(["time_spent"])
videos_col = get_column(["videos_watched"])
doubt_col = get_column(["doubts_raised"])
peer_col = get_column(["peer"])
hackathon_col = get_column(["hackathon"])
workshop_col = get_column(["workshop"])
placement_col = get_column(["placement"])

# -------------------------------------------------------
# FILL NULL VALUES
# -------------------------------------------------------
df = df.fillna(0)

# -------------------------------------------------------
# CREATE SAFE COLUMNS
# -------------------------------------------------------
def safe_column(column_name):

    if column_name is None:
        return pd.Series([0] * len(df))

    return df[column_name]

# -------------------------------------------------------
# SAFE DATA ACCESS
# -------------------------------------------------------
attendance_data = safe_column(attendance_col)
quiz_data = safe_column(quiz_col)
video_data = safe_column(video_col)
login_data = safe_column(login_col)
time_data = safe_column(time_col)
videos_data = safe_column(videos_col)
doubt_data = safe_column(doubt_col)
peer_data = safe_column(peer_col)
hackathon_data = safe_column(hackathon_col)
workshop_data = safe_column(workshop_col)

# -------------------------------------------------------
# CREATE METRICS
# -------------------------------------------------------

# Engagement Score
df["Engagement_Score"] = (
    attendance_data * 0.3 +
    login_data * 5 +
    time_data * 2 +
    videos_data * 0.5 +
    doubt_data * 3
)

# Learning Score
df["Learning_Score"] = (
    quiz_data *
    video_data / 100
)

# Interaction Score
df["Interaction_Score"] = (
    doubt_data +
    peer_data +
    hackathon_data +
    workshop_data
)

# Placement Readiness
df["Placement_Readiness"] = (
    df["Engagement_Score"] * 0.4 +
    df["Learning_Score"] * 0.4 +
    df["Interaction_Score"] * 0.2
)

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------
st.sidebar.header("🔍 Filters")

if "Department" in df.columns:

    selected_dept = st.sidebar.multiselect(
        "Select Department",
        df["Department"].unique(),
        default=df["Department"].unique()
    )

    df = df[df["Department"].isin(selected_dept)]

# -------------------------------------------------------
# KPI SECTION
# -------------------------------------------------------
st.header("📊 Overall Analytics")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Average Attendance",
        f"{attendance_data.mean():.2f}"
    )

with c2:
    st.metric(
        "Average Quiz Score",
        f"{quiz_data.mean():.2f}"
    )

with c3:
    st.metric(
        "Average Engagement",
        f"{df['Engagement_Score'].mean():.2f}"
    )

with c4:
    st.metric(
        "Placement Readiness",
        f"{df['Placement_Readiness'].mean():.2f}"
    )

# -------------------------------------------------------
# ATTENDANCE ANALYSIS
# -------------------------------------------------------
st.header("📌 Attendance vs Quiz Score")

st.write("""
Students with higher attendance generally perform
better in quizzes and placements.
""")

fig1, ax1 = plt.subplots(figsize=(8, 4))

ax1.scatter(attendance_data, quiz_data)

ax1.set_xlabel("Attendance")
ax1.set_ylabel("Quiz Score")
ax1.set_title("Attendance vs Quiz Score")

st.pyplot(fig1)

# -------------------------------------------------------
# LOGIN ANALYSIS
# -------------------------------------------------------
st.header("💻 Login Frequency vs Engagement")

fig2, ax2 = plt.subplots(figsize=(8, 4))

ax2.scatter(login_data, df["Engagement_Score"])

ax2.set_xlabel("Login Frequency")
ax2.set_ylabel("Engagement Score")
ax2.set_title("Login Activity Analysis")

st.pyplot(fig2)

# -------------------------------------------------------
# TIME SPENT ANALYSIS
# -------------------------------------------------------
st.header("⏰ Time Spent vs Placement Readiness")

fig3, ax3 = plt.subplots(figsize=(8, 4))

ax3.scatter(time_data, df["Placement_Readiness"])

ax3.set_xlabel("Time Spent")
ax3.set_ylabel("Placement Readiness")

st.pyplot(fig3)

# -------------------------------------------------------
# VIDEO ANALYSIS
# -------------------------------------------------------
st.header("🎥 Video Completion Analysis")

fig4, ax4 = plt.subplots(figsize=(8, 4))

ax4.hist(video_data, bins=10)

ax4.set_xlabel("Video Completion")
ax4.set_ylabel("Students")

st.pyplot(fig4)

# -------------------------------------------------------
# DOUBT ANALYSIS
# -------------------------------------------------------
st.header("❓ Doubt Analysis")

fig5, ax5 = plt.subplots(figsize=(8, 4))

ax5.scatter(doubt_data, quiz_data)

ax5.set_xlabel("Doubts Raised")
ax5.set_ylabel("Quiz Score")

st.pyplot(fig5)

# -------------------------------------------------------
# EVENT ANALYSIS
# -------------------------------------------------------
st.header("🏆 Event Participation")

event_data = pd.Series({
    "Hackathons": hackathon_data.sum(),
    "Workshops": workshop_data.sum()
})

fig6, ax6 = plt.subplots(figsize=(6, 4))

event_data.plot(kind="bar", ax=ax6)

ax6.set_title("Events Participation")

st.pyplot(fig6)

# -------------------------------------------------------
# RISK DETECTION
# -------------------------------------------------------
st.header("⚠️ High Risk Students")

risk_students = df[
    (attendance_data < 60) &
    (quiz_data < 50)
]

if len(risk_students) > 0:

    cols_to_show = []

    if "Student_ID" in df.columns:
        cols_to_show.append("Student_ID")

    if "Department" in df.columns:
        cols_to_show.append("Department")

    st.dataframe(risk_students[cols_to_show])

else:
    st.success("✅ No High Risk Students Found")

# -------------------------------------------------------
# STUDENT SEGMENTATION
# -------------------------------------------------------
st.header("🧠 Student Segmentation")

conditions = [
    (
        (df["Engagement_Score"] > 120) &
        (quiz_data > 75)
    ),

    (
        (df["Engagement_Score"] > 80) &
        (quiz_data < 50)
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

segment_counts = df["Student_Type"].value_counts()

fig7, ax7 = plt.subplots(figsize=(7, 4))

segment_counts.plot(kind="bar", ax=ax7)

ax7.set_title("Student Segmentation")

st.pyplot(fig7)

# -------------------------------------------------------
# TOP STUDENTS
# -------------------------------------------------------
st.header("🏅 Top Engaged Students")

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

# -------------------------------------------------------
# FINAL INSIGHT
# -------------------------------------------------------
st.header("🚀 Final Insight")

st.success("""
✅ Real Learning =
Watching + Practicing + Asking Doubts + Participating

Students with higher engagement are more likely
to become placement ready.
""")

# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------
st.markdown("---")
st.markdown("PragyanAI Engagement Intelligence Engine")
