import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Student Engagement Intelligence System",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================
st.title("🎓 Student Engagement Intelligence System")

st.markdown("""
### LMS + Behavior → Learning → Placement

This dashboard analyzes:

✅ Attendance  
✅ LMS Activity  
✅ Quiz Performance  
✅ Doubt Solving  
✅ Learning Engagement  
✅ Placement Readiness  
""")

# =========================================================
# LOAD DATA
# =========================================================
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

# =========================================================
# SHOW DATASET
# =========================================================
with st.expander("📂 View Dataset"):
    st.dataframe(df.head(20))

# =========================================================
# COLUMN FINDER
# =========================================================
def find_column(keywords):

    for col in df.columns:

        name = col.lower()

        if all(word in name for word in keywords):
            return col

    return None

# =========================================================
# DETECT COLUMNS
# =========================================================
attendance_col = find_column(["attendance"])
quiz_col = find_column(["quiz"])
video_col = find_column(["video", "completion"])
login_col = find_column(["login"])
time_col = find_column(["time"])
videos_col = find_column(["videos", "watched"])
doubt_col = find_column(["doubt"])
peer_col = find_column(["peer"])
hackathon_col = find_column(["hackathon"])
workshop_col = find_column(["workshop"])

# =========================================================
# SAFE DATA FUNCTION
# =========================================================
def safe_data(column_name):

    if column_name is None:
        return pd.Series([0] * len(df))

    return pd.to_numeric(
        df[column_name],
        errors="coerce"
    ).fillna(0)

# =========================================================
# SAFE DATA
# =========================================================
attendance_data = safe_data(attendance_col)
quiz_data = safe_data(quiz_col)
video_data = safe_data(video_col)
login_data = safe_data(login_col)
time_data = safe_data(time_col)
videos_data = safe_data(videos_col)
doubt_data = safe_data(doubt_col)
peer_data = safe_data(peer_col)
hackathon_data = safe_data(hackathon_col)
workshop_data = safe_data(workshop_col)

# =========================================================
# CREATE METRICS
# =========================================================
df["Engagement_Score"] = (
    attendance_data * 0.3 +
    login_data * 5 +
    time_data * 2 +
    videos_data * 0.5 +
    doubt_data * 3
)

df["Learning_Score"] = (
    quiz_data *
    video_data / 100
)

df["Interaction_Score"] = (
    doubt_data +
    peer_data +
    hackathon_data +
    workshop_data
)

df["Placement_Readiness"] = (
    df["Engagement_Score"] * 0.4 +
    df["Learning_Score"] * 0.4 +
    df["Interaction_Score"] * 0.2
)

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("🔍 Filters")

filtered_df = df.copy()

if "Department" in filtered_df.columns:

    selected_dept = st.sidebar.multiselect(
        "Select Department",
        filtered_df["Department"].unique(),
        default=filtered_df["Department"].unique()
    )

    filtered_df = filtered_df[
        filtered_df["Department"].isin(selected_dept)
    ]

# =========================================================
# FILTERED DATA
# =========================================================
attendance_filtered = pd.to_numeric(
    filtered_df[attendance_col],
    errors="coerce"
).fillna(0)

quiz_filtered = pd.to_numeric(
    filtered_df[quiz_col],
    errors="coerce"
).fillna(0)

video_filtered = pd.to_numeric(
    filtered_df[video_col],
    errors="coerce"
).fillna(0)

login_filtered = pd.to_numeric(
    filtered_df[login_col],
    errors="coerce"
).fillna(0)

time_filtered = pd.to_numeric(
    filtered_df[time_col],
    errors="coerce"
).fillna(0)

doubt_filtered = pd.to_numeric(
    filtered_df[doubt_col],
    errors="coerce"
).fillna(0)

# =========================================================
# KPI SECTION
# =========================================================
st.header("📊 Overall Analytics")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Average Attendance",
        f"{attendance_filtered.mean():.2f}%"
    )

