import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

# =========================================================
# SETTINGS
# =========================================================
warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(
    page_title="PragyanAI Student Intelligence Engine",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.stApp {
    background-color: #0E1117;
}

.metric-card {
    background: linear-gradient(135deg,#1e293b,#0f172a);
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #334155;
    text-align: center;
}

.big-font {
    font-size:22px !important;
    font-weight:bold;
}

.insight {
    padding: 15px;
    border-radius: 10px;
    background-color: #111827;
    border-left: 5px solid #38bdf8;
    margin-top: 10px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("🎓 PragyanAI Student Intelligence Engine")

st.markdown("""
### LMS Behavior → Learning Analytics → Placement Readiness

This dashboard helps identify:

✅ High Performers  
✅ Passive Learners  
✅ Disengaged Students  
✅ Placement Readiness  
✅ Learning Effectiveness  
✅ Risk Detection  
""")

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():

    try:

        df = pd.read_csv(
            "data.csv",
            encoding="utf-8"
        )

    except:

        df = pd.read_csv(
            "data.csv",
            encoding="latin1"
        )

    # CLEAN COLUMN NAMES
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("%", "Pct")
        .str.replace("-", "_")
        .str.replace("/", "_")
    )

    # SAFE CONVERSION
    for c in df.columns:

        try:

            converted = pd.to_numeric(
                df[c],
                errors="coerce"
            )

            if converted.notna().sum() > len(df) * 0.4:
                df[c] = converted

        except:
            pass

    return df

try:

    df = load_data()

except Exception as e:

    st.error(f"Error loading data: {e}")
    st.stop()

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def find_col(keywords):

    for col in df.columns:

        col_name = col.lower()

        if all(word in col_name for word in keywords):
            return col

    return None


def safe_series(col):

    if col is None:
        return pd.Series(np.zeros(len(df)))

    return pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# =========================================================
# FIND COLUMNS
# =========================================================
attendance_col = find_col(["attendance"])
quiz_col = find_col(["quiz"])
video_col = find_col(["video"])
login_col = find_col(["login"])
time_col = find_col(["time"])
doubt_col = find_col(["doubt"])
videos_col = find_col(["watched"])
department_col = find_col(["department"])
student_col = find_col(["student"])

# =========================================================
# SAFE SERIES
# =========================================================
attendance = safe_series(attendance_col)
quiz = safe_series(quiz_col)
video = safe_series(video_col)
login = safe_series(login_col)
time_spent = safe_series(time_col)
doubts = safe_series(doubt_col)
videos = safe_series(videos_col)

# =========================================================
# CREATE SCORES
# =========================================================
df["Engagement_Score"] = (
    attendance * 0.30 +
    login * 5 +
    time_spent * 2 +
    doubts * 3 +
    videos * 0.50
)

df["Learning_Score"] = (
    quiz * video / 100
)

df["Placement_Readiness"] = (
    df["Engagement_Score"] * 0.4 +
    df["Learning_Score"] * 0.4 +
    doubts * 0.2
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🔍 Filters")

filtered_df = df.copy()

if department_col:

    departments = sorted(
        filtered_df[department_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_dept = st.sidebar.multiselect(
        "Select Department",
        departments,
        default=departments
    )

    filtered_df = filtered_df[
        filtered_df[department_col]
        .astype(str)
        .isin(selected_dept)
    ]

# =========================================================
# FILTERED SERIES
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
st.header("📊 Overall Performance")

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
        "⚡ Engagement Score",
        f"{filtered_df['Engagement_Score'].mean():.1f}"
    )

with c4:
    st.metric(
        "🚀 Placement Readiness",
        f"{filtered_df['Placement_Readiness'].mean():.1f}"
    )

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Attendance",
    "💻 LMS Usage",
    "🎥 Learning",
    "❓ Doubts",
    "🏆 Leaderboard"
])

# =========================================================
# TAB 1
# =========================================================
with tab1:

    st.subheader("Attendance vs Quiz Performance")

    attendance_group = pd.cut(
        attendance_f,
        bins=[0, 60, 80, 100],
        labels=["Low", "Medium", "High"]
    )

    analysis = pd.DataFrame({
        "Attendance": attendance_group,
        "Quiz": quiz_f
    })

    avg_scores = analysis.groupby(
        "Attendance"
    )["Quiz"].mean().reset_index()

    fig = px.bar(
        avg_scores,
        x="Attendance",
        y="Quiz",
        color="Attendance",
        text_auto=True,
        title="Attendance Impact on Quiz Scores",
        color_discrete_sequence=[
            "#ef4444",
            "#f59e0b",
            "#10b981"
        ]
    )

    fig.update_layout(
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font_color="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("""
    <div class="insight">
    ✅ Students with higher attendance consistently perform better.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TAB 2
# =========================================================
with tab2:

    st.subheader("Login Frequency vs Engagement")

    login_group = pd.cut(
        login_f,
        bins=[0, 2, 5, 10],
        labels=["Low", "Medium", "High"]
    )

    login_analysis = pd.DataFrame({
        "Login": login_group,
        "Engagement": filtered_df["Engagement_Score"]
    })

    avg_login = login_analysis.groupby(
        "Login"
    )["Engagement"].mean().reset_index()

    fig2 = px.line(
        avg_login,
        x="Login",
        y="Engagement",
        markers=True,
        title="Login Frequency vs Engagement"
    )

    fig2.update_traces(
        line_color="#38bdf8",
        line_width=4
    )

    fig2.update_layout(
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font_color="white"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.markdown("""
    <div class="insight">
    🔥 Habit formation through regular logins improves engagement.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TAB 3
# =========================================================
with tab3:

    st.subheader("Video Completion vs Learning")

    video_group = pd.cut(
        video_f,
        bins=[0, 50, 80, 100],
        labels=["Low", "Medium", "High"]
    )

    video_analysis = pd.DataFrame({
        "Video": video_group,
        "Quiz": quiz_f
    })

    avg_video = video_analysis.groupby(
        "Video"
    )["Quiz"].mean().reset_index()

    fig3 = px.bar(
        avg_video,
        x="Video",
        y="Quiz",
        color="Video",
        text_auto=True,
        title="Video Completion vs Quiz Score",
        color_discrete_sequence=[
            "#ef4444",
            "#f59e0b",
            "#10b981"
        ]
    )

    fig3.update_layout(
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font_color="white"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    heatmap_df = pd.DataFrame({
        "Attendance": attendance_f,
        "Quiz": quiz_f
    })

    fig4 = px.density_heatmap(
        heatmap_df,
        x="Attendance",
        y="Quiz",
        title="Attendance vs Quiz Heatmap"
    )

    fig4.update_layout(
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font_color="white"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# =========================================================
# TAB 4
# =========================================================
with tab4:

    st.subheader("Doubt Solving Behavior")

    doubt_group = pd.cut(
        doubt_f,
        bins=[-1, 0, 5, 20],
        labels=[
            "No Doubts",
            "Some Doubts",
            "Active Learners"
        ]
    )

    doubt_analysis = pd.DataFrame({
        "Doubt": doubt_group,
        "Quiz": quiz_f
    })

    avg_doubt = doubt_analysis.groupby(
        "Doubt"
    )["Quiz"].mean().reset_index()

    fig5 = px.bar(
        avg_doubt,
        x="Doubt",
        y="Quiz",
        color="Doubt",
        text_auto=True,
        title="Doubt Asking vs Quiz Performance",
        color_discrete_sequence=[
            "#ef4444",
            "#f59e0b",
            "#10b981"
        ]
    )

    fig5.update_layout(
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font_color="white"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    st.markdown("""
    <div class="insight">
    🧠 Asking doubts reflects active learning and growth mindset.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# SEGMENTATION
# =========================================================
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
        filtered_df["Engagement_Score"] < 60
    )

]

choices = [
    "🏆 High Performers",
    "🔶 Active but Confused",
    "⚠️ Disengaged"
]

filtered_df["Segment"] = np.select(
    conditions,
    choices,
    default="🔵 Passive Learners"
)

# =========================================================
# PIE CHART
# =========================================================
segment_count = (
    filtered_df["Segment"]
    .value_counts()
    .reset_index()
)

segment_count.columns = [
    "Segment",
    "Count"
]

fig6 = px.pie(
    segment_count,
    names="Segment",
    values="Count",
    hole=0.5,
    title="Student Segmentation"
)

fig6.update_layout(
    plot_bgcolor="#111827",
    paper_bgcolor="#111827",
    font_color="white"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

# =========================================================
# TAB 5
# =========================================================
with tab5:

    st.subheader("🏅 Top Engaged Students")

    top_students = filtered_df.sort_values(
        by="Engagement_Score",
        ascending=False
    ).head(10)

    display_cols = []

    if student_col:
        display_cols.append(student_col)

    if department_col:
        display_cols.append(department_col)

    display_cols.extend([
        "Engagement_Score",
        "Learning_Score",
        "Placement_Readiness",
        "Segment"
    ])

    st.dataframe(
        top_students[display_cols],
        use_container_width=True
    )

# =========================================================
# RISK STUDENTS
# =========================================================
st.header("⚠️ Risk Detection")

risk_students = filtered_df[
    (attendance_f < 60) &
    (quiz_f < 50)
]

st.metric(
    "🚨 High Risk Students",
    len(risk_students)
)

if len(risk_students) > 0:

    cols = []

    if student_col:
        cols.append(student_col)

    if department_col:
        cols.append(department_col)

    st.dataframe(
        risk_students[cols],
        use_container_width=True
    )

# =========================================================
# FINAL INSIGHT
# =========================================================
st.header("💡 Final Master Insight")

st.success("""
✅ Real Learning =
Watching + Practicing + Asking + Applying

Students with:
- High Attendance
- Better Quiz Scores
- Active LMS Usage
- Doubt Solving Behavior

show significantly better placement readiness.
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown("""
<center>
PragyanAI Engagement Intelligence Engine
</center>
""", unsafe_allow_html=True)
