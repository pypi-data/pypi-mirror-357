import tkinter as tk

class SearchableDropdown(tk.Frame):
    def __init__(self, parent, label_text, options, var=None, width=30, font=("Segoe UI", 11),
                 bg="#1e1e1e", fg="#ffffff", **kwargs):
        super().__init__(parent, bg=bg)
        self.var = var or tk.StringVar()
        self.options = options
        self.filtered_options = options.copy()
        self.font = font
        self.bg = bg
        self.fg = fg
        self.enabled = True
        self.last_selected = None
        self._mouse_inside = False
        self._suppress_listbox = False
        self.label = tk.Label(self, text=label_text, font=font, bg=bg, fg=fg, width=25, anchor="w")
        self.label.grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self._skip_next_placeholder_restore = False

        self.placeholder = f"Select {label_text.replace(':','').strip()}"
        if not self.var.get():
            self.var.set(self.placeholder)
        self.bind_all("<Button-1>", self.handle_global_click, add="+")

        self.entry = tk.Entry(self, textvariable=self.var, font=font, bg="#2d2d2d", fg=fg, width=width, state="normal")
        self.entry.grid(row=0, column=1, padx=10, pady=6, sticky="w")
        self.entry.bind("<KeyRelease>", self.update_listbox)
        self.entry.bind("<Button-1>", self.clear_placeholder)
        self.entry.bind("<FocusIn>", self.clear_placeholder)
        self.entry.bind("<FocusOut>", self.restore_placeholder)

        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        self.listbox = tk.Listbox(self, font=font, bg="#2d2d2d", fg=fg, width=width, height=6, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.grid(row=1, column=1, padx=10, pady=(0,6), sticky="w")
        self.scrollbar.grid(row=1, column=2, sticky="nsw", pady=(0,6))

        self.listbox.bind("<ButtonRelease-1>", self.on_select_mouse)
        self.listbox.bind("<Return>", self.on_select)
        self.listbox.bind("<Escape>", self.hide_listbox)
        self.listbox.bind("<FocusOut>", self.hide_listbox)
        self.entry.bind("<Button-1>", self.show_listbox)
        self.entry.bind("<FocusIn>", self.show_listbox)
        self.listbox.grid_remove()
        self.scrollbar.grid_remove()


    def set_enabled(self, enabled=True):
        self.enabled = enabled
        state = "normal" if enabled else "disabled"
        self.entry.config(state=state)
        if not enabled:
            self.listbox.grid_remove()
            self.scrollbar.grid_remove()
            self.var.set(self.placeholder)

    def clear_placeholder(self, event=None):
        if not self.enabled:
            return
        if self.var.get() == self.placeholder:
            self.var.set("")
            self.entry.config(fg=self.fg)
        self.update_listbox()
        if self.filtered_options:
            self.listbox.grid()
            self.scrollbar.grid()

    def restore_placeholder(self, event=None):
        if self._skip_next_placeholder_restore:
            self._skip_next_placeholder_restore = False
            return  # Don't restore placeholder, it was a valid selection
        if not self.enabled:
            return
        if not self.var.get():
            self.var.set(self.placeholder)
            self.entry.config(fg="#888888")
        else:
            self.entry.config(fg=self.fg)
        self.hide_listbox()

    def update_listbox(self, event=None):
        if not self.enabled:
            return
        if self._suppress_listbox:
            self._suppress_listbox = False
            return
        search = self.var.get().lower()
        if self.var.get() == self.placeholder:
            filtered = self.options
        else:
            filtered = [opt for opt in self.options if search in opt.lower()]
        self.filtered_options = filtered
        self.listbox.delete(0, tk.END)
        for opt in self.filtered_options:
            self.listbox.insert(tk.END, opt)
        if self.filtered_options and self.entry.focus_get() == self.entry and event is not None:
            self.listbox.grid()
            self.scrollbar.grid()
        else:
            self.listbox.grid_remove()
            self.scrollbar.grid_remove()



    def show_listbox(self, event=None):
        if not self.enabled:
            return
        self.update_listbox()
        if self.filtered_options:
            self.listbox.grid()
            self.scrollbar.grid()

    def hide_listbox(self, event=None):
        try:
            if self.listbox.winfo_exists():
                self.listbox.grid_remove()
            if self.scrollbar.winfo_exists():
                self.scrollbar.grid_remove()
        except tk.TclError:
            # The widget was already destroyed
            pass

    def on_select(self, event):
        if not self.enabled:
            return
        if self.listbox.curselection():
            value = self.filtered_options[self.listbox.curselection()[0]]
            self._suppress_listbox = True
            self.var.set(value)
            self.last_selected = value
            self.entry.config(fg=self.fg)
            self.entry.focus_set()
            self.hide_listbox()
            self.entry.icursor(tk.END)
            if hasattr(self, "on_selection_callback") and self.on_selection_callback:
                self.on_selection_callback()
        self._suppress_listbox = False

    


    

    def set_on_selection_callback(self, callback):
        self.on_selection_callback = callback


    def handle_global_click(self, event):
        self._check_and_close(event.widget)

    def _check_and_close(self, widget):
        if self.winfo_exists() and not self.is_click_inside(widget):
            self.restore_placeholder()

    def is_click_inside(self, widget):
    # Check if widget is this entry, listbox, scrollbar, or a child of this dropdown
        while widget:
            if widget == self or widget == self.entry or widget == self.listbox or widget == self.scrollbar:
                return True
            try:
                widget = widget.master
            except AttributeError:
                break
        return False
    def on_select_mouse(self, event):
        index = self.listbox.nearest(event.y)
        if 0 <= index < len(self.filtered_options):
            value = self.filtered_options[index]
            self._suppress_listbox = True
            self.var.set(value)
            self.last_selected = value
            self.hide_listbox()  # Hide the listbox immediately after selection
            self.entry.icursor(tk.END)
            self._skip_next_placeholder_restore = True

            self.master.focus_set()
            if hasattr(self, "on_selection_callback") and self.on_selection_callback:
                self.on_selection_callback()
        self._suppress_listbox = False