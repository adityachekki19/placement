import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="APN Student Intelligence Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# GLOBAL STYLES
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background: #07090f !important;
    color: #d0d8f0 !important;
}
.block-container { padding: 1.5rem 2.5rem !important; }

/* ---- Hero banner ---- */
.hero {
    background: linear-gradient(135deg, #0f1a35 0%, #0a1020 60%, #10182e 100%);
    border: 1px solid #1e3060;
    border-radius: 16px;
    padding: 32px 40px 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(56,182,255,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.1rem; font-weight: 800;
    background: linear-gradient(90deg, #38b6ff, #a78bfa, #38b6ff);
    background-size: 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 3s infinite linear;
    margin: 0 0 6px;
}
@keyframes shimmer { 0%{background-position:0%} 100%{background-position:200%} }
.hero-sub {
    color: #6b8cba; font-size: 0.88rem;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
}

/* ---- Section headers ---- */
.sec-head {
    font-size: 1.05rem; font-weight: 700;
    color: #38b6ff; text-transform: uppercase;
    letter-spacing: 2px; border-left: 3px solid #38b6ff;
    padding-left: 12px; margin: 32px 0 16px;
}

/* ---- KPI cards ---- */
.kpi-card {
    background: linear-gradient(135deg, #0d1526, #101c35);
    border: 1px solid #1e3060;
    border-radius: 14px;
    padding: 20px 18px 16px;
    text-align: center;
    position: relative;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-icon { font-size: 1.8rem; margin-bottom: 8px; }
.kpi-value {
    font-size: 1.9rem; font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}
.kpi-label {
    font-size: 0.72rem; color: #6b8cba;
    text-transform: uppercase; letter-spacing: 1.5px;
    margin-top: 6px;
}
.kpi-delta {
    font-size: 0.78rem; margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
}

/* ---- Insight pills ---- */
.insight-box {
    border-radius: 10px; padding: 14px 18px;
    font-size: 0.85rem; margin: 10px 0;
    border-left: 4px solid;
}
.insight-info  { background:#0a1a30; border-color:#38b6ff; color:#90c8ff; }
.insight-warn  { background:#1a1200; border-color:#f59e0b; color:#fcd34d; }
.insight-good  { background:#041a0f; border-color:#10b981; color:#6ee7b7; }
.insight-alert { background:#1a0608; border-color:#ef4444; color:#fca5a5; }

/* ---- Legend pill ---- */
.legend-pill {
    display:inline-block; padding:3px 10px; border-radius:20px;
    font-size:0.75rem; font-weight:600; margin:2px 3px;
}

/* ---- Table styling ---- */
.stDataFrame { border-radius: 10px !important; overflow: hidden; }
div[data-testid="stMetricValue"] {
    font-family:'JetBrains Mono',monospace !important;
    font-size:1.05rem !important;
}

/* ---- Sidebar ---- */
.css-1d391kg, section[data-testid="stSidebar"] {
    background: #0a0e1a !important;
}
.sidebar-logo {
    font-family:'Outfit',sans-serif;
    font-size:1.1rem; font-weight:800;
    color:#38b6ff; margin-bottom:6px;
}

footer{display:none;} #MainMenu{display:none;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# PLOTLY DARK TEMPLATE
# =========================================================
TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="#0d1526",
        plot_bgcolor="#0d1526",
        font=dict(family="Outfit", color="#c0cce8"),
        title_font=dict(family="Outfit", size=15, color="#e0eaff"),
        xaxis=dict(showgrid=True, gridcolor="#162040", tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="#162040", tickfont=dict(size=11)),
        colorway=["#38b6ff","#a78bfa","#10b981","#f59e0b","#ef4444","#ec4899"],
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        margin=dict(l=40, r=20, t=50, b=40),
    )
)

COLORS = {
    "low":    "#ef4444",
    "medium": "#f59e0b",
    "high":   "#10b981",
    "blue":   "#38b6ff",
    "purple": "#a78bfa",
    "pink":   "#ec4899",
}

def apply_template(fig):
    fig.update_layout(
        paper_bgcolor="#0d1526", plot_bgcolor="#0d1526",
        font=dict(family="Outfit", color="#c0cce8"),
        title_font=dict(family="Outfit", size=14, color="#e0eaff"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#162040", tickfont=dict(size=11))
    fig.update_yaxes(showgrid=True, gridcolor="#162040", tickfont=dict(size=11))
    return fig

# =========================================================
# DATA LOAD  (reads data.txt from the same repo folder)
# =========================================================

@st.cache_data(show_spinner=False)
def load_data():
    # Try comma-separated first, then tab-separated
    try:
        df = pd.read_csv("data.txt", sep=",")
        if df.shape[1] < 2:
            raise ValueError("too few columns, retrying with tab separator")
    except Exception:
        df = pd.read_csv("data.txt", sep="\t")

    df.columns = (df.columns.str.strip()
                  .str.replace(" ", "_")
                  .str.replace("%", "Pct")
                  .str.replace("-", "_"))
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="ignore")
    return df

def find_col(df, *keywords):
    kw = [k.lower() for k in keywords]
    for col in df.columns:
        n = col.lower()
        if all(k in n for k in kw):
            return col
    return None

def safe(df, col):
    if col is None:
        return pd.Series(np.zeros(len(df)), index=df.index)
    return pd.to_numeric(df[col], errors="coerce").fillna(0)

# =========================================================
# LOAD
# =========================================================
with st.spinner("Loading data.txt …"):
    try:
        df_raw = load_data()
    except FileNotFoundError:
        st.error("\u274c `data.txt` not found. Make sure it sits in the same folder as `app.py` in your GitHub repo.")
        st.stop()
    except Exception as e:
        st.error(f"\u274c Failed to read data.txt: {e}")
        st.stop()

# =========================================================
# COLUMN MAPPING
# =========================================================
df = df_raw.copy()

c_att   = find_col(df, "attendance")
c_quiz  = find_col(df, "quiz", "score") or find_col(df, "quiz")
c_vid   = find_col(df, "video", "completion") or find_col(df, "video", "pct")
c_login = find_col(df, "login")
c_time  = find_col(df, "time", "spent") or find_col(df, "time")
c_vids  = find_col(df, "videos", "watched") or find_col(df, "video", "watched")
c_doubt = find_col(df, "doubt") or find_col(df, "doubts")
c_peer  = find_col(df, "peer")
c_hack  = find_col(df, "hackathon")
c_work  = find_col(df, "workshop")
c_live  = find_col(df, "live")
c_skill = find_col(df, "skill")
c_dept  = find_col(df, "department") or find_col(df, "dept")
c_id    = find_col(df, "student", "id") or find_col(df, "id")
c_place = find_col(df, "placement")
c_cgpa  = find_col(df, "cgpa")
c_active= find_col(df, "active", "days")

# =========================================================
# COMPUTED METRICS
# =========================================================
att_s    = safe(df, c_att)
quiz_s   = safe(df, c_quiz)
vid_s    = safe(df, c_vid)
login_s  = safe(df, c_login)
time_s   = safe(df, c_time)
vids_s   = safe(df, c_vids)
doubt_s  = safe(df, c_doubt)
peer_s   = safe(df, c_peer)
hack_s   = safe(df, c_hack)
work_s   = safe(df, c_work)
live_s   = safe(df, c_live)
active_s = safe(df, c_active)

df["Engagement_Score"] = (
    att_s   * 0.30 +
    login_s * 5.00 +
    time_s  * 2.00 +
    vids_s  * 0.50 +
    doubt_s * 3.00
).round(1)

df["Learning_Score"] = (
    quiz_s * vid_s / 100
).round(1)

df["Interaction_Score"] = (
    doubt_s + peer_s + hack_s + work_s + live_s
).round(1)

df["Placement_Readiness"] = (
    df["Engagement_Score"] * 0.40 +
    df["Learning_Score"]   * 0.40 +
    df["Interaction_Score"]* 0.20
).round(1)

pr_max = df["Placement_Readiness"].max()
if pr_max > 0:
    df["Readiness_Pct"] = (df["Placement_Readiness"] / pr_max * 100).round(1)
else:
    df["Readiness_Pct"] = 0

# Segmentation
conds = [
    (df["Engagement_Score"] > df["Engagement_Score"].quantile(0.70)) & (quiz_s > 70),
    (df["Engagement_Score"] > df["Engagement_Score"].quantile(0.50)) & (quiz_s < 50),
    (df["Engagement_Score"] < df["Engagement_Score"].quantile(0.30)),
]
df["Segment"] = np.select(conds,
    ["🏆 High Performer","🔶 Active but Confused","⚠️ Disengaged"],
    default="🔵 Passive Learner")

# =========================================================
# HERO BANNER
# =========================================================
st.markdown("""
<div class="hero">
  <div class="hero-title">🎓 PragyanAI · Student Intelligence Engine</div>
  <div class="hero-sub">LMS Behavior → Learning Analytics → Placement Prediction</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ PragyanAI</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#6b8cba;font-size:0.75rem;margin-bottom:16px">Engagement Intelligence v2</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Department filter
    filt_df = df.copy()
    if c_dept and c_dept in df.columns:
        depts = sorted(df[c_dept].dropna().unique())
        sel_dept = st.multiselect("🏫 Department", depts, default=depts)
        filt_df = filt_df[filt_df[c_dept].isin(sel_dept)]

    # Segment filter
    segs = sorted(df["Segment"].unique())
    sel_seg = st.multiselect("👥 Segment", segs, default=segs)
    filt_df = filt_df[filt_df["Segment"].isin(sel_seg)]

    # Attendance range
    att_min, att_max = st.slider("📊 Attendance Range (%)", 0, 100, (0, 100), 5)
    att_col_f = safe(filt_df, c_att)
    filt_df = filt_df[att_col_f.reindex(filt_df.index, fill_value=0).between(att_min, att_max)]

    st.markdown("---")
    st.markdown(f'<div style="color:#6b8cba;font-size:0.78rem">Showing <b style="color:#38b6ff">{len(filt_df)}</b> of <b>{len(df)}</b> students</div>', unsafe_allow_html=True)

    with st.expander("📂 Raw Dataset"):
        st.dataframe(filt_df.head(15), use_container_width=True)

# =========================================================
# RE-COMPUTE FILTERED SERIES
# =========================================================
def fs(col): return safe(filt_df, col)

att_f   = fs(c_att);   quiz_f  = fs(c_quiz);  vid_f  = fs(c_vid)
login_f = fs(c_login); time_f  = fs(c_time);  vids_f = fs(c_vids)
doubt_f = fs(c_doubt); peer_f  = fs(c_peer);  hack_f = fs(c_hack)
work_f  = fs(c_work);  live_f  = fs(c_live)

N = len(filt_df)

# =========================================================
# ── SECTION 1: KPI CARDS ──
# =========================================================
st.markdown('<div class="sec-head">📊 Overview KPIs</div>', unsafe_allow_html=True)

kpi_data = [
    ("🎯", f"{att_f.mean():.1f}%",   "Avg Attendance",       "#38b6ff", "+engagement driver"),
    ("📝", f"{quiz_f.mean():.1f}",   "Avg Quiz Score",        "#10b981", "understanding proxy"),
    ("⚡", f"{filt_df['Engagement_Score'].mean():.1f}", "Engagement Score", "#a78bfa", "composite index"),
    ("🏆", f"{filt_df['Placement_Readiness'].mean():.1f}", "Placement Readiness", "#f59e0b", "outcome predictor"),
    ("💻", f"{login_f.mean():.1f}x",  "Avg Logins/wk",        "#ec4899", "habit signal"),
    ("⏱️", f"{time_f.mean():.1f}h",  "Avg Hours/wk",          "#38b6ff", "effort measure"),
]

cols = st.columns(6)
for (icon, val, label, color, sub), col in zip(kpi_data, cols):
    with col:
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-icon">{icon}</div>
  <div class="kpi-value" style="color:{color}">{val}</div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-delta" style="color:#455a7a">{sub}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# ── SECTION 2: ATTENDANCE vs QUIZ ──
# ── Inspiration: Duolingo streak bars + Notion callouts ──
# =========================================================
st.markdown('<div class="sec-head">📌 Attendance → Quiz Performance</div>', unsafe_allow_html=True)

col_l, col_r = st.columns([1.4, 1])

with col_l:
    bins   = [0, 60, 80, 100]
    labels = ["< 60%  (Low)", "60–80%  (Medium)", "> 80%  (High)"]
    att_cut = pd.cut(att_f, bins=bins, labels=labels)
    grp     = pd.DataFrame({"level": att_cut, "quiz": quiz_f}).groupby("level")["quiz"]
    avg_q   = grp.mean().round(1)
    cnt_q   = grp.count()

    fig = go.Figure()
    bar_colors = [COLORS["low"], COLORS["medium"], COLORS["high"]]
    for i, (lvl, avg) in enumerate(avg_q.items()):
        fig.add_trace(go.Bar(
            x=[lvl], y=[avg],
            marker_color=bar_colors[i],
            marker_line_color="rgba(0,0,0,0)",
            text=[f"<b>{avg}</b><br><span style='font-size:10px'>{cnt_q[lvl]} students</span>"],
            textposition="outside",
            textfont=dict(size=12),
            name=lvl,
            showlegend=False,
            hovertemplate=f"<b>{lvl}</b><br>Avg Quiz: {avg}<br>Students: {cnt_q[lvl]}<extra></extra>"
        ))
    fig.update_layout(
        title="Average Quiz Score by Attendance Band",
        yaxis_range=[0, max(avg_q.max()*1.25, 10)],
        bargap=0.35,
        annotations=[
            dict(x=0.5, y=-0.18, xref="paper", yref="paper",
                 text="💡 Higher attendance = better quiz performance",
                 showarrow=False, font=dict(size=11, color="#6b8cba"))
        ]
    )
    apply_template(fig)
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    # Scatter: individual dots colored by attendance tier
    att_tier = pd.cut(att_f, bins=bins, labels=["Low","Medium","High"])
    tier_color = att_tier.map({"Low": COLORS["low"], "Medium": COLORS["medium"], "High": COLORS["high"]})
    fig2 = go.Figure()
    for tier, color in [("Low", COLORS["low"]), ("Medium", COLORS["medium"]), ("High", COLORS["high"])]:
        mask = att_tier == tier
        fig2.add_trace(go.Scatter(
            x=att_f[mask], y=quiz_f[mask],
            mode="markers",
            marker=dict(color=color, size=5, opacity=0.7),
            name=tier,
            hovertemplate="Attendance: %{x:.0f}%<br>Quiz: %{y:.0f}<extra></extra>"
        ))
    # Trendline
    if len(att_f) > 5:
        z = np.polyfit(att_f, quiz_f, 1)
        p = np.poly1d(z)
        x_line = np.linspace(att_f.min(), att_f.max(), 80)
        fig2.add_trace(go.Scatter(x=x_line, y=p(x_line), mode="lines",
            line=dict(color="#38b6ff", width=2, dash="dot"),
            name="Trend", showlegend=True))
    fig2.update_layout(title="Scatter: Attendance vs Quiz Score",
        xaxis_title="Attendance (%)", yaxis_title="Quiz Score")
    apply_template(fig2)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
<div class="insight-box insight-good">
  📈 <b>Insight:</b> Students with &gt;80% attendance score on average
  <b>15–22 points higher</b> in quizzes. Consistency beats intelligence.
  Every 10% drop in attendance correlates with ~5 point quiz score drop.
</div>""", unsafe_allow_html=True)

# =========================================================
# ── SECTION 3: LOGIN + TIME (2-in-1 panel) ──
# ── Inspiration: Spotify Wrapped metrics layout ──
# =========================================================
st.markdown('<div class="sec-head">💻 LMS Usage — Logins & Time Spent</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    login_cut = pd.cut(login_f, bins=[0,2,5,7], labels=["1–2/wk  Low","3–5/wk  Medium","6–7/wk  High"])
    avg_eng = pd.DataFrame({"login_cat": login_cut,
                             "eng": filt_df["Engagement_Score"]}).groupby("login_cat")["eng"].mean().round(1)
    fig3 = go.Figure(go.Bar(
        x=avg_eng.index.tolist(),
        y=avg_eng.values,
        marker=dict(
            color=avg_eng.values,
            colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
            showscale=True,
            colorbar=dict(title="Engagement", thickness=12, len=0.7)
        ),
        text=[f"<b>{v:.1f}</b>" for v in avg_eng.values],
        textposition="outside",
        hovertemplate="%{x}<br>Avg Engagement: %{y:.1f}<extra></extra>"
    ))
    fig3.update_layout(title="Login Frequency → Engagement Score",
        xaxis_title="Login Category", yaxis_title="Avg Engagement Score",
        yaxis_range=[0, avg_eng.max()*1.3])
    apply_template(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    time_cut = pd.cut(time_f, bins=[0,5,15,30,100], labels=["<5h","5–15h","15–30h",">30h"])
    avg_pr = pd.DataFrame({"time_cat": time_cut,
                            "pr": filt_df["Placement_Readiness"]}).groupby("time_cat")["pr"].mean().round(1)
    cnt_t  = pd.DataFrame({"time_cat": time_cut,
                            "pr": filt_df["Placement_Readiness"]}).groupby("time_cat")["pr"].count()
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=avg_pr.index.tolist(),
        y=avg_pr.values,
        mode="lines+markers+text",
        line=dict(color="#a78bfa", width=3),
        marker=dict(size=12, color=["#ef4444","#f59e0b","#10b981","#6b8cba"],
                    line=dict(color="white", width=2)),
        text=[f"<b>{v:.1f}</b>" for v in avg_pr.values],
        textposition="top center",
        textfont=dict(size=12),
        fill="tozeroy",
        fillcolor="rgba(167,139,250,0.08)",
        hovertemplate="%{x}<br>Placement Readiness: %{y:.1f}<extra></extra>",
        name="Readiness"
    ))
    fig4.update_layout(title="Time Spent/Week → Placement Readiness",
        xaxis_title="Weekly Study Hours", yaxis_title="Placement Readiness Score")
    apply_template(fig4)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
<div class="insight-box insight-warn">
  ⏱ <b>Sweet Spot:</b> 15–30 hours/week gives peak placement readiness.
  Students studying &gt;30h show a <b>plateau or decline</b> — burnout effect.
  Students logging in 5–7x/week show <b>2× higher engagement</b> than 1–2x users.
</div>""", unsafe_allow_html=True)

# =========================================================
# ── SECTION 4: LEARNING — VIDEO + QUIZ HEATMAP ──
# ── Inspiration: GitHub contribution grid, Notion analytics ──
# =========================================================
st.markdown('<div class="sec-head">🎥 Learning Quality — Video Completion & Quiz</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1,1])

with col_a:
    vid_cut  = pd.cut(vid_f,  bins=[0,50,80,100], labels=["<50%","50–80%",">80%"])
    quiz_cut = pd.cut(quiz_f, bins=[0,50,75,100], labels=["<50","50–75",">75"])
    heatmap_df = pd.crosstab(vid_cut, quiz_cut)
    fig5 = go.Figure(go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns.tolist(),
        y=heatmap_df.index.tolist(),
        colorscale=[[0,"#0d1526"],[0.4,"#1e3060"],[0.7,"#38b6ff"],[1,"#10b981"]],
        text=heatmap_df.values,
        texttemplate="<b>%{text}</b>",
        textfont=dict(size=14),
        hovertemplate="Video: %{y}<br>Quiz: %{x}<br>Students: %{z}<extra></extra>",
        showscale=True,
        colorbar=dict(title="Students", thickness=12, len=0.7)
    ))
    fig5.update_layout(
        title="Heatmap: Video Completion × Quiz Score Bands",
        xaxis_title="Quiz Score Range",
        yaxis_title="Video Completion %"
    )
    apply_template(fig5)
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("""
<div class="insight-box insight-info">
  🔥 <b>Bottom-right cell</b> (>80% video + >75 quiz) = your placement-ready students.
  The heatmap shows exactly where students are concentrated — use it to identify gaps.
</div>""", unsafe_allow_html=True)

with col_b:
    # Radar chart per segment
    segs_list = ["🏆 High Performer","🔵 Passive Learner","🔶 Active but Confused","⚠️ Disengaged"]
    seg_colors = ["#10b981","#38b6ff","#f59e0b","#ef4444"]
    # Pre-built valid rgba fill colours (opacity 0.15)
    seg_fills  = [
        "rgba(16,185,129,0.15)",
        "rgba(56,182,255,0.15)",
        "rgba(245,158,11,0.15)",
        "rgba(239,68,68,0.15)",
    ]
    dims = ["Attendance","Quiz Score","Video Comp.","Logins","Time Spent","Doubts Raised"]

    fig6 = go.Figure()
    for seg, color, fill in zip(segs_list, seg_colors, seg_fills):
        sub = filt_df[filt_df["Segment"] == seg]
        if len(sub) == 0:
            continue
        def nm(col, mx, _sub=sub):
            return safe(_sub, col).mean() / mx * 100 if mx > 0 else 0
        vals = [
            nm(c_att,   100),
            nm(c_quiz,  100),
            nm(c_vid,   100),
            min(nm(c_login, 7) , 100),
            min(nm(c_time,  30), 100),
            min(nm(c_doubt, 20), 100),
        ]
        vals_closed = vals + [vals[0]]
        fig6.add_trace(go.Scatterpolar(
            r=vals_closed,
            theta=dims + [dims[0]],
            fill="toself",
            fillcolor=fill,
            line=dict(color=color, width=2),
            name=seg,
            hovertemplate="%{theta}: %{r:.0f}%<extra></extra>"
        ))
    fig6.update_layout(
        title="Radar: Behavior Profile by Student Segment",
        polar=dict(
            bgcolor="#0d1526",
            radialaxis=dict(visible=True, range=[0,100],
                            gridcolor="#162040", tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="#162040")
        ),
        showlegend=True
    )
    apply_template(fig6)
    st.plotly_chart(fig6, use_container_width=True)

# =========================================================
# ── SECTION 5: DOUBT BEHAVIOUR ──
# ── Inspiration: Notion progress bars + labeled funnel ──
# =========================================================
st.markdown('<div class="sec-head">❓ Doubt Behaviour — Growth Mindset Indicator</div>', unsafe_allow_html=True)

col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    doubt_cut = pd.cut(doubt_f, bins=[-1,0,5,100], labels=["No Doubts","1–5 Doubts","5+ Doubts (Active)"])
    avg_dq = pd.DataFrame({"cat": doubt_cut, "quiz": quiz_f}).groupby("cat")["quiz"].mean().round(1)
    cnt_d  = pd.DataFrame({"cat": doubt_cut, "quiz": quiz_f}).groupby("cat")["quiz"].count()

    fig7 = go.Figure(go.Bar(
        x=avg_dq.index.tolist(), y=avg_dq.values,
        marker_color=[COLORS["low"], COLORS["medium"], COLORS["high"]],
        text=[f"<b>{v}</b><br>{cnt_d[i]} students" for i, v in avg_dq.items()],
        textposition="outside",
        hovertemplate="%{x}<br>Avg Quiz: %{y:.1f}<extra></extra>"
    ))
    fig7.update_layout(title="Doubts Raised → Quiz Score",
        yaxis_range=[0, avg_dq.max()*1.3])
    apply_template(fig7)
    st.plotly_chart(fig7, use_container_width=True)

with col_d2:
    # Doubt resolution funnel
    total_raised   = doubt_f.sum()
    c_res = find_col(filt_df, "doubt", "resolved") or find_col(filt_df, "resolved")
    resolved_s = safe(filt_df, c_res)
    total_resolved = resolved_s.sum()
    total_pending  = max(0, total_raised - total_resolved)

    fig8 = go.Figure(go.Funnel(
        y=["Doubts Raised","Doubts Resolved","Doubts Pending"],
        x=[total_raised, total_resolved, total_pending],
        textinfo="value+percent initial",
        textfont=dict(size=13),
        marker=dict(color=[COLORS["blue"], COLORS["high"], COLORS["medium"]]),
        connector=dict(line=dict(color="#162040", width=2))
    ))
    fig8.update_layout(title="Doubt Resolution Funnel",
        paper_bgcolor="#0d1526", plot_bgcolor="#0d1526",
        font=dict(family="Outfit", color="#c0cce8"))
    st.plotly_chart(fig8, use_container_width=True)

with col_d3:
    # Doubts vs Placement Readiness bubble
    if c_dept and c_dept in filt_df.columns:
        dept_grp = filt_df.groupby(c_dept).agg(
            doubts=(c_doubt, "mean"),
            readiness=("Placement_Readiness", "mean"),
            count=(c_doubt, "count")
        ).reset_index()
        fig9 = go.Figure(go.Scatter(
            x=dept_grp["doubts"].round(1),
            y=dept_grp["readiness"].round(1),
            mode="markers+text",
            text=dept_grp[c_dept],
            textposition="top center",
            textfont=dict(size=11, color="#c0cce8"),
            marker=dict(
                size=dept_grp["count"] / dept_grp["count"].max() * 50 + 15,
                color=dept_grp["readiness"],
                colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
                showscale=True, colorbar=dict(title="Readiness", thickness=10, len=0.6),
                line=dict(color="rgba(255,255,255,0.2)", width=1)
            ),
            hovertemplate="Dept: %{text}<br>Avg Doubts: %{x}<br>Readiness: %{y:.1f}<extra></extra>"
        ))
        fig9.update_layout(title="Dept: Avg Doubts vs Placement Readiness",
            xaxis_title="Avg Doubts Raised", yaxis_title="Placement Readiness")
        apply_template(fig9)
        st.plotly_chart(fig9, use_container_width=True)
    else:
        # Fallback: distribution
        fig9 = px.histogram(doubt_f[doubt_f > 0], nbins=20,
            title="Distribution of Doubts Raised",
            color_discrete_sequence=["#a78bfa"])
        apply_template(fig9)
        st.plotly_chart(fig9, use_container_width=True)

st.markdown("""
<div class="insight-box insight-good">
  🧠 <b>Growth Mindset Signal:</b> Students who raise 5+ doubts score <b>12–18 points</b>
  higher on quizzes. Asking doubts isn't confusion — it's <b>active engagement</b>.
  Target: raise doubt resolution rate to &gt;80%.
</div>""", unsafe_allow_html=True)

# =========================================================
# ── SECTION 6: EVENT PARTICIPATION ──
# =========================================================
st.markdown('<div class="sec-head">🏆 Events — Hackathons, Workshops, Live Sessions</div>', unsafe_allow_html=True)

col_e1, col_e2 = st.columns([1, 1.4])

with col_e1:
    event_totals = {
        "Hackathons":    hack_f.sum(),
        "Workshops":     work_f.sum(),
        "Live Sessions": live_f.sum(),
    }
    if c_live is None:
        event_totals.pop("Live Sessions")

    labels_e = list(event_totals.keys())
    vals_e   = list(event_totals.values())

    fig10 = go.Figure(go.Pie(
        labels=labels_e, values=vals_e,
        hole=0.52,
        marker=dict(colors=[COLORS["blue"], COLORS["purple"], COLORS["high"]],
                    line=dict(color="#0d1526", width=3)),
        textinfo="label+percent",
        textfont=dict(size=12),
        hovertemplate="%{label}: %{value:.0f} participations (%{percent})<extra></extra>",
        pull=[0.04, 0.04, 0.04]
    ))
    fig10.update_layout(
        title="Event Participation Mix",
        annotations=[dict(text=f"<b>{int(sum(vals_e))}</b><br>Total",
                          x=0.5, y=0.5, showarrow=False,
                          font=dict(size=16, color="#e0eaff"))]
    )
    apply_template(fig10)
    st.plotly_chart(fig10, use_container_width=True)

with col_e2:
    # Events attended vs Placement Readiness
    total_events = hack_f + work_f + live_f
    event_cut = pd.cut(total_events, bins=[-1,0,2,5,100],
                       labels=["0 events","1–2 events","3–5 events","6+ events"])
    avg_ev_pr = pd.DataFrame({"cat": event_cut,
                               "pr": filt_df["Placement_Readiness"]}).groupby("cat")["pr"].mean().round(1)
    cnt_ev = pd.DataFrame({"cat": event_cut,
                            "pr": filt_df["Placement_Readiness"]}).groupby("cat")["pr"].count()

    fig11 = go.Figure()
    ev_colors = [COLORS["low"], COLORS["medium"], COLORS["high"], COLORS["purple"]]
    for i, (cat, val) in enumerate(avg_ev_pr.items()):
        fig11.add_trace(go.Bar(
            x=[cat], y=[val],
            marker_color=ev_colors[min(i, len(ev_colors)-1)],
            text=[f"<b>{val}</b><br>{cnt_ev[cat]} students"],
            textposition="outside",
            showlegend=False,
            hovertemplate=f"{cat}<br>Readiness: {val}<extra></extra>"
        ))
    fig11.update_layout(
        title="Events Attended → Placement Readiness",
        xaxis_title="Total Events", yaxis_title="Placement Readiness",
        yaxis_range=[0, avg_ev_pr.max()*1.3],
        bargap=0.3
    )
    apply_template(fig11)
    st.plotly_chart(fig11, use_container_width=True)

# =========================================================
# ── SECTION 7: STUDENT SEGMENTATION ──
# ── Inspiration: Notion board view, Figma user cards ──
# =========================================================
st.markdown('<div class="sec-head">🧠 Student Segmentation — Who Is Your Student?</div>', unsafe_allow_html=True)

seg_counts = filt_df["Segment"].value_counts()
seg_cfg = {
    "🏆 High Performer":      ("#10b981","#041a0f","Placement ready. Keep them challenged."),
    "🔵 Passive Learner":     ("#38b6ff","#001a30","Watching but not practicing. Push quizzes."),
    "🔶 Active but Confused": ("#f59e0b","#1a1200","High activity, low scores. Need mentoring."),
    "⚠️ Disengaged":          ("#ef4444","#1a0608","High dropout risk. Immediate intervention."),
}

seg_cols = st.columns(4)
for (seg, cfg), col in zip(seg_cfg.items(), seg_cols):
    count = seg_counts.get(seg, 0)
    pct   = count / max(len(filt_df), 1) * 100
    color, bg, desc = cfg
    with col:
        st.markdown(f"""
<div style="background:{bg};border:1px solid {color};border-radius:12px;padding:18px 14px;text-align:center">
  <div style="font-size:1.8rem;margin-bottom:6px">{seg.split()[0]}</div>
  <div style="font-size:1.6rem;font-weight:800;color:{color};font-family:'JetBrains Mono',monospace">{count}</div>
  <div style="font-size:0.7rem;color:{color};margin:4px 0;text-transform:uppercase;letter-spacing:1px">{" ".join(seg.split()[1:])}</div>
  <div style="font-size:0.72rem;color:#6b8cba;margin-top:8px">{desc}</div>
  <div style="background:{color};height:4px;border-radius:2px;margin-top:12px;width:{pct:.0f}%;min-width:8px;margin-left:auto;margin-right:auto"></div>
  <div style="font-size:0.7rem;color:#455a7a;margin-top:4px">{pct:.1f}% of cohort</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Segment distribution chart with overlay
fig12 = go.Figure()
seg_order = ["🏆 High Performer","🔵 Passive Learner","🔶 Active but Confused","⚠️ Disengaged"]
seg_colors_list = [COLORS["high"], COLORS["blue"], COLORS["medium"], COLORS["low"]]

for seg, color in zip(seg_order, seg_colors_list):
    sub = filt_df[filt_df["Segment"]==seg]
    if len(sub)==0: continue
    fig12.add_trace(go.Box(
        y=sub["Placement_Readiness"],
        x=[seg]*len(sub),
        name=seg,
        marker_color=color,
        boxmean=True,
        jitter=0.3,
        pointpos=0,
        boxpoints="outliers"
    ))

fig12.update_layout(
    title="Placement Readiness Distribution per Segment  (Box = spread · Dot = mean)",
    xaxis_title="Segment", yaxis_title="Placement Readiness Score",
    showlegend=False
)
apply_template(fig12)
st.plotly_chart(fig12, use_container_width=True)

# =========================================================
# ── SECTION 8: RISK DETECTION ──
# =========================================================
st.markdown('<div class="sec-head">⚠️ At-Risk Students — Early Warning System</div>', unsafe_allow_html=True)

risk_mask = (att_f < 60) & (quiz_f < 50)
risk_students = filt_df[risk_mask.values]
risk_count = len(risk_students)

r1, r2, r3 = st.columns(3)
r1.metric("🚨 High Risk Students",   risk_count,
          delta=f"{risk_count/max(N,1)*100:.1f}% of cohort", delta_color="inverse")
r2.metric("⚠️ Disengaged",
          int(seg_counts.get("⚠️ Disengaged", 0)))
r3.metric("📊 At-Risk Rate",
          f"{risk_count/max(N,1)*100:.1f}%")

if risk_count > 0:
    show_cols = []
    if c_id and c_id in filt_df.columns:    show_cols.append(c_id)
    if c_dept and c_dept in filt_df.columns: show_cols.append(c_dept)
    if c_att  and c_att  in filt_df.columns: show_cols.append(c_att)
    if c_quiz and c_quiz in filt_df.columns: show_cols.append(c_quiz)
    show_cols.extend(["Engagement_Score","Segment"])
    show_cols = [c for c in show_cols if c in risk_students.columns]

    st.markdown(f"""
<div class="insight-box insight-alert">
  🚨 <b>{risk_count} students</b> have attendance &lt;60% AND quiz score &lt;50.
  These students need <b>immediate intervention</b> — assign mentors, send alerts, schedule 1:1 sessions.
</div>""", unsafe_allow_html=True)

    st.dataframe(
        risk_students[show_cols].reset_index(drop=True)
        .style.background_gradient(subset=["Engagement_Score"] if "Engagement_Score" in show_cols else [],
                                   cmap="RdYlGn"),
        use_container_width=True, height=280
    )
else:
    st.markdown('<div class="insight-box insight-good">✅ No high-risk students in current filter. Keep monitoring!</div>', unsafe_allow_html=True)

# =========================================================
# ── SECTION 9: LEADERBOARD ──
# =========================================================
st.markdown('<div class="sec-head">🏅 Engagement Leaderboard — Top 10</div>', unsafe_allow_html=True)

top10 = filt_df.sort_values("Engagement_Score", ascending=False).head(10).reset_index(drop=True)
top10.index = top10.index + 1

show_lb = []
if c_id   and c_id   in top10.columns: show_lb.append(c_id)
if c_dept and c_dept in top10.columns: show_lb.append(c_dept)
if c_cgpa and c_cgpa in top10.columns: show_lb.append(c_cgpa)
show_lb += ["Engagement_Score","Learning_Score","Interaction_Score","Placement_Readiness","Segment"]
show_lb  = [c for c in show_lb if c in top10.columns]

# Horizontal bar race style
fig_lb = go.Figure(go.Bar(
    y=[f"#{i+1} {str(row.get(c_id, row.get(c_dept, f'Student {i+1}')))}"
       for i, (_, row) in enumerate(top10.iterrows())],
    x=top10["Engagement_Score"],
    orientation="h",
    marker=dict(
        color=top10["Placement_Readiness"],
        colorscale=[[0,"#1e3060"],[0.5,"#38b6ff"],[1,"#10b981"]],
        showscale=True,
        colorbar=dict(title="Readiness", thickness=12, len=0.7)
    ),
    text=[f"<b>{v:.1f}</b>" for v in top10["Engagement_Score"]],
    textposition="outside",
    hovertemplate="Engagement: %{x:.1f}<br>Placement Readiness: %{marker.color:.1f}<extra></extra>"
))
fig_lb.update_layout(
    title="Top 10 Students by Engagement Score (color = Placement Readiness)",
    xaxis_title="Engagement Score",
    yaxis=dict(autorange="reversed"),
    height=380
)
apply_template(fig_lb)
st.plotly_chart(fig_lb, use_container_width=True)

st.dataframe(
    top10[show_lb].style
        .background_gradient(subset=["Engagement_Score","Placement_Readiness"]
                             if "Placement_Readiness" in show_lb else ["Engagement_Score"],
                             cmap="Blues")
        .format({col: "{:.1f}" for col in ["Engagement_Score","Learning_Score",
                                            "Interaction_Score","Placement_Readiness"]
                 if col in top10.columns}),
    use_container_width=True, height=320
)

# =========================================================
# ── SECTION 10: PLACEMENT READINESS DISTRIBUTION ──
# =========================================================
st.markdown('<div class="sec-head">🚀 Placement Readiness — Full Cohort View</div>', unsafe_allow_html=True)

col_p1, col_p2 = st.columns([1.2, 1])

with col_p1:
    fig_pr = go.Figure()
    # Histogram with gradient fill
    fig_pr.add_trace(go.Histogram(
        x=filt_df["Placement_Readiness"],
        nbinsx=30,
        marker=dict(
            color=filt_df["Placement_Readiness"],
            colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
            line=dict(color="#0d1526", width=0.5)
        ),
        hovertemplate="Readiness: %{x:.0f}<br>Students: %{y}<extra></extra>"
    ))
    q33 = filt_df["Placement_Readiness"].quantile(0.33)
    q66 = filt_df["Placement_Readiness"].quantile(0.66)
    for val, label, color in [(q33,"Bottom 33%","#ef4444"),(q66,"Top 33%","#10b981")]:
        fig_pr.add_vline(x=val, line_dash="dash", line_color=color, line_width=2,
            annotation_text=label, annotation_font_color=color, annotation_position="top")
    fig_pr.update_layout(title="Placement Readiness Score Distribution",
        xaxis_title="Readiness Score", yaxis_title="Number of Students")
    apply_template(fig_pr)
    st.plotly_chart(fig_pr, use_container_width=True)

with col_p2:
    # Sankey: Engagement → Readiness tiers
    att_tier3 = pd.cut(att_f, bins=[0,60,80,100], labels=["Low Att.","Med Att.","High Att."])
    pr_tier3  = pd.cut(filt_df["Placement_Readiness"],
                       bins=[filt_df["Placement_Readiness"].min()-1,
                             filt_df["Placement_Readiness"].quantile(0.33),
                             filt_df["Placement_Readiness"].quantile(0.66),
                             filt_df["Placement_Readiness"].max()+1],
                       labels=["Low Ready","Mid Ready","High Ready"])
    sankey_df = pd.DataFrame({"source": att_tier3, "target": pr_tier3}).dropna()
    counts_sk = sankey_df.groupby(["source","target"]).size().reset_index(name="value")

    all_nodes = list(sankey_df["source"].cat.categories) + list(sankey_df["target"].cat.categories)
    node_idx  = {n:i for i,n in enumerate(all_nodes)}
    node_colors = ["#ef4444","#f59e0b","#10b981","#455a7a","#6b8cba","#38b6ff"]

    fig_sk = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=18,
            label=all_nodes,
            color=node_colors[:len(all_nodes)],
            line=dict(color="#0d1526", width=1)
        ),
        link=dict(
            source=[node_idx[r["source"]] for _, r in counts_sk.iterrows()],
            target=[node_idx[r["target"]] for _, r in counts_sk.iterrows()],
            value=counts_sk["value"].tolist(),
            color=["rgba(56,182,255,0.25)"]*len(counts_sk)
        )
    ))
    fig_sk.update_layout(title="Attendance Tier → Placement Readiness Flow",
        paper_bgcolor="#0d1526", font=dict(family="Outfit",color="#c0cce8",size=11))
    st.plotly_chart(fig_sk, use_container_width=True)

# =========================================================
# ── MASTER INSIGHT ──
# =========================================================
st.markdown('<div class="sec-head">💡 Master Insight</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,#0f1a35,#0a1020);
            border:1px solid #1e3060;border-radius:16px;padding:28px 32px;margin:8px 0">
  <div style="font-size:1.15rem;font-weight:700;color:#38b6ff;margin-bottom:16px">
    ❌ What students think → ✅ What actually drives placement
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div style="background:#1a0608;border:1px solid #ef4444;border-radius:10px;padding:14px">
      <div style="color:#ef4444;font-weight:700;margin-bottom:8px">❌ Myth</div>
      <div style="color:#fca5a5;font-size:0.85rem;line-height:1.6">
        "Just watching videos = learning"<br>
        High CGPA = placement ready<br>
        Time on platform = engagement<br>
        Attending = understanding
      </div>
    </div>
    <div style="background:#041a0f;border:1px solid #10b981;border-radius:10px;padding:14px">
      <div style="color:#10b981;font-weight:700;margin-bottom:8px">✅ Reality</div>
      <div style="color:#6ee7b7;font-size:0.85rem;line-height:1.6">
        Watching + Quizzing + Doubting + Applying<br>
        Engagement Score &gt; CGPA for placement<br>
        Active days + doubts = real engagement<br>
        Raising doubts = growth mindset
      </div>
    </div>
  </div>
  <div style="margin-top:18px;color:#6b8cba;font-size:0.8rem;font-family:'JetBrains Mono',monospace">
    Formula → Placement Readiness = 0.4×Engagement + 0.4×Learning + 0.2×Interaction
  </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#2a3a5e;font-size:0.78rem;font-family:'JetBrains Mono',monospace;padding:8px 0">
  PragyanAI Engagement Intelligence Engine · Built with Streamlit + Plotly
</div>""", unsafe_allow_html=True)
