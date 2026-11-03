
import pandas as pd
import os

# Required columns
REQUIRED_COLUMNS = [
    "roll_number",
    "name",
    "Maths",
    "Physics",
    "Chemistry",
    "English",
    "Computer"
]

SUBJECTS = [
    "Maths",
    "Physics",
    "Chemistry",
    "English",
    "Computer"
]


# Get project folder
def get_data_folder():
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, "data")


# Load CSV file
def load_data():
    folder = get_data_folder()
    file_path = os.path.join(
        folder, "students_with _errors.csv"
    )

    try:
        data = pd.read_csv(file_path)
        print("Dataset Loaded Successfully!")
        print("Total Rows:", len(data))
        return data

    except FileNotFoundError:
        print("Error: CSV file not found!")
        print("Check the file name and data folder.")
        return None

    except Exception as e:
        print("Error loading CSV:", e)
        return None


# Validate and clean student data
def clean_data(data):
    print("\nChecking Dataset...")

    # Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in data.columns
    ]

    if missing_columns:
        print("Missing Columns:", missing_columns)
        print("Cannot clean this dataset.")
        return None

    original_rows = len(data)
    data = data.copy()

    # Remove completely empty rows
    data = data.dropna(how="all")

    # Remove missing or blank student names
    data["name"] = data["name"].astype("string").str.strip()
    data = data[
        data["name"].notna() & data["name"].ne("")
    ].copy()

    # Remove missing roll numbers
    data["roll_number"] = (
        data["roll_number"].astype("string").str.strip()
    )

    data = data[
        data["roll_number"].notna()
        & data["roll_number"].ne("")
    ].copy()

    # Remove duplicate roll numbers
    duplicate_rows = data["roll_number"].duplicated(
        keep=False
    )

    if duplicate_rows.any():
        print("\nDuplicate Roll Numbers Found:")
        print(data.loc[duplicate_rows, ["roll_number", "name"]])

        data = data[~duplicate_rows].copy()

    # Convert marks to numbers
    for subject in SUBJECTS:
        data[subject] = pd.to_numeric(
            data[subject], errors="coerce"
        )

    # Remove missing, non-numeric and out-of-range marks
    for subject in SUBJECTS:
        invalid = (
            data[subject].isna()
            | (data[subject] < 0)
            | (data[subject] > 100)
        )

        if invalid.any():
            print("\nInvalid marks found in:", subject)
            print(
                data.loc[invalid, ["roll_number", "name", subject]]
            )

            data = data[~invalid].copy()

    # Save cleaned CSV
    output_path = os.path.join(
        get_data_folder(), "students_cleaned.csv"
    )

    try:
        data.to_csv(output_path, index=False)

        print("\nCleaning Completed!")
        print("Original Rows:", original_rows)
        print("Cleaned Rows:", len(data))
        print("Removed Rows:", original_rows - len(data))
        print("Cleaned CSV saved at:")
        print(output_path)

        return data

    except Exception as e:
        print("Error saving cleaned CSV:", e)
        return None


# Main program
if __name__ == "__main__":
    data = load_data()

    if data is not None:
        cleaned_data = clean_data(data)

        if cleaned_data is not None:
            print("\nCleaned Dataset Preview:")
            print(cleaned_data.head(10).to_string(index=False))

