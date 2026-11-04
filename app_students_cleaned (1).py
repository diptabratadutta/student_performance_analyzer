import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(page_title="Student Performance Analyzer", page_icon="📊", layout="wide")
st.title("📊 Student Performance Data Analyzer")
st.caption("Analyze cleaned student records and academic performance.")

# --------------------------------------------------
# DATA FILE
# --------------------------------------------------
# Put this app.py in the project root. The cleaned file should be
# inside the data folder. Windows may hide the file extension.
DATA_DIR = Path("data")
CLEANED_FILE = DATA_DIR / "students_cleaned.csv"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data(path):
    # CSV is expected. If the file is actually Excel, use read_excel instead.
    return pd.read_csv(path)

if not CLEANED_FILE.exists():
    st.error(f"File not found: {CLEANED_FILE}")
    st.info(
        "Check the actual extension of students_cleaned. "
        "If it is students_cleaned.xlsx, change the path and use pd.read_excel."
    )
    st.stop()

df = load_data(CLEANED_FILE)

# --------------------------------------------------
# IDENTIFY COLUMNS
# --------------------------------------------------
def find_column(frame, candidates):
    lookup = {str(c).strip().lower(): c for c in frame.columns}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    return None

name_col = find_column(df, ["Name", "Student_Name", "Student Name", "Full_Name"])
id_col = find_column(df, ["Student_ID", "Student ID", "Roll_No", "Roll Number", "ID"])

if name_col is None:
    st.error("Student name column not found.")
    st.write("Columns in your file:", list(df.columns))
    st.stop()

excluded = {name_col}
if id_col:
    excluded.add(id_col)
excluded.update(
    col for col in df.columns
    if str(col).strip().lower() in {"total", "percentage", "percent", "grade", "rank"}
)

subjects = [
    col for col in df.columns
    if col not in excluded and pd.api.types.is_numeric_dtype(df[col])
]

if not subjects:
    st.error("No numeric subject-mark columns found.")
    st.write("Columns in your file:", list(df.columns))
    st.stop()

# --------------------------------------------------
# CALCULATIONS
# --------------------------------------------------
df = df.copy()
df[subjects] = df[subjects].apply(pd.to_numeric, errors="coerce")
df["Total"] = df[subjects].sum(axis=1)

# Assumes every subject is out of 100.
df["Percentage"] = df["Total"] / (len(subjects) * 100) * 100

def assign_grade(p):
    if p >= 90: return "A+"
    if p >= 80: return "A"
    if p >= 70: return "B"
    if p >= 60: return "C"
    if p >= 50: return "D"
    if p >= 40: return "E"
    return "F"

df["Grade"] = df["Percentage"].apply(assign_grade)
df["Rank"] = df["Total"].rank(method="min", ascending=False).astype(int)

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------
page = st.sidebar.radio("Navigation", ["Overview", "Student Records", "Individual Performance"])

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------
if page == "Overview":
    st.header("Class Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", len(df))
    c2.metric("Class Average", f"{df['Percentage'].mean():.2f}%")
    c3.metric("Highest Percentage", f"{df['Percentage'].max():.2f}%")
    c4.metric("Pass Percentage", f"{(df['Percentage'] >= 40).mean() * 100:.2f}%")

    left, right = st.columns(2)
    with left:
        st.subheader("Subject-wise Average Marks")
        fig, ax = plt.subplots(figsize=(8, 4))
        df[subjects].mean().plot(kind="bar", ax=ax)
        ax.set_ylabel("Average Marks")
        plt.xticks(rotation=25)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with right:
        st.subheader("Grade Distribution")
        counts = df["Grade"].value_counts().reindex(["A+", "A", "B", "C", "D", "E", "F"], fill_value=0)
        fig, ax = plt.subplots(figsize=(8, 4))
        counts.plot(kind="bar", ax=ax)
        ax.set_ylabel("Number of Students")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("🏆 Top 5 Students")
    display_cols = [c for c in [id_col, name_col, "Total", "Percentage", "Grade", "Rank"] if c]
    st.dataframe(df.sort_values("Percentage", ascending=False).head(5)[display_cols],
                 use_container_width=True, hide_index=True)

# --------------------------------------------------
# STUDENT RECORDS
# --------------------------------------------------
elif page == "Student Records":
    st.header("Student Records")
    search = st.text_input("🔍 Search by student name or ID")
    grade_filter = st.selectbox("Filter by grade", ["All"] + sorted(df["Grade"].unique().tolist()))

    filtered = df.copy()
    if search:
        mask = filtered[name_col].astype(str).str.contains(search, case=False, na=False)
        if id_col:
            mask |= filtered[id_col].astype(str).str.contains(search, case=False, na=False)
        filtered = filtered[mask]
    if grade_filter != "All":
        filtered = filtered[filtered["Grade"] == grade_filter]

    st.write(f"Showing {len(filtered)} student(s)")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download filtered records",
        filtered.to_csv(index=False).encode("utf-8"),
        "student_performance.csv",
        "text/csv"
    )

# --------------------------------------------------
# INDIVIDUAL PERFORMANCE
# --------------------------------------------------
elif page == "Individual Performance":
    st.header("Individual Student Performance")
    selected_name = st.selectbox("Select student", df[name_col].astype(str).tolist())
    student = df[df[name_col].astype(str) == selected_name].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Marks", student["Total"])
    c2.metric("Percentage", f"{student['Percentage']:.2f}%")
    c3.metric("Grade", student["Grade"])

    st.subheader("Subject-wise Performance")
    fig, ax = plt.subplots(figsize=(9, 4))
    student[subjects].plot(kind="bar", ax=ax)
    ax.set_ylabel("Marks")
    plt.xticks(rotation=25)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Student Details")
    st.dataframe(student.to_frame("Value"), use_container_width=True)
