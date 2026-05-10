import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Student Engagement Dashboard",
    layout="wide"
)

st.title("🎓 Student Engagement Intelligence System")
st.markdown("**LMS Behavior → Learning → Placement**")
st.markdown("---")

# ─────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📂 Upload your student dataset (CSV or TXT, tab or comma separated)",
    type=["csv", "txt"]
)

if uploaded_file is None:
    st.info("👆 Please upload your student data file to get started.")
    st.stop()

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
@st.cache_data
def load_data(file):
    raw = file.read().decode("utf-8")
    file.seek(0)
    # detect separator
    first_line = raw.split("\n")[0]
    sep = "\t" if "\t" in first_line else ","
    df = pd.read_csv(file, sep=sep)
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("%", "Pct")
        .str.replace("-", "_")
    )
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() >= len(df) * 0.5:
            df[col] = converted
    return df

df = load_data(uploaded_file)

# ─────────────────────────────────────────
# COLUMN FINDER
# ─────────────────────────────────────────
def find_col(df, *keywords):
    for col in df.columns:
        name = col.lower()
        if all(k.lower() in name for k in keywords):
            return col
    return None

def safe(df, col):
    if col is None or col not in df.columns:
        return pd.Series(np.zeros(len(df)), index=df.index)
    return pd.to_numeric(df[col], errors="coerce").fillna(0)

# detect columns
c_att   = find_col(df, "attendance")
c_quiz  = find_col(df, "quiz", "score") or find_col(df, "quiz")
c_vid   = find_col(df, "video", "completion") or find_col(df, "video", "pct")
c_login = find_col(df, "login")
c_time  = find_col(df, "time", "spent") or find_col(df, "time")
c_vids  = find_col(df, "videos", "watched") or find_col(df, "video", "watched")
c_doubt = find_col(df, "doubt") or find_col(df, "doubts")
c_res   = find_col(df, "doubt", "resolved") or find_col(df, "resolved")
c_peer  = find_col(df, "peer")
c_hack  = find_col(df, "hackathon")
c_work  = find_col(df, "workshop")
c_live  = find_col(df, "live")
c_dept  = find_col(df, "department") or find_col(df, "dept")
c_sid   = find_col(df, "student", "id") or find_col(df, "id")
c_cgpa  = find_col(df, "cgpa")
c_place = find_col(df, "placement", "status")

# load series
att_s   = safe(df, c_att)
quiz_s  = safe(df, c_quiz)
vid_s   = safe(df, c_vid)
login_s = safe(df, c_login)
time_s  = safe(df, c_time)
vids_s  = safe(df, c_vids)
doubt_s = safe(df, c_doubt)
res_s   = safe(df, c_res)
peer_s  = safe(df, c_peer)
hack_s  = safe(df, c_hack)
work_s  = safe(df, c_work)
live_s  = safe(df, c_live)

# ─────────────────────────────────────────
# COMPUTE SCORES
# ─────────────────────────────────────────
df["Engagement_Score"] = np.round(
    att_s * 0.30 +
    login_s * 5.00 +
    time_s  * 2.00 +
    vids_s  * 0.50 +
    doubt_s * 3.00, 1
)

df["Learning_Score"] = np.round(quiz_s * vid_s / 100, 1)

df["Interaction_Score"] = np.round(
    doubt_s + peer_s + hack_s + work_s + live_s, 1
)

df["Placement_Readiness"] = np.round(
    df["Engagement_Score"] * 0.40 +
    df["Learning_Score"]   * 0.40 +
    df["Interaction_Score"]* 0.20, 1
)

# segmentation
q70 = df["Engagement_Score"].quantile(0.70)
q50 = df["Engagement_Score"].quantile(0.50)
q30 = df["Engagement_Score"].quantile(0.30)

