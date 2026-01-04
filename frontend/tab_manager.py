from tkinter.ttk import Notebook
from tkinter import messagebox

from frontend.core.api_provider import ApiProvider
from frontend.features.note_editor_feature import NoteEditorFeature
from frontend.core.bus import Bus


class TabManager:
    def __init__(self, notebook: Notebook):
        self.notebook = notebook
        self.api = ApiProvider.get()
        self.tabs_active = {}
        self.suscribes()
    
    def suscribes(self):
        Bus.subscribe("CLOSE_NOTE_TAB", self.close_note_tab)
        Bus.subscribe("OPEN_NOTE", self.open_note_in_tab)
        Bus.subscribe("DELETE_NOTES", self.close_notes_tab)
        Bus.subscribe("DELETE_NOTE", self.close_note_tab)
        Bus.subscribe("CHANGE_NOTE_NAME", self.update_tab_title)

    def open_note_in_tab(self, note_id: int):
        if note_id in self.tabs_active:
            self.notebook.select(self.tabs_active[note_id])
            return
        
        res = self.api.get_note_details(note_id=note_id)
        if not res.successful or res.obj is None:
            messagebox.showerror("Error", res.info)
            return

        tab_instance = NoteEditorFeature(
            parent = self.notebook,
            note_id = note_id
        )
        self.tabs_active[note_id] = tab_instance

        self.notebook.add(tab_instance, text=res.obj.name)
        self.notebook.select(tab_instance)

    def close_notes_tab(self, list_note_ids : list[int]):
        for id in list_note_ids:
            self.close_note_tab(id)

    def close_note_tab(self, note_id: int):
        if note_id in self.tabs_active:
            tab_instance = self.tabs_active[note_id]
            self.notebook.forget(tab_instance)
            tab_instance.destroy()
            del self.tabs_active[note_id]

    def update_tab_title(self, note_id: int, new_name: str):
        # 1. Aseguramos el ID como entero (para que no nos pase lo de antes :v)
        nid = int(note_id)
        
        # 2. Buscamos si hay un tab abierto para esa nota
        if nid in self.tabs_active:
            tab_instance = self.tabs_active[nid]
            
            # 3. Cambiamos el texto de la pestaña
            self.notebook.tab(tab_instance, text=new_name)