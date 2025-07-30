# ui_components/dropdown.py

from .searchable_dropdown import SearchableComboBox

def create_dropdown(options: list) -> SearchableComboBox:
    """
    Creates and returns a configured SearchableComboBox.
    The label and placement are now handled by the QFormLayout.
    """
    dropdown = SearchableComboBox()
    dropdown.set_options(options)
    dropdown.setFixedWidth(280)
    return dropdown