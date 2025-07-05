import tkinter as tk

class CustomCombobox(tk.Frame):
    def __init__(self, master, values, width=12, command=None, initial=None, **kwargs):
        super().__init__(master, **kwargs)
        self.values = values
        self.command = command
        self.selected = tk.StringVar(value=initial if initial is not None else values[0])
        self.width = width

        # Main button
        self.button = tk.Button(
            self, textvariable=self.selected, width=self.width,
            bg="#0074D9", fg="white", bd=0, relief="flat",
            font=("Segoe UI", 10, "bold"), anchor="w",
            command=self.toggle_list
        )
        self.button.pack(side="left", fill="x", expand=True)

        # White arrow (using Canvas)
        self.arrow = tk.Canvas(self, width=18, height=18, bg="#0074D9", highlightthickness=0)
        self.arrow.create_polygon(5, 7, 13, 7, 9, 13, fill="white")
        self.arrow.pack(side="right")

        # Listbox (hidden by default)
        self.listbox = None

    def toggle_list(self):
        if self.listbox and self.listbox.winfo_ismapped():
            self.listbox.place_forget()
        else:
            if not self.listbox:
                self.listbox = tk.Listbox(self, bg="#0074D9", fg="white", font=("Segoe UI", 10, "bold"), bd=0, relief="flat")
                for v in self.values:
                    self.listbox.insert("end", v)
                self.listbox.bind("<<ListboxSelect>>", self.on_select)
            self.listbox.place(x=0, y=self.winfo_height(), width=self.button.winfo_width() + self.arrow.winfo_width())

    def on_select(self, event):
        idx = self.listbox.curselection()
        if idx:
            value = self.values[idx[0]]
            self.selected.set(value)
            if self.command:
                self.command(value)
        self.listbox.place_forget()

    def get(self):
        return self.selected.get()

    def set(self, value):
        self.selected.set(value)
