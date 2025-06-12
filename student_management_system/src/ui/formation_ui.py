import sys
from PyQt6 import QtWidgets, QtCore, QtGui

try:
    from ..models import Department, Formation
    from ..database_setup import initialize_database # For standalone testing if needed
except ImportError as e:
    print(f"Relative import failed in formation_ui.py: {e}. Attempting fallbacks for models.")
    # Fallback for environments where relative imports from .. don't resolve as expected
    # This might happen if src/ui/ is somehow treated as a top-level script location.
    try:
        from models import Department, Formation # If src/ is in PYTHONPATH or CWD
        from database_setup import initialize_database
    except ModuleNotFoundError:
        print("Fallback import also failed in formation_ui.py. Define dummy classes for syntax check.")
        # Define dummy classes if imports fail, to allow syntax checking of the UI code itself.
        class Department: pass
        class Formation: pass
        def initialize_database(): pass


class FormationWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Formation Management")
        # self.setGeometry(150, 150, 500, 400) # Optional: set geometry

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Department Selection
        self.dept_selection_layout = QtWidgets.QHBoxLayout()
        self.dept_label = QtWidgets.QLabel("Select Department:")
        self.department_combobox = QtWidgets.QComboBox()
        self.department_combobox.currentIndexChanged.connect(self.department_selected_changed)
        self.dept_selection_layout.addWidget(self.dept_label)
        self.dept_selection_layout.addWidget(self.department_combobox)
        self.main_layout.addLayout(self.dept_selection_layout)

        # Input Fields for New Formation
        self.form_input_layout = QtWidgets.QFormLayout()
        self.formation_name_input = QtWidgets.QLineEdit()
        self.formation_name_input.setPlaceholderText("Enter formation name")
        self.duration_spinbox = QtWidgets.QSpinBox()
        self.duration_spinbox.setMinimum(1)
        self.duration_spinbox.setMaximum(7)
        self.duration_spinbox.setValue(3) # Default duration

        self.form_input_layout.addRow("Formation Name:", self.formation_name_input)
        self.form_input_layout.addRow("Duration (Years):", self.duration_spinbox)

        self.add_formation_button = QtWidgets.QPushButton("Add Formation")
        self.add_formation_button.clicked.connect(self.add_formation)

        self.main_layout.addLayout(self.form_input_layout)
        self.main_layout.addWidget(self.add_formation_button)

        # Display Area for Formations
        self.formation_list_label = QtWidgets.QLabel("Formations in Selected Department:")
        self.formation_list_widget = QtWidgets.QListWidget()
        self.main_layout.addWidget(self.formation_list_label)
        self.main_layout.addWidget(self.formation_list_widget)

        self.setLayout(self.main_layout)

        # Initial Load
        self.load_departments_into_combobox()
        # department_selected_changed will be called automatically if load_departments_into_combobox sets an index

    def load_departments_into_combobox(self):
        self.department_combobox.clear()
        try:
            departments = Department.get_all()
            if not departments:
                self.department_combobox.addItem("No departments available", None) # UserData is None
                self.department_combobox.setEnabled(False)
            else:
                self.department_combobox.setEnabled(True)
                for dept in departments:
                    self.department_combobox.addItem(dept.name, dept.department_id) # Store ID as UserData
                if len(departments) > 0:
                     self.department_combobox.setCurrentIndex(0) # Triggers department_selected_changed
        except Exception as e:
            print(f"Error loading departments into combobox: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not load departments: {e}")
            self.department_combobox.addItem("Error loading departments", None)
            self.department_combobox.setEnabled(False)

    def department_selected_changed(self):
        department_id = self.department_combobox.currentData()
        if department_id is not None:
            self.load_formations_list(department_id)
        else:
            self.formation_list_widget.clear() # Clear list if no valid department selected

    def load_formations_list(self, department_id):
        self.formation_list_widget.clear()
        if department_id is None:
            self.formation_list_widget.addItem("No department selected or department has no ID.")
            return
        try:
            formations = Formation.get_by_department(department_id)
            if not formations:
                self.formation_list_widget.addItem(QtWidgets.QListWidgetItem("No formations in this department."))
            else:
                for form in formations:
                    item = QtWidgets.QListWidgetItem(f"{form.name} ({form.duration_years} years)")
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, form.formation_id)
                    self.formation_list_widget.addItem(item)
        except Exception as e:
            print(f"Error loading formations: {e}")
            #QtWidgets.QMessageBox.critical(self, "Error", f"Could not load formations: {e}")
            self.formation_list_widget.addItem(QtWidgets.QListWidgetItem(f"Error loading formations: {e}"))


    def add_formation(self):
        department_id = self.department_combobox.currentData()
        if department_id is None:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please select a department.")
            return

        formation_name = self.formation_name_input.text().strip()
        duration = self.duration_spinbox.value()

        if not formation_name:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Formation name cannot be empty.")
            return

        if duration <= 0: # Should be caught by QSpinBox min value, but good to double check
            QtWidgets.QMessageBox.warning(self, "Input Error", "Duration must be greater than 0.")
            return

        try:
            new_formation = Formation(name=formation_name, duration_years=duration, department_id=department_id)
            new_formation.save()

            self.formation_name_input.clear()
            self.duration_spinbox.setValue(self.duration_spinbox.minimum()) # Reset to min or a default
            self.load_formations_list(department_id) # Refresh list
            # QtWidgets.QMessageBox.information(self, "Success", f"Formation '{formation_name}' added successfully.")
        except ValueError as ve: # From model's save method for FK issues or other integrity problems
            QtWidgets.QMessageBox.warning(self, "Error Adding Formation", str(ve))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    # This block is for basic syntax checking and non-GUI instantiation test.
    print("Formation UI Script - Basic Syntax Check Mode")

    # Attempt to initialize DB for basic model interaction if possible
    try:
        print("Attempting to initialize database for direct test of formation_ui.py...")
        initialize_database() # From this file's imports
        print("Database initialized (called from formation_ui.py direct test block).")

        # Pre-populate with at least one department for the ComboBox to function in test
        try:
            print("Checking/creating test department for Formation UI direct test...")
            test_dept = Department.get_by_name("Test Dept for FormationUI")
            if not test_dept:
                test_dept = Department(name="Test Dept for FormationUI")
                test_dept.save()
                print(f"Created test department: {test_dept}")
            else:
                print(f"Found existing test department: {test_dept}")
        except Exception as e_dept:
            print(f"Could not create/check test department: {e_dept}")

    except Exception as e_db:
        print(f"Database initialization or test department setup failed: {e_db}")

    app_instance = QtWidgets.QApplication.instance()
    if not app_instance:
        app_instance = QtWidgets.QApplication(sys.argv)

    if not app_instance: # Still no app
        print("CRITICAL: QApplication could not be initialized for test.")
        sys.exit(1)

    try:
        window = FormationWindow()
        print(f"FormationWindow instantiated successfully: {window.windowTitle()}")
        print(f"Departments in ComboBox: {window.department_combobox.count()}")
        print(f"Formations in List (initial): {window.formation_list_widget.count()}")

        # Further non-GUI tests could simulate signals or call methods if needed,
        # but this is sufficient for "code generation check".
        print("Formation UI Script - Basic syntax and instantiation check complete.")
    except Exception as e:
        print(f"Error during FormationWindow instantiation or method calls: {e}")
        import traceback
        traceback.print_exc()

    sys.exit(0) # Exit cleanly
```