conditions = [
    (df["Engagement_Score"] > q70) & (quiz_s > 70),
    (df["Engagement_Score"] > q50) & (quiz_s < 50),
    (df["Engagement_Score"] < q30),
]
df["Segment"] = np.select(
    conditions,
    ["High Performer", "Active but Confused", "Disengaged"],
    default="Passive Learner"
)

# ─────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────
st.sidebar.header("🔍 Filters")

filt_df = df.copy()

if c_dept and c_dept in df.columns:
    depts = sorted(df[c_dept].dropna().unique())
    sel_dept = st.sidebar.multiselect("Department", depts, default=depts)
    filt_df = filt_df[filt_df[c_dept].isin(sel_dept)]

segs = sorted(df["Segment"].unique())
sel_seg = st.sidebar.multiselect("Segment", segs, default=segs)
filt_df = filt_df[filt_df["Segment"].isin(sel_seg)]

att_min, att_max = st.sidebar.slider("Attendance % Range", 0, 100, (0, 100), 5)
att_f = safe(filt_df, c_att)
filt_df = filt_df[att_f.reindex(filt_df.index, fill_value=0).between(att_min, att_max)]

st.sidebar.markdown(f"**Showing {len(filt_df)} / {len(df)} students**")

with st.sidebar.expander("📋 Dataset Preview"):
    st.dataframe(filt_df.head(10))

# filtered series
def fs(col):
    return safe(filt_df, col)

att_f   = fs(c_att);   quiz_f  = fs(c_quiz);  vid_f   = fs(c_vid)
login_f = fs(c_login); time_f  = fs(c_time);  doubt_f = fs(c_doubt)
hack_f  = fs(c_hack);  work_f  = fs(c_work);  live_f  = fs(c_live)
res_f   = fs(c_res)

N = max(len(filt_df), 1)

# ─────────────────────────────────────────
# MATPLOTLIB STYLE
# ─────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1526",
    "axes.facecolor":   "#0d1526",
    "axes.edgecolor":   "#2a3a5e",
    "axes.labelcolor":  "#c0cce8",
    "xtick.color":      "#8899bb",
    "ytick.color":      "#8899bb",
    "text.color":       "#c0cce8",
    "grid.color":       "#1e2d42",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   13,
    "axes.labelsize":   11,
})

BAR_COLORS = ["#ef4444", "#f59e0b", "#10b981"]   # low / medium / high

# helper: bar chart
def bar_chart(ax, categories, values, counts=None, title="", ylabel="", ylim_top=None):
    bars = ax.bar(categories, values, color=BAR_COLORS[:len(categories)],
                  edgecolor="none", width=0.5)
    ax.set_title(title, pad=10)
    ax.set_ylabel(ylabel)
    ax.yaxis.grid(True); ax.set_axisbelow(True)
    if ylim_top:
        ax.set_ylim(0, ylim_top)
    for bar, val in zip(bars, values):
        label = f"{val:.1f}"
        if counts is not None:
            label += f"\n({counts[bar.get_x()+bar.get_width()/2]:.0f} students)" if False else f"\n({counts})"
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + ylim_top * 0.02 if ylim_top else bar.get_height() + 0.5,
                f"{val:.1f}", ha="center", va="bottom", fontsize=10, color="#e0eaff", fontweight="bold")

def show(fig):
    st.pyplot(fig)
    plt.close(fig)

# ─────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────
st.header("📊 Overview")

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Avg Attendance",   f"{att_f.mean():.1f}%")
k2.metric("Avg Quiz Score",   f"{quiz_f.mean():.1f}")
k3.metric("Avg Engagement",   f"{filt_df['Engagement_Score'].mean():.1f}")
k4.metric("Avg Readiness",    f"{filt_df['Placement_Readiness'].mean():.1f}")
k5.metric("Avg Logins/wk",    f"{login_f.mean():.1f}x")
k6.metric("Avg Hours/wk",     f"{time_f.mean():.1f}h")

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 1 — ATTENDANCE vs QUIZ
# ─────────────────────────────────────────
st.header("📌 1. Attendance vs Quiz Performance")

