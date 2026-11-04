import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Student Performance Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Student Performance Data Analyzer")
st.caption("Analyze student marks, academic performance and class results.")

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

DATA_PATH = Path("data/students.csv")


@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)


def get_subject_columns(df):
    excluded = [
        "Student_ID", "Name",
        "Total", "Percentage", "Grade", "Rank"
    ]

    return [
        col for col in df.columns
        if col not in excluded
        and pd.api.types.is_numeric_dtype(df[col])
    ]


def calculate_performance(df, subjects):
    df = df.copy()

    df["Total"] = df[subjects].sum(axis=1)
    df["Percentage"] = (
        df["Total"] / (len(subjects) * 100)
    ) * 100

    def assign_grade(percentage):
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C"
        elif percentage >= 50:
            return "D"
        elif percentage >= 40:
            return "E"
        else:
            return "F"

    df["Grade"] = df["Percentage"].apply(assign_grade)

    df["Rank"] = (
        df["Total"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    return df


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

if not DATA_PATH.exists():
    st.error("students.csv not found in the data folder!")
    st.info("Create a folder named 'data' and add students.csv inside it.")
    st.stop()

df = load_data(DATA_PATH)

subjects = get_subject_columns(df)

if not subjects:
    st.error("No subject columns found in your CSV file.")
    st.stop()

df = calculate_performance(df, subjects)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a page",
    [
        "Overview",
        "Student Records",
        "Individual Performance"
    ]
)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --------------------------------------------------
# OVERVIEW DASHBOARD
# --------------------------------------------------

if page == "Overview":

    st.header("Class Overview")

    total_students = len(df)
    class_average = df["Percentage"].mean()
    highest_percentage = df["Percentage"].max()
    pass_percentage = (
        (df["Percentage"] >= 40).sum()
        / total_students * 100
        if total_students else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", total_students)
    col2.metric("Class Average", f"{class_average:.2f}%")
    col3.metric("Highest Percentage", f"{highest_percentage:.2f}%")
    col4.metric("Pass Percentage", f"{pass_percentage:.2f}%")

    st.divider()

    # SUBJECT AVERAGES
    st.subheader("📚 Subject-wise Average Marks")

    subject_averages = df[subjects].mean()

    fig, ax = plt.subplots(figsize=(10, 5))
    subject_averages.plot(kind="bar", ax=ax)

    ax.set_ylabel("Average Marks")
    ax.set_xlabel("Subjects")
    ax.set_title("Average Marks per Subject")
    ax.set_ylim(0, 100)

    plt.xticks(rotation=30)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    # GRADE DISTRIBUTION
    st.subheader("🎓 Grade Distribution")

    grade_order = ["A+", "A", "B", "C", "D", "E", "F"]
    grade_counts = (
        df["Grade"]
        .value_counts()
        .reindex(grade_order, fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    grade_counts.plot(kind="bar", ax=ax)

    ax.set_xlabel("Grade")
    ax.set_ylabel("Number of Students")
    ax.set_title("Student Grade Distribution")

    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    # TOP STUDENTS
    st.subheader("🏆 Top 5 Students")

    top_students = df.sort_values(
        "Percentage",
        ascending=False
    ).head(5)

    st.dataframe(
        top_students[["Name", "Total", "Percentage", "Grade", "Rank"]],
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# STUDENT RECORDS
# --------------------------------------------------

elif page == "Student Records":

    st.header("Student Records")

    search = st.text_input(
        "🔍 Search Student",
        placeholder="Enter student name..."
    )

    selected_grade = st.selectbox(
        "Filter by Grade",
        ["All"] + sorted(df["Grade"].unique().tolist())
    )

    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df["Name"]
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]

    if selected_grade != "All":
        filtered_df = filtered_df[
            filtered_df["Grade"] == selected_grade
        ]

    st.write(f"Showing {len(filtered_df)} students")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # DOWNLOAD CSV
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Student Records",
        data=csv_data,
        file_name="student_performance.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# INDIVIDUAL PERFORMANCE
# --------------------------------------------------

elif page == "Individual Performance":

    st.header("Individual Student Performance")

    student_names = df["Name"].astype(str).tolist()

    selected_student = st.selectbox(
        "Select Student",
        student_names
    )

    student = df[
        df["Name"].astype(str) == selected_student
    ].iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Marks", student["Total"])
    col2.metric("Percentage", f"{student['Percentage']:.2f}%")
    col3.metric("Grade", student["Grade"])

    st.subheader("Subject-wise Performance")

    marks = student[subjects]

    fig, ax = plt.subplots(figsize=(9, 5))
    marks.plot(kind="bar", ax=ax)

    ax.set_ylabel("Marks")
    ax.set_xlabel("Subjects")
    ax.set_ylim(0, 100)
    ax.set_title(f"{selected_student}'s Performance")

    plt.xticks(rotation=30)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Student Details")

    st.dataframe(
        student.to_frame(name="Value"),
        use_container_width=True
    )
