import sys
from PyQt6 import QtWidgets, QtCore, QtGui

try:
    from ..models import Student, Formation, Enrollment, Department # Department might be needed for context via Formation
    from ..database_setup import initialize_database # For standalone testing if needed
except ImportError as e:
    print(f"Relative import failed in enrollment_ui.py: {e}. Attempting fallbacks.")
    try:
        from models import Student, Formation, Enrollment, Department
        from database_setup import initialize_database
    except ModuleNotFoundError:
        print("Fallback import also failed in enrollment_ui.py. Define dummy classes for syntax check.")
        class Student: pass
        class Formation: pass
        class Enrollment: pass
        class Department: pass # Added for completeness if Formation needs it
        def initialize_database(): pass

class EnrollmentWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Enrollments")
        # self.setGeometry(300, 300, 600, 500) # Optional

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Input Area
        self.input_grid_layout = QtWidgets.QGridLayout() # Using grid for better alignment

        self.student_label = QtWidgets.QLabel("Select Student:")
        self.student_combo = QtWidgets.QComboBox()
        self.input_grid_layout.addWidget(self.student_label, 0, 0)
        self.input_grid_layout.addWidget(self.student_combo, 0, 1)

        self.formation_label = QtWidgets.QLabel("Select Formation:")
        self.formation_combo = QtWidgets.QComboBox()
        self.input_grid_layout.addWidget(self.formation_label, 1, 0)
        self.input_grid_layout.addWidget(self.formation_combo, 1, 1)

        self.year_label = QtWidgets.QLabel("Enrollment Year:")
        self.year_spinbox = QtWidgets.QSpinBox()
        current_year = QtCore.QDate.currentDate().year()
        self.year_spinbox.setMinimum(current_year - 5) # Enroll for past 5 years
        self.year_spinbox.setMaximum(current_year + 1) # Enroll for current or next year
        self.year_spinbox.setValue(current_year)      # Default to current year
        self.input_grid_layout.addWidget(self.year_label, 2, 0)
        self.input_grid_layout.addWidget(self.year_spinbox, 2, 1)

        self.main_layout.addLayout(self.input_grid_layout)

        self.enroll_button = QtWidgets.QPushButton("Enroll Student")
        self.enroll_button.clicked.connect(self.enroll_student)
        self.main_layout.addWidget(self.enroll_button)

        # Display Area for Enrollments
        self.enrollment_list_label = QtWidgets.QLabel("Current Enrollments:")
        self.enrollment_list = QtWidgets.QListWidget()
        self.main_layout.addWidget(self.enrollment_list_label)
        self.main_layout.addWidget(self.enrollment_list)

        self.refresh_button = QtWidgets.QPushButton("Refresh All Data")
        self.refresh_button.clicked.connect(self.load_all_data)
        self.main_layout.addWidget(self.refresh_button)

        self.setLayout(self.main_layout)

        # Initial Load
        self.load_all_data()

    def load_all_data(self):
        self.load_students_into_combobox()
        self.load_formations_into_combobox()
        self.load_enrollments_list()

    def load_students_into_combobox(self):
        self.student_combo.clear()
        try:
            students = Student.get_all()
            if not students:
                self.student_combo.addItem("No students available", None)
                self.student_combo.setEnabled(False)
            else:
                self.student_combo.setEnabled(True)
                for s in students:
                    display_text = f"{s.first_name} {s.last_name} ({s.student_id})"
                    self.student_combo.addItem(display_text, s.student_id) # UserData is student_id
        except Exception as e:
            print(f"Error loading students into combobox: {e}")
            self.student_combo.addItem("Error loading students", None)
            self.student_combo.setEnabled(False)

    def load_formations_into_combobox(self):
        self.formation_combo.clear()
        try:
            formations = Formation.get_all()
            if not formations:
                self.formation_combo.addItem("No formations available", None)
                self.formation_combo.setEnabled(False)
            else:
                self.formation_combo.setEnabled(True)
                for f in formations:
                    self.formation_combo.addItem(f.name, f.formation_id) # UserData is formation_id
        except Exception as e:
            print(f"Error loading formations into combobox: {e}")
            self.formation_combo.addItem("Error loading formations", None)
            self.formation_combo.setEnabled(False)

    def load_enrollments_list(self):
        self.enrollment_list.clear()
        try:
            enrollments = Enrollment.get_all()
            if not enrollments:
                self.enrollment_list.addItem(QtWidgets.QListWidgetItem("No enrollments found."))
                return

            # Optimization: Fetch all students and formations into dicts for quick lookup
            students_dict = {s.student_id: s for s in Student.get_all()}
            formations_dict = {f.formation_id: f for f in Formation.get_all()}

            for e in enrollments:
                student = students_dict.get(e.student_id)
                formation = formations_dict.get(e.formation_id)

                student_name = f"{student.first_name} {student.last_name}" if student else "Unknown Student"
                formation_name = formation.name if formation else "Unknown Formation"

                item_text = f"{student_name} in {formation_name} (Year: {e.enrollment_year})"
                item = QtWidgets.QListWidgetItem(item_text)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, e.enrollment_id)
                self.enrollment_list.addItem(item)
        except Exception as e:
            print(f"Error loading enrollments list: {e}")
            self.enrollment_list.addItem(QtWidgets.QListWidgetItem(f"Error loading enrollments: {e}"))


    def enroll_student(self):
        student_id = self.student_combo.currentData()
        formation_id = self.formation_combo.currentData()
        enrollment_year_val = self.year_spinbox.value()

        if student_id is None:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please select a student.")
            return
        if formation_id is None:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please select a formation.")
            return
        # Year validation is mostly handled by spinbox range, but can add more if needed

        try:
            new_enrollment = Enrollment(student_id=student_id,
                                        formation_id=formation_id,
                                        enrollment_year=enrollment_year_val)
            new_enrollment.save() # This save method should handle UNIQUE constraint violations

            # Optionally reset inputs, though for enrollments, user might want to enroll multiple students
            # in the same formation/year or same student in different formations over time.
            # For now, just refresh the list.
            self.load_enrollments_list()
            # QtWidgets.QMessageBox.information(self, "Success", "Student enrolled successfully.")
        except ValueError as ve: # Custom error from model (e.g., duplicate enrollment, FK violation)
            QtWidgets.QMessageBox.warning(self, "Enrollment Error", str(ve))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred during enrollment: {e}")


