#  Student Engagement Intelligence System

> **LMS Behavior → Learning → Placement**  
> An interactive Business Intelligence dashboard that maps multi-dimensional LMS behavioral data to student learning quality and placement readiness.

---

##  Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [Dataset Format](#dataset-format)
- [Dashboard Modules](#dashboard-modules)
- [Key Insights](#key-insights)
- [Screenshots](#screenshots)
- [Future Enhancements](#future-enhancements)
- [Author](#author)

---

##  About the Project

The **Student Engagement Intelligence System (SEIS)** is an interactive analytical platform built using Python and Streamlit. It ingests student LMS behavioral data via CSV upload and generates a holistic **Placement Readiness Score** by analyzing five key engagement dimensions:

-  Attendance vs. Quiz Performance
-  LMS Login Frequency & Weekly Study Time
-  Video Completion & Learning Quality
-  Doubt Raising Behaviour (Growth Mindset Indicator)
-  Student Segmentation & Placement Readiness Distribution

The system classifies students into four actionable archetypes — **High Performer**, **Passive Learner**, **Active but Confused**, and **Disengaged** — enabling targeted institutional interventions.

---

##  Key Features

- CSV/TXT dataset upload (up to 200MB)
-  Multi-dimensional engagement visualizations (bar charts, scatter plots, heatmaps, line charts, box plots, pie charts)
-  Automated student segmentation into 4 behavioral archetypes
-  Composite Placement Readiness Score calculation
-  Interactive sidebar filters — Department, Segment, Attendance Range
-  Insight callouts highlighting key analytical findings
-  Dark-themed professional BI dashboard aesthetic
-  Supports multi-department cohort analysis (AI/ML, CSE, DS, ECE, EEE, IT, MECH, Civil)

---

##  Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core programming language |
| Streamlit | Interactive dashboard framework |
| Pandas | Data loading, cleaning, aggregation |
| NumPy | Numerical operations, score computation |
| Matplotlib | Static chart generation |
| Seaborn | Statistical visualizations, heatmaps |
| Plotly | Interactive dark-theme charts |
| Scikit-learn | Student segmentation, readiness scoring |

---

## Project Structure

```
SEIS/
│
├── app.py                  # Main Streamlit dashboard application
├── analysis.py             # Data processing & feature engineering logic
├── segmentation.py         # Student segmentation classification logic
├── scoring.py              # Placement readiness score computation
│
├── data/
│   └── student_data.csv    # Sample student engagement dataset
│
├── assets/
│   └── screenshots/        # Dashboard screenshot images
│
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore
```

---

## ⚙️ Installation & Setup

### Prerequisites

Make sure you have the following installed:

- Python 3.10 or above
- pip (Python package manager)
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/student-engagement-intelligence-system.git
cd student-engagement-intelligence-system
```

### Step 2 — Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — macOS/Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Verify Installation

```bash
python -c "import streamlit, pandas, numpy, matplotlib, seaborn, plotly, sklearn; print('All dependencies installed successfully!')"
```

---

## How to Run

```bash
streamlit run app.py
```

The dashboard will open automatically in your browser at:

```
http://localhost:8501
```

---

# Dataset Format

Upload a **CSV or TXT** file (comma or tab separated) with the following columns:

| Column | Description | Example |
|---|---|---|
| `student_id` | Unique student identifier | S001 |
| `name` | Student name | Navjot Kaur |
| `department` | Department name | CSE / DS / ECE |
| `attendance_pct` | Attendance percentage (0–100) | 85.5 |
| `login_frequency` | LMS logins per week | 6 |
| `weekly_study_hours` | Hours studied per week | 20 |
| `video_completion_pct` | % of videos completed (0–100) | 92.0 |
| `doubts_raised` | Number of doubts raised | 7 |
| `events_attended` | Number of events attended | 4 |
| `quiz_score` | Quiz score (0–100) | 89 |
| `placement_status` | Placed / Not Placed | Placed |

>  The system auto-detects column headers. Ensure your CSV has a header row.

---

 Dashboard Modules

 Module 1 — Attendance vs. Quiz Performance
- Bar chart: Average quiz score by attendance band (<60%, 60–80%, >80%)
- Scatter plot: Individual student data points with color-coded attendance bands and trend line

 Module 2 — LMS Usage: Login Frequency & Time Spent
- Bar chart: Login frequency (Low / Med / High) vs. average engagement score
- Line chart: Weekly study hours vs. placement readiness score with sweet spot annotation

 Module 3 — Learning Quality: Video Completion & Quiz Scores
- Heatmap: Video completion % × quiz score range cross-tabulation
- Bar chart: Average quiz score by video completion band

 Module 4 — Doubt Behaviour: Growth Mindset Indicator
- Bar chart: Doubts raised (None / 1–5 / 5+) vs. average quiz score
- Funnel chart: Total doubts raised → resolved → pending
- Bar chart: Events attended vs. placement readiness score

 Module 5 — Student Segmentation & Placement Readiness
- Bar chart: Student count per segment (High Performer / Passive Learner / Active but Confused / Disengaged)
- Box plot: Placement readiness score distribution per segment
- Histogram: Full placement readiness score distribution with percentile markers
- Pie chart: Placed vs. Not Placed breakdown

---

## Key Insights

|Finding | Detail 

Attendance impact | >80% attenders avg **89.7** quiz score vs. **32.6** for <60% attenders |
 LMS engagement | High-frequency users score **4x** higher engagement than low-frequency users |
 Study sweet spot | **15–30 hrs/week** = peak placement readiness; >30 hrs shows burnout plateau |
 Video completion | >80% completers averaged **89.7** quiz score; all scored above 75 |
 Doubt resolution | **93%** of 557 doubts resolved (518/557) — strong mentorship infrastructure |
 Events attendance | 6+ events → avg readiness **135.5** vs. **16.6** for zero events |
Cohort split | Perfectly bimodal — **30 High Performers** (placed) + **30 Disengaged** (not placed) |

---

 Screenshots

| Dashboard Upload | Filter Panel |
|---|---|
| ![Dashboard](assets/screenshots/dashboard.png) | ![Filters](assets/screenshots/filters.png) |

| Attendance vs Quiz | LMS Usage |
|---|---|
| ![Attendance](assets/screenshots/attendance.png) | ![LMS](assets/screenshots/lms.png) |

| Learning Quality | Doubt Behaviour |
|---|---|
| ![Learning](assets/screenshots/learning.png) | ![Doubt](assets/screenshots/doubt.png) |

| Segmentation Count | Readiness Distribution |
|---|---|
| ![Segmentation](assets/screenshots/segmentation.png) | ![Readiness](assets/screenshots/readiness.png) |

---

 Future Enhancements

- [ ] Live LMS API integration (Moodle, Canvas, Google Classroom)
- [ ] Supervised ML model for placement outcome prediction
- [ ] Automated early-warning alerts for faculty when students shift to Disengaged segment
- [ ] Personalized study plan recommendation engine
- [ ] Cloud deployment on AWS / Azure with multi-institution support
- [ ] Role-based access control (Faculty view vs. Administrator view)
- [ ] Mobile-responsive dashboard with push notifications for student self-monitoring

---

 Author

Aditya Chekki
USN: 3GN22EC005  
Department of E&CE   
Guru Nank Dev Engineering College Bidar  
Internship at: **Pragyan SmartAI Technology LLP** (Jan 2026 – May 2026)

---

License

This project was developed as part of an academic internship program.  
© 2026 Navjot Kaur — R.L. Jalappa Institute of Technology

---

> *"Consistency beats intelligence — showing up is the single strongest predictor of success."*