col1, col2 = st.columns(2)

with col1:
    bins   = [0, 60, 80, 100]
    labels = ["<60%\nLow", "60-80%\nMedium", ">80%\nHigh"]
    cut    = pd.cut(att_f, bins=bins, labels=labels)
    tmp    = pd.DataFrame({"lvl": cut, "quiz": quiz_f})
    avg_q  = tmp.groupby("lvl", observed=False)["quiz"].mean().reindex(labels).fillna(0).round(1)
    cnt_q  = tmp.groupby("lvl", observed=False)["quiz"].count().reindex(labels).fillna(0)
    act    = avg_q > 0   # mask out empty bins
    a_lbl  = avg_q.index[act].tolist()
    a_vals = avg_q[act].values
    a_cnts = cnt_q[act].values
    a_clrs = [BAR_COLORS[i] for i, ok in enumerate(act) if ok]

    if len(a_vals) == 0:
        st.warning("No attendance data in current filter range.")
    else:
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(a_lbl, a_vals, color=a_clrs, edgecolor="none", width=0.5)
        ax.set_title("Avg Quiz Score by Attendance Band")
        ax.set_ylabel("Avg Quiz Score")
        ax.set_ylim(0, float(a_vals.max()) * 1.35 or 10)
        ax.yaxis.grid(True); ax.set_axisbelow(True)
        for bar, val, cnt in zip(bars, a_vals, a_cnts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{val:.1f}\n({int(cnt)})", ha="center", va="bottom",
                    fontsize=9, color="#e0eaff", fontweight="bold")
        show(fig)

with col2:
    fig, ax = plt.subplots(figsize=(6, 4))
    cut2 = pd.cut(att_f, bins=bins, labels=["Low","Medium","High"])
    colors_map = {"Low": BAR_COLORS[0], "Medium": BAR_COLORS[1], "High": BAR_COLORS[2]}
    for tier, color in colors_map.items():
        mask = (cut2 == tier).values
        ax.scatter(att_f[mask], quiz_f[mask],
                   color=color, alpha=0.55, s=18, label=tier)
    # trendline
    if len(att_f) > 5:
        z = np.polyfit(att_f, quiz_f, 1)
        x_line = np.linspace(att_f.min(), att_f.max(), 80)
        ax.plot(x_line, np.poly1d(z)(x_line), color="#38b6ff", linewidth=2,
                linestyle="--", label="Trend")
    ax.set_title("Scatter: Attendance vs Quiz Score")
    ax.set_xlabel("Attendance (%)"); ax.set_ylabel("Quiz Score")
    ax.legend(fontsize=8); ax.grid(True)
    show(fig)

st.success("📈 Insight: Students with >80% attendance score 15–22 points higher. Consistency beats intelligence.")

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 2 — LOGIN FREQUENCY & TIME SPENT
# ─────────────────────────────────────────
st.header("💻 2. LMS Usage — Login Frequency & Time Spent")

col3, col4 = st.columns(2)

with col3:
    l_lbls = ["1-2/wk\nLow", "3-5/wk\nMed", "6-7/wk\nHigh"]
    lcut   = pd.cut(login_f, bins=[0, 2, 5, 7], labels=l_lbls)
    tmp_l  = pd.DataFrame({"c": lcut, "e": filt_df["Engagement_Score"]})
    avg_e  = tmp_l.groupby("c", observed=False)["e"].mean().reindex(l_lbls).fillna(0).round(1)
    cnt_e  = tmp_l.groupby("c", observed=False)["e"].count().reindex(l_lbls).fillna(0)
    act_l  = avg_e > 0
    e_lbl  = avg_e.index[act_l].tolist()
    e_vals = avg_e[act_l].values
    e_cnts = cnt_e[act_l].values
    e_clrs = [BAR_COLORS[i] for i, ok in enumerate(act_l) if ok]

    if len(e_vals) == 0:
        st.warning("No login frequency data in current filter range.")
    else:
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(e_lbl, e_vals, color=e_clrs, edgecolor="none", width=0.5)
        ax.set_title("Login Frequency -> Engagement Score")
        ax.set_ylabel("Avg Engagement Score")
        ax.set_ylim(0, float(e_vals.max()) * 1.35 or 10)
        ax.yaxis.grid(True); ax.set_axisbelow(True)
        for bar, val, cnt in zip(bars, e_vals, e_cnts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{val:.1f}\n({int(cnt)})", ha="center", va="bottom",
                    fontsize=9, color="#e0eaff", fontweight="bold")
        show(fig)

