import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from frontend.core.api_provider import ApiProvider
from frontend.core.bus import Bus
from tkinter import filedialog

class ExplorerFeature(ttk.Frame):
    TYPE_THEME = "theme"
    TYPE_NOTE = "note"
    TYPE_IMAGE = "image"
    TYPE_DUMMY = "dummy"
    
    ICON_THEME = "📁"
    ICON_NOTE = "📄"
    ICON_IMAGE = "📸"
    DUMMY_TEXT = "Sin contenido..."

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.api = ApiProvider.get()
        self.loaded_nodes = set()
        self.dragging_item = None

        self._setup_ui()
        self._setup_events()
        self.load_root()

    # --- SETUP ---
    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(self, show="tree", selectmode="extended")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.column("#0", width=250, minwidth=150)

        # Context menu for themes
        self.menu_theme = tk.Menu(self, tearoff=0)
        self.menu_theme.add_command(label="📈 Analiticas", command=self._get_details)
        self.menu_theme.add_separator()
        self.menu_theme.add_command(label=f"{self.ICON_NOTE} Nueva Nota", command=self._ui_new_note)
        self.menu_theme.add_command(label=f"{self.ICON_THEME} Nuevo Tema", command=self._ui_new_theme)
        self.menu_theme.add_command(label=f"{self.ICON_IMAGE} Nueva Imagen", command=self._ui_new_image)
        self.menu_theme.add_separator()
        self.menu_theme.add_command(label="✏️ Renombrar", command=self._ui_start_rename)
        self.menu_theme.add_command(label="🗑️ Eliminar", command=self._ui_delete_item)

        # Context menu for notes
        self.menu_note = tk.Menu(self, tearoff=0)
        self.menu_note.add_command(label="📈 Analiticas", command=self._get_details)
        self.menu_note.add_separator()
        self.menu_note.add_command(label="✏️ Renombrar", command=self._ui_start_rename)
        self.menu_note.add_command(label="🗑️ Eliminar", command=self._ui_delete_item)

        # Menu for when 'nothing' is selected
        self.menu_nothing = tk.Menu(self, tearoff=0)
        self.menu_nothing.add_command(label=f"{self.ICON_NOTE} Nueva Nota", command=self._ui_new_note)
        self.menu_nothing.add_command(label=f"{self.ICON_THEME} Nuevo Tema", command=self._ui_new_theme)
        self.menu_nothing.add_command(label=f"{self.ICON_IMAGE} Nueva Imagen", command=self._ui_new_image)

        # Menu for when 'image' is selected
        self.menu_image = tk.Menu(self, tearoff=0)
        self.menu_image.add_command(label="🗑️ Eliminar", command=self._ui_delete_item)
        self.menu_image.add_command(label="✏️ Renombrar", command=self._ui_start_rename)
        self.menu_image.add_separator()
        self.menu_image.add_command(label="➜] Exportar", command=self._ui_export_image)

    def _setup_events(self):
        self.tree.bind("<<TreeviewOpen>>", self._on_treeview_expand)
        self.tree.bind("<Button-1>", self._on_left_click)
        self.tree.bind("<Button-3>", self._on_right_click)

        #Nuevo comando...
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonPress-1>", self._on_drag_start, add="+")
        self.tree.bind("<ButtonRelease-1>", self._on_drag_finish, add="+")

    # --- EVENTS MOUSE ---
    def _on_left_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid and iid.startswith(self.TYPE_NOTE):
            _, note_id = self._parse_iid(iid)
            Bus.emit("OPEN_TAB_NOTE", note_id=note_id)
        elif iid and iid.startswith(self.TYPE_IMAGE):
            _, image_id = self._parse_iid(iid)
            Bus.emit("OPEN_TAB_IMAGE", image_id=image_id)
        elif not iid:
            self.tree.selection_set(())
            self.tree.focus("")

    def _on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        current_selection = self.tree.selection()

        if iid:
            if iid not in current_selection:
                self.tree.selection_set(iid)
                self.tree.focus(iid)
        else:
            self.tree.selection_set(())
            self.tree.focus("")

        focused_iid = self.tree.identify_row(event.y)
        tipo, _ = self._parse_iid(focused_iid)

        if tipo == self.TYPE_THEME:
            self.menu_theme.post(event.x_root, event.y_root)
        elif tipo == self.TYPE_NOTE:
            self.menu_note.post(event.x_root, event.y_root)
        elif tipo == self.TYPE_IMAGE:
            self.menu_image.post(event.x_root, event.y_root)
        elif tipo is None:
            self.menu_nothing.post(event.x_root, event.y_root)
        
    # --- HELPERS ---
    def _parse_iid(self, iid: str):
        """ Returns (type, id) from an iid 'type_id'"""
        if not iid or "_" not in iid:
            return None, None
        parts = iid.split("_")
        return parts[0], int(parts[1])

    def _call_api(self, api_func, *args, **kwargs):
        """wrapper to handle API errors centrally."""
        res = api_func(*args, **kwargs)
        if not res.successful:
            messagebox.showerror("Error", res.info or "Error desconocido")
            return None
        return res.obj

    def _manage_dummy(self, parent_iid, action="remove"):
        """Manages the existence of the dummy node."""
        _, p_id = self._parse_iid(parent_iid)
        dummy_id = f"{self.TYPE_DUMMY}_{p_id}"
        
        if action == "remove" and self.tree.exists(dummy_id):
            self.tree.delete(dummy_id)
        elif action == "add" and not self.tree.get_children(parent_iid):
            self.tree.insert(parent_iid, "end", iid=dummy_id, text=self.DUMMY_TEXT)

    # --- LOADING LOGIC ---
    def load_root(self, **kwargs):
        self.tree.delete(*self.tree.get_children())
        self.loaded_nodes.clear()
        
        themes = self._call_api(self.api.list_root_themes)
        notes = self._call_api(self.api.get_notes_without_themes)
        images = self._call_api(self.api.get_images_without_theme)
        if themes is not None:
            for t in themes: 
                self.insert_theme("", t.id, t.name) 
        if notes is not None:
            for n in notes: 
                self.insert_note("", n.id, n.name)
        if images is not None:
            for i in images: 
                self.insert_image("", i.id, i.name)

    def _on_treeview_expand(self, event):
        iid = self.tree.focus()
        if iid.startswith(self.TYPE_THEME) and iid not in self.loaded_nodes:
            self._load_children(iid)

    def _load_children(self, parent_iid: str):
        if parent_iid in self.loaded_nodes: return
        
        _, p_id = self._parse_iid(parent_iid)
        res_themes = self._call_api(self.api.list_child_themes, p_id)
        res_notes = self._call_api(self.api.list_notes_by_theme, p_id)
        res_images = self._call_api(self.api.list_images_by_theme, p_id)
        if res_themes is not None and res_notes is not None and res_images is not None:
            if len(res_themes + res_notes + res_images) > 0:
                self._manage_dummy(parent_iid, "remove")
            
            for t in res_themes: 
                self.insert_theme(parent_iid, t.id, t.name)
            for n in res_notes: 
                self.insert_note(parent_iid, n.id, n.name)
            for i in res_images:
                self.insert_image(parent_iid, i.id, i.name)
            
            self.loaded_nodes.add(parent_iid)

    def insert_note(self, parent_iid, note_id, note_name):
        """Inserts note in tkinter tree"""
        iid = f"{self.TYPE_NOTE}_{note_id}"
        self.tree.insert(parent_iid, "end", iid, text=f"{self.ICON_NOTE} {note_name}")
    
    def insert_theme(self, parent_iid, theme_id, theme_name):
        """Inserts theme in tkinter tree"""
        iid = f"{self.TYPE_THEME}_{theme_id}"
        self.tree.insert(parent_iid, "end", iid, text=f"{self.ICON_THEME} {theme_name}")
        self._manage_dummy(iid, "add")

    def insert_image(self, parent_iid, img_id, img_name):
        iid = f"{self.TYPE_IMAGE}_{img_id}"
        self.tree.insert(parent_iid, "end", iid, text=f"{self.ICON_IMAGE} {img_name}")

    # --- OPERATIONS UI ---
    def _ui_new_note(self):
        selected = self.tree.focus()
        """The head node is loaded before a new note is created to avoid errors."""
        self.tree.event_generate("<<TreeviewOpen>>")
        self.tree.item(selected, open=True)

        _, parent_id = self._parse_iid(selected)

        name = self._call_api(self.api.get_unique_note_name, "Nueva Nota", parent_id)
        if name:
            note_id = self._call_api(self.api.create_note, name, parent_id)
            if note_id:
                if selected not in self.loaded_nodes and parent_id: 
                    return
                
                if parent_id: 
                    self._manage_dummy(selected, "remove")

                self.insert_note(selected if parent_id else "", note_id, name)
                self.tree.selection_set(f"{self.TYPE_NOTE}_{note_id}")

                self.tree.focus(f"{self.TYPE_NOTE}_{note_id}")

                self.tree.see(f"{self.TYPE_NOTE}_{note_id}")
                self._ui_start_rename()

    def _ui_new_theme(self):
        selected = self.tree.focus()
        """The head node is loaded before a new theme is created to avoid errors."""
        self.tree.event_generate("<<TreeviewOpen>>")
        self.tree.item(selected, open=True)
        _, parent_id = self._parse_iid(selected)

        name = self._call_api(self.api.get_unique_theme_name, "   Nuevo tema", parent_id)
        if name:
            theme_id = self._call_api(self.api.create_theme, name, parent_id)
            if theme_id:
                if selected not in self.loaded_nodes and parent_id: 
                    return
                
                if parent_id: 
                    self._manage_dummy(selected, "remove")

                self.insert_theme(selected if parent_id else "", theme_id, name)
                self.tree.selection_set(f"{self.TYPE_THEME}_{theme_id}")

                self.tree.focus(f"{self.TYPE_THEME}_{theme_id}")

                self.tree.see(f"{self.TYPE_THEME}_{theme_id}")
                self._ui_start_rename()

    def _ui_new_image(self):
        selected = self.tree.focus()
        self.tree.event_generate("<<TreeviewOpen>>")
        self.tree.item(selected, open=True)
        _, parent_id = self._parse_iid(selected)

        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        name_image = file_path.split("/")[-1]

        unique_name = self._call_api(self.api.get_unique_image_name, name_image, parent_id)
        if unique_name:
            with open(file_path, "rb") as f:
                blob_data = f.read()
            extension = os.path.splitext(file_path)[1][1:]
            image_id = self._call_api(self.api.create_image, unique_name, blob_data, extension, parent_id)
            if image_id:
                if selected not in self.loaded_nodes and parent_id: 
                    return
                
                if parent_id: 
                    self._manage_dummy(selected, "remove")

                self.insert_image(selected if parent_id else "", image_id, unique_name)
                self.tree.selection_set(f"{self.TYPE_IMAGE}_{image_id}")

                self.tree.focus(f"{self.TYPE_IMAGE}_{image_id}")

                self.tree.see(f"{self.TYPE_IMAGE}_{image_id}")
                file_path = self.api.get_image_details(image_id)
                if not file_path.obj: return
                self._ui_start_rename()
        
    def _ui_start_rename(self):
        iid = self.tree.focus()
        if not iid or iid.startswith(self.TYPE_DUMMY): 
            return
        
        bbox = self.tree.bbox(iid)
        if not bbox: 
            return
        x, y, w, h = bbox
        
        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=w, height=h)
        
        current_full_text = self.tree.item(iid, "text")
        clean_text = current_full_text.replace(self.ICON_THEME, "").replace(self.ICON_NOTE, "").replace(self.ICON_IMAGE, "").strip()
        
        entry.insert(0, clean_text)
        entry.select_range(0, tk.END)
        entry.focus_set()

        self.flag = False

        def save_rename(event=None):
            if self.flag: return
            new_name = entry.get().strip()
            item_type, item_id = self._parse_iid(iid)
            if item_id is None:
                return
            
            if not new_name or new_name == clean_text:
                entry.destroy()
                return

            self.flag = True
            if item_type == self.TYPE_THEME:
                api_func = self.api.rename_theme
            elif item_type == self.TYPE_IMAGE:
                api_func = self.api.rename_image
            else:
                api_func = self.api.rename_note
            
            res = api_func(item_id, new_name)
            
            if res.successful:
                icon = ""
                if item_type == self.TYPE_NOTE:
                    icon = self.ICON_NOTE
                elif item_type == self.TYPE_IMAGE:
                    icon = self.ICON_IMAGE
                elif item_type == self.TYPE_THEME:
                    icon = self.ICON_THEME

                full_text = f"{icon} {new_name}"
                self.tree.item(iid, text=full_text)
                
                if item_type == self.TYPE_NOTE:
                    Bus.emit("CHANGE_NAME_NOTE_TAB", note_id=item_id, new_name=new_name)
                elif item_type == self.TYPE_IMAGE:
                    Bus.emit("CHANGE_NAME_IMAGE_TAB", image_id=item_id, new_name=new_name)

                entry.destroy()
            else:
                messagebox.showerror("Error al renombrar", res.info or "Error desconocido")
                self.flag = False
                entry.focus_set()

        def on_focus_out(event):
            if not self.flag:
                entry.destroy()

        entry.bind("<Return>", save_rename)
        entry.bind("<Escape>", lambda e: entry.destroy())
        
        entry.bind("<FocusOut>", on_focus_out)

    def _get_details(self): 
        selected = self.tree.focus()
        if not selected: return

        tipo, item_id = self._parse_iid(selected)
        if not tipo or not item_id: return
        
        api_calls = {
                self.TYPE_NOTE: self.api.get_note_analytics,
                self.TYPE_THEME: self.api.get_theme_analytics
            }

        call = api_calls.get(tipo)
        if call:
            dto_analytics = self._call_api(call, int(item_id))
            if dto_analytics:
                Bus.emit("OPEN_DETAILS_ITEM", dto_analytics = dto_analytics)

    def _ui_delete_item(self):
        raw_selected = self.tree.selection()
        if not raw_selected:
            return

        # Filtred raw_selected to remove redundant selections
        selected_items: list[str] = []
        for iid in raw_selected:
            is_redundant = False
            parent = self.tree.parent(iid)
            while parent:
                if parent in raw_selected:
                    is_redundant = True
                    break
                parent = self.tree.parent(parent)
            
            if not is_redundant:
                selected_items.append(iid)

        note_ids_to_delete: list[int] = []
        theme_ids_to_delete: list[int] = []
        image_ids_to_delete: list[int] = []

        for iid in selected_items:
            item_type, item_id = self._parse_iid(iid)
            if item_type is None or item_id is None: continue
            elif item_type == self.TYPE_NOTE:
                note_ids_to_delete.append(item_id)
            elif item_type == self.TYPE_THEME:
                theme_ids_to_delete.append(item_id)
            elif item_type == self.TYPE_IMAGE:
                image_ids_to_delete.append(item_id)
        
        total_items = len(selected_items)

        # --- Dinamic about the message ---
        if total_items == 1:
            iid = selected_items[0]
            name = self.tree.item(iid, 'text')
            item_type, _ = self._parse_iid(iid)
            
            if item_type == self.TYPE_NOTE:
                msg = f"¿Deseas eliminar la nota '{name}'?"
            elif item_type == self.TYPE_IMAGE:
                msg = f"¿Deseas eliminar la imagen '{name}'?"
            else:
                msg = f"¿Deseas eliminar el tema '{name}' y todo su contenido?"
        else:
            msg = f"¿Deseas eliminar los {total_items} elementos seleccionados?\n\n"
            
            if note_ids_to_delete:
                msg += f"NOTAS ({len(note_ids_to_delete)}):\n"
                for nid in note_ids_to_delete[:5]:
                    name = self.tree.item(f"{self.TYPE_NOTE}_{nid}", "text")
                    msg += f" • {name}\n"
                if len(note_ids_to_delete) > 5: msg += " ... y más.\n"
                msg += "\n"

            if theme_ids_to_delete:
                msg += f"TEMAS Y SU CONTENIDO ({len(theme_ids_to_delete)}):\n"
                for tid in theme_ids_to_delete[:5]:
                    name = self.tree.item(f"{self.TYPE_THEME}_{tid}", "text")
                    msg += f" • {name}\n"
                if len(theme_ids_to_delete) > 5: msg += " ... y más.\n"

            if image_ids_to_delete:
                msg += f"\nIMÁGENES ({len(image_ids_to_delete)}):\n"
                for iid in image_ids_to_delete[:5]:
                    name = self.tree.item(f"{self.TYPE_IMAGE}_{iid}", "text")
                    msg += f" • {name}\n"
                if len(image_ids_to_delete) > 5: msg += " ... y más.\n"

        if not messagebox.askyesno("Confirmar", msg):
            return
        
        if note_ids_to_delete:
            res_delete_n = self.api.delete_many_notes(note_ids_to_delete)
            if not res_delete_n.successful:
                messagebox.showerror("Error", res_delete_n.info or "Error desconocido")
            else:
                Bus.emit("CLOSE_TAB_NOTES", list_note_ids=note_ids_to_delete)

        if theme_ids_to_delete:
            notes_tab_to_delete: list[int] = []
            images_tab_to_delete: list[int] = []

            for theme_id in theme_ids_to_delete:
                res_get_n = self.api.get_note_ids_by_theme_hierarchy(theme_id)
                if res_get_n.successful and res_get_n.obj:
                    notes_tab_to_delete.extend(res_get_n.obj)

                res_get_i = self.api.get_image_ids_by_theme_hierarchy(theme_id)
                if res_get_i.successful and res_get_i.obj:
                    images_tab_to_delete.extend(res_get_i.obj)
            
            res_delete_t = self.api.delete_many_themes(theme_ids_to_delete)
            
            if not res_delete_t.successful:
                messagebox.showerror("Error", res_delete_t.info or "Error desconocido")
            else:
                Bus.emit("CLOSE_TAB_NOTES", list_note_ids=notes_tab_to_delete)
                Bus.emit("CLOSE_TAB_IMAGES", list_image_ids=images_tab_to_delete)
            

        if image_ids_to_delete:
            res = self.api.delete_many_images(image_ids_to_delete)
            if not res.successful:
                messagebox.showerror("Error", res.info or "Error desconocido")
            else:
                Bus.emit("CLOSE_TAB_IMAGES", list_image_ids=image_ids_to_delete)

        for iid in selected_items:
            parent_iid = self.tree.parent(iid)
            self.tree.delete(iid)
                
            if parent_iid:
                self._manage_dummy(parent_iid, "add")
        
