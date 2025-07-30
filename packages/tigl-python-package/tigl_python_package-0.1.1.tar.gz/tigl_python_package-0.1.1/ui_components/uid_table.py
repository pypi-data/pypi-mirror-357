import tkinter as tk
from tkinter import ttk

def show_uid_table(parent, uid, selected_props):
    # Clear any existing Treeview widgets
    for widget in parent.winfo_children():
        widget.destroy()

    # Create a frame for the table and copy button side by side
    container = tk.Frame(parent, bg=parent["bg"])
    container.pack(padx=10, pady=10, fill="x", expand=True)

    # Prepare columns: UID + property names
    columns = ["UID"] + [name for name, _ in selected_props]
    # Create Treeview with two columns: UID and Properties
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
    "Treeview",
    background="#1e1e1e",
    foreground="#ffffff",
    fieldbackground="#1e1e1e",
    rowheight=38,
    font=("Segoe UI", 11)
)
    style.configure(
    "Treeview.Heading",
    background="#2d2d2d",
    foreground="#ffffff",
    font=("Segoe UI", 11, "bold")
)
    style.map("Treeview", background=[("selected", "#3a3a3a")])
    tree = ttk.Treeview(container, columns=columns, show="headings", height=1)

    # Set headings
    tree.heading("UID", text="Generated UID")
    tree.column("UID", anchor="center")
    for name, _ in selected_props:
        tree.heading(name, text=name)
        tree.column(name, anchor="center")

    # Insert values
    values = [uid] + [value for _, value in selected_props]
    tree.insert("", "end", values=values)
    tree.pack(side="left", fill="x", expand=True)

    # Copy all values (tab-separated)
    def copy_to_clipboard():
        formatted = "\t".join(values)
        parent.clipboard_clear()
        parent.clipboard_append(formatted)
        parent.update()

    # Add Copy Button
    copy_button = tk.Button(container, text="Copy", command=copy_to_clipboard)
    copy_button.pack(side="left", padx=10)

