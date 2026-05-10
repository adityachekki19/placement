import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
# THEME / GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Main background */
.stApp { background: #0d0f1a; color: #e8eaf0; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111424 !important;
    border-right: 1px solid #1e2240;
}
[data-testid="stSidebar"] * { color: #c8cce0 !important; }

/* Metric cards */
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
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* Headers */
h1, h2, h3 { color: #e8eaf0 !important; letter-spacing: -0.5px; }

/* Tab styling */
[data-baseweb="tab-list"] {
    background: #111424;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #1e2240;
}
[data-baseweb="tab"] {
    color: #8892b0 !important;
    border-radius: 8px;
    font-weight: 500;
}
[aria-selected="true"] {
    background: #1e2d6b !important;
    color: #7c9eff !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #1e2240; border-radius: 10px; }

/* Selectbox / multiselect */
[data-baseweb="select"] { background: #161928 !important; }

/* Divider */
hr { border-color: #1e2240; }

/* Info boxes */
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
    background: #1f1015;
    border-left: 4px solid #ff6b6b;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 8px 0;
}
.risk-medium {
    background: #1f1a10;
    border-left: 4px solid #ffc857;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 8px 0;
}
.risk-low {
    background: #0f1f16;
    border-left: 4px solid #51cf66;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 8px 0;
}
.segment-card {
    background: #161928;
    border: 1px solid #1e2240;
    border-radius: 12px;
    padding: 18px 22px;
    margin: 8px 0;
}
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}
.badge-green { background: #0d3320; color: #51cf66; border: 1px solid #51cf66; }
.badge-red   { background: #3d1010; color: #ff6b6b; border: 1px solid #ff6b6b; }
.badge-yellow{ background: #3d2e0a; color: #ffc857; border: 1px solid #ffc857; }
.badge-blue  { background: #0d1a40; color: #7c9eff; border: 1px solid #7c9eff; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")

    # ── Derived columns ──────────────────────────────────────
    # Attendance bucket
    df["Attendance_Bucket"] = pd.cut(
        df["Attendance_%"],
        bins=[0, 60, 80, 100],
        labels=["<60% (Low)", "60–80% (Medium)", ">80% (High)"],
    )

    # Login bucket
    df["Login_Bucket"] = pd.cut(
        df["Login_Frequency"],
        bins=[0, 2, 4, 7],
        labels=["1-2/wk (Low)", "3-4/wk (Medium)", "5-7/wk (High)"],
    )

    # Time bucket
    df["Time_Bucket"] = pd.cut(
        df["Time_Spent_Hours"],
        bins=[0, 5, 15, 30, 100],
        labels=["<5h (Low)", "5-15h (Med)", "15-30h (High)", ">30h (Plateau)"],
    )

    # Video completion bucket
    df["Video_Bucket"] = pd.cut(
        df["Video_Completion_%"],
        bins=[0, 50, 80, 100],
        labels=["<50%", "50-80%", ">80%"],
    )

    # Quiz bucket
    df["Quiz_Bucket"] = pd.cut(
        df["Avg_Quiz_Score"],
        bins=[0, 50, 75, 100],
        labels=["<50 (Low)", "50-75 (Med)", ">75 (High)"],
    )

    # Doubt bucket
    df["Doubt_Bucket"] = pd.cut(
        df["Doubts_Raised"],
        bins=[-1, 0, 5, 100],
        labels=["No Doubts", "Some Doubts", "Active Doubts"],
    )

    # Event bucket
    df["Event_Bucket"] = pd.cut(
        df["Hackathons_Attended"] + df["Workshops_Attended"],
        bins=[-1, 0, 2, 100],
        labels=["0 Events", "1-2 Events", "3+ Events"],
    )

    # ── Composite Scores ─────────────────────────────────────
    # Normalize 0-100
    def norm(series):
        mn, mx = series.min(), series.max()
        return (series - mn) / (mx - mn + 1e-9) * 100

    df["Eng_Attendance"]  = norm(df["Attendance_%"])
    df["Eng_Login"]       = norm(df["Login_Frequency"])
    df["Eng_Time"]        = norm(df["Time_Spent_Hours"].clip(0, 30))
    df["Eng_Video"]       = norm(df["Video_Completion_%"])
    df["Eng_Quiz"]        = norm(df["Avg_Quiz_Score"])
    df["Eng_Doubts"]      = norm(df["Doubts_Raised"])

    df["Engagement_Score"] = (
        df["Eng_Attendance"] * 0.20 +
        df["Eng_Login"]      * 0.15 +
        df["Eng_Time"]       * 0.15 +
        df["Eng_Video"]      * 0.15 +
        df["Eng_Quiz"]       * 0.20 +
        df["Eng_Doubts"]     * 0.15
    ).round(1)

    df["Learning_Effectiveness"] = (
        (df["Avg_Quiz_Score"] / 100) * (df["Video_Completion_%"] / 100) * 100
    ).round(1)

    df["Interaction_Score"] = norm(
        df["Doubts_Raised"] + df["Peer_Discussion_Count"] +
        df["Hackathons_Attended"] + df["Workshops_Attended"] + df["Live_Sessions_Joined"]
    ).round(1)

    df["Placement_Readiness"] = (
        df["Engagement_Score"]       * 0.40 +
        df["Learning_Effectiveness"] * 0.35 +
        df["Interaction_Score"]      * 0.25
    ).round(1)

    # ── Segments ─────────────────────────────────────────────
    def segment(row):
        eng  = row["Engagement_Score"]
        quiz = row["Avg_Quiz_Score"]
        doubt= row["Doubts_Raised"]
        if eng >= 70 and quiz >= 75 and doubt >= 8:
            return "High Performer 🏆"
        elif eng >= 50 and quiz < 60:
            return "Active but Confused 🤔"
        elif eng >= 50 and doubt < 3:
            return "Passive Learner 👀"
        else:
            return "Disengaged ⚠️"

    df["Segment"] = df.apply(segment, axis=1)

    # ── Risk Level ───────────────────────────────────────────
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


df = load_data()

# ─────────────────────────────────────────────────────────────
# PLOTLY THEME HELPER
# ─────────────────────────────────────────────────────────────
PLOT_BG   = "#0d0f1a"
PAPER_BG  = "#0d0f1a"
GRID_CLR  = "#1e2240"
FONT_CLR  = "#c8cce0"
PALETTE   = ["#7c9eff", "#51cf66", "#ffc857", "#ff6b6b", "#c084fc", "#38d9a9"]

def base_layout(title="", height=400):
    return dict(
        title=dict(text=title, font=dict(color=FONT_CLR, size=15, family="Space Grotesk")),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_CLR, family="Space Grotesk"),
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
        yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
    )


def placement_rate(sub_df):
    if len(sub_df) == 0:
        return 0
    return round(sub_df["Placement_Status"].eq("Placed").sum() / len(sub_df) * 100, 1)


# ─────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 PragyanAI")
    st.markdown("**Engagement Intelligence Engine**")
    st.markdown("---")

    st.markdown("### 🔧 Filters")

    dept_opts = ["All"] + sorted(df["Department"].unique().tolist())
    dept = st.selectbox("Department", dept_opts)

    tier_opts = ["All"] + sorted(df["College_Tier"].unique().tolist())
    tier = st.selectbox("College Tier", tier_opts)

    gender_opts = ["All"] + sorted(df["Gender"].unique().tolist())
    gender = st.selectbox("Gender", gender_opts)

    program_opts = ["All"] + sorted(df["Program_Type"].unique().tolist())
    program = st.selectbox("Program Type", program_opts)

    placement_opts = ["All", "Placed", "Not Placed"]
    placement_filter = st.selectbox("Placement Status", placement_opts)

    cgpa_range = st.slider("CGPA Range", 5.0, 10.0, (5.0, 10.0), 0.1)

    st.markdown("---")
    st.markdown(
        "<small style='color:#8892b0'>PragyanAI v1.0 · Student Behavior Intelligence</small>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────
fdf = df.copy()
if dept != "All":         fdf = fdf[fdf["Department"] == dept]
if tier != "All":         fdf = fdf[fdf["College_Tier"] == tier]
if gender != "All":       fdf = fdf[fdf["Gender"] == gender]
if program != "All":      fdf = fdf[fdf["Program_Type"] == program]
if placement_filter != "All": fdf = fdf[fdf["Placement_Status"] == placement_filter]
fdf = fdf[(fdf["CGPA"] >= cgpa_range[0]) & (fdf["CGPA"] <= cgpa_range[1])]

# ─────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-size:2.2rem; margin-bottom:4px;'>
  🧠 PragyanAI <span style='color:#7c9eff'>Engagement Intelligence</span>
</h1>
<p style='color:#8892b0; margin-top:0; font-size:1rem;'>
  LMS + Behavior → Learning → Placement · Real-time student analytics dashboard
</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TOP KPI STRIP
# ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
placed   = fdf["Placement_Status"].eq("Placed").sum()
total    = len(fdf)
place_rt = round(placed / total * 100, 1) if total else 0
avg_eng  = fdf["Engagement_Score"].mean() if total else 0
avg_quiz = fdf["Avg_Quiz_Score"].mean() if total else 0
avg_att  = fdf["Attendance_%"].mean() if total else 0
high_risk= (fdf["Risk_Level"] == "High Risk").sum()
avg_ready= fdf["Placement_Readiness"].mean() if total else 0

c1.metric("Total Students", total)
c2.metric("Placed", placed, f"{place_rt}%")
c3.metric("Avg Engagement", f"{avg_eng:.1f}", "/ 100")
c4.metric("Avg Quiz Score", f"{avg_quiz:.1f}", "/ 100")
c5.metric("Avg Attendance", f"{avg_att:.1f}%")
c6.metric("⚠️ High Risk", high_risk, f"{round(high_risk/total*100,1) if total else 0}%")

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

# ══════════════════════════════════════════════════════════════
# TAB 1 — ENGAGEMENT OVERVIEW
# ══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("### Engagement Overview")

    # ── Row 1: Attendance ────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Attendance vs Placement Rate")
        att_tbl = (
            fdf.groupby("Attendance_Bucket", observed=True)
            .apply(lambda x: pd.Series({
                "Students": len(x),
                "Placed %": placement_rate(x),
            }))
            .reset_index()
        )
        fig = go.Figure()
        fig.add_bar(
            x=att_tbl["Attendance_Bucket"].astype(str),
            y=att_tbl["Placed %"],
            marker_color=["#ff6b6b", "#ffc857", "#51cf66"],
            text=att_tbl["Placed %"].apply(lambda v: f"{v}%"),
            textposition="outside",
        )
        fig.update_layout(**base_layout("", 340))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Consistency beats intelligence — attendance >80% correlates strongly with placement.</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown("#### Login Frequency vs Placement Rate")
        login_tbl = (
            fdf.groupby("Login_Bucket", observed=True)
            .apply(lambda x: pd.Series({"Students": len(x), "Placed %": placement_rate(x)}))
            .reset_index()
        )
        fig2 = go.Figure()
        fig2.add_bar(
            x=login_tbl["Login_Bucket"].astype(str),
            y=login_tbl["Placed %"],
            marker_color=["#ff6b6b", "#ffc857", "#51cf66"],
            text=login_tbl["Placed %"].apply(lambda v: f"{v}%"),
            textposition="outside",
        )
        fig2.update_layout(**base_layout("", 340))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Habit formation is key — 5-7 logins/week shows highest placement outcomes.</div>', unsafe_allow_html=True)

    # ── Row 2: Time & Activity ───────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### Time Spent vs Outcome")
        time_tbl = (
            fdf.groupby("Time_Bucket", observed=True)
            .apply(lambda x: pd.Series({"Students": len(x), "Placed %": placement_rate(x)}))
            .reset_index()
        )
        fig3 = go.Figure()
        fig3.add_bar(
            x=time_tbl["Time_Bucket"].astype(str),
            y=time_tbl["Placed %"],
            marker_color=["#ff6b6b", "#ffc857", "#51cf66", "#c084fc"],
            text=time_tbl["Placed %"].apply(lambda v: f"{v}%"),
            textposition="outside",
        )
        fig3.update_layout(**base_layout("", 340))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('<div class="insight-box">💡 15-30 hours/week is the sweet spot — beyond 30 shows burnout plateau.</div>', unsafe_allow_html=True)

    with col_d:
        st.markdown("#### Active Days per Week Distribution")
        fig4 = px.histogram(
            fdf, x="Active_Days_Per_Week", color="Placement_Status",
            color_discrete_map={"Placed": "#51cf66", "Not Placed": "#ff6b6b"},
            barmode="overlay", nbins=7,
        )
        fig4.update_layout(**base_layout("", 340))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Engagement Score Distribution ────────────────────────
    st.markdown("#### Engagement Score Distribution by Placement")
    fig5 = px.violin(
        fdf, x="Placement_Status", y="Engagement_Score",
        color="Placement_Status",
        color_discrete_map={"Placed": "#51cf66", "Not Placed": "#ff6b6b"},
        box=True, points="all",
    )
    fig5.update_layout(**base_layout("", 420))
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — LEARNING ANALYTICS
# ══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### Learning Analytics")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Video Completion % vs Placement Rate")
        vid_tbl = (
            fdf.groupby("Video_Bucket", observed=True)
            .apply(lambda x: pd.Series({"Placed %": placement_rate(x), "Count": len(x)}))
            .reset_index()
        )
        fig = go.Figure()
        fig.add_bar(
            x=vid_tbl["Video_Bucket"].astype(str),
            y=vid_tbl["Placed %"],
            marker_color=["#ff6b6b", "#ffc857", "#51cf66"],
            text=vid_tbl["Placed %"].apply(lambda v: f"{v}%"),
            textposition="outside",
        )
        fig.update_layout(**base_layout("", 340))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Quiz Score vs Placement Rate")
        quiz_tbl = (
            fdf.groupby("Quiz_Bucket", observed=True)
            .apply(lambda x: pd.Series({"Placed %": placement_rate(x), "Count": len(x)}))
            .reset_index()
        )
        fig2 = go.Figure()
        fig2.add_bar(
            x=quiz_tbl["Quiz_Bucket"].astype(str),
            y=quiz_tbl["Placed %"],
            marker_color=["#ff6b6b", "#ffc857", "#51cf66"],
            text=quiz_tbl["Placed %"].apply(lambda v: f"{v}%"),
            textposition="outside",
        )
        fig2.update_layout(**base_layout("", 340))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Understanding > watching — quiz score >75 drives placement significantly.</div>', unsafe_allow_html=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### Learning Effectiveness Score Distribution")
        fig3 = px.histogram(
            fdf, x="Learning_Effectiveness", color="Placement_Status",
            color_discrete_map={"Placed": "#51cf66", "Not Placed": "#ff6b6b"},
            nbins=20, barmode="overlay",
        )
        fig3.update_layout(**base_layout("", 340))
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown("#### Notes Taken vs Avg Quiz Score")
        notes_tbl = fdf.groupby("Notes_Taken")["Avg_Quiz_Score"].mean().reset_index()
        fig4 = go.Figure()
        fig4.add_bar(
            x=notes_tbl["Notes_Taken"].astype(str),
            y=notes_tbl["Avg_Quiz_Score"],
            marker_color=["#ff6b6b", "#51cf66"],
            text=notes_tbl["Avg_Quiz_Score"].round(1),
            textposition="outside",
        )
        fig4.update_layout(**base_layout("", 340))
        st.plotly_chart(fig4, use_container_width=True)

    # Scatter: Video Completion vs Quiz Score
    st.markdown("#### Video Completion % vs Quiz Score (coloured by Placement)")
    fig5 = px.scatter(
        fdf, x="Video_Completion_%", y="Avg_Quiz_Score",
        color="Placement_Status", size="Engagement_Score",
        color_discrete_map={"Placed": "#51cf66", "Not Placed": "#ff6b6b"},
        hover_data=["Student_ID", "Department", "CGPA"],
        opacity=0.8,
    )
    fig5.update_layout(**base_layout("", 420))
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    ❌ Students think <b>watching videos = learning</b><br>
    ✅ Real learning = <b>Watching + Practicing + Asking + Applying</b>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — INTERACTION INSIGHTS
# ══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### Interaction Insights")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Doubt Behavior vs Placement Rate")
        doubt_tbl = (
            fdf.groupby("Doubt_Bucket", observed=True)
            .apply(lambda x: pd.Series({"Placed %": placement_rate(x), "Count": len(x)}))
            .reset_index()
        )
        fig = go.Figure()
        fig.add_bar(
            x=doubt_tbl["Doubt_Bucket"].astype(str),
            y=doubt_tbl["Placed %"],
            marker_color=["#ff6b6b", "#ffc857", "#51cf66"],
            text=doubt_tbl["Placed %"].apply(lambda v: f"{v}%"),
            textposition="outside",
        )
        fig.update_layout(**base_layout("", 340))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Asking doubts = growth mindset — very strong predictor of placement!</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown("#### Event Participation vs Placement Rate")
        event_tbl = (
            fdf.groupby("Event_Bucket", observed=True)
            .apply(lambda x: pd.Series({"Placed %": placement_rate(x), "Count": len(x)}))
            .reset_index()
        )
        fig2 = go.Figure()
        fig2.add_bar(
            x=event_tbl["Event_Bucket"].astype(str),
            y=event_tbl["Placed %"],
            marker_color=["#ff6b6b", "#ffc857", "#51cf66"],
            text=event_tbl["Placed %"].apply(lambda v: f"{v}%"),
            textposition="outside",
        )
        fig2.update_layout(**base_layout("", 340))
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### Doubt Resolution Rate vs Placement")
        fdf["Doubt_Resolution_Rate"] = np.where(
            fdf["Doubts_Raised"] > 0,
            (fdf["Doubts_Resolved"] / fdf["Doubts_Raised"] * 100).round(1),
            0
        )
        fig3 = px.box(
            fdf, x="Placement_Status", y="Doubt_Resolution_Rate",
            color="Placement_Status",
            color_discrete_map={"Placed": "#51cf66", "Not Placed": "#ff6b6b"},
            points="all",
        )
        fig3.update_layout(**base_layout("", 340))
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown("#### Peer Discussion Count vs Placement")
        fig4 = px.box(
            fdf, x="Placement_Status", y="Peer_Discussion_Count",
            color="Placement_Status",
            color_discrete_map={"Placed": "#51cf66", "Not Placed": "#ff6b6b"},
            points="all",
        )
        fig4.update_layout(**base_layout("", 340))
        st.plotly_chart(fig4, use_container_width=True)

    # Event heatmap
    st.markdown("#### Events Participation Heatmap (by Department)")
    dept_event = fdf.groupby("Department")[
        ["Hackathons_Attended", "Workshops_Attended", "Live_Sessions_Joined", "Project_Demo_Events"]
    ].mean().round(1)
    fig5 = px.imshow(
        dept_event.T,
        color_continuous_scale=[[0, "#0d0f1a"], [0.5, "#1e2d6b"], [1, "#7c9eff"]],
        text_auto=True,
        aspect="auto",
    )
    fig5.update_layout(**base_layout("", 360))
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 — PLACEMENT DRIVERS
# ══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### Placement Drivers & Correlations")

    # Correlation with Placement (numeric: 1=Placed, 0=Not)
    num_df = fdf.copy()
    num_df["Placed_Num"] = (num_df["Placement_Status"] == "Placed").astype(int)
    corr_cols = [
        "Attendance_%", "Login_Frequency", "Time_Spent_Hours", "Video_Completion_%",
        "Avg_Quiz_Score", "Doubts_Raised", "Peer_Discussion_Count",
        "Hackathons_Attended", "Workshops_Attended", "Live_Sessions_Joined",
        "Skills_Learned_Count", "Project_Completion_Rate", "Engagement_Score",
        "Learning_Effectiveness", "Interaction_Score", "Placement_Readiness",
    ]
    corr_vals = (
        num_df[corr_cols + ["Placed_Num"]]
        .corr()["Placed_Num"]
        .drop("Placed_Num")
        .sort_values(ascending=True)
    )

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("#### Feature Correlation with Placement")
        fig = go.Figure(go.Bar(
            x=corr_vals.values,
            y=corr_vals.index,
            orientation="h",
            marker_color=[
                "#51cf66" if v >= 0 else "#ff6b6b" for v in corr_vals.values
            ],
            text=[f"{v:.3f}" for v in corr_vals.values],
            textposition="outside",
        ))
        fig.update_layout(**base_layout("", 520))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Top Predictors")
        top5 = corr_vals.sort_values(ascending=False).head(5)
        for feat, val in top5.items():
            badge = "badge-green" if val >= 0.6 else "badge-blue"
            st.markdown(f"""
            <div class="segment-card">
                <b style='color:#e8eaf0'>{feat}</b><br>
                <span class="badge {badge}">r = {val:.3f}</span>
            </div>
            """, unsafe_allow_html=True)

    # Scatter: Engagement Score vs Placement Readiness
    st.markdown("#### Engagement Score vs Placement Readiness")
    fig2 = px.scatter(
        fdf, x="Engagement_Score", y="Placement_Readiness",
        color="Placement_Status", size="Avg_Quiz_Score",
        color_discrete_map={"Placed": "#51cf66", "Not Placed": "#ff6b6b"},
        hover_data=["Student_ID", "Department", "CGPA", "Segment"],
        opacity=0.85,
        trendline="ols",
    )
    fig2.update_layout(**base_layout("", 430))
    st.plotly_chart(fig2, use_container_width=True)

    # Department-wise placement rate
    st.markdown("#### Placement Rate by Department")
    dept_place = (
        fdf.groupby("Department")
        .apply(lambda x: pd.Series({"Placement Rate %": placement_rate(x), "Count": len(x)}))
        .reset_index()
        .sort_values("Placement Rate %", ascending=False)
    )
    fig3 = px.bar(
        dept_place, x="Department", y="Placement Rate %",
        color="Placement Rate %",
        color_continuous_scale=[[0, "#ff6b6b"], [0.5, "#ffc857"], [1, "#51cf66"]],
        text="Placement Rate %",
    )
    fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig3.update_layout(**base_layout("", 360))
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — RISK DETECTION
# ══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### ⚠️ Risk Detection Engine")

    # Summary
    risk_counts = fdf["Risk_Level"].value_counts()
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("🔴 High Risk", int(risk_counts.get("High Risk", 0)),
               f"{round(risk_counts.get('High Risk',0)/total*100,1)}% of cohort")
    rc2.metric("🟡 Medium Risk", int(risk_counts.get("Medium Risk", 0)),
               f"{round(risk_counts.get('Medium Risk',0)/total*100,1)}% of cohort")
    rc3.metric("🟢 Low Risk", int(risk_counts.get("Low Risk", 0)),
               f"{round(risk_counts.get('Low Risk',0)/total*100,1)}% of cohort")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Risk Distribution")
        fig = px.pie(
            names=risk_counts.index, values=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map={
                "High Risk": "#ff6b6b",
                "Medium Risk": "#ffc857",
                "Low Risk": "#51cf66",
            },
            hole=0.45,
        )
        fig.update_layout(**base_layout("", 360))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Risk by Department")
        dept_risk = (
            fdf.groupby(["Department", "Risk_Level"])
            .size().reset_index(name="Count")
        )
        fig2 = px.bar(
            dept_risk, x="Department", y="Count", color="Risk_Level",
            color_discrete_map={
                "High Risk": "#ff6b6b",
                "Medium Risk": "#ffc857",
                "Low Risk": "#51cf66",
            },
            barmode="stack",
        )
        fig2.update_layout(**base_layout("", 360))
        st.plotly_chart(fig2, use_container_width=True)

    # Risk rules display
    st.markdown("#### Risk Detection Rules")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown("""
        <div class="risk-high">
            <b style='color:#ff6b6b'>🔴 HIGH RISK</b><br>
            <small style='color:#e8c0c0'>
            • Attendance < 60% <b>AND</b><br>
            • Quiz Score < 50<br><br>
            → Immediate intervention needed
            </small>
        </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown("""
        <div class="risk-medium">
            <b style='color:#ffc857'>🟡 MEDIUM RISK</b><br>
            <small style='color:#e8d5a0'>
            • No doubts raised <b>AND</b><br>
            • Engagement Score < 50<br><br>
            → Passive learner — push interaction
            </small>
        </div>
        """, unsafe_allow_html=True)
    with r3:
        st.markdown("""
        <div class="risk-low">
            <b style='color:#51cf66'>🟢 LOW RISK</b><br>
            <small style='color:#a0e8b0'>
            • Engagement Score ≥ 70<br><br>
            → On track for placement<br>
            → Continue monitoring
            </small>
        </div>
        """, unsafe_allow_html=True)

    # High Risk Students Table
    st.markdown("#### 🔴 High Risk Students")
    high_risk_df = fdf[fdf["Risk_Level"] == "High Risk"][[
        "Student_ID", "College", "Department", "CGPA",
        "Attendance_%", "Avg_Quiz_Score", "Doubts_Raised",
        "Engagement_Score", "Risk_Level"
    ]].sort_values("Engagement_Score")
    if len(high_risk_df):
        st.dataframe(
            high_risk_df.style.applymap(
                lambda v: "color: #ff6b6b" if isinstance(v, str) and v == "High Risk" else "",
            ),
            use_container_width=True, height=280,
        )
    else:
        st.info("No high-risk students in current filter.")

# ══════════════════════════════════════════════════════════════
# TAB 6 — LEADERBOARD
# ══════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("### 🏅 Top Engaged Students — Leaderboard")

    top_n = st.slider("Show top N students", 5, 30, 10)
    sort_by = st.selectbox(
        "Rank by",
        ["Placement_Readiness", "Engagement_Score", "Learning_Effectiveness",
         "Interaction_Score", "Avg_Quiz_Score", "Attendance_%"],
    )

    leaderboard = (
        fdf.sort_values(sort_by, ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    leaderboard.index += 1  # start rank from 1

    display_cols = [
        "Student_ID", "College", "Department", "CGPA",
        "Engagement_Score", "Learning_Effectiveness", "Interaction_Score",
        "Placement_Readiness", "Avg_Quiz_Score", "Placement_Status", "Segment",
    ]

    def color_row(row):
        styles = [""] * len(row)
        idx = row.index.tolist()
        if "Placement_Status" in idx:
            i = idx.index("Placement_Status")
            styles[i] = "color: #51cf66" if row["Placement_Status"] == "Placed" else "color: #ff6b6b"
        return styles

    st.dataframe(
        leaderboard[display_cols].style.apply(color_row, axis=1),
        use_container_width=True,
        height=420,
    )

    # Radar chart for top 5
    st.markdown("#### Top 5 Students — Radar Profile")
    top5 = leaderboard.head(5)
    radar_cats = [
        "Engagement_Score", "Learning_Effectiveness", "Interaction_Score",
        "Placement_Readiness", "Avg_Quiz_Score",
    ]
    fig_radar = go.Figure()
    for _, row in top5.iterrows():
        vals = [row[c] for c in radar_cats] + [row[radar_cats[0]]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals,
            theta=radar_cats + [radar_cats[0]],
            fill="toself",
            name=row["Student_ID"],
            opacity=0.7,
        ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#111424",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=GRID_CLR, color=FONT_CLR),
            angularaxis=dict(gridcolor=GRID_CLR, color=FONT_CLR),
        ),
        paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_CLR, family="Space Grotesk"),
        height=450,
        margin=dict(l=60, r=60, t=40, b=40),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 7 — SEGMENTATION
# ══════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("### 🔬 Student Segmentation")

    seg_counts = fdf["Segment"].value_counts()

    col_a, col_b = st.columns([1, 2])

    with col_a:
        st.markdown("#### Segment Distribution")
        fig = px.pie(
            names=seg_counts.index, values=seg_counts.values,
            color=seg_counts.index,
            color_discrete_map={
                "High Performer 🏆": "#51cf66",
                "Passive Learner 👀": "#7c9eff",
                "Active but Confused 🤔": "#ffc857",
                "Disengaged ⚠️": "#ff6b6b",
            },
            hole=0.40,
        )
        fig.update_layout(**base_layout("", 360))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Segment Profiles")
        seg_profile = (
            fdf.groupby("Segment")[
                ["Engagement_Score", "Avg_Quiz_Score", "Doubts_Raised",
                 "Attendance_%", "Placement_Readiness"]
            ].mean().round(1).reset_index()
        )
        fig2 = px.bar(
            seg_profile.melt(id_vars="Segment"),
            x="Segment", y="value", color="variable",
            barmode="group",
            color_discrete_sequence=PALETTE,
        )
        fig2.update_layout(**base_layout("", 380))
        st.plotly_chart(fig2, use_container_width=True)

    # Segment cards
    st.markdown("#### Segment Action Plans")
    sc1, sc2, sc3, sc4 = st.columns(4)

    hp = int(seg_counts.get("High Performer 🏆", 0))
    pl = int(seg_counts.get("Passive Learner 👀", 0))
    ac = int(seg_counts.get("Active but Confused 🤔", 0))
    dis = int(seg_counts.get("Disengaged ⚠️", 0))

    with sc1:
        st.markdown(f"""
        <div class="segment-card">
            <b style='color:#51cf66'>🏆 High Performers</b><br>
            <span class="badge badge-green">{hp} students</span><br><br>
            <small style='color:#a0d8a8'>
            ✅ High engagement<br>
            ✅ High quiz scores<br>
            ✅ Active doubts<br><br>
            👉 Placement ready
            </small>
        </div>
        """, unsafe_allow_html=True)

    with sc2:
        st.markdown(f"""
        <div class="segment-card">
            <b style='color:#7c9eff'>👀 Passive Learners</b><br>
            <span class="badge badge-blue">{pl} students</span><br><br>
            <small style='color:#a0b8e8'>
            ✅ Watches videos<br>
            ❌ Low interaction<br>
            ❌ Few doubts<br><br>
            👉 Encourage doubts + quizzes
            </small>
        </div>
        """, unsafe_allow_html=True)

    with sc3:
        st.markdown(f"""
        <div class="segment-card">
            <b style='color:#ffc857'>🤔 Active but Confused</b><br>
            <span class="badge badge-yellow">{ac} students</span><br><br>
            <small style='color:#e8d5a0'>
            ✅ High activity<br>
            ❌ Low quiz scores<br>
            ❌ Misaligned effort<br><br>
            👉 Need mentoring
            </small>
        </div>
        """, unsafe_allow_html=True)

    with sc4:
        st.markdown(f"""
        <div class="segment-card">
            <b style='color:#ff6b6b'>⚠️ Disengaged</b><br>
            <span class="badge badge-red">{dis} students</span><br><br>
            <small style='color:#e8c0c0'>
            ❌ Low attendance<br>
            ❌ Low logins<br>
            ❌ No interaction<br><br>
            👉 High dropout risk
            </small>
        </div>
        """, unsafe_allow_html=True)

    # Scatter coloured by segment
    st.markdown("#### Engagement Score vs Learning Effectiveness (by Segment)")
    fig3 = px.scatter(
        fdf, x="Engagement_Score", y="Learning_Effectiveness",
        color="Segment",
        color_discrete_map={
            "High Performer 🏆": "#51cf66",
            "Passive Learner 👀": "#7c9eff",
            "Active but Confused 🤔": "#ffc857",
            "Disengaged ⚠️": "#ff6b6b",
        },
        size="Avg_Quiz_Score",
        hover_data=["Student_ID", "Department", "CGPA", "Placement_Status"],
        opacity=0.85,
    )
    fig3.update_layout(**base_layout("", 440))
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 8 — ADVANCED METRICS
# ══════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("### 📈 Advanced Metrics & Score Analysis")

    # ── Score formulas ────────────────────────────────────────
    st.markdown("#### Score Formulas")
    fa, fb, fc, fd = st.columns(4)
    for col, label, formula, color in [
        (fa, "Engagement Score",     "Attendance×0.20 + Logins×0.15 + Time×0.15 + Video×0.15 + Quiz×0.20 + Doubts×0.15", "#7c9eff"),
        (fb, "Learning Effectiveness","(Quiz/100) × (VideoCompletion/100) × 100", "#51cf66"),
        (fc, "Interaction Score",    "Norm(Doubts + Discussions + Events)", "#ffc857"),
        (fd, "Placement Readiness",  "Engagement×0.40 + Effectiveness×0.35 + Interaction×0.25", "#c084fc"),
    ]:
        col.markdown(f"""
        <div class="segment-card" style="border-top:3px solid {color}">
            <b style='color:{color}'>{label}</b><br>
            <code style='font-size:0.72rem;color:#c8cce0'>{formula}</code>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Distributions
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Placement Readiness Score Distribution")
        fig = px.histogram(
            fdf, x="Placement_Readiness", color="Placement_Status",
            color_discrete_map={"Placed": "#51cf66", "Not Placed": "#ff6b6b"},
            nbins=20, barmode="overlay",
        )
        fig.update_layout(**base_layout("", 340))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Score Comparison by College Tier")
        tier_scores = fdf.groupby("College_Tier")[
            ["Engagement_Score", "Learning_Effectiveness", "Interaction_Score", "Placement_Readiness"]
        ].mean().round(1).reset_index()
        fig2 = px.bar(
            tier_scores.melt(id_vars="College_Tier"),
            x="College_Tier", y="value", color="variable",
            barmode="group",
            color_discrete_sequence=PALETTE,
        )
        fig2.update_layout(**base_layout("", 340))
        st.plotly_chart(fig2, use_container_width=True)

    # Heatmap: correlation matrix
    st.markdown("#### Full Correlation Matrix")
    numeric_cols = [
        "Attendance_%", "Login_Frequency", "Time_Spent_Hours",
        "Video_Completion_%", "Avg_Quiz_Score", "Doubts_Raised",
        "Peer_Discussion_Count", "Hackathons_Attended", "Workshops_Attended",
        "Skills_Learned_Count", "Project_Completion_Rate",
        "Engagement_Score", "Learning_Effectiveness",
        "Interaction_Score", "Placement_Readiness",
    ]
    corr_matrix = fdf[numeric_cols].corr().round(2)
    fig3 = px.imshow(
        corr_matrix,
        color_continuous_scale=[[0, "#ff6b6b"], [0.5, "#0d0f1a"], [1, "#51cf66"]],
        zmin=-1, zmax=1,
        text_auto=True,
        aspect="auto",
    )
    fig3.update_layout(**base_layout("", 600))
    st.plotly_chart(fig3, use_container_width=True)

    # Raw data explorer
    st.markdown("#### Raw Data Explorer")
    search_id = st.text_input("Search by Student_ID (partial match)")
    show_df = fdf if not search_id else fdf[fdf["Student_ID"].str.contains(search_id, case=False)]
    st.dataframe(show_df.reset_index(drop=True), use_container_width=True, height=380)
    st.download_button(
        "⬇️ Download Filtered Data as CSV",
        data=show_df.to_csv(index=False),
        file_name="pragyanai_filtered.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#8892b0; font-size:0.85rem; padding:10px 0'>
    🧠 <b>PragyanAI Engagement Intelligence Engine</b> · Tracks behavior → Predicts success → Improves learning → Drives placements<br>
    <span style='font-family:JetBrains Mono, monospace; font-size:0.75rem'>
    ❌ Watching videos ≠ Learning &nbsp;|&nbsp; ✅ Watching + Practicing + Asking + Applying = Real Learning
    </span>
</div>
""", unsafe_allow_html=True)
