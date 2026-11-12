import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

from flask import Flask, abort, flash, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = Path(os.environ.get("DATA_FILE", str(BASE_DIR / "instance" / "records.json")))
STUDENT_FIELDS = ("student_id", "name", "grade")
ATTENDANCE_STATUSES = ("Present", "Absent")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "local-development-key")


def load_store() -> dict[str, list[dict[str, Any]]]:
    if not DATA_FILE.exists():
        return {"students": [], "teachers": []}

    with DATA_FILE.open("r", encoding="utf-8") as data_file:
        store = json.load(data_file)

    if (
        not isinstance(store, dict)
        or not isinstance(store.get("students"), list)
        or not isinstance(store.get("teachers"), list)
    ):
        raise ValueError(f"Invalid student management data format in {DATA_FILE}")
    return store


def save_store(store: dict[str, list[dict[str, Any]]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_FILE.parent,
            suffix=".tmp",
            delete=False,
        ) as data_file:
            temporary_path = Path(data_file.name)
            json.dump(store, data_file, indent=2)
            data_file.write("\n")
        temporary_path.replace(DATA_FILE)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def find_record(records: list[dict[str, Any]], field: str, value: str) -> dict[str, Any] | None:
    return next((record for record in records if record.get(field) == value), None)


def get_student_or_404(store: dict[str, list[dict[str, Any]]], student_id: str) -> dict[str, Any]:
    student = find_record(store["students"], "student_id", student_id)
    if student is None:
        abort(404)
    return student


def clean_form_values(*fields: str) -> dict[str, str]:
    return {field: request.form.get(field, "").strip() for field in fields}


@app.get("/")
def dashboard():
    store = load_store()
    students = store["students"]
    attendance = [
        {
            "student_id": student["student_id"],
            "student_name": student["name"],
            "date": attendance_date,
            "status": status,
        }
        for student in students
        for attendance_date, status in student.get("attendance", {}).items()
    ]
    attendance.sort(key=lambda entry: entry["date"], reverse=True)
    return render_template(
        "dashboard.html",
        student_count=len(students),
        teacher_count=len(store["teachers"]),
        attendance_count=len(attendance),
        recent_attendance=attendance[:5],
    )


@app.route("/students", methods=["GET", "POST"])
def students():
    store = load_store()
    if request.method == "POST":
        values = clean_form_values(*STUDENT_FIELDS)
        if not all(values.values()):
            flash("Enter a student ID, name, and grade.", "error")
        elif find_record(store["students"], "student_id", values["student_id"]):
            flash("That student ID is already in use.", "error")
        else:
            store["students"].append({**values, "attendance": {}})
            save_store(store)
            flash("Student added successfully.", "success")
            return redirect(url_for("students"))
    return render_template("students.html", students=store["students"])


@app.route("/students/<student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id: str):
    store = load_store()
    student = get_student_or_404(store, student_id)
    if request.method == "POST":
        values = clean_form_values("name", "grade")
        if not all(values.values()):
            flash("Enter the student's name and grade.", "error")
        else:
            student.update(values)
            save_store(store)
            flash("Student updated successfully.", "success")
            return redirect(url_for("students"))
    return render_template("student_form.html", student=student)


@app.post("/students/<student_id>/delete")
def delete_student(student_id: str):
    store = load_store()
    student = get_student_or_404(store, student_id)
    store["students"].remove(student)
    save_store(store)
    flash("Student and their attendance records deleted.", "success")
    return redirect(url_for("students"))


@app.route("/teachers", methods=["GET", "POST"])
def teachers():
    store = load_store()
    if request.method == "POST":
        values = clean_form_values("teacher_id", "name")
        if not all(values.values()):
            flash("Enter a teacher ID and name.", "error")
        elif find_record(store["teachers"], "teacher_id", values["teacher_id"]):
            flash("That teacher ID is already in use.", "error")
        else:
            store["teachers"].append(values)
            save_store(store)
            flash("Teacher added successfully.", "success")
            return redirect(url_for("teachers"))
    return render_template("teachers.html", teachers=store["teachers"])


@app.route("/teachers/<teacher_id>/edit", methods=["GET", "POST"])
def edit_teacher(teacher_id: str):
    store = load_store()
    teacher = find_record(store["teachers"], "teacher_id", teacher_id)
    if teacher is None:
        abort(404)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Enter the teacher's name.", "error")
        else:
            teacher["name"] = name
            save_store(store)
            flash("Teacher updated successfully.", "success")
            return redirect(url_for("teachers"))
    return render_template("teacher_form.html", teacher=teacher)


@app.post("/teachers/<teacher_id>/delete")
def delete_teacher(teacher_id: str):
    store = load_store()
    teacher = find_record(store["teachers"], "teacher_id", teacher_id)
    if teacher is None:
        abort(404)
    store["teachers"].remove(teacher)
    save_store(store)
    flash("Teacher deleted successfully.", "success")
    return redirect(url_for("teachers"))


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    store = load_store()
    if request.method == "POST":
        values = clean_form_values("student_id", "date", "status")
        student = find_record(store["students"], "student_id", values["student_id"])
        try:
            parsed_date = date.fromisoformat(values["date"])
            if parsed_date.isoformat() != values["date"]:
                parsed_date = None
        except ValueError:
            parsed_date = None

        if student is None:
            flash("Select a valid student.", "error")
        elif parsed_date is None:
            flash("Enter a valid attendance date.", "error")
        elif values["status"] not in ATTENDANCE_STATUSES:
            flash("Choose Present or Absent for the attendance status.", "error")
        elif values["date"] in student.setdefault("attendance", {}):
            flash("Attendance is already recorded for this student and date.", "error")
        else:
            student["attendance"][values["date"]] = values["status"]
            save_store(store)
            flash("Attendance recorded successfully.", "success")
            return redirect(url_for("attendance"))
    return render_template(
        "attendance.html",
        students=store["students"],
        today=date.today().isoformat(),
        records=[
            {
                "student_id": student["student_id"],
                "student_name": student["name"],
                "date": attendance_date,
                "status": status,
            }
            for student in store["students"]
            for attendance_date, status in student.get("attendance", {}).items()
        ],
    )


@app.route("/attendance/<student_id>/<attendance_date>/edit", methods=["GET", "POST"])
def edit_attendance(student_id: str, attendance_date: str):
    store = load_store()
    student = get_student_or_404(store, student_id)
    records = student.setdefault("attendance", {})
    if attendance_date not in records:
        abort(404)
    if request.method == "POST":
        values = clean_form_values("date", "status")
        try:
            parsed_date = date.fromisoformat(values["date"])
        except ValueError:
            parsed_date = None
        if parsed_date is None or parsed_date.isoformat() != values["date"]:
            flash("Enter a valid attendance date.", "error")
        else:
            if values["status"] not in ATTENDANCE_STATUSES:
                flash("Choose Present or Absent for the attendance status.", "error")
            elif values["date"] != attendance_date and values["date"] in records:
                flash("Attendance is already recorded for this student and date.", "error")
            else:
                del records[attendance_date]
                records[values["date"]] = values["status"]
                save_store(store)
                flash("Attendance updated successfully.", "success")
                return redirect(url_for("attendance"))
    return render_template(
        "attendance_form.html",
        student=student,
        attendance_date=attendance_date,
        status=records[attendance_date],
    )


@app.post("/attendance/<student_id>/<attendance_date>/delete")
def delete_attendance(student_id: str, attendance_date: str):
    store = load_store()
    student = get_student_or_404(store, student_id)
    records = student.setdefault("attendance", {})
    if attendance_date not in records:
        abort(404)
    del records[attendance_date]
    save_store(store)
    flash("Attendance record deleted.", "success")
    return redirect(url_for("attendance"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
