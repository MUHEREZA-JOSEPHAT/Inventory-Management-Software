from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from models.category import Category

class CategoryDialog(QDialog):
    def __init__(self, parent=None, category_data=None):
        super().__init__(parent)
        self.category_data = category_data
        self.setWindowTitle("Add Category" if not category_data else "Edit Category")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.name_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        
        layout.addRow("Category Name:", self.name_edit)
        layout.addRow("Description:", self.desc_edit)
        
        if self.category_data:
            self.name_edit.setText(self.category_data[1])
            self.desc_edit.setText(self.category_data[2] or "")
            
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip()
        }

class CategoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.category_model = Category()
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header section
        header_layout = QHBoxLayout()
        title = QLabel("Product Categories")
        title.setObjectName("page-title")
        header_layout.addWidget(title)
        
        add_btn = QPushButton("+ Add New Category")
        add_btn.setObjectName("add-btn")
        add_btn.clicked.connect(self.add_category)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3) # ID, Name, Description
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnHidden(0, True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")
        refresh_btn = QPushButton("Refresh")
        
        edit_btn.clicked.connect(self.edit_selected_category)
        delete_btn.clicked.connect(self.delete_selected_category)
        refresh_btn.clicked.connect(self.refresh_data)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Double click to edit
        self.table.doubleClicked.connect(lambda index: self.edit_category(index))
        
    def refresh_data(self):
        categories = self.category_model.get_all_categories()
        self.table.setRowCount(len(categories))
        for row, cat in enumerate(categories):
            self.table.setItem(row, 0, QTableWidgetItem(str(cat[0])))
            self.table.setItem(row, 1, QTableWidgetItem(cat[1]))
            self.table.setItem(row, 2, QTableWidgetItem(cat[2] or ""))
            
    def add_category(self):
        dialog = CategoryDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Category name is required")
                return
            if self.category_model.add_category(data['name'], data['description']):
                self.refresh_data()
                self.window().show_success(f"Category '{data['name']}' added!")
            else:
                QMessageBox.critical(self, "Error", "Failed to add category (name might already exist)")
                
    def edit_category(self, index):
        row = index.row()
        cat_id = int(self.table.item(row, 0).text())
        cat_name = self.table.item(row, 1).text()
        cat_desc = self.table.item(row, 2).text()
        
        dialog = CategoryDialog(self, (cat_id, cat_name, cat_desc))
        if dialog.exec():
            data = dialog.get_data()
            if self.category_model.update_category(cat_id, data['name'], data['description']):
                self.refresh_data()
                self.window().show_success("Category updated!")
            else:
                QMessageBox.critical(self, "Error", "Failed to update category")
                
    def edit_selected_category(self):
        row = self.table.currentRow()
        if row >= 0:
            self.edit_category(self.table.model().index(row, 0))
        else:
            QMessageBox.warning(self, "Selection Required", "Please select a category to edit")
            
    def delete_selected_category(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a category to delete")
            return
            
        cat_id = int(self.table.item(row, 0).text())
        cat_name = self.table.item(row, 1).text()
        
        msg = f"Are you sure you want to delete the category '{cat_name}'?\nNote: Products in this category will remain but will be uncategorized."
        if QMessageBox.question(self, "Confirm Delete", msg) == QMessageBox.StandardButton.Yes:
            if self.category_model.delete_category(cat_id):
                self.refresh_data()
                self.window().show_success(f"Category '{cat_name}' deleted!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete category")
