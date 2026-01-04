import tkinter as tk
from tkinter import ttk, messagebox
from frontend.core.api_provider import ApiProvider
from frontend.core.bus import Bus

# Importamos los componentes de UI (widgets de tipo Feature)
from frontend.features.markdown_editor_feature import MarkdownEditorFeature
from frontend.features.chronometer_feature import ChronometerFeature
from frontend.features.messagebox import custom_messagebox

class NoteEditorFeature(ttk.Frame):
    """
    Feature: NoteEditor
    Muestra características del tema y la nota...
    """
    def __init__(self, parent, note_id: int):
        super().__init__(parent, padding=0)
        self.api = ApiProvider.get()
        self.note_id = note_id
        self.note_data = None

        self._create_widgets()
        self._load_note_data()

    def _create_widgets(self):
        # Contenedor principal
        content = ttk.Frame(self)
        content.pack(expand=True, fill="both")

        # ====== TOP BAR (Barra de herramientas) =========
        top = ttk.Frame(content)
        top.pack(fill="x", padx=8, pady=(8, 0))

        # Sub-Feature: Cronómetro (Autónomo)
        self.chrono = ChronometerFeature(top, note_id=self.note_id)
        self.chrono.pack(side="left", padx=(0, 3), pady=3)

        self.label_status = ttk.Label(top, text="", font=("Segoe UI", 9, "italic"))
        self.label_status.pack(side="left", padx=10, pady=3)

        # Botones de acción global de la nota
        tk.Button(top, text="✖", command=self._ui_cerrar_pestana).pack(side="right", padx=(3, 0))
        tk.Button(top, text="💾", command=self.guardar_contenido).pack(side="right", padx=3)

        # ====== EDITOR AREA (Markdown Feature) =========
        # Como MarkdownEditorFeature ya es un Frame con Scrollbar, solo hacemos pack
        self.editor = MarkdownEditorFeature(
            content, 
            id_note = self.note_id,
            bg="#F0F0F0" 
        )
        self.editor.pack(fill="both", expand=True, padx=8, pady=8)
        Bus.subscribe("ACTIVE_MARKDOWN", self._toggle_preview_label)

    def _load_note_data(self):
        """Pide los datos de la nota a la API y los carga en el editor."""
        res = self.api.get_note_details(self.note_id)
        if not res.successful or res.obj is None:
            messagebox.showerror("Error", res.info)
            return

        self.note_data = res.obj
        self.editor.insert("1.0", self.note_data.content)
        self.editor.edit_reset()
        self.editor.edit_modified(False)

    def guardar_contenido(self):
        """Extrae el texto del editor y lo persiste vía API."""
        nuevo_contenido = self.editor.get_markdown()
        res = self.api.update_note_content(self.note_id, nuevo_contenido)
        
        if not res.successful:
            messagebox.showerror("Error", res.info)
            return
         
        self.editor.edit_modified(False)
        Bus.emit("NOTE_SAVED", note_id=self.note_id)
        messagebox.showinfo("Éxito", "Nota guardada correctamente.")


    def _ui_cerrar_pestana(self):
        """Verifica cambios pendientes antes de emitir la orden de cierre."""
        if self.editor.edit_modified():
            choice = custom_messagebox(
                "Notas",
                "Hay cambios sin guardar. ¿Qué desea hacer?",
                ["Guardar", "No Guardar", "Cancelar"]
            )
            if choice == "Guardar":
                self.guardar_contenido()
            elif choice == "Cancelar":
                return
        
        # Notificamos al Bus que esta nota debe cerrarse
        Bus.emit("CLOSE_NOTE_TAB", note_id=self.note_id)

    def _toggle_preview_label(self, is_active: bool, id_note: int):
        """Actualiza el label de estado cuando el editor cambia a preview."""
        if id_note == self.note_id:
            self.label_status.config(text="MODO PREVIEW" if is_active else "")

    def destroy(self):
        Bus.unsubscribe("ACTIVE_MARKDOWN", self._toggle_preview_label)
        super().destroy()