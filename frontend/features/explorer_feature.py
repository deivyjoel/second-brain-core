import tkinter as tk
from tkinter import ttk, messagebox
from frontend.core.api_provider import ApiProvider
from frontend.core.bus import Bus

class ExplorerFeature(ttk.Frame):
    # Constantes para evitar "magic strings"
    TYPE_THEME = "theme"
    TYPE_NOTE = "note"
    TYPE_DUMMY = "dummy"
    
    ICON_THEME = "📁"
    ICON_NOTE = "📄"
    DUMMY_TEXT = "No hay contenido wey"

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

        self.tree = ttk.Treeview(self, show="tree", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.column("#0", width=250, minwidth=150)

        # Menú Contextual para temas
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="📈 Analiticas", command=self._get_details)
        self.menu.add_separator()
        self.menu.add_command(label=f"{self.ICON_NOTE} Nueva Nota", command=self._ui_new_note)
        self.menu.add_command(label=f"{self.ICON_THEME} Nuevo Tema", command=self._ui_new_theme)
        self.menu.add_separator()
        self.menu.add_command(label="✏️ Renombrar", command=self._ui_start_rename)
        self.menu.add_command(label="🗑️ Eliminar", command=self._ui_delete_item)
        self.menu.add_command(label="🗺️ Mapa de estudio", command=self._generate_study_map)

        # Menú contextual para notas
        self.menu2 = tk.Menu(self, tearoff=0)
        self.menu2.add_command(label="📈 Analiticas", command=self._get_details)
        self.menu2.add_separator()
        self.menu2.add_command(label="✏️ Renombrar", command=self._ui_start_rename)
        self.menu2.add_command(label="🗑️ Eliminar", command=self._ui_delete_item)

        # Menú para cuando se selecciona a la 'nada'
        self.menu3 = tk.Menu(self, tearoff=0)
        self.menu3.add_command(label=f"{self.ICON_NOTE} Nueva Nota", command=self._ui_new_note)
        self.menu3.add_command(label=f"{self.ICON_THEME} Nuevo Tema", command=self._ui_new_theme)
        self.menu3.add_command(label="🗺️ Mapa de estudio", command=self._generate_study_map)

    def _setup_events(self):
        self.tree.bind("<<TreeviewOpen>>", self._on_treeview_expand)
        self.tree.bind("<Button-1>", self._on_left_click)
        self.tree.bind("<Button-3>", self._on_right_click)
        
    # --- HELPERS (Mejora de legibilidad) ---

    def _parse_iid(self, iid: str):
        """Retorna (tipo, id) a partir de un iid 'tipo_id'."""
        if not iid or "_" not in iid:
            return None, None
        parts = iid.split("_")
        return parts[0], int(parts[1])

    def _call_api(self, api_func, *args, **kwargs):
        """Wrapper para manejar errores de API de forma centralizada."""
        res = api_func(*args, **kwargs)
        if not res.successful:
            messagebox.showerror("Error", res.info or "Error desconocido")
            return None
        return res.obj

    def _manage_dummy(self, parent_iid, action="remove"):
        """Gestiona la existencia del nodo dummy."""
        _, p_id = self._parse_iid(parent_iid)
        dummy_id = f"{self.TYPE_DUMMY}_{p_id}"
        
        if action == "remove" and self.tree.exists(dummy_id):
            self.tree.delete(dummy_id)
        elif action == "add" and not self.tree.get_children(parent_iid):
            self.tree.insert(parent_iid, "end", iid=dummy_id, text=self.DUMMY_TEXT)

    # --- LÓGICA DE CARGA ---
    def load_root(self, **kwargs):
        self.tree.delete(*self.tree.get_children())
        self.loaded_nodes.clear()
        
        themes = self._call_api(self.api.list_root_themes)
        notes = self._call_api(self.api.get_notes_without_themes)

        if themes is not None:
            for t in themes: 
                self.insert_theme("", t.id, t.name) 
        if notes is not None:
            for n in notes: 
                self.insert_note("", n.id, n.name)

    def _on_treeview_expand(self, event):
        iid = self.tree.focus()
        if iid.startswith(self.TYPE_THEME) and iid not in self.loaded_nodes:
            self._load_children(iid)

    def _load_children(self, parent_iid: str):
        if parent_iid in self.loaded_nodes: return
        
        _, p_id = self._parse_iid(parent_iid)
        res_themes = self._call_api(self.api.list_child_themes, p_id)
        res_notes = self._call_api(self.api.list_notes_by_theme, p_id)
        print(res_themes)
        print(res_notes)

        if res_themes is not None and res_notes is not None:
            if len(res_themes + res_notes) > 0:
                self._manage_dummy(parent_iid, "remove")
            
            for t in res_themes: 
                self.insert_theme(parent_iid, t.id, t.name)
            for n in res_notes: 
                self.insert_note(parent_iid, n.id, n.name)
            
            self.loaded_nodes.add(parent_iid)

    def insert_note(self, parent_iid, note_id, note_name):
        iid = f"{self.TYPE_NOTE}_{note_id}"
        print(iid)
        self.tree.insert(parent_iid, "end", iid, text=f"{self.ICON_NOTE} {note_name}")
    
    def insert_theme(self, parent_iid, theme_id, theme_name):
        iid = f"{self.TYPE_THEME}_{theme_id}"
        print(iid)
        self.tree.insert(parent_iid, "end", iid, text=f"{self.ICON_THEME} {theme_name}")
        self._manage_dummy(iid, "add")

    # --- OPERACIONES DE UI ---
    def _ui_new_note(self):
        selected = self.tree.focus()
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
        self.tree.event_generate("<<TreeviewOpen>>")
        self.tree.item(selected, open=True)
        _, parent_id = self._parse_iid(selected)

        name = self._call_api(self.api.get_unique_theme_name, "Nuevo tema", parent_id)
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

    def _ui_delete_item(self):
        iid = self.tree.focus()
        item_type, item_id = iid.split("_")
        
        if item_type == self.TYPE_NOTE:
            msg="¿Deseas eliminar la nota?"
        elif item_type == self.TYPE_THEME:
            msg="¿Deseas eliminar el tema?\n(Esto eliminará también todo su contenido)"
        else:
            msg = ""
        if messagebox.askyesno("Confirmar", msg):

            api_func = self.api.delete_note if item_type == self.TYPE_NOTE else self.api.delete_theme

            res2 = False
            if item_type == self.TYPE_THEME:
                res2 = self._call_api(self.api.get_notes_descendants, int(item_id))

            res = api_func(int(item_id))
            if not res.successful:
                messagebox.showerror("Error", res.info)

            if item_type == self.TYPE_NOTE:
                Bus.emit("DELETE_NOTE", note_id=int(item_id))
            if item_type == self.TYPE_THEME:
                if res2:
                    Bus.emit("DELETE_NOTES", list_note_ids = res2)

            parent_iid = self.tree.parent(iid)
            self.tree.delete(iid)
                
            if parent_iid:
                self._manage_dummy(parent_iid, "add")
                
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
        clean_text = current_full_text.replace(self.ICON_THEME, "").replace(self.ICON_NOTE, "").strip()
        
        entry.insert(0, clean_text)
        entry.select_range(0, tk.END) # Selecciona todo para facilitar el cambio
        entry.focus_set()

        self.flag = False

        def save_rename(event=None):
            if self.flag: return
            new_name = entry.get().strip()
            item_type, item_id = self._parse_iid(iid)
            if item_id is None:
                return
            
            # Si el nombre es vacío o no cambió, simplemente cerramos el entry
            if not new_name or new_name == clean_text:
                entry.destroy()
                return

            # Elegir función de API
            self.flag = True
            api_func = self.api.rename_note if item_type == self.TYPE_NOTE else self.api.rename_theme
            
            # Ejecución directa evaluando OperationResult
            res = api_func(item_id, new_name)
            
            if res.successful:
                # Actualizar la interfaz de Tkinter
                icon = self.ICON_THEME if item_type == self.TYPE_THEME else self.ICON_NOTE
                full_text = f"{icon} {new_name}"
                self.tree.item(iid, text=full_text)
                
                # Notificar al resto del sistema si es una nota
                if item_type == self.TYPE_NOTE:
                    Bus.emit("CHANGE_NOTE_NAME", note_id=item_id, new_name=new_name)
                
                entry.destroy()
            else:
                # Si falló la DB, mostramos el error y NO destruimos el entry 
                # para que el usuario pueda corregir el nombre
                messagebox.showerror("Error al renombrar", res.info or "Error desconocido")
                self.flag = False
                entry.focus_set()

        def on_focus_out(event):
            print("alo?2|")
            if not self.flag:
                entry.destroy()

        # 3. Bindings
        entry.bind("<Return>", save_rename)
        entry.bind("<Escape>", lambda e: entry.destroy())
        
        # El FocusOut destruye el entry si el usuario hace clic en otro lado
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
                print("alo?")


    # --- EVENTOS DE MOUSE ---
    def _on_left_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid and iid.startswith(self.TYPE_NOTE):
            _, note_id = self._parse_iid(iid)
            Bus.emit("OPEN_NOTE", note_id=note_id)
        elif not iid:
            self.tree.selection_set(())
            self.tree.focus("")

    def _on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        tipo, _ = self._parse_iid(iid)

        if iid:
            self.tree.selection_set(iid)
            self.tree.focus(iid)

        else:
            self.tree.selection_set(())
            self.tree.focus("")


        if tipo == self.TYPE_THEME:
            self.menu.post(event.x_root, event.y_root)
        elif tipo == self.TYPE_NOTE:
            self.menu2.post(event.x_root, event.y_root)
        elif tipo is None:
            self.menu3.post(event.x_root, event.y_root)
    
    def _generate_study_map(self):...