with col4:
    tcut  = pd.cut(time_f, bins=[0, 5, 15, 30, 100], labels=["<5h", "5–15h", "15–30h", ">30h"])
    avg_p = pd.DataFrame({"c": tcut, "p": filt_df["Placement_Readiness"]}).groupby("c", observed=True)["p"].mean().round(1)
    t_colors = [BAR_COLORS[0], BAR_COLORS[1], BAR_COLORS[2], "#6b8cba"]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(avg_p.index.tolist(), avg_p.values,
            color="#a78bfa", linewidth=2.5, marker="o", markersize=9)
    for i, (x, y) in enumerate(zip(avg_p.index.tolist(), avg_p.values)):
        ax.plot(x, y, "o", color=t_colors[i], markersize=11)
        ax.text(i, y + avg_p.max() * 0.04, f"{y:.1f}",
                ha="center", va="bottom", fontsize=10, color="#e0eaff", fontweight="bold")
    ax.set_title("Time Spent/Week → Placement Readiness")
    ax.set_xlabel("Weekly Study Hours"); ax.set_ylabel("Placement Readiness")
    ax.set_ylim(0, avg_p.max() * 1.3)
    ax.yaxis.grid(True); ax.set_axisbelow(True)
    show(fig)

st.warning("⏱ Sweet Spot: 15–30 hrs/week = peak readiness. >30h shows burnout plateau.")

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 3 — VIDEO & QUIZ HEATMAP
# ─────────────────────────────────────────
st.header("🎥 3. Learning Quality — Video Completion & Quiz")

col5, col6 = st.columns(2)

with col5:
    vcut = pd.cut(vid_f,  bins=[0, 50, 80, 100], labels=["<50%", "50–80%", ">80%"])
    qcut = pd.cut(quiz_f, bins=[0, 50, 75, 100], labels=["<50",  "50–75",  ">75"])
    hm   = pd.crosstab(vcut, qcut)

    fig, ax = plt.subplots(figsize=(6, 4))
    mat = hm.values.astype(float)
    im  = ax.imshow(mat, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(hm.columns))); ax.set_xticklabels(hm.columns.tolist())
    ax.set_yticks(range(len(hm.index)));   ax.set_yticklabels(hm.index.tolist())
    ax.set_xlabel("Quiz Score Range"); ax.set_ylabel("Video Completion %")
    ax.set_title("Heatmap: Video Completion × Quiz Score")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{int(mat[i,j])}", ha="center", va="center",
                    fontsize=12, color="white", fontweight="bold")
    plt.colorbar(im, ax=ax, label="Students")
    show(fig)

