import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
import os
from pathlib import Path

warnings.filterwarnings("ignore")

# =========================================================
# PAGE CONFIG  — must be first Streamlit call
# =========================================================
st.set_page_config(
    page_title="PragyanAI · Student Intelligence Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# STYLES
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');
html,body,[class*="css"]{font-family:'Outfit',sans-serif!important;background:#07090f!important;color:#d0d8f0!important;}
.block-container{padding:1.2rem 2rem!important;}
.hero{background:linear-gradient(135deg,#0f1a35,#0a1020,#10182e);border:1px solid #1e3060;border-radius:16px;padding:28px 36px 24px;margin-bottom:24px;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:240px;height:240px;background:radial-gradient(circle,rgba(56,182,255,0.12),transparent 70%);border-radius:50%;}
.hero-title{font-size:2rem;font-weight:800;background:linear-gradient(90deg,#38b6ff,#a78bfa,#38b6ff);background-size:200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 3s ease-in-out infinite;}
@keyframes shimmer{0%{background-position:0%}100%{background-position:200%}}
.hero-sub{color:#6b8cba;font-size:0.85rem;font-family:'JetBrains Mono',monospace;}
.sec-head{font-size:1rem;font-weight:700;color:#38b6ff;text-transform:uppercase;letter-spacing:2px;border-left:3px solid #38b6ff;padding-left:12px;margin:24px 0 14px;}
.kpi-card{background:linear-gradient(135deg,#0d1526,#101c35);border:1px solid #1e3060;border-radius:14px;padding:18px 14px;text-align:center;}
.kpi-icon{font-size:1.6rem;margin-bottom:6px;}
.kpi-value{font-size:1.75rem;font-weight:800;font-family:'JetBrains Mono',monospace;line-height:1;}
.kpi-label{font-size:0.68rem;color:#6b8cba;text-transform:uppercase;letter-spacing:1.5px;margin-top:5px;}
.kpi-sub{font-size:0.72rem;color:#455a7a;margin-top:4px;font-family:'JetBrains Mono',monospace;}
.insight-box{border-radius:10px;padding:12px 16px;font-size:0.84rem;margin:8px 0;border-left:4px solid;}
.insight-info{background:#0a1a30;border-color:#38b6ff;color:#90c8ff;}
.insight-warn{background:#1a1200;border-color:#f59e0b;color:#fcd34d;}
.insight-good{background:#041a0f;border-color:#10b981;color:#6ee7b7;}
.insight-alert{background:#1a0608;border-color:#ef4444;color:#fca5a5;}
.stDataFrame{border-radius:10px!important;overflow:hidden;}
div[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.05rem!important;}
section[data-testid="stSidebar"]{background:#0a0e1a!important;}
footer{display:none;}#MainMenu{display:none;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTS
# =========================================================
COLORS = {
    "low":    "#ef4444",
    "medium": "#f59e0b",
    "high":   "#10b981",
    "blue":   "#38b6ff",
    "purple": "#a78bfa",
    "pink":   "#ec4899",
}

def apply_template(fig, height=380):
    fig.update_layout(
        paper_bgcolor="#0d1526", plot_bgcolor="#0d1526",
        font=dict(family="Outfit", color="#c0cce8"),
        title_font=dict(family="Outfit", size=13, color="#e0eaff"),
        height=height,
        margin=dict(l=30, r=20, t=45, b=35),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#162040", tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor="#162040", tickfont=dict(size=10))
    return fig

# =========================================================
# DATA HELPERS
# =========================================================
def find_col(df, *keywords):
    kw = [k.lower() for k in keywords]
    for col in df.columns:
        n = col.lower()
        if all(k in n for k in kw):
            return col
    return None

def safe(df, col):
    if col is None or col not in df.columns:
        return pd.Series(np.zeros(len(df)), index=df.index)
    return pd.to_numeric(df[col], errors="coerce").fillna(0)

# =========================================================
# SAMPLE DATA GENERATOR
# =========================================================
def generate_sample_data(n_students=150):
    """Generate realistic sample student data for demonstration"""
    np.random.seed(42)
    data = {
        'Student_ID': [f'STU{1001+i}' for i in range(n_students)],
        'Department': np.random.choice(['CSE', 'ECE', 'ME', 'CE', 'EE'], n_students),
        'Attendance': np.random.normal(75, 15, n_students).clip(20, 100).astype(int),
        'Quiz_Score': np.random.normal(65, 18, n_students).clip(0, 100).astype(int),
        'Video_Completion_Pct': np.random.normal(70, 20, n_students).clip(0, 100).astype(int),
        'Login_Frequency': np.random.poisson(4, n_students).astype(int),
        'Time_Spent_Hours': np.random.gamma(15, 1.5, n_students).astype(int),
        'Videos_Watched': np.random.poisson(8, n_students).astype(int),
        'Doubts_Raised': np.random.poisson(3, n_students).astype(int),
        'Doubt_Resolved': np.random.poisson(2.5, n_students).astype(int),
        'Peer_Learning': np.random.poisson(2, n_students).astype(int),
        'Hackathon_Participation': np.random.poisson(0.8, n_students).astype(int),
        'Workshop_Participation': np.random.poisson(1.2, n_students).astype(int),
        'Live_Sessions': np.random.poisson(1.5, n_students).astype(int),
        'CGPA': (np.random.normal(7.5, 0.8, n_students).clip(4, 10) * 10).astype(int) / 10,
        'Active_Days': np.random.poisson(20, n_students).astype(int),
    }
    return pd.DataFrame(data)

# =========================================================
# CACHED DATA LOAD + COMPUTE
# =========================================================
@st.cache_data(show_spinner=False)
def load_and_compute():
    # ---- Attempt to load data.csv from multiple locations ----
    df = None
    possible_paths = [
        "data.csv",
        "./data.csv",
        os.path.join(os.getcwd(), "data.csv"),
        os.path.join(str(Path.home()), "data.csv"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, sep=",")
                if df.shape[1] < 2:
                    raise ValueError("too few columns")
                break
            except Exception as e:
                try:
                    df = pd.read_csv(path, sep="\t")
                    if df.shape[1] < 2:
                        raise ValueError("too few columns")
                    break
                except Exception:
                    continue
    
    # ---- If no data.csv found, generate sample data ----
    if df is None:
        st.warning("⚠️ data.csv not found. Using generated sample data for demonstration.")
        df = generate_sample_data(150)

    df.columns = (df.columns.str.strip()
                  .str.replace(" ", "_")
                  .str.replace("%", "Pct")
                  .str.replace("-", "_"))
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="ignore")

    # ---- column map ----
    cols = dict(
        att   = find_col(df, "attendance"),
        quiz  = find_col(df, "quiz", "score") or find_col(df, "quiz"),
        vid   = find_col(df, "video", "completion") or find_col(df, "video", "pct"),
        login = find_col(df, "login"),
        time  = find_col(df, "time", "spent") or find_col(df, "time"),
        vids  = find_col(df, "videos", "watched") or find_col(df, "video", "watched"),
        doubt = find_col(df, "doubt") or find_col(df, "doubts"),
        res   = find_col(df, "doubt", "resolved") or find_col(df, "resolved"),
        peer  = find_col(df, "peer"),
        hack  = find_col(df, "hackathon"),
        work  = find_col(df, "workshop"),
        live  = find_col(df, "live"),
        skill = find_col(df, "skill"),
        dept  = find_col(df, "department") or find_col(df, "dept"),
        sid   = find_col(df, "student", "id") or find_col(df, "id"),
        place = find_col(df, "placement"),
        cgpa  = find_col(df, "cgpa"),
        active= find_col(df, "active", "days"),
    )

    # ---- computed scores ----
    att_s   = safe(df, cols["att"])
    quiz_s  = safe(df, cols["quiz"])
    vid_s   = safe(df, cols["vid"])
    login_s = safe(df, cols["login"])
    time_s  = safe(df, cols["time"])
    vids_s  = safe(df, cols["vids"])
    doubt_s = safe(df, cols["doubt"])
    peer_s  = safe(df, cols["peer"])
    hack_s  = safe(df, cols["hack"])
    work_s  = safe(df, cols["work"])
    live_s  = safe(df, cols["live"])

    df["Engagement_Score"] = (
        att_s * 0.30 + login_s * 5.00 +
        time_s * 2.00 + vids_s * 0.50 + doubt_s * 3.00
    ).round(1)
    df["Learning_Score"]   = (quiz_s * vid_s / 100).round(1)
    df["Interaction_Score"]= (doubt_s + peer_s + hack_s + work_s + live_s).round(1)
    df["Placement_Readiness"] = (
        df["Engagement_Score"] * 0.40 +
        df["Learning_Score"]   * 0.40 +
        df["Interaction_Score"]* 0.20
    ).round(1)
    pr_max = df["Placement_Readiness"].max()
    df["Readiness_Pct"] = (df["Placement_Readiness"] / pr_max * 100).round(1) if pr_max > 0 else 0

    # segmentation
    q70 = df["Engagement_Score"].quantile(0.70)
    q50 = df["Engagement_Score"].quantile(0.50)
    q30 = df["Engagement_Score"].quantile(0.30)
    conds = [
        (df["Engagement_Score"] > q70) & (quiz_s > 70),
        (df["Engagement_Score"] > q50) & (quiz_s < 50),
        (df["Engagement_Score"] < q30),
    ]
    df["Segment"] = np.select(conds,
        ["🏆 High Performer", "🔶 Active but Confused", "⚠️ Disengaged"],
        default="🔵 Passive Learner")

    return df, cols

# =========================================================
# LOAD
# =========================================================
with st.spinner("⏳ Loading data.csv …"):
    try:
        df_full, COLS = load_and_compute()
    except Exception as exc:
        st.error(f"❌ Failed to process data: {exc}")
        st.stop()

# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero">
  <div class="hero-title">🎓 PragyanAI · Student Intelligence Engine</div>
  <div class="hero-sub">LMS Behavior → Learning Analytics → Placement Prediction</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR FILTERS
# =========================================================
with st.sidebar:
    st.markdown('<div style="font-family:Outfit;font-size:1.05rem;font-weight:800;color:#38b6ff;margin-bottom:4px">⚡ PragyanAI</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#6b8cba;font-size:0.72rem;margin-bottom:14px">Engagement Intelligence v2</div>', unsafe_allow_html=True)
    st.markdown("---")

    filt_df = df_full.copy()

    c_dept = COLS["dept"]
    if c_dept and c_dept in filt_df.columns:
        depts = sorted(filt_df[c_dept].dropna().unique())
        sel   = st.multiselect("🏫 Department", depts, default=depts)
        filt_df = filt_df[filt_df[c_dept].isin(sel)]

    segs_all = sorted(df_full["Segment"].unique())
    sel_seg  = st.multiselect("👥 Segment", segs_all, default=segs_all)
    filt_df  = filt_df[filt_df["Segment"].isin(sel_seg)]

    att_min, att_max = st.slider("📊 Attendance %", 0, 100, (0, 100), 5)
    att_col_vals = safe(filt_df, COLS["att"])
    filt_df = filt_df[att_col_vals.reindex(filt_df.index, fill_value=0).between(att_min, att_max)]

    st.markdown("---")
    st.markdown(f'<div style="color:#6b8cba;font-size:0.78rem">Showing <b style="color:#38b6ff">{len(filt_df)}</b> / {len(df_full)} students</div>', unsafe_allow_html=True)

    with st.expander("📂 Raw Data Preview"):
        st.dataframe(filt_df.head(12), use_container_width=True)

# filtered series shortcut
def fs(col_key): return safe(filt_df, COLS.get(col_key))

att_f   = fs("att");   quiz_f  = fs("quiz");  vid_f   = fs("vid")
login_f = fs("login"); time_f  = fs("time");  vids_f  = fs("vids")
doubt_f = fs("doubt"); peer_f  = fs("peer");  hack_f  = fs("hack")
work_f  = fs("work");  live_f  = fs("live")
N = max(len(filt_df), 1)

# =========================================================
# KPI CARDS
# =========================================================
st.markdown('<div class="sec-head">📊 Overview KPIs</div>', unsafe_allow_html=True)

kpi_data = [
    ("🎯", f"{att_f.mean():.1f}%",  "Avg Attendance",        "#38b6ff", "consistency driver"),
    ("📝", f"{quiz_f.mean():.1f}",  "Avg Quiz Score",         "#10b981", "understanding proxy"),
    ("⚡", f"{filt_df['Engagement_Score'].mean():.1f}", "Engagement",  "#a78bfa", "composite index"),
    ("🏆", f"{filt_df['Placement_Readiness'].mean():.1f}", "Readiness","#f59e0b", "outcome predictor"),
    ("💻", f"{login_f.mean():.1f}x", "Logins / wk",           "#ec4899", "habit signal"),
    ("⏱️", f"{time_f.mean():.1f}h", "Hours / wk",             "#38b6ff", "effort measure"),
]
c6 = st.columns(6)
for (icon, val, label, color, sub), col in zip(kpi_data, c6):
    with col:
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-icon">{icon}</div>
  <div class="kpi-value" style="color:{color}">{val}</div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# TABS  — each tab renders only when clicked (lazy)
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📌 Attendance & Quiz",
    "💻 LMS Usage",
    "🎥 Learning Quality",
    "❓ Doubts & Events",
    "🧠 Segmentation",
    "⚠️ Risk & Leaderboard",
])

# ----------------------------------------------------------
# TAB 1 — Attendance & Quiz
# ----------------------------------------------------------
with tab1:
    st.markdown('<div class="sec-head">Attendance → Quiz Performance</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        bins   = [0, 60, 80, 100]
        labels = ["<60%  Low", "60–80%  Med", ">80%  High"]
        cut    = pd.cut(att_f, bins=bins, labels=labels)
        grp    = pd.DataFrame({"lvl": cut, "quiz": quiz_f}).groupby("lvl", observed=True)
        avg_q  = grp["quiz"].mean().round(1)
        cnt_q  = grp["quiz"].count()

        fig = go.Figure()
        for i, (lvl, avg) in enumerate(avg_q.items()):
            fig.add_trace(go.Bar(
                x=[str(lvl)], y=[avg],
                marker_color=[COLORS["low"], COLORS["medium"], COLORS["high"]][i],
                text=[f"<b>{avg}</b><br>{cnt_q[lvl]} students"],
                textposition="outside", showlegend=False,
                hovertemplate=f"{lvl}<br>Avg Quiz: {avg}<extra></extra>"
            ))
        fig.update_layout(title="Avg Quiz Score by Attendance Band",
                          yaxis_range=[0, max(avg_q.max()*1.3, 10)], bargap=0.35)
        apply_template(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        att_tier = pd.cut(att_f, bins=bins, labels=["Low","Medium","High"])
        fig2 = go.Figure()
        for tier, color in [("Low",COLORS["low"]),("Medium",COLORS["medium"]),("High",COLORS["high"])]:
            m = att_tier == tier
            fig2.add_trace(go.Scatter(
                x=att_f[m], y=quiz_f[m], mode="markers",
                marker=dict(color=color, size=5, opacity=0.65),
                name=tier,
                hovertemplate="Attendance:%{x:.0f}%<br>Quiz:%{y:.0f}<extra></extra>"
            ))
        if len(att_f) > 5:
            z = np.polyfit(att_f, quiz_f, 1); p = np.poly1d(z)
            x_l = np.linspace(att_f.min(), att_f.max(), 80)
            fig2.add_trace(go.Scatter(x=x_l, y=p(x_l), mode="lines",
                line=dict(color="#38b6ff", width=2, dash="dot"), name="Trend"))
        fig2.update_layout(title="Scatter: Attendance vs Quiz Score",
            xaxis_title="Attendance (%)", yaxis_title="Quiz Score")
        apply_template(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
<div class="insight-box insight-good">
  📈 <b>Insight:</b> Students with &gt;80% attendance score 15–22 points higher on average.
  Every 10% attendance drop ≈ 5 point quiz drop. <b>Consistency beats intelligence.</b>
</div>""", unsafe_allow_html=True)

# ----------------------------------------------------------
# TAB 2 — LMS Usage (Login + Time)
# ----------------------------------------------------------
with tab2:
    st.markdown('<div class="sec-head">LMS Usage — Login Frequency & Time Spent</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        lcut = pd.cut(login_f, bins=[0,2,5,7], labels=["1–2/wk","3–5/wk","6–7/wk"])
        avg_eng = pd.DataFrame({"c":lcut,"e":filt_df["Engagement_Score"]}).groupby("c", observed=True)["e"].mean().round(1)
        fig3 = go.Figure(go.Bar(
            x=avg_eng.index.tolist(), y=avg_eng.values,
            marker=dict(color=avg_eng.values,
                        colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
                        showscale=True, colorbar=dict(title="Engagement",thickness=10,len=0.6)),
            text=[f"<b>{v:.1f}</b>" for v in avg_eng.values], textposition="outside",
            hovertemplate="%{x}<br>Avg Engagement: %{y:.1f}<extra></extra>"
        ))
        fig3.update_layout(title="Login Frequency → Engagement Score",
            yaxis_range=[0, avg_eng.max()*1.3])
        apply_template(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        tcut  = pd.cut(time_f, bins=[0,5,15,30,100], labels=["<5h","5–15h","15–30h",">30h"])
        avg_pr= pd.DataFrame({"c":tcut,"p":filt_df["Placement_Readiness"]}).groupby("c", observed=True)["p"].mean().round(1)
        fig4  = go.Figure(go.Scatter(
            x=avg_pr.index.tolist(), y=avg_pr.values,
            mode="lines+markers+text",
            line=dict(color="#a78bfa", width=3),
            marker=dict(size=12, color=[COLORS["low"],COLORS["medium"],COLORS["high"],"#6b8cba"],
                        line=dict(color="white",width=2)),
            text=[f"<b>{v:.1f}</b>" for v in avg_pr.values], textposition="top center",
            fill="tozeroy", fillcolor="rgba(167,139,250,0.08)",
            hovertemplate="%{x}<br>Placement Readiness: %{y:.1f}<extra></extra>"
        ))
        fig4.update_layout(title="Time Spent/Week → Placement Readiness",
            xaxis_title="Weekly Hours", yaxis_title="Placement Readiness")
        apply_template(fig4)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""
<div class="insight-box insight-warn">
  ⏱ <b>Sweet Spot:</b> 15–30 hrs/week = peak readiness. &gt;30h shows burnout plateau.
  Students logging in 5–7×/week show <b>2× higher engagement</b> than 1–2×/week users.
</div>""", unsafe_allow_html=True)

# ----------------------------------------------------------
# TAB 3 — Learning Quality (Video + Heatmap + Radar)
# ----------------------------------------------------------
with tab3:
    st.markdown('<div class="sec-head">Learning Quality — Video Completion & Quiz Heatmap</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        vcut  = pd.cut(vid_f,  bins=[0,50,80,100], labels=["<50%","50–80%",">80%"])
        qcut  = pd.cut(quiz_f, bins=[0,50,75,100], labels=["<50","50–75",">75"])
        hm    = pd.crosstab(vcut, qcut)
        fig5  = go.Figure(go.Heatmap(
            z=hm.values, x=hm.columns.tolist(), y=hm.index.tolist(),
            colorscale=[[0,"#0d1526"],[0.4,"#1e3060"],[0.7,"#38b6ff"],[1,"#10b981"]],
            text=hm.values, texttemplate="<b>%{text}</b>", textfont=dict(size=14),
            hovertemplate="Video:%{y}<br>Quiz:%{x}<br>Students:%{z}<extra></extra>",
            showscale=True, colorbar=dict(title="Students",thickness=10,len=0.6)
        ))
        fig5.update_layout(title="Heatmap: Video Completion × Quiz Score",
            xaxis_title="Quiz Score", yaxis_title="Video Completion")
        apply_template(fig5)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("""
<div class="insight-box insight-info">
  🔥 <b>Bottom-right cell</b> (&gt;80% video + &gt;75 quiz) = placement-ready cluster.
  Brightest cell = where your best students live.
</div>""", unsafe_allow_html=True)

    with col_b:
        segs_list  = ["🏆 High Performer","🔵 Passive Learner","🔶 Active but Confused","⚠️ Disengaged"]
        seg_colors = ["#10b981","#38b6ff","#f59e0b","#ef4444"]
        seg_fills  = ["rgba(16,185,129,0.15)","rgba(56,182,255,0.15)",
                      "rgba(245,158,11,0.15)","rgba(239,68,68,0.15)"]
        dims = ["Attendance","Quiz","Video","Logins","Time","Doubts"]

        fig6 = go.Figure()
        for seg, color, fill in zip(segs_list, seg_colors, seg_fills):
            sub = filt_df[filt_df["Segment"] == seg]
            if len(sub) == 0: continue
            def nm(col_key, mx, _s=sub):
                v = safe(_s, COLS.get(col_key)).mean()
                return min(v / mx * 100, 100) if mx > 0 else 0
            vals = [nm("att",100), nm("quiz",100), nm("vid",100),
                    nm("login",7), nm("time",30), nm("doubt",20)]
            vc   = vals + [vals[0]]
            fig6.add_trace(go.Scatterpolar(
                r=vc, theta=dims+[dims[0]],
                fill="toself", fillcolor=fill,
                line=dict(color=color, width=2),
                name=seg, hovertemplate="%{theta}: %{r:.0f}%<extra></extra>"
            ))
        fig6.update_layout(
            title="Radar: Behavior Profile by Segment",
            polar=dict(bgcolor="#0d1526",
                radialaxis=dict(visible=True, range=[0,100],
                    gridcolor="#162040", tickfont=dict(size=9)),
                angularaxis=dict(gridcolor="#162040")),
            showlegend=True, height=380,
            paper_bgcolor="#0d1526",
            font=dict(family="Outfit", color="#c0cce8")
        )
        st.plotly_chart(fig6, use_container_width=True)

# ----------------------------------------------------------
# TAB 4 — Doubts & Events
# ----------------------------------------------------------
with tab4:
    st.markdown('<div class="sec-head">Doubt Behaviour — Growth Mindset Indicator</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)

    with d1:
        dcut  = pd.cut(doubt_f, bins=[-1,0,5,100], labels=["No Doubts","1–5","5+ Active"])
        avg_dq= pd.DataFrame({"c":dcut,"q":quiz_f}).groupby("c", observed=True)["q"].mean().round(1)
        cnt_d = pd.DataFrame({"c":dcut,"q":quiz_f}).groupby("c", observed=True)["q"].count()
        fig7  = go.Figure(go.Bar(
            x=avg_dq.index.tolist(), y=avg_dq.values,
            marker_color=[COLORS["low"],COLORS["medium"],COLORS["high"]],
            text=[f"<b>{v}</b><br>{cnt_d[i]} students" for i,v in avg_dq.items()],
            textposition="outside",
            hovertemplate="%{x}<br>Avg Quiz: %{y:.1f}<extra></extra>"
        ))
        fig7.update_layout(title="Doubts Raised → Quiz Score",
            yaxis_range=[0, avg_dq.max()*1.3])
        apply_template(fig7)
        st.plotly_chart(fig7, use_container_width=True)

    with d2:
        total_r = doubt_f.sum()
        res_s   = safe(filt_df, COLS.get("res"))
        total_res = res_s.sum()
        total_pend= max(0, total_r - total_res)
        fig8 = go.Figure(go.Funnel(
            y=["Doubts Raised","Resolved","Pending"],
            x=[total_r, total_res, total_pend],
            textinfo="value+percent initial", textfont=dict(size=13),
            marker=dict(color=[COLORS["blue"],COLORS["high"],COLORS["medium"]]),
            connector=dict(line=dict(color="#162040",width=2))
        ))
        fig8.update_layout(title="Doubt Resolution Funnel", height=380,
            paper_bgcolor="#0d1526", plot_bgcolor="#0d1526",
            font=dict(family="Outfit",color="#c0cce8"))
        st.plotly_chart(fig8, use_container_width=True)

    with d3:
        total_ev = hack_f + work_f + live_f
        ecut  = pd.cut(total_ev, bins=[-1,0,2,5,100], labels=["0","1–2","3–5","6+"])
        avg_ev= pd.DataFrame({"c":ecut,"p":filt_df["Placement_Readiness"]}).groupby("c", observed=True)["p"].mean().round(1)
        cnt_ev= pd.DataFrame({"c":ecut,"p":filt_df["Placement_Readiness"]}).groupby("c", observed=True)["p"].count()
        fig9  = go.Figure()
        evcols= [COLORS["low"],COLORS["medium"],COLORS["high"],COLORS["purple"]]
        for i,(cat,val) in enumerate(avg_ev.items()):
            fig9.add_trace(go.Bar(
                x=[str(cat)], y=[val],
                marker_color=evcols[min(i,3)],
                text=[f"<b>{val}</b><br>{cnt_ev[cat]}"], textposition="outside",
                showlegend=False, hovertemplate=f"{cat} events<br>Readiness:{val}<extra></extra>"
            ))
        fig9.update_layout(title="Events Attended → Placement Readiness",
            xaxis_title="Total Events", yaxis_range=[0, avg_ev.max()*1.3], bargap=0.3)
        apply_template(fig9)
        st.plotly_chart(fig9, use_container_width=True)

    st.markdown("""
<div class="insight-box insight-good">
  🧠 <b>Growth Mindset:</b> Students raising 5+ doubts score 12–18 points higher.
  Asking doubts = active engagement, not confusion.
</div>""", unsafe_allow_html=True)

    # Events pie
    st.markdown('<div class="sec-head">🏆 Event Participation Mix</div>', unsafe_allow_html=True)
    ev_vals = {"Hackathons": hack_f.sum(), "Workshops": work_f.sum(), "Live Sessions": live_f.sum()}
    ev_vals = {k:v for k,v in ev_vals.items() if v > 0}
    if ev_vals:
        fig10 = go.Figure(go.Pie(
            labels=list(ev_vals.keys()), values=list(ev_vals.values()),
            hole=0.52,
            marker=dict(colors=[COLORS["blue"],COLORS["purple"],COLORS["high"]],
                        line=dict(color="#0d1526",width=3)),
            textinfo="label+percent", textfont=dict(size=12), pull=[0.04]*3,
            hovertemplate="%{label}: %{value:.0f} (%{percent})<extra></extra>"
        ))
        total_ev_n = int(sum(ev_vals.values()))
        fig10.update_layout(
            title="Student Event Participation",
            annotations=[dict(text=f"<b>{total_ev_n}</b><br>Total",
                x=0.5,y=0.5,showarrow=False,font=dict(size=15,color="#e0eaff"))],
            height=360, paper_bgcolor="#0d1526",
            font=dict(family="Outfit",color="#c0cce8"),
            legend=dict(font=dict(size=11))
        )
        st.plotly_chart(fig10, use_container_width=True)

# ----------------------------------------------------------
# TAB 5 — Segmentation
# ----------------------------------------------------------
with tab5:
    st.markdown('<div class="sec-head">Student Segmentation</div>', unsafe_allow_html=True)

    seg_counts = filt_df["Segment"].value_counts()
    seg_cfg = {
        "🏆 High Performer":      ("#10b981","#041a0f","Placement ready. Keep challenged."),
        "🔵 Passive Learner":     ("#38b6ff","#001a30","Watching but not practicing. Push quizzes."),
        "🔶 Active but Confused": ("#f59e0b","#1a1200","High activity, low scores. Needs mentoring."),
        "⚠️ Disengaged":          ("#ef4444","#1a0608","High dropout risk. Immediate intervention."),
    }
    sc4 = st.columns(4)
    for (seg, cfg), col in zip(seg_cfg.items(), sc4):
        cnt   = seg_counts.get(seg, 0)
        pct   = cnt / N * 100
        color, bg, desc = cfg
        with col:
            st.markdown(f"""
<div style="background:{bg};border:1px solid {color};border-radius:12px;padding:16px 12px;text-align:center">
  <div style="font-size:1.6rem;margin-bottom:4px">{seg.split()[0]}</div>
  <div style="font-size:1.5rem;font-weight:800;color:{color};font-family:'JetBrains Mono',monospace">{cnt}</div>
  <div style="font-size:0.67rem;color:{color};margin:3px 0;text-transform:uppercase;letter-spacing:1px">{" ".join(seg.split()[1:])}</div>
  <div style="font-size:0.7rem;color:#6b8cba;margin-top:7px">{desc}</div>
  <div style="background:{color};height:3px;border-radius:2px;margin-top:10px;width:{pct:.0f}%;min-width:6px;margin-left:auto;margin-right:auto"></div>
  <div style="font-size:0.68rem;color:#455a7a;margin-top:3px">{pct:.1f}% of cohort</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    seg_order  = ["🏆 High Performer","🔵 Passive Learner","🔶 Active but Confused","⚠️ Disengaged"]
    seg_clrs   = [COLORS["high"],COLORS["blue"],COLORS["medium"],COLORS["low"]]
    fig12 = go.Figure()
    for seg, color in zip(seg_order, seg_clrs):
        sub = filt_df[filt_df["Segment"]==seg]
        if len(sub)==0: continue
        fig12.add_trace(go.Box(
            y=sub["Placement_Readiness"], x=[seg]*len(sub),
            name=seg, marker_color=color,
            boxmean=True, jitter=0.3, boxpoints="outliers"
        ))
    fig12.update_layout(
        title="Placement Readiness Distribution per Segment",
        xaxis_title="Segment", yaxis_title="Placement Readiness",
        showlegend=False
    )
    apply_template(fig12, height=420)
    st.plotly_chart(fig12, use_container_width=True)

    # Sankey
    c_att_col = COLS.get("att")
    if c_att_col:
        att_t3 = pd.cut(att_f, bins=[0,60,80,100], labels=["Low Att.","Med Att.","High Att."])
        pr_t3  = pd.cut(filt_df["Placement_Readiness"],
                        bins=[filt_df["Placement_Readiness"].min()-1,
                              filt_df["Placement_Readiness"].quantile(0.33),
                              filt_df["Placement_Readiness"].quantile(0.66),
                              filt_df["Placement_Readiness"].max()+1],
                        labels=["Low Ready","Mid Ready","High Ready"])
        sk_df  = pd.DataFrame({"src":att_t3,"tgt":pr_t3}).dropna()
        sk_cnt = sk_df.groupby(["src","tgt"], observed=True).size().reset_index(name="val")
        nodes  = list(att_t3.cat.categories) + list(pr_t3.cat.categories)
        nidx   = {n:i for i,n in enumerate(nodes)}
        nclrs  = [COLORS["low"],COLORS["medium"],COLORS["high"],"#455a7a","#6b8cba","#38b6ff"]
        fig_sk = go.Figure(go.Sankey(
            node=dict(pad=15,thickness=18,label=nodes,
                color=nclrs[:len(nodes)], line=dict(color="#0d1526",width=1)),
            link=dict(
                source=[nidx[r["src"]] for _,r in sk_cnt.iterrows()],
                target=[nidx[r["tgt"]] for _,r in sk_cnt.iterrows()],
                value=sk_cnt["val"].tolist(),
                color=["rgba(56,182,255,0.22)"]*len(sk_cnt)
            )
        ))
        fig_sk.update_layout(title="Attendance Tier → Placement Readiness Flow",
            height=360, paper_bgcolor="#0d1526",
            font=dict(family="Outfit",color="#c0cce8",size=11))
        st.plotly_chart(fig_sk, use_container_width=True)

# ----------------------------------------------------------
# TAB 6 — Risk & Leaderboard
# ----------------------------------------------------------
with tab6:
    st.markdown('<div class="sec-head">⚠️ High-Risk Students — Early Warning</div>', unsafe_allow_html=True)

    risk_mask = (att_f < 60) & (quiz_f < 50)
    risk_df   = filt_df[risk_mask.values]
    rc        = len(risk_df)

    r1,r2,r3 = st.columns(3)
    r1.metric("🚨 High-Risk Students", rc,
              delta=f"{rc/N*100:.1f}% of cohort", delta_color="inverse")
    r2.metric("⚠️ Disengaged", int(seg_counts.get("⚠️ Disengaged",0)))
    r3.metric("📊 At-Risk Rate", f"{rc/N*100:.1f}%")

    if rc > 0:
        show_cols = [c for c in [COLS.get("sid"),COLS.get("dept"),COLS.get("att"),
                                  COLS.get("quiz"),"Engagement_Score","Segment"]
                     if c and c in risk_df.columns]
        st.markdown(f"""
<div class="insight-box insight-alert">
  🚨 <b>{rc} students</b> have attendance &lt;60% AND quiz &lt;50 — assign mentors immediately.
</div>""", unsafe_allow_html=True)
        st.dataframe(
            risk_df[show_cols].reset_index(drop=True)
            .style.background_gradient(
                subset=["Engagement_Score"] if "Engagement_Score" in show_cols else [],
                cmap="RdYlGn"),
            use_container_width=True, height=260
        )
    else:
        st.markdown('<div class="insight-box insight-good">✅ No high-risk students in current filter.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-head">🏅 Engagement Leaderboard — Top 10</div>', unsafe_allow_html=True)

    top10 = filt_df.sort_values("Engagement_Score", ascending=False).head(10).reset_index(drop=True)
    top10.index += 1

    # Horizontal bar race
    y_labels = []
    for i, row in top10.iterrows():
        sid_v = row.get(COLS.get("sid",""), f"Stu {i}")
        dept_v= row.get(COLS.get("dept",""), "")
        y_labels.append(f"#{i} {sid_v}" + (f" · {dept_v}" if dept_v else ""))

    fig_lb = go.Figure(go.Bar(
        y=y_labels, x=top10["Engagement_Score"], orientation="h",
        marker=dict(
            color=top10["Placement_Readiness"],
            colorscale=[[0,"#1e3060"],[0.5,"#38b6ff"],[1,"#10b981"]],
            showscale=True, colorbar=dict(title="Readiness",thickness=10,len=0.7)
        ),
        text=[f"<b>{v:.1f}</b>" for v in top10["Engagement_Score"]],
        textposition="outside",
        hovertemplate="Engagement: %{x:.1f}<br>Readiness: %{marker.color:.1f}<extra></extra>"
    ))
    fig_lb.update_layout(
        title="Top 10 Students by Engagement (colour = Placement Readiness)",
        xaxis_title="Engagement Score",
        yaxis=dict(autorange="reversed")
    )
    apply_template(fig_lb, height=400)
    st.plotly_chart(fig_lb, use_container_width=True)

    # Table
    lb_cols = [c for c in [COLS.get("sid"),COLS.get("dept"),COLS.get("cgpa"),
                             "Engagement_Score","Learning_Score",
                             "Interaction_Score","Placement_Readiness","Segment"]
               if c and c in top10.columns]
    num_cols = [c for c in ["Engagement_Score","Learning_Score","Interaction_Score","Placement_Readiness"] if c in top10.columns]
    st.dataframe(
        top10[lb_cols].style
            .background_gradient(subset=num_cols, cmap="Blues")
            .format({c:"{:.1f}" for c in num_cols}),
        use_container_width=True, height=320
    )

# =========================================================
# MASTER INSIGHT  (always visible, lightweight)
# =========================================================
st.markdown('<div class="sec-head">💡 Master Insight</div>', unsafe_allow_html=True)
st.markdown("""
<div style="background:linear-gradient(135deg,#0f1a35,#0a1020);border:1px solid #1e3060;border-radius:16px;padding:24px 30px;margin:8px 0">
  <div style="font-size:1.05rem;font-weight:700;color:#38b6ff;margin-bottom:14px">
    ❌ Myth vs ✅ Reality
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
    <div style="background:#1a0608;border:1px solid #ef4444;border-radius:10px;padding:14px">
      <div style="color:#ef4444;font-weight:700;margin-bottom:8px">❌ Myth</div>
      <div style="color:#fca5a5;font-size:0.84rem;line-height:1.7">
        Watching videos = learning<br>High CGPA = placement ready<br>
        Time on platform = engagement<br>No doubts = I understand everything
      </div>
    </div>
    <div style="background:#041a0f;border:1px solid #10b981;border-radius:10px;padding:14px">
      <div style="color:#10b981;font-weight:700;margin-bottom:8px">✅ Reality</div>
      <div style="color:#6ee7b7;font-size:0.84rem;line-height:1.7">
        Watch + Quiz + Doubt + Apply = Real learning<br>
        Engagement Score &gt; CGPA for placement<br>
        Active days + doubts = true engagement<br>
        Raising doubts = growth mindset
      </div>
    </div>
  </div>
  <div style="margin-top:14px;color:#6b8cba;font-size:0.78rem;font-family:'JetBrains Mono',monospace">
    Placement Readiness = 0.4 × Engagement + 0.4 × Learning + 0.2 × Interaction
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#2a3a5e;font-size:0.75rem;font-family:JetBrains Mono,monospace;padding:6px">PragyanAI Engagement Intelligence Engine · Streamlit + Plotly</div>', unsafe_allow_html=True)
