import pandas as pd #we need pandas becoz data record is stored dataFrame
from Performance import calculate_performance
from data_manager import load_data, clean_data
SUBJECTS = [
    "Maths",
    "Physics",
    "Chemistry",
    "English",
    "Computer"]
# 1. Calculate subject wise average
def subject_wise_average(data):

    averages = {}

    for subject in SUBJECTS:
        averages[subject] = round(data[subject].mean(), 2)

    return averages
# 2. Calculating overall class average
def overall_class_average(data):

    average = data["Percentage"].mean()

    return round(average, 2)

# 3. Calculating grade distribution
def grade_distribution(data):

    distribution = data["Grade"].value_counts()

    return distribution.to_dict()

# 4. Top performer 
def top_performers(data, n=3):

    top_students = data.sort_values(
        by="Total",
        ascending=False
    )

    return top_students.head(n)

#5. Failed student
def students_below_threshold(data, threshold=33):

    weak_students = data[
        data["Percentage"] < threshold
    ]

    if weak_students.empty:
        print("Great! No students below the threshold.")
        return

    return weak_students

if __name__ == "__main__":

    # Step 1: Load original data
    data = load_data()

    if data is not None:

        # Step 2: Clean data
        cleaned_data = clean_data(data)

        if cleaned_data is not None and not cleaned_data.empty:

            # Step 3: Calculate performance
            result = calculate_performance(cleaned_data)

            # Step 4: Subject averages
            print("\nSUBJECT-WISE AVERAGES")
            print(subject_wise_average(result))

            # Step 5: Overall class average
            print("\nCLASS AVERAGE")
            print(overall_class_average(result))

            # Step 6: Grade distribution
            print("\nGRADE DISTRIBUTION")
            print(grade_distribution(result))

            # Step 7: Top performers
            print("\nTOP PERFORMERS")
            print(top_performers(result))

            # Step 8: Students below threshold
            print("\nSTUDENTS BELOW 33%")
            if students_below_threshold(result, 33):
                print(students_below_threshold(result, 33))