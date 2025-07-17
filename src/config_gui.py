import customtkinter as ctk
from tkinter import messagebox

class ChunkConfigDialog(ctk.CTkToplevel):
    """Simple configuration dialog for chunk settings."""

    def __init__(self, master, doc_length: int):
        super().__init__(master)
        self.title("Chunk Einstellungen")
        self.resizable(False, False)
        self.doc_length = doc_length
        self.result = None

        self.chunk_var = ctk.StringVar(value="5000")
        self.mode_var = ctk.StringVar(value="all")
        self.start_var = ctk.StringVar(value="1")
        self.end_var = ctk.StringVar(value=str(doc_length))

        self._build_ui()

    def _build_ui(self):
        info = ctk.CTkLabel(self, text=f"Gesamtlänge des Dokuments: {self.doc_length:,} Zeichen")
        info.pack(padx=20, pady=(10, 5))

        size_frame = ctk.CTkFrame(self)
        size_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(size_frame, text="Chunk-Größe in Zeichen:").pack(side="left")
        self.size_entry = ctk.CTkEntry(size_frame, textvariable=self.chunk_var, width=80)
        self.size_entry.pack(side="right")

        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=20, pady=(10, 5))
        ctk.CTkLabel(mode_frame, text="Zu verarbeitender Bereich:").pack(anchor="w")
        rb_all = ctk.CTkRadioButton(mode_frame, text="Gesamtes Dokument", variable=self.mode_var, value="all", command=self._toggle_range)
        rb_all.pack(anchor="w")
        rb_range = ctk.CTkRadioButton(mode_frame, text="Spezifischer Bereich", variable=self.mode_var, value="range", command=self._toggle_range)
        rb_range.pack(anchor="w")

        range_frame = ctk.CTkFrame(self)
        range_frame.pack(fill="x", padx=20, pady=(5, 5))
        ctk.CTkLabel(range_frame, text="Start-Zeichen:").grid(row=0, column=0, padx=5, pady=2)
        self.start_entry = ctk.CTkEntry(range_frame, textvariable=self.start_var, width=80)
        self.start_entry.grid(row=0, column=1, padx=5, pady=2)
        ctk.CTkLabel(range_frame, text="End-Zeichen:").grid(row=1, column=0, padx=5, pady=2)
        self.end_entry = ctk.CTkEntry(range_frame, textvariable=self.end_var, width=80)
        self.end_entry.grid(row=1, column=1, padx=5, pady=2)

        self._range_widgets = (self.start_entry, self.end_entry)
        self._toggle_range()

        start_btn = ctk.CTkButton(self, text="Start", command=self._on_start)
        start_btn.pack(pady=(10, 10))

        self.bind("<Return>", lambda _e: self._on_start())

    def _toggle_range(self):
        state = "normal" if self.mode_var.get() == "range" else "disabled"
        for widget in self._range_widgets:
            widget.configure(state=state)

    def _on_start(self):
        try:
            chunk_size = int(self.chunk_var.get())
        except ValueError:
            messagebox.showerror("Fehler", "Chunk-Größe muss eine Zahl sein.")
            return
        if chunk_size < 500 or chunk_size > 50000:
            messagebox.showerror("Fehler", "Chunk-Größe muss zwischen 500 und 50000 liegen.")
            return

        if self.mode_var.get() == "range":
            try:
                start = int(self.start_var.get())
                end = int(self.end_var.get())
            except ValueError:
                messagebox.showerror("Fehler", "Start und Ende müssen Ganzzahlen sein.")
                return
            if not (1 <= start < end <= self.doc_length):
                messagebox.showerror("Fehler", "Ungültiger Bereich angegeben.")
                return
        else:
            start = 1
            end = self.doc_length

        self.result = {
            "chunk_size": chunk_size,
            "start": start - 1,
            "end": end,
            "mode": self.mode_var.get(),
        }
        self.destroy()

    def show(self):
        self.grab_set()
        self.wait_window()
        return self.result
