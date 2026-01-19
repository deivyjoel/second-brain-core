import tkinter as tk
from tkinter import ttk, messagebox
from frontend.core.api_provider import ApiProvider
from frontend.core.bus import Bus

from frontend.features.markdown_editor_feature import MarkdownEditorFeature
from frontend.features.chronometer_feature import ChronometerFeature
from frontend.features.messagebox import custom_messagebox

class NoteEditorFeature(ttk.Frame):
    def __init__(self, parent, 
                 note_id: int,
                 note_data):
        super().__init__(parent, padding=0)
        self.api = ApiProvider.get()
        self.note_id = note_id
        self.note_data = note_data

        self._create_widgets()
        self._load_content()

    def _create_widgets(self):
        content = ttk.Frame(self)
        content.pack(expand=True, fill="both")

        top = ttk.Frame(content, height=30)
        top.pack(fill="x", padx=8, pady=(8, 0))
        top.propagate(False)

        # Chronometer Feature
        self.chrono = ChronometerFeature(top, note_id=self.note_id)
        self.chrono.pack(side="left", padx=(0, 3), pady=3)

        # Status Label
        self.label_status = ttk.Label(top, text="", font=("Segoe UI", 9, "italic"))
        self.label_status.pack(side="left", padx=10, pady=3)

        # Action Buttons
        tk.Button(top, text="✖", command=self._ui_close_tab).pack(side="right", padx=(3, 0))
        tk.Button(top, text="💾", command=self.save_content).pack(side="right", padx=3)
        
        # Markdown Editor
        self.editor = MarkdownEditorFeature(
            content, 
            id_note = self.note_id,
            bg="#F0F0F0" 
        )
        self.editor.pack(fill="both", expand=True, padx=8, pady=8)
        Bus.subscribe("ACTIVE_MARKDOWN", self._toggle_preview_label)

    def _load_content(self):
        self.editor.insert("1.0", self.note_data.content)
        self.editor.edit_reset()
        self.editor.edit_modified(False)

    def save_content(self):
        nuevo_contenido = self.editor.get_markdown()
        res = self.api.update_note_content(self.note_id, nuevo_contenido)
        
        if not res.successful:
            messagebox.showerror("Error", res.info)
            return
         
        self.editor.edit_modified(False)
        messagebox.showinfo("Éxito", "Nota guardada correctamente.")


    def _ui_close_tab(self):
        if self.editor.edit_modified():
            choice = custom_messagebox(
                "Notas",
                "Hay cambios sin guardar. ¿Qué desea hacer?",
                ["Guardar", "No Guardar", "Cancelar"]
            )
            if choice == "Guardar":
                self.save_content()
            elif choice == "Cancelar":
                return
        Bus.emit("CLOSE_TAB_NOTE", note_id=self.note_id)

    def _toggle_preview_label(self, is_active: bool, id_note: int):
        """Update the status label when the editor switches to preview mode."""
        if id_note == self.note_id:
            self.label_status.config(text="MODO PREVIEW" if is_active else "")

    def destroy(self):
        """Cleanup subscriptions on destroy."""
        Bus.unsubscribe("ACTIVE_MARKDOWN", self._toggle_preview_label)
        super().destroy()