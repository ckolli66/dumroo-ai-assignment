import csv
import random
from datetime import datetime, timedelta

names = [
    "Ava Patel", "Liam Smith", "Sophia Lee", "Noah Kim", "Mia Chen", "Ethan Brown",
    "Isabella Garcia", "Mason Wilson", "Charlotte Martinez", "Logan Anderson",
    "Oliver Clark", "Emma Davis", "Benjamin Hall", "Amelia Young", "Lucas King",
    "Harper Wright", "Elijah Scott", "Emily Green", "James Adams", "Abigail Baker"
]
classes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
grades = ["A", "B", "C"]
statuses = ["Submitted", "Pending", "Missing"]

with open("student_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["student_name", "class", "grade", "submission_status", "quiz_score", "quiz_date"])
    for _ in range(200):
            name = random.choice(names)
            cls = random.choice(classes)
            grade = random.choice(grades)
            status = random.choice(statuses)
            score = random.randint(0, 100) if status != "Missing" else 0
            start_date = datetime(2025, 7, 1)
            end_date = datetime(2026, 6, 30)
            random_days = random.randint(0, (end_date - start_date).days)
            date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
            writer.writerow([name, cls, grade, status, score, date])