with c2:
    st.metric(
        "Average Quiz Score",
        f"{quiz_filtered.mean():.2f}"
    )

with c3:
    st.metric(
        "Average Engagement",
        f"{filtered_df['Engagement_Score'].mean():.2f}"
    )

with c4:
    st.metric(
        "Placement Readiness",
        f"{filtered_df['Placement_Readiness'].mean():.2f}"
    )

# =========================================================
# ATTENDANCE ANALYSIS
# =========================================================
st.header("📌 Attendance vs Quiz Performance")

attendance_bins = pd.cut(
    attendance_filtered,
    bins=[0, 60, 80, 100],
    labels=["Low", "Medium", "High"]
)

attendance_analysis = pd.DataFrame({
    "Attendance_Level": attendance_bins,
    "Quiz_Score": quiz_filtered
})

avg_scores = attendance_analysis.groupby(
    "Attendance_Level"
)["Quiz_Score"].mean()

fig1, ax1 = plt.subplots(figsize=(8, 5))

avg_scores.plot(
    kind="bar",
    ax=ax1,
    color=["red", "orange", "green"]
)

ax1.set_title("Average Quiz Score by Attendance")
ax1.set_xlabel("Attendance Category")
ax1.set_ylabel("Average Quiz Score")

st.pyplot(fig1)

st.info("""
Students with higher attendance perform better in quizzes.
""")

# =========================================================
# LOGIN ANALYSIS
# =========================================================
st.header("💻 Login Frequency Analysis")

login_bins = pd.cut(
    login_filtered,
    bins=[0, 2, 5, 10],
    labels=["Low Login", "Medium Login", "High Login"]
)

login_analysis = pd.DataFrame({
    "Login_Category": login_bins,
    "Engagement": filtered_df["Engagement_Score"]
})

avg_engagement = login_analysis.groupby(
    "Login_Category"
)["Engagement"].mean()

fig2, ax2 = plt.subplots(figsize=(8, 5))

avg_engagement.plot(
    kind="bar",
    ax=ax2,
    color=["red", "orange", "green"]
)

ax2.set_title("Login Frequency vs Engagement")
ax2.set_ylabel("Average Engagement Score")

st.pyplot(fig2)

st.success("""
Regular LMS users show higher engagement levels.
""")

# =========================================================
# TIME SPENT ANALYSIS
# =========================================================
st.header("⏰ Time Spent Analysis")

time_bins = pd.cut(
    time_filtered,
    bins=[0, 5, 15, 30, 100],
    labels=["Low", "Medium", "High", "Overload"]
)

time_analysis = pd.DataFrame({
    "Time_Category": time_bins,
    "Placement": filtered_df["Placement_Readiness"]
})

avg_placement = time_analysis.groupby(
    "Time_Category"
)["Placement"].mean()

fig3, ax3 = plt.subplots(figsize=(8, 5))

avg_placement.plot(
    kind="line",
    marker="o",
    linewidth=3,
    ax=ax3
)

ax3.set_title("Time Spent vs Placement Readiness")
ax3.set_ylabel("Placement Readiness")

st.pyplot(fig3)

st.warning("""
Optimal learning time improves placement readiness.
""")

# =========================================================
# VIDEO ANALYSIS
# =========================================================
st.header("🎥 Video Completion Analysis")

video_bins = pd.cut(
    video_filtered,
    bins=[0, 50, 80, 100],
    labels=["Low", "Medium", "High"]
)

video_analysis = pd.DataFrame({
    "Video_Category": video_bins,
    "Quiz": quiz_filtered
})

avg_quiz = video_analysis.groupby(
    "Video_Category"
)["Quiz"].mean()

fig4, ax4 = plt.subplots(figsize=(8, 5))

avg_quiz.plot(
    kind="bar",
    color=["red", "orange", "green"],
    ax=ax4
)

ax4.set_title("Video Completion vs Quiz Performance")
ax4.set_ylabel("Average Quiz Score")

