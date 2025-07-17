import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import messagebox
import os
from pathlib import Path
from typing import List, Optional
import threading
from .text_chunker import TextChunker
from .file_handler import FileHandler
from .logger import setup_logger
from .config_gui import ChunkConfigDialog

logger = setup_logger("gui")

# CustomTkinter Appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChunkerGUI:
    """
    GUI für den Chat Chunker mit Drag & Drop Funktionalität.
    """
    
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("Chat Chunker")
        self.root.geometry("800x600")
        
        # Core-Komponenten
        self.text_chunker = TextChunker()
        self.file_handler = FileHandler()
        
        # Dateiliste
        self.loaded_files: List[str] = []
        
        # GUI aufbauen
        self._setup_gui()
        
        logger.info("GUI initialisiert")
    
    def _setup_gui(self):
        """Baut die GUI-Komponenten auf."""
        # Hauptframe
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Chat Chunker", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Drop Zone
        self.drop_frame = ctk.CTkFrame(main_frame, height=200)
        self.drop_frame.pack(fill="x", pady=(0, 20))
        
        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text="📁 Dateien hier hineinziehen\noder klicken zum Auswählen",
            font=ctk.CTkFont(size=16),
            height=150
        )
        self.drop_label.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Drag & Drop aktivieren
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self._on_drop)
        
        # Dateiliste Frame
        files_frame = ctk.CTkFrame(main_frame)
        files_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        files_label = ctk.CTkLabel(
            files_frame,
            text="Geladene Dateien:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        files_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Scrollable Frame für Dateiliste
        self.files_scroll = ctk.CTkScrollableFrame(files_frame, height=150)
        self.files_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Button Frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        # Process Button
        self.process_button = ctk.CTkButton(
            button_frame,
            text="Verarbeiten",
            command=self._process_files,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40
        )
        self.process_button.pack(side="left", padx=(0, 10))
        
        # Clear Button
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Liste leeren",
            command=self._clear_files,
            font=ctk.CTkFont(size=14),
            height=40,
            width=100
        )
        self.clear_button.pack(side="left")
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", pady=(20, 0))
        self.progress_bar.set(0)
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Bereit",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(10, 0))
    
    def _on_drop(self, event):
        """Handler für Drag & Drop Events."""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.endswith('.txt') and file not in self.loaded_files:
                self.loaded_files.append(file)
                self._add_file_to_list(file)
                logger.info(f"Datei hinzugefügt: {file}")
        self._update_ui_state()
    
    def _add_file_to_list(self, file_path: str):
        """Fügt eine Datei zur visuellen Liste hinzu."""
        file_frame = ctk.CTkFrame(self.files_scroll)
        file_frame.pack(fill="x", pady=2)
        
        # Dateiname
        file_name = os.path.basename(file_path)
        file_label = ctk.CTkLabel(
            file_frame,
            text=file_name,
            anchor="w"
        )
        file_label.pack(side="left", fill="x", expand=True, padx=10)
        
        # Dateigröße
        file_size = os.path.getsize(file_path)
        size_label = ctk.CTkLabel(
            file_frame,
            text=f"{file_size:,} Bytes",
            anchor="e",
            width=100
        )
        size_label.pack(side="right", padx=10)
    
    def _clear_files(self):
        """Leert die Dateiliste."""
        self.loaded_files.clear()
        for widget in self.files_scroll.winfo_children():
            widget.destroy()
        self._update_ui_state()
        self.status_label.configure(text="Liste geleert")
        logger.info("Dateiliste geleert")
    
    def _update_ui_state(self):
        """Aktualisiert den UI-Status basierend auf geladenen Dateien."""
        if self.loaded_files:
            self.process_button.configure(state="normal")
            self.drop_label.configure(text=f"📁 {len(self.loaded_files)} Datei(en) geladen\nWeitere hinzufügen oder verarbeiten")
        else:
            self.process_button.configure(state="disabled")
            self.drop_label.configure(text="📁 Dateien hier hineinziehen\noder klicken zum Auswählen")
    
    def _process_files(self):
        """Startet die Verarbeitung nach Konfiguration durch den Benutzer."""
        if not self.loaded_files:
            return

        # Länge der ersten Datei ermitteln um sie im Dialog anzuzeigen
        sample_content = self.file_handler.read_file(self.loaded_files[0])
        if sample_content is None:
            messagebox.showerror("Fehler", "Datei konnte nicht gelesen werden.")
            return

        dialog = ChunkConfigDialog(self.root, len(sample_content))
        config = dialog.show()
        if not config:
            self._update_ui_state()
            return

        self.process_button.configure(state="disabled")
        self.clear_button.configure(state="disabled")

        thread = threading.Thread(target=self._process_files_thread, args=(config,))
        thread.start()

    def _process_files_thread(self, config: dict):
        """Thread-Funktion für die Dateiverarbeitung."""
        total_files = len(self.loaded_files)
        
        for i, file_path in enumerate(self.loaded_files):
            progress = (i / total_files)
            self.progress_bar.set(progress)
            self.status_label.configure(text=f"Verarbeite: {os.path.basename(file_path)}")

            content = self.file_handler.read_file(file_path)
            if content:
                selection = content[config["start"]:config["end"]]
                formatted_content = self.text_chunker.format_with_speakers(selection)

                self.text_chunker.max_chunk_size = config["chunk_size"]
                chunks = self.text_chunker.split_text(formatted_content)

                self.file_handler.save_chunks(chunks, os.path.basename(file_path))
            
            logger.info(f"Datei verarbeitet: {file_path}")
        
        # Abschluss
        self.progress_bar.set(1.0)
        self.status_label.configure(text=f"✅ {total_files} Datei(en) erfolgreich verarbeitet")
        self.process_button.configure(state="normal")
        self.clear_button.configure(state="normal")
        
        logger.info(f"Verarbeitung abgeschlossen: {total_files} Dateien")
    
    def run(self):
        """Startet die GUI."""
        self.root.mainloop() 