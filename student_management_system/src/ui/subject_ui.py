import sys
from PyQt6 import QtWidgets, QtCore, QtGui

try:
    from ..models import Subject, Formation # Formation might be needed for context or future enhancements
    from ..database_setup import initialize_database # For standalone testing
except ImportError as e:
    print(f"Relative import failed in subject_ui.py: {e}. Attempting fallbacks.")
    try:
        from models import Subject, Formation
        from database_setup import initialize_database
    except ModuleNotFoundError:
        print("Fallback import also failed in subject_ui.py. Define dummy classes for syntax check.")
        class Subject: pass
        class Formation: pass # Not strictly used by SubjectWindow methods yet, but good for context
        def initialize_database(): pass


class SubjectWindow(QtWidgets.QWidget):
    def __init__(self, formation_id, formation_name, duration_years, parent=None):
        super().__init__(parent)

        self.formation_id = formation_id
        self.formation_name = formation_name
        self.duration_years = duration_years

        self.setWindowTitle(f"Manage Subjects - {self.formation_name}")
        # self.setGeometry(200, 200, 450, 350) # Optional

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Display selected formation name
        self.formation_label = QtWidgets.QLabel(f"Subjects for: {self.formation_name} (ID: {self.formation_id})")
        self.formation_label.setStyleSheet("font-weight: bold;")
        self.main_layout.addWidget(self.formation_label)

        # Year Selection
        self.year_selection_layout = QtWidgets.QHBoxLayout()
        self.year_label = QtWidgets.QLabel("Select Year:")
        self.year_spinbox = QtWidgets.QSpinBox()
        if self.duration_years > 0:
            self.year_spinbox.setMinimum(1)
            self.year_spinbox.setMaximum(self.duration_years)
        else: # Handle case of 0 or negative duration, though unlikely
            self.year_spinbox.setMinimum(1)
            self.year_spinbox.setMaximum(1)
            self.year_spinbox.setEnabled(False)

        self.year_spinbox.valueChanged.connect(self.year_selected_changed)
        self.year_selection_layout.addWidget(self.year_label)
        self.year_selection_layout.addWidget(self.year_spinbox)
        self.year_selection_layout.addStretch() # Push to left
        self.main_layout.addLayout(self.year_selection_layout)

        # Input Fields for New Subject (using QFormLayout for better alignment)
        self.subject_input_form_layout = QtWidgets.QFormLayout()
        self.subject_name_input = QtWidgets.QLineEdit()
        self.subject_name_input.setPlaceholderText("Enter subject name")
        self.credits_spinbox = QtWidgets.QSpinBox()
        self.credits_spinbox.setMinimum(1)
        self.credits_spinbox.setMaximum(15) # Max credits for a subject
        self.credits_spinbox.setValue(3)   # Default credits

        self.subject_input_form_layout.addRow("Subject Name:", self.subject_name_input)
        self.subject_input_form_layout.addRow("Credits:", self.credits_spinbox)
        self.main_layout.addLayout(self.subject_input_form_layout)

        self.add_subject_button = QtWidgets.QPushButton("Add Subject")
        self.add_subject_button.clicked.connect(self.add_subject)
        self.main_layout.addWidget(self.add_subject_button)

        # Display Area for Subjects
        self.subject_list_label = QtWidgets.QLabel("Subjects in selected year:")
        self.subject_list_widget = QtWidgets.QListWidget()
        self.main_layout.addWidget(self.subject_list_label)
        self.main_layout.addWidget(self.subject_list_widget)

        self.setLayout(self.main_layout)

        # Initial Load
        if self.duration_years > 0:
            self.year_spinbox.setValue(1) # This will trigger year_selected_changed -> load_subjects_list
        else:
            self.load_subjects_list(1) # Load for year 1 even if duration is invalid, list will be empty/show error

    def year_selected_changed(self):
        current_year = self.year_spinbox.value()
        self.load_subjects_list(current_year)

    def load_subjects_list(self, year=None): # year can be optional if we want to refresh current view
        if year is None:
            year = self.year_spinbox.value() # Default to current year in spinbox

        self.subject_list_widget.clear()
        try:
            subjects = Subject.get_by_formation_and_year(self.formation_id, year)
            if not subjects:
                self.subject_list_widget.addItem(QtWidgets.QListWidgetItem(f"No subjects found for year {year}."))
            else:
                for sub in subjects:
                    item_text = f"{sub.name} ({sub.credits} credits)"
                    item = QtWidgets.QListWidgetItem(item_text)
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, sub.subject_id)
                    self.subject_list_widget.addItem(item)
        except Exception as e:
            print(f"Error loading subjects: {e}")
            #QtWidgets.QMessageBox.critical(self, "Error", f"Could not load subjects: {e}")
            self.subject_list_widget.addItem(QtWidgets.QListWidgetItem(f"Error loading subjects: {e}"))


    def add_subject(self):
        current_year = self.year_spinbox.value()
        subject_name = self.subject_name_input.text().strip()
        credits_value = self.credits_spinbox.value()

        if not subject_name:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Subject name cannot be empty.")
            return

        if credits_value <= 0: # Should be caught by QSpinBox min, but good practice
            QtWidgets.QMessageBox.warning(self, "Input Error", "Credits must be greater than 0.")
            return

        try:
            new_subject = Subject(name=subject_name, credits=credits_value,
                                  year=current_year, formation_id=self.formation_id)
            new_subject.save()

            self.subject_name_input.clear()
            self.credits_spinbox.setValue(3) # Reset to default
            self.load_subjects_list(current_year) # Refresh list for the current year
            # QtWidgets.QMessageBox.information(self, "Success", f"Subject '{subject_name}' added successfully.")
        except ValueError as ve:
            QtWidgets.QMessageBox.warning(self, "Error Adding Subject", str(ve))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    print("Subject UI Script - Basic Syntax Check Mode")

    # For true standalone testing, we'd need a QApplication and a dummy Formation.
    # This is complex due to dependencies (Department -> Formation -> Subject).
    # The primary goal here is code generation and syntax validity.

    # Attempt to initialize DB for basic model interaction if possible
    # This helps if one wants to test this file in isolation.
    dummy_formation_id = None
    try:
        print("Attempting to initialize database for direct test of subject_ui.py...")
        initialize_database() # From this file's imports
        print("Database initialized (called from subject_ui.py direct test block).")

        # To test SubjectWindow, we need a formation. Let's try to create/use a dummy one.
        # This requires Department model too.
        from ..models import Department # Explicitly import for this test block

        test_dept = Department.get_by_name("Test Dept for SubjectUI")
        if not test_dept:
            test_dept = Department(name="Test Dept for SubjectUI")
            test_dept.save()
            print(f"Created temporary department: {test_dept.name} (ID: {test_dept.department_id})")

        if test_dept and test_dept.department_id:
            test_formation = Formation.get_by_name("Test Formation for SubjectUI") # Assuming get_by_name exists
            if not test_formation: # Simple check, might need get_by_name_and_dept_id
                 # Check if a formation with this name exists in this dept
                existing_formations = Formation.get_by_department(test_dept.department_id)
                found_form = None
                for f in existing_formations:
                    if f.name == "Test Formation for SubjectUI":
                        found_form = f
                        break
                if not found_form:
                    test_formation = Formation(name="Test Formation for SubjectUI", duration_years=3, department_id=test_dept.department_id)
                    test_formation.save()
                    print(f"Created temporary formation: {test_formation.name} (ID: {test_formation.formation_id})")
                else:
                    test_formation = found_form

            if test_formation and test_formation.formation_id:
                dummy_formation_id = test_formation.formation_id
                dummy_formation_name = test_formation.name
                dummy_duration = test_formation.duration_years
                print(f"Using formation for test: ID={dummy_formation_id}, Name='{dummy_formation_name}', Duration={dummy_duration}")
            else:
                print("Could not create/find a test formation.")
        else:
            print("Could not create/find a test department for creating a test formation.")

    except Exception as e_db_setup:
        print(f"Database/test data setup failed in subject_ui.py: {e_db_setup}")
        import traceback
        traceback.print_exc()

    app_instance = QtWidgets.QApplication.instance()
    if not app_instance:
        app_instance = QtWidgets.QApplication(sys.argv)

    if not app_instance:
        print("CRITICAL: QApplication could not be initialized for test.")
        sys.exit(1)

    if dummy_formation_id:
        try:
            # Instantiate with dummy/test data
            window = SubjectWindow(formation_id=dummy_formation_id,
                                   formation_name=dummy_formation_name,
                                   duration_years=dummy_duration)
            print(f"SubjectWindow instantiated successfully: {window.windowTitle()}")
            # Basic method call
            window.load_subjects_list(1)
            print(f"Subjects in list after initial load (Year 1): {window.subject_list_widget.count()}")
            print("Subject UI Script - Basic syntax and instantiation check complete.")
        except Exception as e_inst:
            print(f"Error during SubjectWindow instantiation or method calls: {e_inst}")
            import traceback
            traceback.print_exc()
    else:
        print("Skipping SubjectWindow instantiation test as no dummy formation ID was available.")
        print("Subject UI Script - Basic syntax check (mostly) complete.")

    sys.exit(0) # Exit cleanly
```