st.pyplot(fig4)

st.info("""
Students completing videos perform better in quizzes.
""")

# =========================================================
# DOUBT ANALYSIS
# =========================================================
st.header("❓ Doubt Solving Analysis")

doubt_bins = pd.cut(
    doubt_filtered,
    bins=[-1, 0, 5, 20],
    labels=["No Doubts", "Some Doubts", "Active Learners"]
)

doubt_analysis = pd.DataFrame({
    "Doubt_Category": doubt_bins,
    "Quiz": quiz_filtered
})

avg_doubt = doubt_analysis.groupby(
    "Doubt_Category"
)["Quiz"].mean()

fig5, ax5 = plt.subplots(figsize=(8, 5))

avg_doubt.plot(
    kind="bar",
    color=["red", "orange", "green"],
    ax=ax5
)

ax5.set_title("Doubt Solving vs Quiz Performance")
ax5.set_ylabel("Average Quiz Score")

st.pyplot(fig5)

st.success("""
Students asking doubts generally score higher.
""")

# =========================================================
# EVENT PARTICIPATION
# =========================================================
st.header("🏆 Event Participation")

event_data = pd.Series({
    "Hackathons": hackathon_data.sum(),
    "Workshops": workshop_data.sum()
})

fig6, ax6 = plt.subplots(figsize=(7, 5))

event_data.plot(
    kind="pie",
    autopct="%1.1f%%",
    ax=ax6
)

ax6.set_ylabel("")
ax6.set_title("Student Event Participation")

st.pyplot(fig6)

# =========================================================
# STUDENT SEGMENTATION
# =========================================================
st.header("🧠 Student Segmentation")

conditions = [
    (
        (filtered_df["Engagement_Score"] > 120) &
        (quiz_filtered > 75)
    ),

    (
        (filtered_df["Engagement_Score"] > 80) &
        (quiz_filtered < 50)
    ),

    (
        (filtered_df["Engagement_Score"] < 60)
    )
]

choices = [
    "High Performers",
    "Active But Confused",
    "Disengaged Students"
]

filtered_df["Student_Type"] = np.select(
    conditions,
    choices,
    default="Passive Learners"
)

segment_count = filtered_df["Student_Type"].value_counts()

fig7, ax7 = plt.subplots(figsize=(8, 5))

segment_count.plot(
    kind="bar",
    color=["green", "orange", "red", "blue"],
    ax=ax7
)

ax7.set_title("Student Segmentation")
ax7.set_ylabel("Students")

st.pyplot(fig7)

# =========================================================
# RISK DETECTION
# =========================================================
st.header("⚠️ High Risk Students")

risk_students = filtered_df[
    (attendance_filtered < 60) &
    (quiz_filtered < 50)
]

if len(risk_students) > 0:

    show_cols = []

    if "Student_ID" in filtered_df.columns:
        show_cols.append("Student_ID")

    if "Department" in filtered_df.columns:
        show_cols.append("Department")

    st.dataframe(risk_students[show_cols])

else:
    st.success("✅ No High Risk Students Found")

# =========================================================
# LEADERBOARD
# =========================================================
st.header("🏅 Top Engaged Students")

top_students = filtered_df.sort_values(
    by="Engagement_Score",
    ascending=False
).head(10)

display_cols = []

if "Student_ID" in filtered_df.columns:
    display_cols.append("Student_ID")

if "Department" in filtered_df.columns:
    display_cols.append("Department")

display_cols.extend([
    "Engagement_Score",
    "Placement_Readiness"
])

st.dataframe(top_students[display_cols])

# =========================================================
# FINAL INSIGHT
# =========================================================
st.header("🚀 Final Insight")

st.success("""
✅ Real Learning =
Watching + Practicing + Asking + Participating

Students with:
- Higher Attendance
- Better Quiz Scores
- Active LMS Usage
- Active Doubt Solving

show stronger placement readiness.
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown("### PragyanAI Engagement Intelligence Engine")
