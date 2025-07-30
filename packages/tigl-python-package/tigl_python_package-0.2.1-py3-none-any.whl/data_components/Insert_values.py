import sys
import os
from tkinter import BooleanVar, IntVar, StringVar, Tk, Frame, ttk
from tkinter import Label, Entry
from tkinter import Button
#TODO: Add validation and error handling for database operations
#TODO: Add authentication and authorization for database access
#for dpi
import ctypes

from ui_components.error_msg import clear_message, display_message
from ui_components.excel_file_upload import upload_excel_file
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # For Windows 8.1 or later
except:
    pass

# Module path imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui_components.dropdown import create_dropdown


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller .exe """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


  # Style constants
dropdown_font = ("Segoe UI", 11)
bg_color = "#1e1e1e"          # Background for label and menu
fg_color = "#ffffff"          # White text
button_bg_color = "#2d2d2d"   # Dropdown button background
highlight_color = "#3a3a3a"   # Hover background
button_style = {
    "bg": "#2d2d2d",                # Dark background
    "fg": "#ffffff",                # White text
    "activebackground": "#3a3a3a",  # Slightly lighter on hover
    "activeforeground": "#ffffff",  # Keep text white on hover
    "highlightbackground": "#1e1e1e",  # Match frame background to avoid border glow
    "font": dropdown_font,
    "relief": "raised",
    "bd": 2,
    "cursor": "hand2"
}
widgets = []
def clear_widgets(widgets, i):
    for i in range(len(widgets)-1, i-1, -1):
        widgets[i].destroy()
        print(f"Cleared widget at {i} index: {widgets[i]}")
    del widgets[i:]
def on_insert_value(*args, root):
    
    insert_value_frame = Frame(root, bg="#1e1e1e")
    insert_value_frame.pack(padx=20, pady=10, fill='x')
    prop_var = StringVar(value="Select Option")
    def on_option_change(*args):
        if prop_var.get() == "Insert value in Category Table":
            on_category_selection(insert_value_frame=insert_value_frame)
        elif prop_var.get() == "Insert value in Property Table":
            on_property_selection(insert_value_frame=insert_value_frame)
        elif prop_var.get() == "Insert values in bulk in Property Table":
            on_insert_values_in_bulk(*args, insert_value_frame=insert_value_frame)
    prop_var.trace_add("write", on_option_change)
    clear_widgets(widgets, 0)

    dropdown, prop_var=create_dropdown(insert_value_frame, "Select Option:",["Insert value in Category Table", "Insert value in Property Table", "Insert values in bulk in Property Table"] , row=0, var=prop_var)
    if len(widgets) > 0:
        widgets[0] = dropdown
    else:
        widgets.insert(0, dropdown)
    print(f"Widget created at index 0: {widgets[0]}")





def on_category_selection(*args, insert_value_frame):
    print("Category Selection Triggered")
     

    # Label with wider width
    label = Label(
        insert_value_frame,
        text="Enter Category Name:",
        font=dropdown_font,
        bg=bg_color,
        fg=fg_color,
        width=25,          # Increased width
        anchor="w"         # Left-align text
    )
    label.grid(row=1, column=0, padx=10, pady=6, sticky='w')

    entry_var = StringVar(value="")
    entry = Entry(insert_value_frame, textvariable=entry_var, width=40, font=dropdown_font, bg=button_bg_color, fg=fg_color)
    entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
    
    def submit_category():
        cat_key = entry_var.get()
        print(f"Category Key: {cat_key}")
        
        cat_key= entry_var.get()
        print(f"Category Key: {cat_key}")
        if cat_key:
            db_path_cat = resource_path("databases/Category.db")
            if not os.path.exists(db_path_cat):
                print(f"Database file not found: {db_path_cat}")
                display_message(insert_value_frame, f"Invalid Category: {db_path_cat}", "error")
                return
            else:
                no_of_properties = IntVar(value=0)
                label = Label(
                insert_value_frame,
                text="Enter No. of Properties the Category will have:",
                font=dropdown_font,
                bg=bg_color,
                fg=fg_color,
                width=25,          # Increased width
                anchor="w"         # Left-align text
                )
                label.grid(row=2, column=0, padx=10, pady=6, sticky='w')

                entry = Entry(insert_value_frame, textvariable=no_of_properties, width=40, font=dropdown_font, bg=button_bg_color, fg=fg_color)
                entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
                
                def on_insert_no_of_properties():
                    print(f"No. of Properties: {no_of_properties.get()}")
                    no_of_props = no_of_properties.get()
                    if no_of_props < 1:
                        display_message(insert_value_frame, "Please enter a valid number of properties.", "error")
                        return
                    elif no_of_props > 6:
                        display_message(insert_value_frame, "Maximum 6 properties allowed.", "error")
                        return
                
                    def create_tables(*args,i, props, property_dynamic, row):
                        print(f"i={i}")
                        if i == no_of_props:
                            print(f"Creating table for {cat_key} with {i} properties.")
                            if not cat_key:
                                display_message(insert_value_frame, "You cannot leave the category field empty")
                                return
                            cat_conn = sqlite3.connect(resource_path(f"databases/{cat_key}.db"))
                            cat_cursor = cat_conn.cursor()
                            for( prop, dynamic) in zip(props, property_dynamic):
                                table_name= prop.get().replace(" ", "_").replace("-", "_")
                                is_dynamic= dynamic.get()
                                if not table_name:
                                    display_message(insert_value_frame, "Property name cannot be empty.", "error")
                                    return
                                try:
                                    
                                    if(is_dynamic):
                                        cat_cursor.execute(f'''
                                        CREATE TABLE IF NOT EXISTS {table_name} (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            {table_name}_key TEXT,
                                            {table_name}_value TEXT,
                                            Filter TEXT,
                                            Dependent_Variable TEXT
                                        )
                                        ''')
                                        cat_conn.commit()
                                    else:
                                        cat_cursor.execute(f'''
                                        CREATE TABLE IF NOT EXISTS {table_name} (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            {table_name}_key TEXT UNIQUE,
                                            {table_name}_value TEXT UNIQUE
                                        )
                                        ''')
                                        cat_conn.commit()
                                except sqlite3.Error as e:
                                    print(f"Error creating table {table_name}: {e}")
                                    display_message(insert_value_frame, f"Error creating table {table_name}: {e}", "error")
                                    return
                                print(f"Table {table_name} created successfully.")
                                

                            display_message(insert_value_frame, "All properties created successfully.", "success")
                            
                            return
                        prop_label = Label(
                            insert_value_frame,
                            text=f"Enter Property {i+1} Name:",
                            font=dropdown_font,
                            bg=bg_color,
                            fg=fg_color,
                            width=25,          # Increased width
                            anchor="w"         # Left-align text
                        )
                        
                        prop_label.grid(row=row, column=0, padx=10, pady=6, sticky='w')
                        prop_entry_var = StringVar(value="")
                        prop_entry = Entry(insert_value_frame, textvariable=prop_entry_var, width=40, font=dropdown_font, bg=button_bg_color, fg=fg_color)
                        
                        prop_entry.grid(row=row, column=1, padx=10, pady=10, sticky="w")
                        row= row+1
                        is_property_dynamic = BooleanVar(value=False)
                        dropdown, prop_var = create_dropdown(
                            insert_value_frame,
                            f"Is Property {i+1} Dynamic?",
                            ["True", "False"],
                            row=row,
                            var=is_property_dynamic,
                        )
                        props.append(prop_entry_var)
                        property_dynamic.append(is_property_dynamic)
                        submit_btn = Button(
                            insert_value_frame,
                            text=f"Submit Property {i+1}",
                            command=lambda i=i+1: create_tables(i=i, props=props, property_dynamic=property_dynamic, row=row+1),
                            **button_style
                        )
                        submit_btn.grid(row=row, column=3, padx=10, pady=10, sticky="w")
                    create_tables(i=0, props=[], property_dynamic=[],row=3)





                submit_btn = Button(insert_value_frame, text="Submit", command=on_insert_no_of_properties, **button_style)
                submit_btn.grid(row=2, column=2, padx=10, pady=10, sticky="w")



                        

                       

                        
                    


    submit_btn = Button(insert_value_frame, text="Submit", command=submit_category)
    submit_btn.grid(row=1, column=2, padx=10, pady=10, sticky="w")


def on_property_selection(*args, insert_value_frame):
    if not os.path.exists(resource_path("databases/Category.db")):
                print(f"Database file not found: ../databases/Category.db")
                display_message(insert_value_frame, "Database file not found: ../databases/Category.db", "error")
                return
    cat_conn = sqlite3.connect(resource_path("databases/Category.db"))
    cat_cursor = cat_conn.cursor()
    res = cat_cursor.execute('''
                SELECT Category_key FROM Category
            ''').fetchall()
    cat_keys = [item[0] for item in res]
    selected_category = StringVar(value="Select Category")

    def on_select_category(*args):
        selected_cat = selected_category.get()
        
        if selected_cat != "Select Category":
            db_path = resource_path(f"databases/{selected_cat}.db")
            prop_conn = sqlite3.connect(db_path)
            prop_cursor = prop_conn.cursor()
            prop_names=prop_cursor.execute(f'''SELECT Properties
    FROM Headers ''').fetchall()
            props = [name[0] for name in prop_names if name[0] != 'sqlite_sequence']
            if not props:
                display_message(insert_value_frame, f"No properties found for category {selected_cat}.", "error")
                prop_conn.close()
                return
            prop_conn.commit()
            prop_conn.close()
            if not os.path.exists(db_path):
                display_message(insert_value_frame, f"Database file not found: {db_path}", "error")
                return
            else:
                selected_property = StringVar(value="Select Property")
                def on_property_selected(*args):
                    selected_prop = selected_property.get()
                    table_name = selected_prop
                    
                    if selected_prop != "Select Property":
                        prop_conn = sqlite3.connect(db_path)
                        prop_cursor = prop_conn.cursor()
                        
                        res = prop_cursor.execute(f'''
                            SELECT {table_name}_value FROM {table_name}
                                 ''').fetchall()
                        prop_values= [item[0] for item in res]
                        last_prop_value=int(prop_values[0])
                        for item in prop_values:
                            fill_value= len(item)
                            integer_value = int(item)
                            if integer_value > int(last_prop_value):
                                last_prop_value = integer_value
                                if( len(str(last_prop_value+1)) > fill_value):
                                    display_message(insert_value_frame, f"You have reached maximum limit for {table_name}.", "error")
                                    return
                        curr_cat_value = str(last_prop_value + 1).zfill(fill_value)
                     
                        prop_conn.close()
                        clear_widgets(widgets, 3)

                        container_1= Frame(insert_value_frame, bg=bg_color)
                        container_1.grid(row=3, column=0,columnspan=3, padx=10, pady=10, sticky='w')


                        label = Label(
                        container_1,
                        text="Enter Property Key:",
                        font=dropdown_font,
                        bg=bg_color,
                        fg=fg_color,
                        width=25,          # Increased width
                        anchor="w"         # Left-align text
                        )
                        label.grid(row=3, column=0, padx=(0,10), pady=6, sticky='w')

                        prop_val = StringVar(value="")
                        entry = Entry(container_1, textvariable=prop_val, width=30,font=dropdown_font, bg=button_bg_color, fg=fg_color)
                        entry.grid(row=3, column=1,padx=10, pady=6, sticky="w")
                    
                        if len(widgets) > 3:
                            widgets[3] = container_1
                        else:
                            widgets.insert(3,container_1)
                        print(f"Widget created at index 3: {widgets[3]}")
                        

                        def submit_property_value():
                            prop_key = prop_val.get()
                            if(prop_val.get() == "" or prop_val.get() == "Enter Property Key"):
                                print("No property name provided, setting default value.")
                            else:
                                prop_key= prop_val.get()
                            if prop_key:
                                column_to_check = 'Filter'
                                prop_conn = sqlite3.connect(db_path)
                                prop_cursor = prop_conn.cursor()
                                prop_cursor.execute(f"PRAGMA table_info({table_name})")
                                columns = [row[1] for row in prop_cursor.fetchall()]

                                if column_to_check in columns:
                                    dependent_prop=prop_cursor.execute(f'''SELECT Dependent_Variable FROM {table_name} WHERE id = 1''').fetchone()
                                    if not dependent_prop or not dependent_prop[0]:
                                        dependent_prop = ("property")

                                    container_2 = Frame(insert_value_frame, bg= bg_color)
                                    container_2.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='w')

                                    label = Label(
                                     container_2,
                                     text=f"Enter {dependent_prop[0]} value/values:",
                                     font=dropdown_font,
                                     bg=bg_color,
                                     fg=fg_color,
                                     width=25,          # Increased width
                                     anchor="w"         # Left-align text
                                    )
                                    label.grid(row=4, column=0, padx=(0,10), pady=6, sticky='w')
                                    filter_val = StringVar(value="")
                                    entry = Entry(container_2, textvariable=filter_val, width=30, font=dropdown_font, bg=button_bg_color, fg=fg_color)
                                    entry.grid(row=4, column=1,padx=10, pady=6, sticky="w")
                                    


                                    if len(widgets) > 4:
                                        widgets[4] = container_2
                                    else:
                                        widgets.insert(4, container_2)
                                    print(f"Widget created at index 4: {widgets[4]}")
                                    
                                    def insert_property_value():
                                        filter_value = filter_val.get()
                                        if(filter_val.get() == "" or filter_val.get() == "Enter Filter value"):
                                            print("No filter value provided, setting default value.")
                                            filter_value = "Default Filter"
                                        else:
                                            filter_value = filter_val.get()
                                        if prop_key:
                                            filter_values= filter_value.split(",") if filter_value else []
                                            for fil_val in filter_values:
                                                prop_conn = sqlite3.connect(db_path)
                                                prop_cursor = prop_conn.cursor()
                                                unique_check= prop_cursor.execute(f'''
                                                SELECT COUNT(*) FROM {table_name} WHERE {table_name}_key = ? AND Filter = ?''', (prop_key, fil_val.strip())).fetchone()[0]
                                                if unique_check > 0:
                                                    print(f"Property {prop_key} with filter {fil_val.strip()} already exists in table {table_name}.")
                                                    display_message(insert_value_frame, f"Property {prop_key} with filter {fil_val.strip()} already exists in table {table_name}.", "error")
                                                    prop_conn.close()
                                                    return
                                                else:
                                                    clear_message(insert_value_frame)
                                                res = prop_cursor.execute(
                                                f"SELECT {table_name}_value FROM {table_name} WHERE Filter = ?",
                                                (fil_val.strip(),)
                                                ).fetchall()
                                                prop_values= [item[0] for item in res]
                                                print(f"Prop Values for {fil_val.strip()}: {prop_values}")

                                                last_prop_value = int(prop_values[0]) if prop_values else 0
                                                for item in prop_values:
                                                    fill_value= len(item)
                                                    integer_value = int(item)
                                                if integer_value > int(last_prop_value):
                                                    last_prop_value = integer_value
                                                if last_prop_value + 1 >= 10 ** fill_value:
                                                    print("Property value exceeds maximum limit.")
                                                    return
                                                curr_cat_value = str(last_prop_value + 1).zfill(fill_value)
                                                try:
                                                   #prop_cursor.execute(f"INSERT INTO {table_name} ({table_name}_key, {table_name}_value, Filter) VALUES (?,?,?)", (prop_key, curr_cat_value, fil_val))
                                                   #prop_conn.commit()
                                                   print(f"Property {prop_key} with value {curr_cat_value} and filter {fil_val.strip()} inserted into table {table_name}.")
                                                   display_message(insert_value_frame, f"Property key {prop_key} with value {curr_cat_value} and filter {fil_val.strip()} inserted into table {table_name}.", "success")
                                                except sqlite3.Error as e:
                                                    print(f"Error inserting property {prop_key} with value {curr_cat_value} and filter {fil_val.strip()} into table {table_name}: {e}")
                                                    display_message(insert_value_frame, f"Error inserting property key: {e}", "error")
                                                    return 
                                                prop_conn.close()
                                           
                                        
                                        else:
                                            print("No property name or category value provided.")
                                            display_message(insert_value_frame, "No property name or category value provided.", "error")
                                        prop_conn.close()

                                    submit_btn = Button(container_2, text="Submit", command=insert_property_value, **button_style)
                                    submit_btn.grid(row=4, column=2, padx=10, pady=10, sticky="w")
                                    
                                else:
                                    if prop_key and curr_cat_value:
                                        unique_check= prop_cursor.execute(f'''
                                                SELECT COUNT(*) FROM {table_name} WHERE {table_name}_key = ?''', (prop_key,)).fetchone()[0]
                                        if unique_check > 0:
                                            print(f"Property {prop_key} already exists in table {table_name}.")
                                            display_message(insert_value_frame, f"Property key {prop_key} already exists in table {table_name}.", "error")
                                            prop_conn.close()
                                            return
                                        else:
                                            clear_message(insert_value_frame)
                                        try:    
                                            #prop_cursor.execute(f"INSERT INTO {table_name} ({table_name}_key, {table_name}_value) VALUES (?,?)", (prop_key, curr_cat_value))
                                            #prop_conn.commit()

                                            print(f"Property {prop_key} with value {curr_cat_value} inserted into table {table_name}.")
                                            display_message(insert_value_frame, f"Property key {prop_key} with value {curr_cat_value} inserted into table {table_name}.", "success")
                                        except sqlite3.Error as e:
                                            print(f"Error inserting property {prop_key} with value {curr_cat_value} into table {table_name}: {e}")
                                            display_message(insert_value_frame, f"Error inserting property: {e}", "error")
                                            return
                                    prop_conn.close()
                                
                                
                            else:
                                print("No property name provided.")
                                
                        submit_btn = Button(container_1, text="Submit", command=submit_property_value, **button_style)
                        submit_btn.grid(row=3, column=2, padx=10, pady=10, sticky="w")
                        print(f"Table {table_name} ready for new property insertion.")
                    else:
                        print("No property selected.")
                selected_property.trace_add("write", on_property_selected)
                clear_widgets(widgets, 2)

                dropdown, prop_val= create_dropdown(insert_value_frame,"Select Property:", props, row=2, var=selected_property)
                if len(widgets) > 2:
                    widgets[2] = dropdown
                else:
                    widgets.insert(2, dropdown)
                print(f"Widget created at index 2: {widgets[2]}")
                


            
            
        else:
            print("No category selected.")
    selected_category.trace_add("write", on_select_category)
    clear_widgets(widgets, 1)
    dropdown, prop_var= create_dropdown(insert_value_frame,"Select Category:", cat_keys, row=1, var=selected_category)
    if len(widgets) > 1:
        widgets[1] = dropdown
    else:
        widgets.insert(1, dropdown)
    print(f"Widget created at index 1: {widgets[1]}")

def on_insert_values_in_bulk(*args, insert_value_frame):
    if not os.path.exists(resource_path("databases/Category.db")):
                print(f"Database file not found: ../databases/Category.db")
                display_message(insert_value_frame, "Database file not found: ../databases/Category.db", "error")
                return
    cat_conn = sqlite3.connect(resource_path("databases/Category.db"))
    cat_cursor = cat_conn.cursor()
    res = cat_cursor.execute('''
                SELECT Category_key FROM Category
            ''').fetchall()
    cat_keys = [item[0] for item in res]
    selected_category = StringVar(value="Select Category")
    def on_selected_category(*args):
        selected_cat = selected_category.get()
        
        if selected_cat != "Select Category":
            db_path = resource_path(f"databases/{selected_cat}.db")
            prop_conn = sqlite3.connect(db_path)
            prop_cursor = prop_conn.cursor()
            prop_names=prop_cursor.execute(f'''SELECT Properties
    FROM Headers ''').fetchall()
            props = [name[0] for name in prop_names if name[0] != 'sqlite_sequence']
            if not props:
                display_message(insert_value_frame, f"No properties found for category {selected_cat}.", "error")
                prop_conn.close()
                return
            prop_conn.commit()
            prop_conn.close()
            if not os.path.exists(db_path):
                display_message(insert_value_frame, f"Database file not found: {db_path}", "error")
                return
            else:
                selected_property = StringVar(value="Select Property")
                def on_property_selected(*args):
                        selected_prop = selected_property.get()
                        if(selected_prop==""):
                            return
                        table_name = selected_prop
                        label = Label(
                            insert_value_frame,
                            text=f"Upload Excel file:",
                            font=dropdown_font,
                            bg=bg_color,
                            fg=fg_color,
                            width=25,          # Increased width
                            anchor="w"         # Left-align text
                            )
                        label.grid(row=3, column=0, padx=(0,10), pady=6, sticky='w')
                        upload_file_btn = Button(
                            insert_value_frame,
                            text="Upload",
                            command=lambda: upload_excel_file(table_name=table_name, category= selected_cat, frame= insert_value_frame),
                            **button_style
                        )
                        upload_file_btn.grid(row=3, column=1, padx=10, pady=10, sticky="w")
                    
                selected_property.trace_add("write", on_property_selected)
                clear_widgets(widgets, 2)
                dropdown, prop_val= create_dropdown(insert_value_frame,"Select Property:", props, row=2, var=selected_property)
                
                

    selected_category.trace_add("write", on_selected_category)
    dropdown, prop_var= create_dropdown(insert_value_frame,"Select Category:", cat_keys, row=1, var=selected_category)
    





    




