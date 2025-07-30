# data_components/category_dropdown.py

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from PySide6.QtWidgets import QLabel

from ui_components.dropdown import create_dropdown
from ui_components.uid_table import show_uid_table
from data_components.Property_dropdown import on_category_change

from backend.DB_Operations import fetch_category_details

load_dotenv()

def display_categories(form_layout, results_container):
    def clear_results():
        layout = results_container.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def handle_final_uid(uid, selected_props):
        show_uid_table(results_container, uid, selected_props)

    def get_category_values():
        engine = create_engine(os.getenv("NEON_DB_Category_URL"))
        with engine.connect() as conn:
            
            return fetch_category_details(conn)

    result = list(get_category_values())
    options = [""] + [item[0] for item in result]

    category_label = QLabel("Category:")
    dropdown = create_dropdown(options)
    form_layout.addRow(category_label, dropdown)

    def on_change(selected_text):
        clear_results()
        
        if selected_text:
            cat_mapped_value = None
            for row in result:
                if row[0] == selected_text:
                    cat_mapped_value = row[1]
                    break
            
            if cat_mapped_value:
                on_category_change(
                    category=selected_text,
                    cat_mapped_value=cat_mapped_value,
                    form_layout=form_layout,
                    on_final_uid=handle_final_uid,
                    clear_results=clear_results
                )
        else:
            on_category_change(None, None, form_layout, handle_final_uid, clear_results)

    dropdown.currentTextChanged.connect(on_change)