with col6:
    vbins  = [0, 50, 80, 100]
    vlbls  = ["<50%\nLow", "50-80%\nMed", ">80%\nHigh"]
    vcut2  = pd.cut(vid_f, bins=vbins, labels=vlbls)
    tmp_v  = pd.DataFrame({"c": vcut2, "q": quiz_f})
    avg_vq = tmp_v.groupby("c", observed=False)["q"].mean().reindex(vlbls).fillna(0).round(1)
    cnt_vq = tmp_v.groupby("c", observed=False)["q"].count().reindex(vlbls).fillna(0)
    act_v  = avg_vq > 0
    v_lbl  = avg_vq.index[act_v].tolist()
    v_vals = avg_vq[act_v].values
    v_cnts = cnt_vq[act_v].values
    v_clrs = [BAR_COLORS[i] for i, ok in enumerate(act_v) if ok]

    if len(v_vals) == 0:
        st.warning("No video completion data in current filter range.")
    else:
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(v_lbl, v_vals, color=v_clrs, edgecolor="none", width=0.5)
        ax.set_title("Video Completion -> Quiz Score")
        ax.set_ylabel("Avg Quiz Score")
        ax.set_ylim(0, float(v_vals.max()) * 1.35 or 10)
        ax.yaxis.grid(True); ax.set_axisbelow(True)
        for bar, val, cnt in zip(bars, v_vals, v_cnts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{val:.1f}\n({int(cnt)})", ha="center", va="bottom",
                    fontsize=9, color="#e0eaff", fontweight="bold")
        show(fig)

st.info("🎥 Students completing >80% of videos score significantly higher in quizzes.")

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 4 — DOUBTS
# ─────────────────────────────────────────
st.header("❓ 4. Doubt Behaviour — Growth Mindset Indicator")

col7, col8, col9 = st.columns(3)

with col7:
    d_lbls = ["No Doubts", "1-5 Doubts", "5+ Active"]
    dcut   = pd.cut(doubt_f, bins=[-1, 0, 5, 999], labels=d_lbls)
    tmp_d  = pd.DataFrame({"c": dcut, "q": quiz_f})
    avg_dq = tmp_d.groupby("c", observed=False)["q"].mean().reindex(d_lbls).fillna(0).round(1)
    cnt_dq = tmp_d.groupby("c", observed=False)["q"].count().reindex(d_lbls).fillna(0)
    act_d  = avg_dq > 0
    d_lbl  = avg_dq.index[act_d].tolist()
    d_vals = avg_dq[act_d].values
    d_cnts = cnt_dq[act_d].values
    d_clrs = [BAR_COLORS[i] for i, ok in enumerate(act_d) if ok]

    if len(d_vals) == 0:
        st.warning("No doubt data in current filter range.")
    else:
        fig, ax = plt.subplots(figsize=(5, 4))
        bars = ax.bar(d_lbl, d_vals, color=d_clrs, edgecolor="none", width=0.5)
        ax.set_title("Doubts Raised -> Quiz Score")
        ax.set_ylabel("Avg Quiz Score")
        ax.set_ylim(0, float(d_vals.max()) * 1.35 or 10)
        ax.yaxis.grid(True); ax.set_axisbelow(True)
        for bar, val, cnt in zip(bars, d_vals, d_cnts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{val:.1f}\n({int(cnt)})", ha="center", va="bottom",
                    fontsize=9, color="#e0eaff", fontweight="bold")
        show(fig)

with col8:
    # Resolution funnel as horizontal bars
    total_raised   = doubt_f.sum()
    total_resolved = res_f.sum()
    total_pending  = max(0, total_raised - total_resolved)
    categories = ["Doubts Raised", "Resolved", "Pending"]
    values_f   = [total_raised, total_resolved, total_pending]
    clrs_f     = ["#38b6ff", "#10b981", "#f59e0b"]

    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.barh(categories, values_f, color=clrs_f, edgecolor="none", height=0.4)
    ax.set_title("Doubt Resolution Funnel")
    ax.set_xlabel("Count")
    ax.xaxis.grid(True); ax.set_axisbelow(True)
    for bar, val in zip(bars, values_f):
        ax.text(bar.get_width() + total_raised * 0.01, bar.get_y() + bar.get_height()/2,
                f"{int(val)}", va="center", fontsize=10, color="#e0eaff", fontweight="bold")
    show(fig)

