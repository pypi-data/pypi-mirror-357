from tkinter import Label


def display_message(frame, message, msg_type="error"):
    """Display a message in the given frame."""
    # Remove existing message label if any
    for widget in frame.winfo_children():
        if getattr(widget, "_is_msg_label", False):
            widget.destroy()

    color_map = {
        "error": "#ff4c4c",      # Red
        "success": "#4caf50",    # Green
        "info": "#2196f3",       # Blue
        "warning": "#ff9800"     # Orange
    }
    msg_color = color_map.get(msg_type, "#ffffff")

    msg_label = Label(
        frame,
        text=message,
        font=("Segoe UI", 10, "bold"),
        fg=msg_color,
        bg="#1e1e1e",
        wraplength=400,
        justify="left",
        anchor="w"
    )
    msg_label._is_msg_label = True  # Tag the label so we can identify and replace it
    msg_label.grid(row=99, column=0, columnspan=3, sticky="w", padx=10, pady=(5, 10))
def clear_message(frame):
    """Remove message label from the frame if present."""
    for widget in frame.winfo_children():
        if getattr(widget, "_is_msg_label", False):
            widget.destroy()
