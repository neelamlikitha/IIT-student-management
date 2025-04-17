import datetime

class Student:
    def __init__(self, student_id, name, grade):
        self.student_id = student_id
        self.name = name
        self.grade = grade
        self.attendance = {}

    def mark_attendance(self, date, status):
        self.attendance[date] = status

    def get_attendance(self):
        return self.attendance


class Teacher:
    def __init__(self, teacher_id, name):
        self.teacher_id = teacher_id
        self.name = name

    def __str__(self):
        return f"Teacher ID: {self.teacher_id}, Name: {self.name}"


class StudentManagementSystem:
    def __init__(self):
        self.students = {}
        self.teachers = {}

    def add_student(self, student_id, name, grade):
        self.students[student_id] = Student(student_id, name, grade)

    def add_teacher(self, teacher_id, name):
        self.teachers[teacher_id] = Teacher(teacher_id, name)

    def get_student(self, student_id):
        return self.students.get(student_id)

    def get_teacher(self, teacher_id):
        return self.teachers.get(teacher_id)

    def mark_student_attendance(self, student_id, date, status):
        student = self.get_student(student_id)
        if student:
            student.mark_attendance(date, status)

    def get_student_attendance(self, student_id):
        student = self.get_student(student_id)
        if student:
            return student.get_attendance()

    def display_output(self):
        print("#"*50)
        print("Student Management System".center(50))
        print("#"*50)
        print("\nStudent Enrollment".center(50))
        print("-"*50)
        print(f"| {'Student ID':^10} | {'Name':^20} | {'Grade':^5} |")
        print("-"*50)
        for student_id, student in self.students.items():
            print(f"| {student_id:^10} | {student.name:^20} | {student.grade:^5} |")
        print("-"*50)

        print("\nTeacher Details".center(50))
        print("-"*50)
        print(f"| {'Teacher ID':^10} | {'Name':^20} |")
        print("-"*50)
        for teacher_id, teacher in self.teachers.items():
            print(f"| {teacher_id:^10} | {teacher.name:^20} |")
        print("-"*50)

        print("\nAttendance Tracking".center(50))
        print("-"*50)
        print(f"| {'Student ID':^10} | {'Date':^15} | {'Status':^6} |")
        print("-"*50)
        for student_id, student in self.students.items():
            for date, status in student.attendance.items():
                print(f"| {student_id:^10} | {str(date):^15} | {status:^6} |")
        print("-"*50)

        for student_id in self.students:
            print(f"\nStudent {student_id} Attendance".center(50))
            print("-"*50)
            print(f"| {'Date':^15} | {'Status':^6} |")
            print("-"*50)
            student = self.get_student(student_id)
            if student:
                for date, status in student.attendance.items():
                    print(f"| {str(date):^15} | {status:^6} |")
            print("-"*50)


def main():
    sms = StudentManagementSystem()

    # Add students
    sms.add_student("S1", "John Doe", "A")
    sms.add_student("S2", "Jane Doe", "B")

    # Add teachers
    sms.add_teacher("T1", "Mr. Smith")
    sms.add_teacher("T2", "Ms. Johnson")

    # Mark student attendance
    sms.mark_student_attendance("S1", datetime.date.today(), "Present")
    sms.mark_student_attendance("S2", datetime.date.today(), "Absent")

    # Display output
    sms.display_output()


if __name__ == "__main__":
    main()
    