if __name__ == '__main__':
    print("Enrollment UI Script - Basic Syntax Check Mode")

    # For true standalone testing, we'd need a QApplication and dummy data.
    # This is complex due to dependencies (Department -> Formation, Student -> Enrollment).
    # The primary goal here is code generation and syntax validity.

    try:
        print("Attempting to initialize database for direct test of enrollment_ui.py...")
        initialize_database() # From this file's imports
        print("Database initialized (called from enrollment_ui.py direct test block).")

        # Create dummy data for comboboxes to populate for a basic instantiation test
        # Department for Formation
        dept_enroll_ui_test = Department.get_by_name("EnrollUI Test Dept")
        if not dept_enroll_ui_test:
            dept_enroll_ui_test = Department(name="EnrollUI Test Dept")
            dept_enroll_ui_test.save()

        # Formation
        form_enroll_ui_test = Formation.get_by_name("EnrollUI Test Formation") # Assuming simple get_by_name
        if not form_enroll_ui_test: # More robust check would be by name AND dept_id
             existing_forms = Formation.get_by_department(dept_enroll_ui_test.department_id)
             found = any(f.name == "EnrollUI Test Formation" for f in existing_forms)
             if not found:
                form_enroll_ui_test = Formation(name="EnrollUI Test Formation", duration_years=3, department_id=dept_enroll_ui_test.department_id)
                form_enroll_ui_test.save()

        # Student
        stud_enroll_ui_test = Student.get_by_id("EnrollUITestS001")
        if not stud_enroll_ui_test:
            stud_enroll_ui_test = Student(student_id="EnrollUITestS001", first_name="EnrollTest", last_name="User")
            stud_enroll_ui_test.save()

    except Exception as e_db_setup:
        print(f"Database/test data setup failed in enrollment_ui.py: {e_db_setup}")

    app_instance = QtWidgets.QApplication.instance()
    if not app_instance:
        app_instance = QtWidgets.QApplication(sys.argv)

    if not app_instance:
        print("CRITICAL: QApplication could not be initialized for test.")
        sys.exit(1)

    try:
        window = EnrollmentWindow()
        print(f"EnrollmentWindow instantiated successfully: {window.windowTitle()}")
        # Basic method call checks
        print(f"Students in combo: {window.student_combo.count()}")
        print(f"Formations in combo: {window.formation_combo.count()}")
        print(f"Enrollments in list after initial load: {window.enrollment_list.count()}")
        print("Enrollment UI Script - Basic syntax and instantiation check complete.")
    except Exception as e_inst:
        print(f"Error during EnrollmentWindow instantiation or method calls: {e_inst}")
        import traceback
        traceback.print_exc()

    sys.exit(0) # Exit cleanly
```
