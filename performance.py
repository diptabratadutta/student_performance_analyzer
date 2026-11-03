import pandas as pd
import os
# Subjects in our project
SUBJECTS = ["Maths", "Physics", "Chemistry", "English", "Computer"]


# 1. Calculate total marks
def calculate_total(row):
    total = 0

    for subject in SUBJECTS:
        total = total + row[subject]

    return total


# 2. Calculate percentage
def calculate_percentage(total):
    # maximum_marks = len(SUBJECTS) * 100

    percentage = (total / (len(SUBJECTS) * 100)) * 100

    return round(percentage, 2)

# 3. Calculate grade
def calculate_grade(percentage):

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

    elif percentage >= 33:
        return "E"

    else:
        return "F"


# 4. Check whether the student passes
def calculate_result(row, percentage):

    # Check whether every subject has at least 33 marks
    for subject in SUBJECTS:
        if row[subject] < 33:
            return "Fail"

    # Check the overall percentage
    if percentage >= 33:
        return "Pass"

    else:
        return "Fail"


# 5. Calculate total, percentage, grade, result and rank
def calculate_performance(data):

    # Make a copy so the original data is not changed
    data = data.copy()

    # Calculate total marks
    data["Total"] = data.apply(calculate_total, axis=1)

    # Calculate percentage
    data["Percentage"] = data["Total"].apply(calculate_percentage)

    # Calculate grade
    data["Grade"] = data["Percentage"].apply(calculate_grade)

    # Calculate pass or fail
    data["Result"] = data.apply(
        lambda row: calculate_result(row, row["Percentage"]),
        axis=1
    )

    # Calculate rank: highest total gets rank 1
    data["Rank"] = data["Total"].rank(
        method="min",
        ascending=False
    ).astype(int)

    return data


# Run this part when we execute performance.py directly
if __name__ == "__main__":

    # Load the cleaned CSV created by Member 1
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(folder, "data", "students_cleaned.csv")

        data = pd.read_csv(file_path)

        # Calculate student performance
        result = calculate_performance(data)

        # Display the results
        print("\nSTUDENT PERFORMANCE REPORT")
        print("-" * 100)

        print(
            result[
                [
                    "roll_number",
                    "name",
                    "Total",
                    "Percentage",
                    "Grade",
                    "Result",
                    "Rank"
                ]
            ].to_string(index=False)
        )

        print("-" * 100)

    except FileNotFoundError:
        print("CSV file not found!")
        print("Make sure data/students_cleaned.csv exists.")
        print("Run data_manager.py first.")