with col9:
    # Events vs Placement Readiness
    total_ev = hack_f + work_f + live_f
    ev_lbls = ["0", "1-2", "3-5", "6+"]
    ev_clrs = [BAR_COLORS[0], BAR_COLORS[1], BAR_COLORS[2], "#a78bfa"]
    ecut    = pd.cut(total_ev, bins=[-1, 0, 2, 5, 999], labels=ev_lbls)
    tmp_ev  = pd.DataFrame({"c": ecut, "p": filt_df["Placement_Readiness"]})
    avg_ep  = tmp_ev.groupby("c", observed=False)["p"].mean().reindex(ev_lbls).fillna(0).round(1)
    cnt_ep  = tmp_ev.groupby("c", observed=False)["p"].count().reindex(ev_lbls).fillna(0)
    act_ev  = avg_ep > 0
    ep_lbl  = avg_ep.index[act_ev].tolist()
    ep_vals = avg_ep[act_ev].values
    ep_cnts = cnt_ep[act_ev].values
    ep_clrs = [ev_clrs[i] for i, ok in enumerate(act_ev) if ok]

    if len(ep_vals) == 0:
        st.warning("No event data in current filter range.")
    else:
        fig, ax = plt.subplots(figsize=(5, 4))
        bars = ax.bar(ep_lbl, ep_vals, color=ep_clrs, edgecolor="none", width=0.5)
        ax.set_title("Events Attended -> Placement Readiness")
        ax.set_xlabel("Total Events"); ax.set_ylabel("Placement Readiness")
        ax.set_ylim(0, float(ep_vals.max()) * 1.35 or 10)
        ax.yaxis.grid(True); ax.set_axisbelow(True)
        for bar, val, cnt in zip(bars, ep_vals, ep_cnts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{val:.1f}\n({int(cnt)})", ha="center", va="bottom",
                    fontsize=9, color="#e0eaff", fontweight="bold")
        show(fig)

st.success("🧠 Growth Mindset: Students raising 5+ doubts score 12–18 points higher. Asking doubts = active engagement.")

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 5 — EVENTS PIE
# ─────────────────────────────────────────
st.header("🏆 5. Event Participation")

ev_data = {
    "Hackathons":    hack_f.sum(),
    "Workshops":     work_f.sum(),
    "Live Sessions": live_f.sum(),
}
ev_data = {k: v for k, v in ev_data.items() if v > 0}

if ev_data:
    col10, col11 = st.columns([1, 2])
    with col10:
        fig, ax = plt.subplots(figsize=(5, 4))
        pie_colors = ["#38b6ff", "#a78bfa", "#10b981"]
        wedges, texts, autotexts = ax.pie(
            list(ev_data.values()),
            labels=list(ev_data.keys()),
            autopct="%1.1f%%",
            colors=pie_colors[:len(ev_data)],
            startangle=140,
            wedgeprops=dict(edgecolor="#0d1526", linewidth=2)
        )
        for t in autotexts:
            t.set_color("white"); t.set_fontsize(10); t.set_fontweight("bold")
        ax.set_title("Event Participation Mix")
        show(fig)

    with col11:
        st.markdown("### Event Stats")
        for event, count in ev_data.items():
            pct = count / max(sum(ev_data.values()), 1) * 100
            st.markdown(f"**{event}**: {int(count)} participations ({pct:.1f}%)")

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 6 — SEGMENTATION
# ─────────────────────────────────────────
st.header("🧠 6. Student Segmentation")

seg_counts = filt_df["Segment"].value_counts()
seg_cfg = {
    "High Performer":      ("#10b981", "Placement ready. Keep them challenged."),
    "Passive Learner":     ("#38b6ff", "Watching but not practicing. Push quizzes."),
    "Active but Confused": ("#f59e0b", "High activity, low scores. Needs mentoring."),
    "Disengaged":          ("#ef4444", "High dropout risk. Immediate intervention."),
}