# --- DRAG & DROP LOGIC ---
    def _on_drag_motion(self, event):
        """Visual effect while dragging."""
        if not self.dragging_item:
            return
        self.tree.tag_configure(
        "celeste_claro",
        background="#5c9fe6",
        foreground="black"
        )
        self.tree.item(self.dragging_item, tags=("celeste_claro",))
        target_iid = self.tree.identify_row(event.y)
        
        # Clean previous highlights 
        self.tree.selection_set(target_iid) 
        
        if target_iid == self.dragging_item:
            self.tree.config(cursor="")
        else:
            self.tree.config(cursor="hand2")

    def _on_drag_start(self, event):
        """Detects what item is being started to drag."""
        iid = self.tree.identify_row(event.y)
        if iid and not iid.startswith(self.TYPE_DUMMY):
            self.dragging_item = iid
            self.tree.config(cursor="hand2")

    def _on_drag_finish(self, event):
        """Detects where it was dropped and executes the parent change."""
        if not self.dragging_item:
            return
        self.tree.config(cursor="") 
        
        # Identify target
        target_iid = self.tree.identify_row(event.y)

        # Identify source
        source_iid = self.dragging_item

        # Clean dragging state and visual effects
        self.dragging_item = None 
        self.tree.item(source_iid, tags=())

        if source_iid == target_iid:
            return

        dest_parent_iid = ""
        if target_iid:
            t_type, _ = self._parse_iid(target_iid)
            if t_type == self.TYPE_THEME:
                dest_parent_iid = target_iid
            elif t_type == self.TYPE_NOTE:
                dest_parent_iid = self.tree.parent(target_iid)
            elif t_type == self.TYPE_IMAGE:
                dest_parent_iid = self.tree.parent(target_iid)
        
        # Prevents moving to the same parent
        parent_source_iid = self.tree.parent(source_iid)
        if dest_parent_iid == parent_source_iid:
            return

        source_type, source_id = self._parse_iid(source_iid)
        _, new_parent_id = self._parse_iid(dest_parent_iid)
        if source_type is None or source_id is None:
            return

        """
        The target node must be loaded to avoid losing its children in the change.
        """
        if dest_parent_iid != "":
            self.tree.focus(dest_parent_iid)
            self.tree.event_generate("<<TreeviewOpen>>")
            self.tree.focus_set()

        # Call API to perform the move 
        if source_type == self.TYPE_THEME:
            res = self.api.remove_theme(source_id, new_parent_id)
            if not res.successful:
                messagebox.showwarning("Movimiento no permitido", res.info or "No se pudo mover el elemento.")
                return

        elif source_type == self.TYPE_NOTE:
            res = self.api.move_note_to_theme(source_id, new_parent_id)
            if not res.successful:
                messagebox.showwarning("Movimiento no permitido", res.info or "No se pudo mover el elemento.")
                return
        
        elif source_type == self.TYPE_IMAGE:
            res = self.api.move_image_to_theme(source_id, new_parent_id)
            if not res.successful:
                messagebox.showwarning("Movimiento no permitido", res.info or "No se pudo mover el elemento.")
                return
            

        # Update the UI
        old_parent = self.tree.parent(source_iid)

        # If the destiny is not load and is not root.
        if dest_parent_iid not in self.loaded_nodes and dest_parent_iid != "":
            self.tree.delete(source_iid)
            if old_parent:
                self._manage_dummy(old_parent, "add")

        # If the destiny is not load and is root
        if dest_parent_iid not in self.loaded_nodes and dest_parent_iid == "":
            self.tree.move(source_iid, dest_parent_iid, "end")
            if old_parent:
                self._manage_dummy(old_parent, "add")
        
        # If the destiny is load
        if dest_parent_iid in self.loaded_nodes:
            self.tree.move(source_iid, dest_parent_iid, "end")
            if old_parent:
                self._manage_dummy(old_parent, "add")
  
            self._manage_dummy(dest_parent_iid, "remove")
 
    def _ui_export_image(self):
        selected = self.tree.focus()
        if not selected: 
            return

        item_type, image_id = self._parse_iid(selected)
        if item_type != self.TYPE_IMAGE:
            return
        if image_id is None:
            return

        res = self.api.get_image_details(image_id)
        if not res.successful or not res.obj:
            messagebox.showerror("Error", res.info or "No se pudo recuperar la imagen")
            return

        image_dto = res.obj 
        
        res = self.api.get_image_extension(image_id)
        if not res.successful or res.obj is None:
            messagebox.showerror("Error", res.info or "No se pudo obtener el formato de la imagen.")
            return
        extension = "." + res.obj
        file_path = filedialog.asksaveasfilename(
            title="Exportar imagen",
            initialfile=image_dto.name,
            defaultextension=extension,
            filetypes=[("Imagen", f"*{extension}"), ("Todos los archivos", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(image_dto.file_path, "rb") as f:
                blob_data = f.read()
            with open(file_path, "wb") as f:
                f.write(blob_data)

            messagebox.showinfo("Éxito", f"Imagen exportada correctamente en:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error de escritura", f"No se pudo guardar el archivo: {str(e)}")