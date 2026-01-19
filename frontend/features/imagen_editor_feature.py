import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

from frontend.core.api_provider import ApiProvider
from frontend.core.bus import Bus
from datetime import datetime, timezone

class ImageEditorFeature(ttk.Frame):
    def __init__(self, 
                 parent, 
                 image_id,
                 image_data
                 ):
        super().__init__(parent)

        self.api = ApiProvider.get()
        self.image_id = image_id
        self.image_data = image_data
        self.pil_original = None
        self._resize_job = None
        self.zoom_factor = 1.0

        self._setup_ui()
        self.load_image()
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _setup_ui(self):
        content = ttk.Frame(self)
        content.pack(expand=True, fill="both")
        

        self.top = ttk.Frame(content, height=30)
        self.top.pack(fill="x", padx=8, pady=(8, 0))
        self.top.propagate(False)

        # --- ZOOM (Slider) ---
        ttk.Label(self.top, text="Zoom:").pack(side="left", pady= 3, padx=(10, 2))
        self.zoom_slider = ttk.Scale(
            self.top, 
            from_=1, 
            to=5, 
            orient="horizontal"
        )
        self.zoom_slider.set(1)
        self.zoom_slider.pack(side="left", padx=5, fill="x")
        self.zoom_slider.bind("<ButtonRelease-1>", self._on_slider_release)

        tk.Button(self.top, text="✖", command=self._ui_close_tab).pack(side="right", padx=(3, 0))

        # Area work (Donde irá el canvas y los scrollbars)
        self.area_work = ttk.Frame(content)
        self.area_work.pack(fill="both", expand=True, padx=8, pady=8)

        self.canvas_cont = ttk.Frame(self.area_work)
        self.canvas_cont.pack(fill="both", expand=True)

        # Scrollbars
        self.scroll_y = ttk.Scrollbar(self.canvas_cont, orient="vertical")
        self.scroll_y.pack(side="right", fill="y")

        self.scroll_x = ttk.Scrollbar(self.canvas_cont, orient="horizontal")
        self.scroll_x.pack(side="bottom", fill="x")

        # Canvas (SIEMPRE al final)
        self.canvas = tk.Canvas(self.canvas_cont, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Vinculación
        self.canvas.configure(
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set
        )
        self.scroll_y.config(command=self.canvas.yview)
        self.scroll_x.config(command=self.canvas.xview)

    def _fmt(self, dt: datetime):
        if dt is None:
            return ""
        utc_dt = dt.replace(tzinfo=timezone.utc)
        local_dt = utc_dt.astimezone()
        
        return local_dt.strftime("%d %b %Y, %H:%M")
    
    def load_image(self):
        ttk.Label(self.top, text=self._fmt(self.image_data.created_at)).pack(side="left", padx=(2, 10))
        format = self.api.get_image_extension(self.image_id)
        if not format.successful:
            messagebox.showerror("Error", format.info or "No se pudo obtener el formato de la imagen.")
            return
        ttk.Label(self.top, text=f"Formato: {format.obj}").pack(side="left", padx=(2, 10))
        file_path = self.image_data.file_path
        self.pil_original = Image.open(file_path)

    def _on_slider_release(self, event):
        """Este método SOLO se ejecuta cuando el usuario suelta el click"""
        # Obtenemos el valor actual donde quedó la perilla
        valor = self.zoom_slider.get()
            
        self.view_mode = "zoom"
        self.zoom_factor = float(valor)
        self._render_view()

    def _render_view(self):
        self._resize_job = None
        if not self.pil_original: return
        self.canvas.update_idletasks()
                
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w < 10: canvas_w, canvas_h = 800, 600 

        img_w, img_h = self.pil_original.size
            
        ratio_fit = min(canvas_w/img_w, canvas_h/img_h)
            
        value_slider = self.zoom_slider.get()
            
        zoom_final = ratio_fit * value_slider
            
        new_size = (int(img_w * zoom_final), int(img_h * zoom_final))
            

        pil_resized = self.pil_original.resize(new_size, Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(pil_resized)
        self.canvas.delete("all")

        self.canvas.create_image(canvas_w//2, canvas_h//2, anchor="center", image=self.tk_img)
        if value_slider <= 1.01:
            self.canvas.config(scrollregion=(0, 0, canvas_w, canvas_h))
        else:
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        if self._resize_job:
            self.after_cancel(self._resize_job)
            
        self._resize_job = self.after(200, self._render_view)

    def _ui_close_tab(self):
        Bus.emit("CLOSE_TAB_IMAGE", image_id=self.image_id)
    
