import sqlite3
import os

# Adjust the path to be relative to this file's location (src/)
# Then navigate to the project root and then to data/
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'school.db')

class Department:
    def __init__(self, name, department_id=None):
        self.department_id = department_id
        self.name = name

    def save(self):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        try:
            if self.department_id is None:
                cursor.execute("INSERT INTO departments (name) VALUES (?)", (self.name,))
                self.department_id = cursor.lastrowid
            else:
                cursor.execute("UPDATE departments SET name = ? WHERE department_id = ?", (self.name, self.department_id))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Department with name '{self.name}' already exists.")
        finally:
            conn.close()
        return self

    @staticmethod
    def delete(department_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM departments WHERE department_id = ?", (department_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(department_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT department_id, name FROM departments WHERE department_id = ?", (department_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Department(name=row[1], department_id=row[0])
        return None

    @staticmethod
    def get_by_name(name):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT department_id, name FROM departments WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Department(name=row[1], department_id=row[0])
        return None

    @staticmethod
    def get_all():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT department_id, name FROM departments")
        rows = cursor.fetchall()
        conn.close()
        return [Department(name=row[1], department_id=row[0]) for row in rows]

    def __repr__(self):
        return f"<Department(id={self.department_id}, name='{self.name}')>"

class Formation:
    def __init__(self, name, duration_years, department_id, formation_id=None):
        self.formation_id = formation_id
        self.name = name
        self.duration_years = duration_years
        self.department_id = department_id

    def save(self):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        try:
            if self.formation_id is None:
                cursor.execute("INSERT INTO formations (name, duration_years, department_id) VALUES (?, ?, ?)",
                               (self.name, self.duration_years, self.department_id))
                self.formation_id = cursor.lastrowid
            else:
                cursor.execute("UPDATE formations SET name = ?, duration_years = ?, department_id = ? WHERE formation_id = ?",
                               (self.name, self.duration_years, self.department_id, self.formation_id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            # Could be due to department_id not existing (FOREIGN KEY constraint)
            # Or other integrity issues if more constraints are added
            raise ValueError(f"Could not save formation. Department ID {self.department_id} may not exist or other integrity constraint failed: {e}")
        finally:
            conn.close()
        return self

    @staticmethod
    def delete(formation_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM formations WHERE formation_id = ?", (formation_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(formation_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT formation_id, name, duration_years, department_id FROM formations WHERE formation_id = ?", (formation_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Formation(name=row[1], duration_years=row[2], department_id=row[3], formation_id=row[0])
        return None

    @staticmethod
    def get_all():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT formation_id, name, duration_years, department_id FROM formations")
        rows = cursor.fetchall()
        conn.close()
        return [Formation(name=row[1], duration_years=row[2], department_id=row[3], formation_id=row[0]) for row in rows]

    @staticmethod
    def get_by_department(department_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT formation_id, name, duration_years, department_id FROM formations WHERE department_id = ?", (department_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Formation(name=row[1], duration_years=row[2], department_id=row[3], formation_id=row[0]) for row in rows]

    def __repr__(self):
        return f"<Formation(id={self.formation_id}, name='{self.name}', duration={self.duration_years}, dept_id={self.department_id})>"

class Student:
    def __init__(self, student_id, first_name, last_name):
        self.student_id = student_id # User-provided PK
        self.first_name = first_name
        self.last_name = last_name

    def save(self):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        # Check if student exists by student_id
        cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (self.student_id,))
        existing_student = cursor.fetchone()

        try:
            if existing_student:
                # Update existing student
                cursor.execute("UPDATE students SET first_name = ?, last_name = ? WHERE student_id = ?",
                               (self.first_name, self.last_name, self.student_id))
            else:
                # Insert new student
                cursor.execute("INSERT INTO students (student_id, first_name, last_name) VALUES (?, ?, ?)",
                               (self.student_id, self.first_name, self.last_name))
            conn.commit()
        except sqlite3.IntegrityError as e:
             # This should ideally not happen for PK if we check first, but other constraints might fail
            raise ValueError(f"Could not save student. Student ID '{self.student_id}' may already exist or another integrity constraint failed: {e}")
        finally:
            conn.close()
        return self

    @staticmethod
    def delete(student_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(student_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, first_name, last_name FROM students WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Student(student_id=row[0], first_name=row[1], last_name=row[2])
        return None

    @staticmethod
    def get_all():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, first_name, last_name FROM students")
        rows = cursor.fetchall()
        conn.close()
        return [Student(student_id=row[0], first_name=row[1], last_name=row[2]) for row in rows]

    def __repr__(self):
        return f"<Student(id='{self.student_id}', name='{self.first_name} {self.last_name}')>"

class Subject:
    def __init__(self, name, credits, year, formation_id, subject_id=None):
        self.subject_id = subject_id
        self.name = name
        self.credits = credits
        self.year = year
        self.formation_id = formation_id

    def save(self):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        try:
            if self.subject_id is None:
                cursor.execute("INSERT INTO subjects (name, credits, year, formation_id) VALUES (?, ?, ?, ?)",
                               (self.name, self.credits, self.year, self.formation_id))
                self.subject_id = cursor.lastrowid
            else:
                cursor.execute("UPDATE subjects SET name = ?, credits = ?, year = ?, formation_id = ? WHERE subject_id = ?",
                               (self.name, self.credits, self.year, self.formation_id, self.subject_id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Could not save subject. Formation ID {self.formation_id} may not exist or other integrity constraint failed: {e}")
        finally:
            conn.close()
        return self

    @staticmethod
    def delete(subject_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE subject_id = ?", (subject_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(subject_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT subject_id, name, credits, year, formation_id FROM subjects WHERE subject_id = ?", (subject_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Subject(name=row[1], credits=row[2], year=row[3], formation_id=row[4], subject_id=row[0])
        return None

    @staticmethod
    def get_all():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT subject_id, name, credits, year, formation_id FROM subjects")
        rows = cursor.fetchall()
        conn.close()
        return [Subject(name=row[1], credits=row[2], year=row[3], formation_id=row[4], subject_id=row[0]) for row in rows]

    @staticmethod
    def get_by_formation_and_year(formation_id, year):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT subject_id, name, credits, year, formation_id FROM subjects WHERE formation_id = ? AND year = ?", (formation_id, year))
        rows = cursor.fetchall()
        conn.close()
        return [Subject(name=row[1], credits=row[2], year=row[3], formation_id=row[4], subject_id=row[0]) for row in rows]

    def __repr__(self):
        return f"<Subject(id={self.subject_id}, name='{self.name}', credits={self.credits}, year={self.year}, form_id={self.formation_id})>"

class Enrollment:
    def __init__(self, student_id, formation_id, enrollment_year, enrollment_id=None):
        self.enrollment_id = enrollment_id
        self.student_id = student_id
        self.formation_id = formation_id
        self.enrollment_year = enrollment_year

    def save(self):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        try:
            if self.enrollment_id is None:
                # Check for existing enrollment for this student in this formation due to UNIQUE constraint
                cursor.execute("SELECT enrollment_id FROM enrollments WHERE student_id = ? AND formation_id = ?",
                               (self.student_id, self.formation_id))
                existing = cursor.fetchone()
                if existing:
                    raise ValueError(f"Student {self.student_id} is already enrolled in formation {self.formation_id}.")

                cursor.execute("INSERT INTO enrollments (student_id, formation_id, enrollment_year) VALUES (?, ?, ?)",
                               (self.student_id, self.formation_id, self.enrollment_year))
                self.enrollment_id = cursor.lastrowid
            else:
                # Update: Be cautious here. What fields of an enrollment should be updatable?
                # Typically, student_id and formation_id would not change (that's a new enrollment).
                # Only enrollment_year might be updatable.
                # For now, let's assume only enrollment_year can be updated.
                # The UNIQUE constraint on (student_id, formation_id) means we can't change those to values that already exist for another enrollment.
                cursor.execute("UPDATE enrollments SET enrollment_year = ? WHERE enrollment_id = ?",
                               (self.enrollment_year, self.enrollment_id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            # Handles FK constraints (student_id, formation_id must exist)
            # and the UNIQUE(student_id, formation_id) constraint if the initial check missed it (race condition, unlikely in this app)
            raise ValueError(f"Could not save enrollment. Student/Formation ID may not exist or student already enrolled in this formation. Error: {e}")
        finally:
            conn.close()
        return self

    @staticmethod
    def delete(enrollment_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM enrollments WHERE enrollment_id = ?", (enrollment_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(enrollment_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT enrollment_id, student_id, formation_id, enrollment_year FROM enrollments WHERE enrollment_id = ?", (enrollment_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Enrollment(student_id=row[1], formation_id=row[2], enrollment_year=row[3], enrollment_id=row[0])
        return None

    @staticmethod
    def get_all():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT enrollment_id, student_id, formation_id, enrollment_year FROM enrollments")
        rows = cursor.fetchall()
        conn.close()
        return [Enrollment(student_id=row[1], formation_id=row[2], enrollment_year=row[3], enrollment_id=row[0]) for row in rows]

    @staticmethod
    def get_by_student(student_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT enrollment_id, student_id, formation_id, enrollment_year FROM enrollments WHERE student_id = ?", (student_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Enrollment(student_id=row[1], formation_id=row[2], enrollment_year=row[3], enrollment_id=row[0]) for row in rows]

    @staticmethod
    def get_by_formation(formation_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT enrollment_id, student_id, formation_id, enrollment_year FROM enrollments WHERE formation_id = ?", (formation_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Enrollment(student_id=row[1], formation_id=row[2], enrollment_year=row[3], enrollment_id=row[0]) for row in rows]

    @staticmethod
    def get_by_student_and_formation(student_id, formation_id):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT enrollment_id, student_id, formation_id, enrollment_year FROM enrollments WHERE student_id = ? AND formation_id = ?", (student_id, formation_id))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Enrollment(student_id=row[1], formation_id=row[2], enrollment_year=row[3], enrollment_id=row[0])
        return None

    def __repr__(self):
        return f"<Enrollment(id={self.enrollment_id}, student='{self.student_id}', formation={self.formation_id}, year={self.enrollment_year})>"

if __name__ == '__main__':
    try:
        from database_setup import initialize_database
        print(f"Using database at: {DATABASE_PATH}")
        # Ensure data directory exists, initialize_database handles this now
        initialize_database()
        print("Database initialized/verified.")

        # Temporary storage for created IDs to ensure cleanup
        dept_ids_to_delete = []
        formation_ids_to_delete = []
        student_ids_to_delete = []
        subject_ids_to_delete = []
        enrollment_ids_to_delete = []

        # --- Testing Department Model ---
        print("\n--- Testing Department Model ---")
        cs_dept = Department(name="Computer Science Test")
        cs_dept.save()
        dept_ids_to_delete.append(cs_dept.department_id)
        print(f"Saved: {cs_dept}")

        math_dept = Department(name="Mathematics Test")
        math_dept.save()
        dept_ids_to_delete.append(math_dept.department_id)
        print(f"Saved: {math_dept}")

        fetched_cs = Department.get_by_id(cs_dept.department_id)
        print(f"Fetched by ID: {fetched_cs}")
        fetched_cs_by_name = Department.get_by_name("Computer Science Test")
        print(f"Fetched by Name: {fetched_cs_by_name}")

        all_depts = Department.get_all()
        print(f"All departments ({len(all_depts)}): {all_depts}")

        try:
            dup_dept = Department(name="Computer Science Test")
            dup_dept.save()
        except ValueError as e:
            print(f"Caught expected error for duplicate dept: {e}")

        fetched_cs.name = "CS Engineering Test"
        fetched_cs.save()
        print(f"Updated dept: {Department.get_by_id(fetched_cs.department_id)}")

        # --- Testing Formation Model ---
        print("\n--- Testing Formation Model ---")
        if not cs_dept.department_id: # Should have an ID after saving
            print("Error: CS Department ID not set for Formation tests.")
        else:
            swe_formation = Formation(name="Software Engineering", duration_years=4, department_id=cs_dept.department_id)
            swe_formation.save()
            formation_ids_to_delete.append(swe_formation.formation_id)
            print(f"Saved: {swe_formation}")

            ds_formation = Formation(name="Data Science", duration_years=3, department_id=cs_dept.department_id)
            ds_formation.save()
            formation_ids_to_delete.append(ds_formation.formation_id)
            print(f"Saved: {ds_formation}")

            fetched_swe = Formation.get_by_id(swe_formation.formation_id)
            print(f"Fetched by ID: {fetched_swe}")

            swe_formation.duration_years = 5
            swe_formation.save()
            print(f"Updated formation: {Formation.get_by_id(swe_formation.formation_id)}")

            formations_in_cs = Formation.get_by_department(cs_dept.department_id)
            print(f"Formations in CS ({len(formations_in_cs)}): {formations_in_cs}")

            all_formations = Formation.get_all()
            print(f"All formations ({len(all_formations)}): {all_formations}")

        # --- Testing Student Model ---
        print("\n--- Testing Student Model ---")
        student1 = Student(student_id="S1001", first_name="John", last_name="Doe")
        student1.save()
        student_ids_to_delete.append(student1.student_id)
        print(f"Saved: {student1}")

        student2 = Student(student_id="S1002", first_name="Jane", last_name="Smith")
        student2.save()
        student_ids_to_delete.append(student2.student_id)
        print(f"Saved: {student2}")

        fetched_s1 = Student.get_by_id("S1001")
        print(f"Fetched by ID: {fetched_s1}")

        fetched_s1.last_name = "Doe Jr."
        fetched_s1.save()
        print(f"Updated student: {Student.get_by_id('S1001')}")

        all_students = Student.get_all()
        print(f"All students ({len(all_students)}): {all_students}")

        # --- Testing Subject Model ---
        print("\n--- Testing Subject Model ---")
        # Requires a formation, use swe_formation if available
        if 'swe_formation' in locals() and swe_formation.formation_id:
            algo_subject = Subject(name="Algorithms", credits=6, year=1, formation_id=swe_formation.formation_id)
            algo_subject.save()
            subject_ids_to_delete.append(algo_subject.subject_id)
            print(f"Saved: {algo_subject}")

            db_subject = Subject(name="Databases", credits=4, year=1, formation_id=swe_formation.formation_id)
            db_subject.save()
            subject_ids_to_delete.append(db_subject.subject_id)
            print(f"Saved: {db_subject}")

            fetched_algo = Subject.get_by_id(algo_subject.subject_id)
            print(f"Fetched by ID: {fetched_algo}")

            algo_subject.credits = 5
            algo_subject.save()
            print(f"Updated subject: {Subject.get_by_id(algo_subject.subject_id)}")

            subjects_in_swe_y1 = Subject.get_by_formation_and_year(swe_formation.formation_id, 1)
            print(f"Subjects in SWE Year 1 ({len(subjects_in_swe_y1)}): {subjects_in_swe_y1}")

            all_subjects = Subject.get_all()
            print(f"All subjects ({len(all_subjects)}): {all_subjects}")
        else:
            print("Skipping Subject tests as prerequisite formation not available.")

        # --- Testing Enrollment Model ---
        print("\n--- Testing Enrollment Model ---")
        # Requires student, formation (which requires department)
        if ('student1' in locals() and student1.student_id and
            'swe_formation' in locals() and swe_formation.formation_id):

            enrollment1 = Enrollment(student_id=student1.student_id,
                                     formation_id=swe_formation.formation_id,
                                     enrollment_year=2023)
            enrollment1.save()
            enrollment_ids_to_delete.append(enrollment1.enrollment_id)
            print(f"Saved: {enrollment1}")

            fetched_enrollment = Enrollment.get_by_id(enrollment1.enrollment_id)
            print(f"Fetched by ID: {fetched_enrollment}")

            enrollments_for_s1 = Enrollment.get_by_student(student1.student_id)
            print(f"Enrollments for student {student1.student_id} ({len(enrollments_for_s1)}): {enrollments_for_s1}")

            enrollments_in_swe = Enrollment.get_by_formation(swe_formation.formation_id)
            print(f"Enrollments in formation {swe_formation.formation_id} ({len(enrollments_in_swe)}): {enrollments_in_swe}")

            s1_swe_enrollment = Enrollment.get_by_student_and_formation(student1.student_id, swe_formation.formation_id)
            print(f"Enrollment for S1 in SWE: {s1_swe_enrollment}")

            # Test update
            enrollment1.enrollment_year = 2024
            enrollment1.save()
            updated_enrollment1 = Enrollment.get_by_id(enrollment1.enrollment_id)
            print(f"Updated enrollment: {updated_enrollment1}")

            # Test duplicate enrollment
            print("Attempting to create duplicate enrollment...")
            try:
                enrollment_dup = Enrollment(student_id=student1.student_id,
                                            formation_id=swe_formation.formation_id,
                                            enrollment_year=2025)
                enrollment_dup.save()
                enrollment_ids_to_delete.append(enrollment_dup.enrollment_id) # Should not happen
                print(f"ERROR: Duplicate enrollment created: {enrollment_dup}")
            except ValueError as e_dup:
                print(f"Caught expected error for duplicate enrollment: {e_dup}")

            all_enrollments = Enrollment.get_all()
            print(f"All enrollments ({len(all_enrollments)}): {all_enrollments}")
        else:
            print("Skipping Enrollment tests as prerequisite student or formation not available.")

    except Exception as e:
        print(f"An error occurred during the test run: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # --- Cleanup ---
        print("\n--- Cleaning up test data ---")
        # Delete in reverse order of creation (roughly, due to dependencies)
        # Enrollments and Grades should be deleted before Subjects, Students, Formations, Departments.
        for enrollment_id in enrollment_ids_to_delete:
            Enrollment.delete(enrollment_id)
            print(f"Deleted Enrollment ID: {enrollment_id}")

        for subject_id in subject_ids_to_delete:
            Subject.delete(subject_id)
            print(f"Deleted Subject ID: {subject_id}")
        for formation_id in formation_ids_to_delete:
            Formation.delete(formation_id)
            print(f"Deleted Formation ID: {formation_id}")
        for student_id in student_ids_to_delete:
            Student.delete(student_id)
            print(f"Deleted Student ID: {student_id}")
        for dept_id in dept_ids_to_delete:
            Department.delete(dept_id)
            print(f"Deleted Department ID: {dept_id}")

        print("\n--- Final State Check ---")
        print(f"Remaining Departments: {len(Department.get_all())}")
        print(f"Remaining Formations: {len(Formation.get_all())}")
        print(f"Remaining Students: {len(Student.get_all())}")
        print(f"Remaining Subjects: {len(Subject.get_all())}")
        print(f"Remaining Enrollments: {len(Enrollment.get_all())}")
        print("Cleanup finished.")