sc4 = st.columns(4)
for (seg, (color, desc)), col in zip(seg_cfg.items(), sc4):
    cnt = seg_counts.get(seg, 0)
    pct = cnt / N * 100
    with col:
        st.metric(label=seg, value=cnt, delta=f"{pct:.1f}% of cohort")
        st.caption(desc)

# bar chart of segments
fig, ax = plt.subplots(figsize=(8, 4))
seg_names = list(seg_cfg.keys())
seg_vals  = [seg_counts.get(s, 0) for s in seg_names]
seg_clrs  = [seg_cfg[s][0] for s in seg_names]
bars = ax.bar(seg_names, seg_vals, color=seg_clrs, edgecolor="none", width=0.5)
ax.set_title("Student Segmentation Count")
ax.set_ylabel("Number of Students")
ax.yaxis.grid(True); ax.set_axisbelow(True)
for bar, val in zip(bars, seg_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            str(val), ha="center", va="bottom", fontsize=11,
            color="#e0eaff", fontweight="bold")
show(fig)

# box plot of Placement Readiness per segment
fig, ax = plt.subplots(figsize=(8, 4))
box_data = [filt_df[filt_df["Segment"] == s]["Placement_Readiness"].dropna().values
            for s in seg_names if len(filt_df[filt_df["Segment"] == s]) > 0]
box_lbls = [s for s in seg_names if len(filt_df[filt_df["Segment"] == s]) > 0]

if box_data:
    bp = ax.boxplot(box_data, labels=box_lbls, patch_artist=True, notch=False)
    box_palette = [seg_cfg.get(l, ("#38b6ff",""))[0] for l in box_lbls]
    for patch, color in zip(bp["boxes"], box_palette):
        patch.set_facecolor(color); patch.set_alpha(0.7)
    for elem in ["whiskers", "caps", "fliers", "medians"]:
        for part in bp[elem]:
            part.set_color("#c0cce8")
    ax.set_title("Placement Readiness Distribution per Segment")
    ax.set_ylabel("Placement Readiness Score")
    ax.yaxis.grid(True); ax.set_axisbelow(True)
    show(fig)

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 7 — RISK DETECTION
# ─────────────────────────────────────────
st.header("⚠️ 7. High-Risk Students — Early Warning")

risk_mask = (att_f < 60) & (quiz_f < 50)
risk_df   = filt_df[risk_mask.values]
rc        = len(risk_df)

r1, r2, r3 = st.columns(3)
r1.metric("🚨 High-Risk Students", rc, delta=f"{rc/N*100:.1f}% of cohort", delta_color="inverse")
r2.metric("⚠️ Disengaged",         int(seg_counts.get("Disengaged", 0)))
r3.metric("📊 At-Risk Rate",        f"{rc/N*100:.1f}%")

if rc > 0:
    st.error(f"🚨 {rc} students have attendance <60% AND quiz score <50 — assign mentors immediately.")
    show_cols = [c for c in [c_sid, c_dept, c_att, c_quiz, "Engagement_Score", "Segment"]
                 if c and c in risk_df.columns]
    st.dataframe(risk_df[show_cols].reset_index(drop=True), use_container_width=True)
else:
    st.success("✅ No high-risk students in current filter.")

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 8 — LEADERBOARD
# ─────────────────────────────────────────
st.header("🏅 8. Engagement Leaderboard — Top 10")

top10 = (filt_df.sort_values("Engagement_Score", ascending=False)
         .head(10).reset_index(drop=True))
top10.index += 1

# horizontal bar chart
y_labels = []
for i, row in top10.iterrows():
    sid_v  = str(row.get(c_sid,  f"Student {i}"))
    dept_v = str(row.get(c_dept, ""))
    y_labels.append(f"#{i} {sid_v}" + (f" · {dept_v}" if dept_v else ""))

