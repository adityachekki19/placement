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
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.metric-card {
    background-color: white;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}

.insight-box {
    background-color: #ffffff;
    padding: 15px;
    border-left: 5px solid #4CAF50;
    border-radius: 10px;
    margin-top: 10px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("🎓 Student Engagement Intelligence System")

st.markdown("""
### 📚 LMS + Behavior → Learning → Placement

This intelligent dashboard helps colleges identify:

✅ High performers  
✅ Passive learners  
✅ Placement readiness  
✅ Risk students  
✅ Engagement trends  
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
# VIEW DATA
# =========================================================
with st.expander("📂 View Dataset"):
    st.dataframe(df.head(20))

# =========================================================
# AUTO DETECT COLUMNS
# =========================================================
def find_column(keywords):

    for col in df.columns:

        name = col.lower()

        if all(word in name for word in keywords):
            return col

    return None

attendance_col = find_column(["attendance"])
quiz_col = find_column(["quiz"])
video_col = find_column(["video", "completion"])
login_col = find_column(["login"])
time_col = find_column(["time"])
videos_col = find_column(["videos", "watched"])
doubt_col = find_column(["doubt"])
hackathon_col = find_column(["hackathon"])
workshop_col = find_column(["workshop"])

# =========================================================
# SAFE DATA
# =========================================================
def safe_data(col):

    if col is None:
        return pd.Series([0] * len(df))

    return pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

attendance = safe_data(attendance_col)
quiz = safe_data(quiz_col)
video = safe_data(video_col)
login = safe_data(login_col)
time_spent = safe_data(time_col)
videos = safe_data(videos_col)
doubts = safe_data(doubt_col)
hackathons = safe_data(hackathon_col)
workshops = safe_data(workshop_col)

# =========================================================
# CREATE SCORES
# =========================================================
df["Engagement_Score"] = (
    attendance * 0.3 +
    login * 5 +
    time_spent * 2 +
    doubts * 3 +
    videos * 0.5
)

df["Learning_Score"] = (
    quiz *
    video / 100
)

df["Placement_Readiness"] = (
    df["Engagement_Score"] * 0.5 +
    df["Learning_Score"] * 0.5
)

# =========================================================
# SIDEBAR
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
attendance_f = pd.to_numeric(
    filtered_df[attendance_col],
    errors="coerce"
).fillna(0)

quiz_f = pd.to_numeric(
    filtered_df[quiz_col],
    errors="coerce"
).fillna(0)

video_f = pd.to_numeric(
    filtered_df[video_col],
    errors="coerce"
).fillna(0)

login_f = pd.to_numeric(
    filtered_df[login_col],
    errors="coerce"
).fillna(0)

time_f = pd.to_numeric(
    filtered_df[time_col],
    errors="coerce"
).fillna(0)

doubt_f = pd.to_numeric(
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
        "📌 Avg Attendance",
        f"{attendance_f.mean():.1f}%"
    )

with c2:
    st.metric(
        "📝 Avg Quiz Score",
        f"{quiz_f.mean():.1f}"
    )

with c3:
    st.metric(
        "🔥 Avg Engagement",
        f"{filtered_df['Engagement_Score'].mean():.1f}"
    )

with c4:
    st.metric(
        "🚀 Placement Readiness",
        f"{filtered_df['Placement_Readiness'].mean():.1f}"
    )

# =========================================================
# STUDENT HEALTH METER
# =========================================================
st.header("🧠 Student Health Meter")

high = len(filtered_df[filtered_df["Engagement_Score"] > 120])
medium = len(filtered_df[
    (filtered_df["Engagement_Score"] > 70) &
    (filtered_df["Engagement_Score"] <= 120)
])
low = len(filtered_df[filtered_df["Engagement_Score"] <= 70])

health_df = pd.DataFrame({
    "Category": ["High", "Medium", "Low"],
    "Students": [high, medium, low]
})

fig0, ax0 = plt.subplots(figsize=(7, 4))

ax0.bar(
    health_df["Category"],
    health_df["Students"],
    color=["green", "orange", "red"]
)

for i, v in enumerate(health_df["Students"]):
    ax0.text(i, v + 1, str(v), ha="center", fontsize=12)

ax0.set_title("Overall Student Engagement Health")

st.pyplot(fig0)

# =========================================================
# ATTENDANCE ANALYSIS
# =========================================================
st.header("📌 Attendance Impact")

attendance_bins = pd.cut(
    attendance_f,
    bins=[0, 60, 80, 100],
    labels=["Low", "Medium", "High"]
)

attendance_analysis = pd.DataFrame({
    "Attendance": attendance_bins,
    "Quiz": quiz_f
})

avg_scores = attendance_analysis.groupby(
    "Attendance"
)["Quiz"].mean()

fig1, ax1 = plt.subplots(figsize=(8, 5))

bars = ax1.bar(
    avg_scores.index.astype(str),
    avg_scores.values,
    color=["red", "orange", "green"]
)

for bar in bars:
    y = bar.get_height()
    ax1.text(
        bar.get_x() + bar.get_width()/2,
        y + 1,
        round(y, 1),
        ha='center'
    )

ax1.set_title("Attendance vs Quiz Performance")
ax1.set_ylabel("Average Quiz Score")

st.pyplot(fig1)

st.markdown("""
<div class="insight-box">
✅ Students with high attendance consistently score better.
</div>
""", unsafe_allow_html=True)

# =========================================================
# LOGIN ANALYSIS
# =========================================================
st.header("💻 LMS Usage Analysis")

login_bins = pd.cut(
    login_f,
    bins=[0, 2, 5, 10],
    labels=["Low", "Medium", "High"]
)

login_analysis = pd.DataFrame({
    "Login": login_bins,
    "Engagement": filtered_df["Engagement_Score"]
})

avg_login = login_analysis.groupby(
    "Login"
)["Engagement"].mean()

fig2, ax2 = plt.subplots(figsize=(8, 5))

ax2.plot(
    avg_login.index.astype(str),
    avg_login.values,
    marker="o",
    linewidth=4
)

for i, v in enumerate(avg_login.values):
    ax2.text(i, v + 2, round(v, 1), ha='center')

ax2.set_title("Login Frequency vs Engagement")
ax2.set_ylabel("Engagement Score")

st.pyplot(fig2)

st.markdown("""
<div class="insight-box">
🔥 Regular LMS usage increases engagement significantly.
</div>
""", unsafe_allow_html=True)

# =========================================================
# VIDEO ANALYSIS
# =========================================================
st.header("🎥 Video Completion Analysis")

video_bins = pd.cut(
    video_f,
    bins=[0, 50, 80, 100],
    labels=["Low", "Medium", "High"]
)

video_analysis = pd.DataFrame({
    "Video": video_bins,
    "Quiz": quiz_f
})

avg_video = video_analysis.groupby(
    "Video"
)["Quiz"].mean()

fig3, ax3 = plt.subplots(figsize=(8, 5))

bars = ax3.bar(
    avg_video.index.astype(str),
    avg_video.values,
    color=["red", "orange", "green"]
)

for bar in bars:
    y = bar.get_height()
    ax3.text(
        bar.get_x() + bar.get_width()/2,
        y + 1,
        round(y, 1),
        ha='center'
    )

ax3.set_title("Video Completion vs Quiz Score")
ax3.set_ylabel("Average Quiz Score")

st.pyplot(fig3)

# =========================================================
# DOUBT ANALYSIS
# =========================================================
st.header("❓ Doubt Solving Analysis")

doubt_bins = pd.cut(
    doubt_f,
    bins=[-1, 0, 5, 20],
    labels=["No Doubts", "Some Doubts", "Active Learners"]
)

doubt_analysis = pd.DataFrame({
    "Doubt": doubt_bins,
    "Quiz": quiz_f
})

avg_doubt = doubt_analysis.groupby(
    "Doubt"
)["Quiz"].mean()

fig4, ax4 = plt.subplots(figsize=(8, 5))

bars = ax4.bar(
    avg_doubt.index.astype(str),
    avg_doubt.values,
    color=["red", "orange", "green"]
)

for bar in bars:
    y = bar.get_height()
    ax4.text(
        bar.get_x() + bar.get_width()/2,
        y + 1,
        round(y, 1),
        ha='center'
    )

ax4.set_title("Doubt Solving vs Quiz Score")
ax4.set_ylabel("Average Quiz Score")

st.pyplot(fig4)

st.markdown("""
<div class="insight-box">
🧠 Students asking doubts perform significantly better.
</div>
""", unsafe_allow_html=True)

# =========================================================
# STUDENT SEGMENTATION
# =========================================================
st.header("🧠 Student Segmentation")

conditions = [
    (
        (filtered_df["Engagement_Score"] > 120) &
        (quiz_f > 75)
    ),

    (
        (filtered_df["Engagement_Score"] > 80) &
        (quiz_f < 50)
    ),

    (
        (filtered_df["Engagement_Score"] < 60)
    )
]

choices = [
    "High Performers",
    "Active But Confused",
    "Disengaged"
]

filtered_df["Student_Type"] = np.select(
    conditions,
    choices,
    default="Passive Learners"
)

segment = filtered_df["Student_Type"].value_counts()

fig5, ax5 = plt.subplots(figsize=(8, 5))

wedges, texts, autotexts = ax5.pie(
    segment.values,
    labels=segment.index,
    autopct="%1.1f%%",
    startangle=90
)

ax5.set_title("Student Segmentation")

st.pyplot(fig5)

# =========================================================
# HIGH RISK STUDENTS
# =========================================================
st.header("⚠️ High Risk Detection")

risk_students = filtered_df[
    (attendance_f < 60) &
    (quiz_f < 50)
]

st.metric(
    "High Risk Students",
    len(risk_students)
)

if len(risk_students) > 0:

    cols = []

    if "Student_ID" in filtered_df.columns:
        cols.append("Student_ID")

    if "Department" in filtered_df.columns:
        cols.append("Department")

    st.dataframe(risk_students[cols])

# =========================================================
# TOP STUDENTS
# =========================================================
st.header("🏅 Top Engaged Students")

top_students = filtered_df.sort_values(
    by="Engagement_Score",
    ascending=False
).head(10)

cols = []

if "Student_ID" in filtered_df.columns:
    cols.append("Student_ID")

if "Department" in filtered_df.columns:
    cols.append("Department")

cols.extend([
    "Engagement_Score",
    "Placement_Readiness"
])

st.dataframe(top_students[cols])

# =========================================================
# FINAL INSIGHT
# =========================================================
st.header("🚀 Final Master Insight")

st.success("""
✅ Real Learning =
Watching + Practicing + Asking + Participating

Students with:
- High Attendance
- Active LMS Usage
- Better Quiz Scores
- Active Doubt Solving

show better placement readiness.
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown("### PragyanAI Engagement Intelligence Engine")
