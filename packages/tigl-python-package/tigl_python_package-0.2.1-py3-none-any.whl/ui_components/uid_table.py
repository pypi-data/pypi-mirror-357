# ui_components/uid_table.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QApplication, QHeaderView
from PySide6.QtCore import Qt

class IntelligentTableWidget(QTableWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.resizeColumnsToContents()

        total_content_width = sum(self.columnWidth(i) for i in range(self.columnCount()))
        
        try:
            # viewport() can be None during widget destruction, so we check for it.
            available_width = self.viewport().width()
        except AttributeError:
            return # Stop if the viewport doesn't exist

        if total_content_width < available_width and self.columnCount() > 0:
            extra_space = available_width - total_content_width
            space_per_column = extra_space / self.columnCount()
            for i in range(self.columnCount()):
                # Add the distributed extra space to the baseline width
                self.setColumnWidth(i, int(self.columnWidth(i) + space_per_column))


def show_uid_table(parent_container, uid, selected_props):
    # Clear any previous table from the container
    layout = parent_container.layout()
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

    # Create the container for the table and button
    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(10)

    # Prepare data for the table
    columns = ["UID"] + [name for name, _ in selected_props]
    values = [uid] + [value for _, value in selected_props]

    table = IntelligentTableWidget(1, len(columns))
    table.setHorizontalHeaderLabels(columns)
    
    # Populate the table cells
    for col, value in enumerate(values):
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(0, col, item)
        
    # Apply styling
    table.setStyleSheet("""
        IntelligentTableWidget { /* Target our custom class */
            background-color: #1e1e1e; color: #ffffff;
            font-family: 'Segoe UI'; font-size: 11pt;
            gridline-color: #3a3a3a;
        }
        QHeaderView::section {
            background-color: #2d2d2d;
            color: #ffffff;
            font-weight: bold;
            padding-left: 6px;
            text-align: left;
        }
    """)
    table.verticalHeader().setVisible(False)
    
    # Set a fixed height to prevent vertical gaps
    table_height = table.horizontalHeader().height() + table.rowHeight(0) + 4
    table.setFixedHeight(table_height)
    
    content_layout.addWidget(table)

    # Create and add the copy button
    def copy_to_clipboard():
        formatted = "\t".join(map(str, values))
        QApplication.clipboard().setText(formatted)

    copy_button = QPushButton("Copy")
    copy_button.setFixedWidth(120)
    copy_button.setStyleSheet("""
        QPushButton {
            background-color: #2d2d2d; color: #ffffff; font: 11pt 'Segoe UI';
            border-radius: 5px; padding: 8px 16px;
        }
        QPushButton:hover { background-color: #3a3a3a; }
    """)
    content_layout.addWidget(copy_button, alignment=Qt.AlignRight)

    content_layout.addStretch()

    parent_container.layout().addWidget(content_widget)