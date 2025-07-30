import os
import sqlite3
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from data_components.Category_dropdown import resource_path
from ui_components.error_msg import display_message
def upload_excel_file(*args,category,table_name, frame):
    # Create the Tkinter root and hide it
    root = Tk()
    root.withdraw()  # Hide the root window

    # Keep the root alive until file is selected
    root.update()

# Open the file dialog
    file_path = askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )

    #   Optional: destroy root after dialog
    root.destroy()

    # Read and show data
    if file_path:
        flag=0
        df = pd.read_excel(file_path)
        keys= df[table_name+"_key"]
        values= df[table_name+"_value"]
        filters= df["Filter"]
        dependant_var= df["Dependant_Variable"]
        if not os.path.exists(resource_path(f"databases/{category}.db")):
                print(f"Database file not found: databases/{category}.db")
                display_message(frame, f"Database file not found: databases/{category}.db", "error")
                return
        conn = sqlite3.connect(resource_path(f"databases/{category}.db"))
        cursor = conn.cursor()
        if not filter and not dependant_var:
            for key, value in zip(keys,values):
                if(key is None or value is None):
                    flag=1
                    display_message(frame, "Insertion stopped because null value found in cell, please fill the cell with appropriate value and try inserting again from the missing value row")
                    return
                try:
                
                    cursor.execute(
                    f'INSERT INTO {table_name} ({table_name}_key, {table_name}_value) VALUES (?, ?)',
                    (key, value)
                    )
                except sqlite3.Error as e:
                    print(f"Error inserting property {key} with value {value} into table {table_name}: {e}")
                    display_message(frame, f"Error inserting property {key} with value {value} into table {table_name}: {e}", "error")
                    return
        else:
            for key, value, filter, dependant in zip(keys,values,filters,dependant_var):
                if(key is None or value is None or filter is None or dependant is None):
                    flag=1
                    display_message(frame, "Insertion stopped because null value found in cell, please fill the cell with appropriate value and try inserting again continuing from the row that had the missing value")
                    return
                try:
                
                    cursor.execute(
                    f'INSERT INTO {table_name} ({table_name}_key, {table_name}_value, Filter, Dependant_Variable) VALUES (?, ?, ?, ?)',
                    (key, value, filter, dependant)
                    )
                except sqlite3.Error as e:
                    print(f"Error inserting property {key} with value {value}, Filter: {filter} and dependant variable: {dependant} into table {table_name}: {e}")
                    display_message(frame, f"Error inserting property {key} with value {value}, Filter: {filter} and dependant variable: {dependant} into table {table_name}: {e}", "error")
                    return

        conn.commit()
        conn.close() 
    else:
        print("No file selected.")
