import os
from dotenv import load_dotenv
from tkinter import StringVar, Frame

#for dpi
import ctypes

from sqlalchemy import create_engine
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # For Windows 8.1 or later
except:
    pass


# Module path imports
from backend.DB_Operations import fetch_category_details
from ui_components.dropdown import create_dropdown
from ui_components.uid_table import show_uid_table
from data_components.Property_dropdown import on_category_change
load_dotenv()

# Check for DB


def display_categories(*args,root):
    # Consistent dark frames
    frame = Frame(root, bg="#1e1e1e")
    frame.pack(padx=20, pady=10, fill='x')
    property_frame = Frame(root, bg="#1e1e1e")
    property_frame.pack(padx=20, pady=10, fill='x')

    #table frame
    uid_frame = Frame(root, bg="#1e1e1e")
    uid_frame.pack(padx=20, pady=10, fill='x')

    # Function to clear the UID table
    def clear_uid_table():
        for widget in uid_frame.winfo_children():
            widget.destroy()

    # Callback to display table
    def handle_final_uid(uid, selected_props):
        show_uid_table(uid_frame, uid, selected_props)

    def get_category_values():
        db_path= os.getenv("NEON_DB_Category_URL")
        engine = create_engine(db_path)
        conn = engine.connect()
        categories = fetch_category_details(conn)
        return categories           

    result = list(get_category_values())
    options = [item[0] for item in result]
    prop_var = StringVar(value="Select Category")

    def on_change(*args, prop_var=prop_var):
        clear_uid_table()
        cat_val = prop_var.get()
        cat_mapped_value = None
        for row in result:
            if row[0] == cat_val:
                cat_mapped_value = row[1]
                on_category_change(
                    category=cat_val,
                    cat_mapped_value=cat_mapped_value,
                    property_frame=property_frame,
                    root=root,
                    on_final_uid=handle_final_uid,  # ← Pass UID and props
                    clear_uid_table=clear_uid_table
                )
                break

    prop_var.trace_add("write", on_change)
    create_dropdown(frame, "Category:", options, row=0, var=prop_var)
