from tkinter.ttk import Notebook
from tkinter import messagebox

from frontend.core.api_provider import ApiProvider
from frontend.features.note_editor_feature import NoteEditorFeature
from frontend.features.imagen_editor_feature import ImageEditorFeature
from frontend.core.bus import Bus
import os

class TabManager:
    """
    Manages the creation, deletion, and lifecycle of 
    Tkinter Notebook tabs.
    """
    def __init__(self, notebook: Notebook):
        self.notebook = notebook
        self.api = ApiProvider.get()
        self.tabs_notes_active = {}
        self.tabs_images_active = {}
        self.suscribes()
    
    def suscribes(self):
        Bus.subscribe("OPEN_TAB_NOTE", self.open_note_in_tab)
        Bus.subscribe("CLOSE_TAB_NOTE", self.close_note_tab)
        Bus.subscribe("CLOSE_TAB_NOTES", self.close_notes_tab)
        Bus.subscribe("CHANGE_NAME_NOTE_TAB", self.update_tab_note_title)

        Bus.subscribe("OPEN_TAB_IMAGE", self.open_image_in_tab)
        Bus.subscribe("CLOSE_TAB_IMAGE", self.close_image_tab)
        Bus.subscribe("CLOSE_TAB_IMAGES", self.close_images_tab)
        Bus.subscribe("CHANGE_NAME_IMAGE_TAB", self.update_tab_image_title)

    def open_note_in_tab(self, note_id: int):
        if note_id in self.tabs_notes_active:
            self.notebook.select(self.tabs_notes_active[note_id])
            return
        
        res = self.api.get_note_details(note_id=note_id)
        if not res.successful or res.obj is None:
            messagebox.showerror("Error", res.info)
            return

        tab_instance = NoteEditorFeature(
            parent = self.notebook,
            note_id = note_id,
            note_data = res.obj   
        )
        self.tabs_notes_active[note_id] = tab_instance

        self.notebook.add(tab_instance, text=res.obj.name)
        self.notebook.select(tab_instance)

    def open_image_in_tab(self, image_id: int):
        if image_id in self.tabs_images_active:
            self.notebook.select(self.tabs_images_active[image_id])
            return
        
        res = self.api.get_image_details(image_id=image_id)
        if not res.successful or res.obj is None:
            messagebox.showerror("Error", res.info)
            return
        
        file_path = res.obj.file_path
        if not os.path.exists(file_path):
            messagebox.showerror(
            "Archivo No Encontrado", 
            f"El registro existe, pero la imagen física ha sido borrada o movida:\n\n{file_path}"
            )
            return
        
        tab_instance = ImageEditorFeature(
            parent = self.notebook,
            image_id = image_id,
            image_data = res.obj
        ) 
        self.tabs_images_active[image_id] = tab_instance

        self.notebook.add(tab_instance, text=res.obj.name)
        self.notebook.select(tab_instance)

    def close_images_tab(self, list_image_ids : list[int]):
        for id in list_image_ids:
            self.close_image_tab(id)

    def close_notes_tab(self, list_note_ids : list[int]):
        for id in list_note_ids:
            self.close_note_tab(id)

    def close_note_tab(self, note_id: int):
        if note_id in self.tabs_notes_active:
            tab_instance = self.tabs_notes_active[note_id]
            self.notebook.forget(tab_instance)
            tab_instance.destroy()
            del self.tabs_notes_active[note_id]
    
    def close_image_tab(self, image_id: int):
        if image_id in self.tabs_images_active:
            tab_instance = self.tabs_images_active[image_id]
            self.notebook.forget(tab_instance)
            tab_instance.destroy()
            del self.tabs_images_active[image_id]

    def update_tab_note_title(self, note_id: int, new_name: str):
        nid = int(note_id)
        
        if nid in self.tabs_notes_active:
            tab_instance = self.tabs_notes_active[nid]
            
            self.notebook.tab(tab_instance, text=new_name)
    
    def update_tab_image_title(self, image_id: int, new_name: str):
        iid = int(image_id)
        
        if iid in self.tabs_images_active:
            tab_instance = self.tabs_images_active[iid]
            
            self.notebook.tab(tab_instance, text=new_name)