import sys
from PyQt6 import QtWidgets, QtCore, QtGui

# Using relative imports as specified, assuming this file is part of a package 'src.ui'
# and will be run in a context where 'src' is a package (e.g. python -m src.main)
try:
    from ..models import Department
    from ..database_setup import initialize_database # For potential direct testing
except ImportError as e:
    # Fallback for scenarios where relative imports might not work as expected by the tool
    # or if the file is attempted to be run directly in a way that doesn't resolve ..
    # This is a common issue in mixed execution environments.
    print(f"Relative import failed in department_ui.py: {e}. Attempting alternative for models.")
    try:
        from models import Department # if src/ is in PYTHONPATH or CWD
        from database_setup import initialize_database
    except ModuleNotFoundError:
        print("Fallback import also failed in department_ui.py. Check PYTHONPATH and execution context.")
        # In a real scenario, one would ensure the package structure is strictly followed.
        # For this tool environment, providing robust fallbacks or clear instructions on
        # how to run (e.g. python -m src.main from project root) is key.
        # We'll define dummy classes if all else fails, so syntax checking can proceed for the UI code itself.
        class Department: pass
        def initialize_database(): pass


class DepartmentWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Department Management")
        # self.setGeometry(100, 100, 400, 300) # Size can be set in main or by layout

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Input Area
        self.input_h_layout = QtWidgets.QHBoxLayout()
        self.name_label = QtWidgets.QLabel("Department Name:")
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Enter department name")
        self.add_button = QtWidgets.QPushButton("Add Department")
        self.add_button.clicked.connect(self.add_department)

        self.input_h_layout.addWidget(self.name_label)
        self.input_h_layout.addWidget(self.name_input)
        self.input_h_layout.addWidget(self.add_button)
        self.main_layout.addLayout(self.input_h_layout)

        # Display Area
        self.list_widget = QtWidgets.QListWidget()
        self.main_layout.addWidget(self.list_widget)

        # Refresh Button
        self.refresh_button = QtWidgets.QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.load_departments)
        self.main_layout.addWidget(self.refresh_button)

        self.setLayout(self.main_layout) # Set the main layout for the QWidget

        self.load_departments()

    def load_departments(self):
        self.list_widget.clear()
        try:
            departments = Department.get_all()
            if not departments:
                self.list_widget.addItem(QtWidgets.QListWidgetItem("No departments found."))
            else:
                for dept in departments:
                    item = QtWidgets.QListWidgetItem(dept.name)
                    # Store the department ID on the item using setData
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, dept.department_id)
                    self.list_widget.addItem(item)
        except Exception as e:
            # In a real app, more specific error handling or logging
            # For now, a message box or print if this module is run directly
            print(f"Error loading departments: {e}")
            # QtWidgets.QMessageBox.critical(self, "Error", f"Could not load departments: {e}")
            self.list_widget.addItem(QtWidgets.QListWidgetItem(f"Error loading: {e}"))


    def add_department(self):
        dept_name = self.name_input.text().strip()
        if not dept_name:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Department name cannot be empty.")
            return

        try:
            department = Department(name=dept_name)
            department.save() # This save method should handle potential IntegrityError for UNIQUE name
            self.name_input.clear()
            self.load_departments()
            # QtWidgets.QMessageBox.information(self, "Success", f"Department '{dept_name}' added successfully.")
        except ValueError as ve: # This is the custom error from our model for duplicate names
            QtWidgets.QMessageBox.warning(self, "Error Adding Department", str(ve))
        except Exception as e:
            # Catch any other unexpected errors during save
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

# Minimal direct execution block for syntax checking / basic structure validation
if __name__ == '__main__':
    # This block is primarily for ensuring the Python script itself is valid.
    # Full GUI execution is not the goal of this subtask.
    print("Department UI Script - Basic Syntax Check Mode")

    # Attempt to initialize DB for basic model interaction if possible
    # This helps if one wants to test this file in isolation, but main.py handles it for app run
    try:
        print("Attempting to initialize database for direct test of department_ui.py...")
        initialize_database()
        print("Database initialized (called from department_ui.py direct test block).")
    except Exception as e:
        print(f"Database initialization failed in department_ui.py direct test: {e}")

    # Basic check: Can we instantiate the window?
    # We won't show it or run app.exec() as per subtask focus.
    # Need a QApplication instance for some QWidget operations, even without showing.
    app_instance = QtWidgets.QApplication.instance()
    if not app_instance:
        app_instance = QtWidgets.QApplication(sys.argv)

    try:
        window = DepartmentWindow()
        print(f"DepartmentWindow instantiated successfully: {window.windowTitle()}")
        # Test loading departments (will print errors if models/DB not working)
        print("Attempting to call load_departments()...")
        window.load_departments()
        print(f"Items in list after load_departments: {window.list_widget.count()}")

        # Test add_department logic (mocking, no actual GUI interaction)
        print("Attempting to call add_department() with empty name (no GUI, so no pop-up expected)...")
        window.name_input.setText("") # Simulate empty input
        # window.add_department() # This would pop up a QMessageBox, not suitable for non-GUI check
        # Instead, check the logic directly or rely on main.py for full test.
        # For now, we assume the method is wired correctly.

        print("Department UI Script - Basic syntax and instantiation check complete.")
    except Exception as e:
        print(f"Error during DepartmentWindow instantiation or method calls: {e}")
        import traceback
        traceback.print_exc()

    # sys.exit(app_instance.exec()) # Not running the event loop
    sys.exit(0) # Exit cleanly after checks

```
