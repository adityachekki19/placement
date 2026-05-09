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
This dashboard helps analyze:

✅ Student Attendance  
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

# =========================================================
# SHOW DATA
# =========================================================
with st.expander("📂 Dataset Preview"):
    st.dataframe(df.head())

with st.expander("📌 Dataset Columns"):
    st.write(df.columns.tolist())

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
# SAFE COLUMN FUNCTION
# =========================================================
def get_safe_data(column_name):

    if column_name is None:
        return pd.Series([0] * len(df))

    return pd.to_numeric(
        df[column_name],
        errors="coerce"
    ).fillna(0)

# =========================================================
# SAFE DATA
# =========================================================
attendance_data = get_safe_data(attendance_col)
quiz_data = get_safe_data(quiz_col)
video_data = get_safe_data(video_col)
login_data = get_safe_data(login_col)
time_data = get_safe_data(time_col)
videos_data = get_safe_data(videos_col)
doubt_data = get_safe_data(doubt_col)
peer_data = get_safe_data(peer_col)
hackathon_data = get_safe_data(hackathon_col)
workshop_data = get_safe_data(workshop_col)

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
# FILTERS
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
# FILTERED SAFE DATA
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
# ATTENDANCE VS QUIZ
# =========================================================
st.header("📌 Attendance vs Quiz Performance")

fig1, ax1 = plt.subplots(figsize=(8, 4))

ax1.scatter(
    attendance_filtered,
    quiz_filtered
)

ax1.set_xlabel("Attendance")
ax1.set_ylabel("Quiz Score")
ax1.set_title("Attendance vs Quiz Score")

st.pyplot(fig1)

# =========================================================
# LOGIN ANALYSIS
# =========================================================
st.header("💻 Login Frequency vs Engagement")

fig2, ax2 = plt.subplots(figsize=(8, 4))

ax2.scatter(
    login_filtered,
    filtered_df["Engagement_Score"]
)

ax2.set_xlabel("Login Frequency")
ax2.set_ylabel("Engagement Score")
ax2.set_title("Login vs Engagement")

st.pyplot(fig2)

# =========================================================
# TIME SPENT ANALYSIS
# =========================================================
st.header("⏰ Time Spent vs Placement Readiness")

fig3, ax3 = plt.subplots(figsize=(8, 4))

ax3.scatter(
    time_filtered,
    filtered_df["Placement_Readiness"]
)

ax3.set_xlabel("Time Spent")
ax3.set_ylabel("Placement Readiness")

st.pyplot(fig3)

# =========================================================
# VIDEO COMPLETION
# =========================================================
st.header("🎥 Video Completion Analysis")

fig4, ax4 = plt.subplots(figsize=(8, 4))

ax4.hist(
    video_filtered,
    bins=10
)

ax4.set_xlabel("Video Completion")
ax4.set_ylabel("Students")

st.pyplot(fig4)

# =========================================================
# DOUBT ANALYSIS
# =========================================================
st.header("❓ Doubt Solving Analysis")

fig5, ax5 = plt.subplots(figsize=(8, 4))

ax5.scatter(
    doubt_filtered,
    quiz_filtered
)

ax5.set_xlabel("Doubts Raised")
ax5.set_ylabel("Quiz Score")

st.pyplot(fig5)

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

fig6, ax6 = plt.subplots(figsize=(7, 4))

segment_count.plot(
    kind="bar",
    ax=ax6
)

ax6.set_title("Student Segments")

st.pyplot(fig6)

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
Students with:

✅ Higher Attendance  
✅ Regular LMS Usage  
✅ Better Quiz Scores  
✅ Active Doubt Solving  

show stronger placement readiness.

Real Learning =
Watching + Practicing + Asking + Applying
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown("PragyanAI Engagement Intelligence Engine")