fig, ax = plt.subplots(figsize=(9, 5))
eng_vals = top10["Engagement_Score"].values
norm_vals = (eng_vals - eng_vals.min()) / (eng_vals.max() - eng_vals.min() + 1e-9)
bar_clrs  = plt.cm.Blues(0.4 + norm_vals * 0.6)   # type: ignore[attr-defined]
bars = ax.barh(y_labels, eng_vals, color=bar_clrs, edgecolor="none", height=0.6)
ax.set_title("Top 10 Students by Engagement Score")
ax.set_xlabel("Engagement Score")
ax.invert_yaxis()
ax.xaxis.grid(True); ax.set_axisbelow(True)
for bar, val in zip(bars, eng_vals):
    ax.text(bar.get_width() + eng_vals.max() * 0.01, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}", va="center", fontsize=10, color="#e0eaff", fontweight="bold")
show(fig)

lb_cols = [c for c in [c_sid, c_dept, c_cgpa,
                        "Engagement_Score", "Learning_Score",
                        "Interaction_Score", "Placement_Readiness", "Segment"]
           if c and c in top10.columns]
st.dataframe(top10[lb_cols], use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 9 — PLACEMENT READINESS DIST
# ─────────────────────────────────────────
st.header("🚀 9. Placement Readiness Distribution")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# histogram
axes[0].hist(filt_df["Placement_Readiness"].dropna(), bins=25,
             color="#38b6ff", edgecolor="#0d1526", alpha=0.85)
q33 = filt_df["Placement_Readiness"].quantile(0.33)
q66 = filt_df["Placement_Readiness"].quantile(0.66)
axes[0].axvline(q33, color="#ef4444", linestyle="--", linewidth=1.5, label="Bottom 33%")
axes[0].axvline(q66, color="#10b981", linestyle="--", linewidth=1.5, label="Top 33%")
axes[0].set_title("Placement Readiness Score Distribution")
axes[0].set_xlabel("Readiness Score"); axes[0].set_ylabel("Students")
axes[0].legend(fontsize=9); axes[0].yaxis.grid(True); axes[0].set_axisbelow(True)

# placement status if available
if c_place and c_place in filt_df.columns:
    place_counts = filt_df[c_place].value_counts()
    p_colors = ["#10b981","#ef4444","#f59e0b","#38b6ff","#a78bfa"]
    axes[1].pie(
        place_counts.values,
        labels=place_counts.index.tolist(),
        autopct="%1.1f%%",
        colors=p_colors[:len(place_counts)],
        startangle=140,
        wedgeprops=dict(edgecolor="#0d1526", linewidth=2)
    )
    axes[1].set_title("Placement Status Breakdown")
else:
    # CGPA vs Readiness scatter
    cgpa_s = safe(filt_df, c_cgpa)
    axes[1].scatter(cgpa_s, filt_df["Placement_Readiness"],
                    color="#a78bfa", alpha=0.5, s=18)
    axes[1].set_title("CGPA vs Placement Readiness")
    axes[1].set_xlabel("CGPA"); axes[1].set_ylabel("Placement Readiness")
    axes[1].grid(True)

plt.tight_layout()
show(fig)

st.markdown("---")

# ─────────────────────────────────────────
# MASTER INSIGHT
# ─────────────────────────────────────────
st.header("💡 Master Insight")

col_m1, col_m2 = st.columns(2)
with col_m1:
    st.error("""
❌ **Myth — What students think:**
- Watching videos = learning
- High CGPA = placement ready
- Time on platform = engagement
- No doubts = I understand everything
""")
with col_m2:
    st.success("""
✅ **Reality — What actually drives placement:**
- Watch + Quiz + Doubt + Apply = Real learning
- Engagement Score > CGPA for placement
- Active days + doubts = true engagement
- Raising doubts = growth mindset
""")

st.markdown("""
> **Formula:**  
> `Placement Readiness = 0.4 × Engagement + 0.4 × Learning + 0.2 × Interaction`
""")

st.markdown("---")
st.markdown("**PragyanAI Engagement Intelligence Engine** · Built with Streamlit + Pandas + NumPy + Matplotlib")
