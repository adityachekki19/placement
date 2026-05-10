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
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

.stApp { background: #0d0f1a; color: #e8eaf0; }

[data-testid="stSidebar"] {
    background: #111424 !important;
    border-right: 1px solid #1e2240;
}
[data-testid="stSidebar"] * { color: #c8cce0 !important; }

[data-testid="stMetric"] {
    background: #161928;
    border: 1px solid #1e2240;
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2rem !important;
    color: #7c9eff !important;
}
[data-testid="stMetricLabel"] { color: #8892b0 !important; }

h1, h2, h3 { color: #e8eaf0 !important; letter-spacing: -0.5px; }

[data-baseweb="tab-list"] {
    background: #111424;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #1e2240;
}
[data-baseweb="tab"] { color: #8892b0 !important; border-radius: 8px; font-weight: 500; }
[aria-selected="true"] { background: #1e2d6b !important; color: #7c9eff !important; }

hr { border-color: #1e2240; }

.insight-box {
    background: #111930;
    border-left: 4px solid #7c9eff;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #c8cce0;
}
.risk-high {
    background: #1f1015; border-left: 4px solid #ff6b6b;
    border-radius: 0 10px 10px 0; padding: 14px 18px; margin: 8px 0;
}
.risk-medium {
    background: #1f1a10; border-left: 4px solid #ffc857;
    border-radius: 0 10px 10px 0; padding: 14px 18px; margin: 8px 0;
}
.risk-low {
    background: #0f1f16; border-left: 4px solid #51cf66;
    border-radius: 0 10px 10px 0; padding: 14px 18px; margin: 8px 0;
}
.segment-card {
    background: #161928;
    border: 1px solid #1e2240;
    border-radius: 12px;
    padding: 18px 22px;
    margin: 8px 0;
}
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; font-family: 'JetBrains Mono', monospace;
}
.badge-green  { background: #0d3320; color: #51cf66; border: 1px solid #51cf66; }
.badge-red    { background: #3d1010; color: #ff6b6b; border: 1px solid #ff6b6b; }
.badge-yellow { background: #3d2e0a; color: #ffc857; border: 1px solid #ffc857; }
.badge-blue   { background: #0d1a40; color: #7c9eff; border: 1px solid #7c9eff; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
PLOT_BG  = "#0d0f1a"
PAPER_BG = "#0d0f1a"
GRID_CLR = "#1e2240"
FONT_CLR = "#c8cce0"
PALETTE  = ["#7c9eff","#51cf66","#ffc857","#ff6b6b","#c084fc","#38d9a9"]

def base_layout(title="", height=400):
    return dict(
        title=dict(text=title, font=dict(color=FONT_CLR, size=15, family="Space Grotesk")),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_CLR, family="Space Grotesk"),
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
        yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
        legend=dict(bgcolor="#161928", bordercolor=GRID_CLR),
    )

def placement_rate(sub):
    if len(sub) == 0:
        return 0
    return round(sub["Placement_Status"].astype(str).str.strip().eq("Placed").sum() / len(sub) * 100, 1)

# ─────────────────────────────────────────────────────────────
# COLUMN RESOLVER — handles any reasonable CSV column naming
# ─────────────────────────────────────────────────────────────
# Maps internal name → list of candidate CSV column names (lowercase, stripped)
COLUMN_ALIASES = {
    "Student_ID":               ["student_id","student id","studentid","id"],
    "College":                  ["college","college_name"],
    "College_Tier":             ["college_tier","college tier","collegetier","tier"],
    "Department":               ["department","dept"],
    "CGPA":                     ["cgpa","gpa"],
    "Gender":                   ["gender","sex"],
    "Program_Type":             ["program_type","program type","program","programme"],
    "Attendance_%":             ["attendance_%","attendance_percent","attendance_%","attendance"],
    "Sessions_Attended":        ["sessions_attended","sessions attended","sessionsattended"],
    "Sessions_Missed":          ["sessions_missed","sessions missed","sessionsmissed"],
    "Weekly_Consistency_Score": ["weekly_consistency_score","weekly_consistency","weeklyconsistency","_weekly_c","weekly c"],
    "Login_Frequency":          ["login_frequency","login frequency","loginfrequency","logins","login_freq"],
    "Time_Spent_Hours":         ["time_spent_hours","time_spent","time spent","timespent","time_sper","time sper"],
    "Active_Days_Per_Week":     ["active_days_per_week","active_days","activedays","active days"],
    "Session_Duration_Avg":     ["session_duration_avg","session_duration","sessionduration","session duration","session_dur"],
    "Videos_Watched":           ["videos_watched","videos watched","videoswatched","_videos","videos"],
    "Video_Completion_%":       ["video_completion_%","video_completion","videocompletion","video completion","video_comp"],
    "Rewatch_Rate":             ["rewatch_rate","rewatch rate","rewatchrate"],
    "Notes_Taken":              ["notes_taken","notes taken","notestaken","notes"],
    "Quizzes_Attempted":        ["quizzes_attempted","quizzes attempted","quizzesattempted","quizzes_a","quizzes"],
    "Quiz_Submission_Rate":     ["quiz_submission_rate","quiz submission rate","quiz_sub","quiz_s"],
    "Avg_Quiz_Score":           ["avg_quiz_score","avg quiz score","avgquizscore","quiz_score","quizscore","avg_quiz"],
    "Assignment_Submissions":   ["assignment_submissions","assignment submissions","assignments"],
    "On_Time_Submission_%":     ["on_time_submission_%","on_time_submission","ontime","on time submission"],
    "Doubts_Raised":            ["doubts_raised","doubts raised","doubtsraised","doubts"],
    "Doubts_Resolved":          ["doubts_resolved","doubts resolved","doubtsresolved"],
    "Doubt_Response_Time":      ["doubt_response_time","doubt response time","doubtresponsetime"],
    "Peer_Discussion_Count":    ["peer_discussion_count","peer_discussion","peer discussion","peerdiscussion","peer"],
    "Hackathons_Attended":      ["hackathons_attended","hackathons attended","hackathonsattended","hackathon","hackathons"],
    "Workshops_Attended":       ["workshops_attended","workshops attended","workshopsattended","workshop","workshops"],
    "Live_Sessions_Joined":     ["live_sessions_joined","live_sessions","live sessions","livesessions","live_sessi"],
    "Project_Demo_Events":      ["project_demo_events","project_demo","project demo","projectdemo","project_d"],
    "Skills_Learned_Count":     ["skills_learned_count","skills_learned","skills learned","skillslearned","skills"],
    "Domain_Transition":        ["domain_transition","domain transition","domaintransition"],
    "Project_Completion_Rate":  ["project_completion_rate","project_completion","project completion","project_comp"],
    "Placement_Status":         ["placement_status","placement status","placementstatus","placement"],
    "Job_Inquiries":            ["job_inquiries","job inquiries","jobinquiries","job_inquir"],
    "Leads_Generated":          ["leads_generated","leads generated","leadsgenerated","leads"],
}

def resolve_columns(df):
    """Rename CSV columns to internal names using fuzzy alias matching."""
    # Build lookup: stripped-lowercase CSV col → original CSV col
    col_map = {c.strip().lower(): c for c in df.columns}
    rename = {}
    for internal, aliases in COLUMN_ALIASES.items():
        if internal in df.columns:
            continue  # already correct
        for alias in aliases:
            if alias in col_map:
                src = col_map[alias]
                if src != internal:
                    rename[src] = internal
                break
    df = df.rename(columns=rename)
    df.columns = df.columns.str.strip()
    return df

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df.columns = df.columns.str.strip()
    df = resolve_columns(df)

    # Coerce numerics
    num_cols = [
        "Attendance_%","Sessions_Attended","Sessions_Missed","Weekly_Consistency_Score",
        "Login_Frequency","Time_Spent_Hours","Active_Days_Per_Week","Session_Duration_Avg",
        "Videos_Watched","Video_Completion_%","Rewatch_Rate",
        "Quizzes_Attempted","Quiz_Submission_Rate","Avg_Quiz_Score",
        "Assignment_Submissions","On_Time_Submission_%",
        "Doubts_Raised","Doubts_Resolved","Doubt_Response_Time","Peer_Discussion_Count",
        "Hackathons_Attended","Workshops_Attended","Live_Sessions_Joined","Project_Demo_Events",
        "Skills_Learned_Count","Project_Completion_Rate","Job_Inquiries","Leads_Generated","CGPA",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # ── Buckets ──────────────────────────────────────────────
    df["Attendance_Bucket"] = pd.cut(
        df["Attendance_%"], bins=[0,60,80,100],
        labels=["<60% (Low)","60–80% (Medium)",">80% (High)"], right=True)

    df["Login_Bucket"] = pd.cut(
        df["Login_Frequency"], bins=[0,2,4,7],
        labels=["1-2/wk","3-4/wk","5-7/wk"], right=True)

    df["Time_Bucket"] = pd.cut(
        df["Time_Spent_Hours"], bins=[0,5,15,30,999],
        labels=["<5h","5-15h","15-30h",">30h"], right=True)

    df["Video_Bucket"] = pd.cut(
        df["Video_Completion_%"], bins=[0,50,80,100],
        labels=["<50%","50-80%",">80%"], right=True)

    df["Quiz_Bucket"] = pd.cut(
        df["Avg_Quiz_Score"], bins=[0,50,75,100],
        labels=["<50","50-75",">75"], right=True)

    df["Doubt_Bucket"] = pd.cut(
        df["Doubts_Raised"], bins=[-1,0,5,9999],
        labels=["No Doubts","Some Doubts","Active Doubts"], right=True)

    df["Total_Events"] = (
        df.get("Hackathons_Attended", pd.Series(0, index=df.index)) +
        df.get("Workshops_Attended",  pd.Series(0, index=df.index))
    )
    df["Event_Bucket"] = pd.cut(
        df["Total_Events"], bins=[-1,0,2,9999],
        labels=["0 Events","1-2 Events","3+ Events"], right=True)

    # ── Composite scores ─────────────────────────────────────
    def norm(s):
        mn, mx = s.min(), s.max()
        return (s - mn) / (mx - mn + 1e-9) * 100

    df["Engagement_Score"] = (
        norm(df["Attendance_%"])                  * 0.20 +
        norm(df["Login_Frequency"])               * 0.15 +
        norm(df["Time_Spent_Hours"].clip(0, 30))  * 0.15 +
        norm(df["Video_Completion_%"])            * 0.15 +
        norm(df["Avg_Quiz_Score"])                * 0.20 +
        norm(df["Doubts_Raised"])                 * 0.15
    ).round(1)

    df["Learning_Effectiveness"] = (
        (df["Avg_Quiz_Score"] / 100) * (df["Video_Completion_%"] / 100) * 100
    ).round(1)

    df["Interaction_Score"] = norm(
        df["Doubts_Raised"] +
        df.get("Peer_Discussion_Count", pd.Series(0, index=df.index)) +
        df.get("Hackathons_Attended",   pd.Series(0, index=df.index)) +
        df.get("Workshops_Attended",    pd.Series(0, index=df.index)) +
        df.get("Live_Sessions_Joined",  pd.Series(0, index=df.index))
    ).round(1)

    df["Placement_Readiness"] = (
        df["Engagement_Score"]       * 0.40 +
        df["Learning_Effectiveness"] * 0.35 +
        df["Interaction_Score"]      * 0.25
    ).round(1)

    df["Doubt_Resolution_Rate"] = np.where(
        df["Doubts_Raised"] > 0,
        (df["Doubts_Resolved"] / df["Doubts_Raised"] * 100).round(1),
        0,
    )

    # ── Segmentation ─────────────────────────────────────────
    def segment(row):
        if row["Engagement_Score"] >= 70 and row["Avg_Quiz_Score"] >= 75 and row["Doubts_Raised"] >= 5:
            return "High Performer 🏆"
        elif row["Engagement_Score"] >= 50 and row["Avg_Quiz_Score"] < 60:
            return "Active but Confused 🤔"
        elif row["Engagement_Score"] >= 50 and row["Doubts_Raised"] < 3:
            return "Passive Learner 👀"
        else:
            return "Disengaged ⚠️"

    df["Segment"] = df.apply(segment, axis=1)

    # ── Risk ─────────────────────────────────────────────────
    def risk(row):
        if row["Attendance_%"] < 60 and row["Avg_Quiz_Score"] < 50:
            return "High Risk"
        elif row["Doubts_Raised"] == 0 and row["Engagement_Score"] < 50:
            return "Medium Risk"
        elif row["Engagement_Score"] >= 70:
            return "Low Risk"
        else:
            return "Medium Risk"

    df["Risk_Level"] = df.apply(risk, axis=1)
    return df

# ─────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────
try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ `data.csv` not found — place it in the same folder as `app.py`.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 PragyanAI")
    st.markdown("**Engagement Intelligence Engine**")
    st.markdown("---")
    st.markdown("### 🔧 Filters")

    def opts(col):
        if col not in df.columns:
            return ["All"]
        return ["All"] + sorted(df[col].dropna().astype(str).unique().tolist())

    dept      = st.selectbox("Department",       opts("Department"))
    tier      = st.selectbox("College Tier",     opts("College_Tier"))
    gender    = st.selectbox("Gender",           opts("Gender"))
    program   = st.selectbox("Program Type",     opts("Program_Type"))
    pl_filter = st.selectbox("Placement Status", ["All","Placed","Not Placed"])
    cgpa_min  = float(df["CGPA"].min())
    cgpa_max  = float(df["CGPA"].max())
    cgpa_rng  = st.slider("CGPA Range", cgpa_min, cgpa_max, (cgpa_min, cgpa_max), 0.1)

    st.markdown("---")
    st.markdown("<small style='color:#8892b0'>PragyanAI v2.0</small>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────────────────────────
fdf = df.copy()
if dept      != "All": fdf = fdf[fdf["Department"].astype(str)      == dept]
if tier      != "All": fdf = fdf[fdf["College_Tier"].astype(str)    == tier]
if gender    != "All": fdf = fdf[fdf["Gender"].astype(str)          == gender]
if program   != "All": fdf = fdf[fdf["Program_Type"].astype(str)    == program]
if pl_filter != "All": fdf = fdf[fdf["Placement_Status"].astype(str).str.strip() == pl_filter]
fdf = fdf[(fdf["CGPA"] >= cgpa_rng[0]) & (fdf["CGPA"] <= cgpa_rng[1])]
total = len(fdf)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-size:2.2rem;margin-bottom:4px;'>
  🧠 PragyanAI <span style='color:#7c9eff'>Engagement Intelligence</span>
</h1>
<p style='color:#8892b0;margin-top:0;font-size:1rem;'>
  LMS + Behavior → Learning → Placement · Real-time student analytics
</p>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────
placed    = fdf["Placement_Status"].astype(str).str.strip().eq("Placed").sum() if total else 0
place_rt  = round(placed / total * 100, 1) if total else 0
avg_eng   = round(fdf["Engagement_Score"].mean(), 1)       if total else 0
avg_quiz  = round(fdf["Avg_Quiz_Score"].mean(), 1)         if total else 0
avg_att   = round(fdf["Attendance_%"].mean(), 1)           if total else 0
high_risk = int((fdf["Risk_Level"] == "High Risk").sum())  if total else 0

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Total Students",  total)
k2.metric("Placed",          int(placed),  f"{place_rt}%")
k3.metric("Avg Engagement",  avg_eng,      "/ 100")
k4.metric("Avg Quiz Score",  avg_quiz,     "/ 100")
k5.metric("Avg Attendance",  f"{avg_att}%")
k6.metric("⚠️ High Risk",    high_risk,    f"{round(high_risk/total*100,1) if total else 0}%")
st.markdown("---")

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Engagement Overview",
    "📚 Learning Analytics",
    "💬 Interaction Insights",
    "🎯 Placement Drivers",
    "⚠️ Risk Detection",
    "🏅 Leaderboard",
    "🔬 Segmentation",
    "📈 Advanced Metrics",
])

# ══════════════════════════ TAB 1 ══════════════════════════
with tabs[0]:
    st.markdown("### Engagement Overview")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Attendance % vs Placement Rate")
        t = (fdf.groupby("Attendance_Bucket", observed=True)
             .apply(lambda x: pd.Series({"Students":len(x),"Placed %":placement_rate(x)}))
             .reset_index())
        fig = go.Figure(go.Bar(
            x=t["Attendance_Bucket"].astype(str), y=t["Placed %"],
            marker_color=["#ff6b6b","#ffc857","#51cf66"],
            text=t["Placed %"].apply(lambda v:f"{v}%"), textposition="outside"))
        fig.update_layout(**base_layout("",340))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Consistency beats intelligence — attendance >80% drives placement.</div>',
                    unsafe_allow_html=True)

    with c2:
        st.markdown("#### Login Frequency vs Placement Rate")
        t2 = (fdf.groupby("Login_Bucket", observed=True)
              .apply(lambda x: pd.Series({"Students":len(x),"Placed %":placement_rate(x)}))
              .reset_index())
        fig2 = go.Figure(go.Bar(
            x=t2["Login_Bucket"].astype(str), y=t2["Placed %"],
            marker_color=["#ff6b6b","#ffc857","#51cf66"],
            text=t2["Placed %"].apply(lambda v:f"{v}%"), textposition="outside"))
        fig2.update_layout(**base_layout("",340))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Habit formation is key — 5-7 logins/week = highest placement.</div>',
                    unsafe_allow_html=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("#### Time Spent (hrs/week) vs Outcome")
        t3 = (fdf.groupby("Time_Bucket", observed=True)
              .apply(lambda x: pd.Series({"Students":len(x),"Placed %":placement_rate(x)}))
              .reset_index())
        fig3 = go.Figure(go.Bar(
            x=t3["Time_Bucket"].astype(str), y=t3["Placed %"],
            marker_color=["#ff6b6b","#ffc857","#51cf66","#c084fc"],
            text=t3["Placed %"].apply(lambda v:f"{v}%"), textposition="outside"))
        fig3.update_layout(**base_layout("",340))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('<div class="insight-box">💡 15-30 hrs/week is the sweet spot — beyond 30 shows burnout plateau.</div>',
                    unsafe_allow_html=True)

    with c4:
        st.markdown("#### Active Days Per Week")
        fig4 = px.histogram(fdf, x="Active_Days_Per_Week", color="Placement_Status",
            color_discrete_map={"Placed":"#51cf66","Not Placed":"#ff6b6b"},
            barmode="overlay", nbins=7)
        fig4.update_layout(**base_layout("",340))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("#### Engagement Score Distribution by Placement")
    fig5 = px.violin(fdf, x="Placement_Status", y="Engagement_Score",
        color="Placement_Status",
        color_discrete_map={"Placed":"#51cf66","Not Placed":"#ff6b6b"},
        box=True, points="all")
    fig5.update_layout(**base_layout("",420))
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════ TAB 2 ══════════════════════════
with tabs[1]:
    st.markdown("### Learning Analytics")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Video Completion % vs Placement Rate")
        t = (fdf.groupby("Video_Bucket", observed=True)
             .apply(lambda x: pd.Series({"Placed %":placement_rate(x)})).reset_index())
        fig = go.Figure(go.Bar(
            x=t["Video_Bucket"].astype(str), y=t["Placed %"],
            marker_color=["#ff6b6b","#ffc857","#51cf66"],
            text=t["Placed %"].apply(lambda v:f"{v}%"), textposition="outside"))
        fig.update_layout(**base_layout("",340))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Quiz Score vs Placement Rate")
        t2 = (fdf.groupby("Quiz_Bucket", observed=True)
              .apply(lambda x: pd.Series({"Placed %":placement_rate(x)})).reset_index())
        fig2 = go.Figure(go.Bar(
            x=t2["Quiz_Bucket"].astype(str), y=t2["Placed %"],
            marker_color=["#ff6b6b","#ffc857","#51cf66"],
            text=t2["Placed %"].apply(lambda v:f"{v}%"), textposition="outside"))
        fig2.update_layout(**base_layout("",340))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Understanding > watching — quiz >75 is a strong placement signal.</div>',
                    unsafe_allow_html=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("#### Learning Effectiveness Distribution")
        fig3 = px.histogram(fdf, x="Learning_Effectiveness", color="Placement_Status",
            color_discrete_map={"Placed":"#51cf66","Not Placed":"#ff6b6b"},
            nbins=20, barmode="overlay")
        fig3.update_layout(**base_layout("",340))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown("#### Notes Taken → Avg Quiz Score")
        if "Notes_Taken" in fdf.columns:
            nt = fdf.groupby("Notes_Taken")["Avg_Quiz_Score"].mean().reset_index()
            fig4 = go.Figure(go.Bar(
                x=nt["Notes_Taken"].astype(str), y=nt["Avg_Quiz_Score"],
                marker_color=["#ff6b6b","#51cf66"],
                text=nt["Avg_Quiz_Score"].round(1), textposition="outside"))
            fig4.update_layout(**base_layout("",340))
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown("#### Video Completion % vs Quiz Score")
    fig5 = px.scatter(fdf, x="Video_Completion_%", y="Avg_Quiz_Score",
        color="Placement_Status", size="Engagement_Score",
        color_discrete_map={"Placed":"#51cf66","Not Placed":"#ff6b6b"},
        hover_data=["Student_ID","Department","CGPA"], opacity=0.8)
    fig5.update_layout(**base_layout("",420))
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""<div class="insight-box">
    ❌ Students think <b>watching videos = learning</b><br>
    ✅ Real learning = <b>Watching + Practicing + Asking + Applying</b>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════ TAB 3 ══════════════════════════
with tabs[2]:
    st.markdown("### Interaction Insights")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Doubt Behavior vs Placement Rate")
        t = (fdf.groupby("Doubt_Bucket", observed=True)
             .apply(lambda x: pd.Series({"Placed %":placement_rate(x)})).reset_index())
        fig = go.Figure(go.Bar(
            x=t["Doubt_Bucket"].astype(str), y=t["Placed %"],
            marker_color=["#ff6b6b","#ffc857","#51cf66"],
            text=t["Placed %"].apply(lambda v:f"{v}%"), textposition="outside"))
        fig.update_layout(**base_layout("",340))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Asking doubts = growth mindset — strongest placement predictor!</div>',
                    unsafe_allow_html=True)

    with c2:
        st.markdown("#### Event Participation vs Placement Rate")
        t2 = (fdf.groupby("Event_Bucket", observed=True)
              .apply(lambda x: pd.Series({"Placed %":placement_rate(x)})).reset_index())
        fig2 = go.Figure(go.Bar(
            x=t2["Event_Bucket"].astype(str), y=t2["Placed %"],
            marker_color=["#ff6b6b","#ffc857","#51cf66"],
            text=t2["Placed %"].apply(lambda v:f"{v}%"), textposition="outside"))
        fig2.update_layout(**base_layout("",340))
        st.plotly_chart(fig2, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("#### Doubt Resolution Rate vs Placement")
        fig3 = px.box(fdf, x="Placement_Status", y="Doubt_Resolution_Rate",
            color="Placement_Status",
            color_discrete_map={"Placed":"#51cf66","Not Placed":"#ff6b6b"}, points="all")
        fig3.update_layout(**base_layout("",340))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        if "Peer_Discussion_Count" in fdf.columns:
            st.markdown("#### Peer Discussion Count vs Placement")
            fig4 = px.box(fdf, x="Placement_Status", y="Peer_Discussion_Count",
                color="Placement_Status",
                color_discrete_map={"Placed":"#51cf66","Not Placed":"#ff6b6b"}, points="all")
            fig4.update_layout(**base_layout("",340))
            st.plotly_chart(fig4, use_container_width=True)

    event_cols = [c for c in ["Hackathons_Attended","Workshops_Attended",
                               "Live_Sessions_Joined","Project_Demo_Events"] if c in fdf.columns]
    if event_cols and "Department" in fdf.columns:
        st.markdown("#### Events Heatmap by Department")
        dept_ev = fdf.groupby("Department")[event_cols].mean().round(1)
        fig5 = px.imshow(dept_ev.T,
            color_continuous_scale=[[0,"#0d0f1a"],[0.5,"#1e2d6b"],[1,"#7c9eff"]],
            text_auto=True, aspect="auto")
        fig5.update_layout(**base_layout("",360))
        st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════ TAB 4 ══════════════════════════
with tabs[3]:
    st.markdown("### Placement Drivers & Correlations")

    num_df = fdf.copy()
    num_df["Placed_Num"] = num_df["Placement_Status"].astype(str).str.strip().eq("Placed").astype(int)
    want = ["Attendance_%","Login_Frequency","Time_Spent_Hours","Video_Completion_%",
            "Avg_Quiz_Score","Doubts_Raised","Peer_Discussion_Count",
            "Hackathons_Attended","Workshops_Attended","Live_Sessions_Joined",
            "Skills_Learned_Count","Project_Completion_Rate",
            "Engagement_Score","Learning_Effectiveness","Interaction_Score","Placement_Readiness"]
    existing = [c for c in want if c in num_df.columns]
    corr_vals = (num_df[existing+["Placed_Num"]].corr()["Placed_Num"]
                 .drop("Placed_Num").sort_values(ascending=True))

    c1,c2 = st.columns([2,1])
    with c1:
        st.markdown("#### Feature Correlation with Placement")
        fig = go.Figure(go.Bar(
            x=corr_vals.values, y=corr_vals.index, orientation="h",
            marker_color=["#51cf66" if v>=0 else "#ff6b6b" for v in corr_vals.values],
            text=[f"{v:.3f}" for v in corr_vals.values], textposition="outside"))
        fig.update_layout(**base_layout("",520))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Top 5 Predictors")
        for feat,val in corr_vals.sort_values(ascending=False).head(5).items():
            badge = "badge-green" if val>=0.5 else "badge-blue"
            st.markdown(f"""<div class="segment-card">
                <b style='color:#e8eaf0'>{feat}</b><br>
                <span class="badge {badge}">r = {val:.3f}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("#### Engagement Score vs Placement Readiness")
    fig2 = px.scatter(fdf, x="Engagement_Score", y="Placement_Readiness",
        color="Placement_Status", size="Avg_Quiz_Score",
        color_discrete_map={"Placed":"#51cf66","Not Placed":"#ff6b6b"},
        hover_data=["Student_ID","Department","CGPA","Segment"],
        opacity=0.85, trendline="ols")
    fig2.update_layout(**base_layout("",430))
    st.plotly_chart(fig2, use_container_width=True)

    if "Department" in fdf.columns:
        st.markdown("#### Placement Rate by Department")
        dp = (fdf.groupby("Department")
              .apply(lambda x: pd.Series({"Placement Rate %":placement_rate(x),"Count":len(x)}))
              .reset_index().sort_values("Placement Rate %", ascending=False))
        fig3 = px.bar(dp, x="Department", y="Placement Rate %",
            color="Placement Rate %",
            color_continuous_scale=[[0,"#ff6b6b"],[0.5,"#ffc857"],[1,"#51cf66"]],
            text="Placement Rate %")
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig3.update_layout(**base_layout("",360))
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════ TAB 5 ══════════════════════════
with tabs[4]:
    st.markdown("### ⚠️ Risk Detection Engine")

    rc = fdf["Risk_Level"].value_counts()
    r1,r2,r3 = st.columns(3)
    r1.metric("🔴 High Risk",   int(rc.get("High Risk",0)),
              f"{round(rc.get('High Risk',0)/total*100,1) if total else 0}%")
    r2.metric("🟡 Medium Risk", int(rc.get("Medium Risk",0)),
              f"{round(rc.get('Medium Risk',0)/total*100,1) if total else 0}%")
    r3.metric("🟢 Low Risk",    int(rc.get("Low Risk",0)),
              f"{round(rc.get('Low Risk',0)/total*100,1) if total else 0}%")
    st.markdown("---")

    c1,c2 = st.columns(2)
    with c1:
        fig = px.pie(names=rc.index, values=rc.values, color=rc.index,
            color_discrete_map={"High Risk":"#ff6b6b","Medium Risk":"#ffc857","Low Risk":"#51cf66"},
            hole=0.45)
        fig.update_layout(**base_layout("Risk Distribution",360))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "Department" in fdf.columns:
            dr = fdf.groupby(["Department","Risk_Level"]).size().reset_index(name="Count")
            fig2 = px.bar(dr, x="Department", y="Count", color="Risk_Level",
                color_discrete_map={"High Risk":"#ff6b6b","Medium Risk":"#ffc857","Low Risk":"#51cf66"},
                barmode="stack")
            fig2.update_layout(**base_layout("Risk by Department",360))
            st.plotly_chart(fig2, use_container_width=True)

    b1,b2,b3 = st.columns(3)
    with b1:
        st.markdown("""<div class="risk-high"><b style='color:#ff6b6b'>🔴 HIGH RISK</b><br>
            <small style='color:#e8c0c0'>Attendance &lt;60% AND Quiz &lt;50<br>→ Immediate intervention</small>
        </div>""", unsafe_allow_html=True)
    with b2:
        st.markdown("""<div class="risk-medium"><b style='color:#ffc857'>🟡 MEDIUM RISK</b><br>
            <small style='color:#e8d5a0'>No doubts + Engagement &lt;50<br>→ Push interaction</small>
        </div>""", unsafe_allow_html=True)
    with b3:
        st.markdown("""<div class="risk-low"><b style='color:#51cf66'>🟢 LOW RISK</b><br>
            <small style='color:#a0e8b0'>Engagement ≥ 70<br>→ On track, keep monitoring</small>
        </div>""", unsafe_allow_html=True)

    st.markdown("#### 🔴 High Risk Students")
    show_cols = [c for c in ["Student_ID","College","Department","CGPA",
                              "Attendance_%","Avg_Quiz_Score","Doubts_Raised",
                              "Engagement_Score","Risk_Level"] if c in fdf.columns]
    hr_df = fdf[fdf["Risk_Level"]=="High Risk"][show_cols].sort_values("Engagement_Score")
    if len(hr_df):
        st.dataframe(hr_df.reset_index(drop=True), use_container_width=True, height=280)
    else:
        st.info("No high-risk students in current selection.")

# ══════════════════════════ TAB 6 ══════════════════════════
with tabs[5]:
    st.markdown("### 🏅 Top Engaged Students — Leaderboard")

    top_n   = st.slider("Show top N students", 5, 50, 10)
    sort_by = st.selectbox("Rank by", [c for c in [
        "Placement_Readiness","Engagement_Score","Learning_Effectiveness",
        "Interaction_Score","Avg_Quiz_Score","Attendance_%"] if c in fdf.columns])

    lb = fdf.sort_values(sort_by, ascending=False).head(top_n).reset_index(drop=True)
    lb.index += 1
    disp = [c for c in ["Student_ID","College","Department","CGPA","Engagement_Score",
                         "Learning_Effectiveness","Interaction_Score","Placement_Readiness",
                         "Avg_Quiz_Score","Placement_Status","Segment"] if c in lb.columns]
    st.dataframe(lb[disp], use_container_width=True, height=420)

    st.markdown("#### Top 5 — Radar Profile")
    radar_cats = [c for c in ["Engagement_Score","Learning_Effectiveness","Interaction_Score",
                               "Placement_Readiness","Avg_Quiz_Score"] if c in lb.columns]
    fig_r = go.Figure()
    for _, row in lb.head(5).iterrows():
        vals = [row[c] for c in radar_cats] + [row[radar_cats[0]]]
        fig_r.add_trace(go.Scatterpolar(
            r=vals, theta=radar_cats+[radar_cats[0]],
            fill="toself", name=str(row.get("Student_ID","")), opacity=0.7))
    fig_r.update_layout(
        polar=dict(bgcolor="#111424",
                   radialaxis=dict(visible=True, range=[0,100], gridcolor=GRID_CLR, color=FONT_CLR),
                   angularaxis=dict(gridcolor=GRID_CLR, color=FONT_CLR)),
        paper_bgcolor=PAPER_BG, font=dict(color=FONT_CLR, family="Space Grotesk"),
        height=450, margin=dict(l=60,r=60,t=40,b=40))
    st.plotly_chart(fig_r, use_container_width=True)

# ══════════════════════════ TAB 7 ══════════════════════════
with tabs[6]:
    st.markdown("### 🔬 Student Segmentation")

    sc = fdf["Segment"].value_counts()
    c1,c2 = st.columns([1,2])
    with c1:
        fig = px.pie(names=sc.index, values=sc.values, color=sc.index,
            color_discrete_map={"High Performer 🏆":"#51cf66","Passive Learner 👀":"#7c9eff",
                                "Active but Confused 🤔":"#ffc857","Disengaged ⚠️":"#ff6b6b"},
            hole=0.40)
        fig.update_layout(**base_layout("Segment Distribution",360))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sp_cols = [c for c in ["Engagement_Score","Avg_Quiz_Score","Doubts_Raised",
                                "Attendance_%","Placement_Readiness"] if c in fdf.columns]
        sp = fdf.groupby("Segment")[sp_cols].mean().round(1).reset_index()
        fig2 = px.bar(sp.melt(id_vars="Segment"), x="Segment", y="value", color="variable",
            barmode="group", color_discrete_sequence=PALETTE)
        fig2.update_layout(**base_layout("Segment Profiles",380))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Action Plans")
    a1,a2,a3,a4 = st.columns(4)
    for col, seg, badge_cls, color, action in [
        (a1,"High Performer 🏆",    "badge-green", "#51cf66","👉 Placement ready"),
        (a2,"Passive Learner 👀",   "badge-blue",  "#7c9eff","👉 Push doubts & quizzes"),
        (a3,"Active but Confused 🤔","badge-yellow","#ffc857","👉 Needs mentoring"),
        (a4,"Disengaged ⚠️",        "badge-red",   "#ff6b6b","👉 High dropout risk"),
    ]:
        n = int(sc.get(seg,0))
        col.markdown(f"""<div class="segment-card" style="border-top:3px solid {color}">
            <b style='color:{color}'>{seg}</b><br>
            <span class="badge {badge_cls}">{n} students</span><br><br>
            <small style='color:#c8cce0'>{action}</small>
        </div>""", unsafe_allow_html=True)

    st.markdown("#### Engagement vs Learning Effectiveness (by Segment)")
    fig3 = px.scatter(fdf, x="Engagement_Score", y="Learning_Effectiveness", color="Segment",
        color_discrete_map={"High Performer 🏆":"#51cf66","Passive Learner 👀":"#7c9eff",
                            "Active but Confused 🤔":"#ffc857","Disengaged ⚠️":"#ff6b6b"},
        size="Avg_Quiz_Score",
        hover_data=[c for c in ["Student_ID","Department","CGPA","Placement_Status"] if c in fdf.columns],
        opacity=0.85)
    fig3.update_layout(**base_layout("",440))
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════ TAB 8 ══════════════════════════
with tabs[7]:
    st.markdown("### 📈 Advanced Metrics")

    fa,fb,fc,fd = st.columns(4)
    for col, label, formula, color in [
        (fa,"Engagement Score",
         "Attendance×0.20 + Logins×0.15 + Time×0.15 + Video×0.15 + Quiz×0.20 + Doubts×0.15","#7c9eff"),
        (fb,"Learning Effectiveness","(Quiz÷100)×(Video÷100)×100","#51cf66"),
        (fc,"Interaction Score","Norm(Doubts+Discussions+Events)","#ffc857"),
        (fd,"Placement Readiness","Engagement×0.40+Effectiveness×0.35+Interaction×0.25","#c084fc"),
    ]:
        col.markdown(f"""<div class="segment-card" style="border-top:3px solid {color}">
            <b style='color:{color}'>{label}</b><br>
            <code style='font-size:0.72rem;color:#c8cce0'>{formula}</code>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1:
        fig = px.histogram(fdf, x="Placement_Readiness", color="Placement_Status",
            color_discrete_map={"Placed":"#51cf66","Not Placed":"#ff6b6b"},
            nbins=20, barmode="overlay")
        fig.update_layout(**base_layout("Placement Readiness Distribution",340))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "College_Tier" in fdf.columns:
            tier_cols = [c for c in ["Engagement_Score","Learning_Effectiveness",
                                      "Interaction_Score","Placement_Readiness"] if c in fdf.columns]
            ts = fdf.groupby("College_Tier")[tier_cols].mean().round(1).reset_index()
            fig2 = px.bar(ts.melt(id_vars="College_Tier"), x="College_Tier", y="value",
                color="variable", barmode="group", color_discrete_sequence=PALETTE)
            fig2.update_layout(**base_layout("Scores by College Tier",340))
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Full Correlation Matrix")
    num_cols = [c for c in ["Attendance_%","Login_Frequency","Time_Spent_Hours",
                              "Video_Completion_%","Avg_Quiz_Score","Doubts_Raised",
                              "Peer_Discussion_Count","Hackathons_Attended","Workshops_Attended",
                              "Skills_Learned_Count","Project_Completion_Rate",
                              "Engagement_Score","Learning_Effectiveness",
                              "Interaction_Score","Placement_Readiness"] if c in fdf.columns]
    fig3 = px.imshow(fdf[num_cols].corr().round(2),
        color_continuous_scale=[[0,"#ff6b6b"],[0.5,"#0d0f1a"],[1,"#51cf66"]],
        zmin=-1, zmax=1, text_auto=True, aspect="auto")
    fig3.update_layout(**base_layout("",600))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Raw Data Explorer")
    sid_col = "Student_ID" if "Student_ID" in fdf.columns else fdf.columns[0]
    search = st.text_input(f"Search {sid_col}")
    view_df = fdf if not search else fdf[fdf[sid_col].astype(str).str.contains(search, case=False)]
    st.dataframe(view_df.reset_index(drop=True), use_container_width=True, height=380)
    st.download_button("⬇️ Download Filtered CSV",
        data=view_df.to_csv(index=False), file_name="pragyanai_filtered.csv", mime="text/csv")

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#8892b0;font-size:0.85rem;padding:10px 0'>
🧠 <b>PragyanAI Engagement Intelligence Engine</b> ·
Tracks behavior → Predicts success → Improves learning → Drives placements<br>
<span style='font-family:JetBrains Mono,monospace;font-size:0.75rem'>
❌ Watching videos ≠ Learning &nbsp;|&nbsp;
✅ Watching + Practicing + Asking + Applying = Real Learning
</span>
</div>
""", unsafe_allow_html=True)
