from tkinter import Label, OptionMenu, StringVar
from ui_components.searchable_dropdown import SearchableDropdown

def create_dropdown(parent, label_text, options, row=0, var=None):
    dropdown = SearchableDropdown(parent, label_text, options, var=var)
    dropdown.grid(row=row, column=0, columnspan=2, sticky="w")
    return dropdown, dropdown.var
