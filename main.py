import json
import os


class InvalidStudentData(Exception):
    pass


def check_student_Data(record):
    if not isinstance(record, dict):
        raise TypeError("Student record must be a dictionary.")

    student_id = record["student_id"]
    name = record["name"]
    department = record["department"]
    marks = record["marks"]

    if not isinstance(student_id, str) or not student_id.strip():
        raise ValueError("Invalid student ID.")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Invalid student name.")

    if not isinstance(department, str) or not department.strip():
        raise ValueError("Invalid department.")

    if not isinstance(marks, list) or len(marks) != 3:
        raise InvalidStudentData(
            "Marks must contain exactly 3 values between 0 and 100."
        )

    for mark in marks:
        if isinstance(mark, bool) or not isinstance(mark, (int, float)):
            raise InvalidStudentData("Marks must be numeric values.")

        if mark < 0 or mark > 100:
            raise InvalidStudentData("Marks must be between 0 and 100.")

    return record


def save_rejected_record(errors):
    try:
        with open("import_errors.txt", "w") as file:
            for error in errors:
                file.write(error + "\n")
    except OSError as e:
        print("Error while writing error log:", e)


def main():
    source_path = input("Enter input file path (press Enter for default): ")
    if not source_path.strip():
        source_path = "students_input.json"

    print("\nImport started:", source_path)

    try:
        with open(source_path, "r") as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise TypeError("JSON data must contain a list of records.")

    except FileNotFoundError:
        print("Error: Input file not found.")
        save_rejected_record(["Input file not found: " + source_path])
        return

    except PermissionError:
        print("Error: Permission denied while reading the file.")
        save_rejected_record(["Permission denied: " + source_path])
        return

    except json.JSONDecodeError as e:
        print("Error: Invalid JSON format:", e)
        save_rejected_record(["Invalid JSON format: " + str(e)])
        return

    except (TypeError, ValueError) as e:
        print("Error:", e)
        save_rejected_record([str(e)])
        return

    except OSError as e:
        print("File error:", e)
        save_rejected_record(["File error: " + str(e)])
        return

    else:
        print("Input file read successfully.")

    finally:
        print("Input reading process finished.\n")

    accepted_students = []
    errors = []
    student_ids = set()

    for i, record in enumerate(records, start=1):
        try:
            student = check_student_Data(record)

            if student["student_id"] in student_ids:
                raise InvalidStudentData("Duplicate student ID.")

            student_ids.add(student["student_id"])
            accepted_students.append(student)

            print("Accepted:", student["student_id"], "-", student["name"])

        except InvalidStudentData as e:
            errors.append(f"Record {i}: {e}")
            print(f"Rejected record {i}:", e)

        except KeyError as e:
            errors.append(f"Record {i}: Missing required field {e}")
            print(f"Rejected record {i}: Missing required field {e}")

        except TypeError as e:
            errors.append(f"Record {i}: {e}")
            print(f"Rejected record {i}:", e)

        except ValueError as e:
            errors.append(f"Record {i}: {e}")
            print(f"Rejected record {i}:", e)

        except IndexError as e:
            errors.append(f"Record {i}: {e}")
            print(f"Rejected record {i}:", e)

    try:
        with open("students_valid.json", "w") as file:
            json.dump(accepted_students, file, indent=4)

        save_rejected_record(errors)

        print("\nImport completed.")
        print("Accepted records:", len(accepted_students))
        print("Rejected records:", len(errors))
        print("Valid output:", os.path.abspath("students_valid.json"))
        print("Error log:", os.path.abspath("import_errors.txt"))

    except OSError as e:
        print("Error while writing output files:", e)


if __name__ == "__main__":
    main()
