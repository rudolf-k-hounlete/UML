import sys
from PyQt6 import QtWidgets, QtCore, QtGui

try:
    from ..models import Student
    from ..database_setup import initialize_database # For standalone testing if needed
except ImportError as e:
    print(f"Relative import failed in student_ui.py: {e}. Attempting fallbacks.")
    try:
        from models import Student
        from database_setup import initialize_database
    except ModuleNotFoundError:
        print("Fallback import also failed in student_ui.py. Define dummy classes for syntax check.")
        class Student: pass
        def initialize_database(): pass

class StudentWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Students")
        # self.setGeometry(250, 250, 500, 400) # Optional

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Input Fields for New Student
        self.input_form_layout = QtWidgets.QFormLayout()
        self.student_id_input = QtWidgets.QLineEdit()
        self.student_id_input.setPlaceholderText("e.g., S001, 10023, etc.")
        self.first_name_input = QtWidgets.QLineEdit()
        self.first_name_input.setPlaceholderText("Enter first name")
        self.last_name_input = QtWidgets.QLineEdit()
        self.last_name_input.setPlaceholderText("Enter last name")

        self.input_form_layout.addRow("Student ID:", self.student_id_input)
        self.input_form_layout.addRow("First Name:", self.first_name_input)
        self.input_form_layout.addRow("Last Name:", self.last_name_input)

        self.main_layout.addLayout(self.input_form_layout)

        self.add_student_button = QtWidgets.QPushButton("Add/Update Student") # Button text reflects save logic
        self.add_student_button.clicked.connect(self.add_student)
        self.main_layout.addWidget(self.add_student_button)

        # Display Area for Students
        self.student_list_label = QtWidgets.QLabel("Registered Students:")
        self.student_list_widget = QtWidgets.QListWidget()
        self.main_layout.addWidget(self.student_list_label)
        self.main_layout.addWidget(self.student_list_widget)

        self.refresh_button = QtWidgets.QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.load_students)
        self.main_layout.addWidget(self.refresh_button)

        self.setLayout(self.main_layout)

        # Initial Load
        self.load_students()

    def load_students(self):
        self.student_list_widget.clear()
        try:
            students = Student.get_all()
            if not students:
                self.student_list_widget.addItem(QtWidgets.QListWidgetItem("No students found."))
            else:
                for stud in students:
                    item_text = f"ID: {stud.student_id}, Name: {stud.first_name} {stud.last_name}"
                    item = QtWidgets.QListWidgetItem(item_text)
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, stud.student_id) # Store student_id
                    self.student_list_widget.addItem(item)
        except Exception as e:
            print(f"Error loading students: {e}")
            #QtWidgets.QMessageBox.critical(self, "Error", f"Could not load students: {e}")
            self.student_list_widget.addItem(QtWidgets.QListWidgetItem(f"Error loading students: {e}"))

    def add_student(self):
        student_id = self.student_id_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()

        if not student_id:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Student ID cannot be empty.")
            return
        if not first_name:
            QtWidgets.QMessageBox.warning(self, "Input Error", "First name cannot be empty.")
            return
        if not last_name:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Last name cannot be empty.")
            return

        try:
            # The Student model's save() method handles both insert and update.
            student_to_save = Student(student_id=student_id, first_name=first_name, last_name=last_name)
            student_to_save.save()

            self.student_id_input.clear()
            self.first_name_input.clear()
            self.last_name_input.clear()
            self.load_students() # Refresh the list
            # QtWidgets.QMessageBox.information(self, "Success", f"Student '{first_name} {last_name}' (ID: {student_id}) saved successfully.")
        except ValueError as ve: # If Student.save() raises ValueError for specific issues
            QtWidgets.QMessageBox.warning(self, "Error Saving Student", str(ve))
        except Exception as e:
            # Catch any other unexpected errors during save
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred while saving student: {e}")


if __name__ == '__main__':
    print("Student UI Script - Basic Syntax Check Mode")

    # Attempt to initialize DB for basic model interaction if possible
    try:
        print("Attempting to initialize database for direct test of student_ui.py...")
        initialize_database() # From this file's imports
        print("Database initialized (called from student_ui.py direct test block).")
    except Exception as e_db_setup:
        print(f"Database initialization failed in student_ui.py: {e_db_setup}")

    app_instance = QtWidgets.QApplication.instance()
    if not app_instance:
        app_instance = QtWidgets.QApplication(sys.argv)

    if not app_instance:
        print("CRITICAL: QApplication could not be initialized for test.")
        sys.exit(1)

    try:
        window = StudentWindow()
        print(f"StudentWindow instantiated successfully: {window.windowTitle()}")
        # Basic method call
        window.load_students()
        print(f"Students in list after initial load: {window.student_list_widget.count()}")
        print("Student UI Script - Basic syntax and instantiation check complete.")
    except Exception as e_inst:
        print(f"Error during StudentWindow instantiation or method calls: {e_inst}")
        import traceback
        traceback.print_exc()

    sys.exit(0) # Exit cleanly
```
