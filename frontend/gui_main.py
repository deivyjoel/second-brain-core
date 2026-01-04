import tkinter as tk
from tkinter import ttk
from frontend.features.explorer_feature import ExplorerFeature
from frontend.tab_manager import TabManager
from frontend.analytics_manager import AnalyticsManager
"""
from frontend.explorer.explorer_controller import ExplorerController
from frontend.explorer.explorer_view import Explorer
"""
def setup_style():
    style = ttk.Style()
    # Usamos 'default' para un aspecto limpio o 'alt'
    style.theme_use("default")


class Gui():
    def __init__(self):
        self.root = tk.Tk()

        setup_style()
        self.root.geometry("1000x600")

        # PanedWindow horizontal
        pw = tk.PanedWindow(self.root, orient="horizontal")
        pw.pack(fill="both", expand=True)

        # Frame IZQUIERDO
        frame_left = tk.Frame(pw, width=250, bg="#252526")
        pw.add(frame_left, minsize=200)

        # Frame DERECHO 
        frame_right = tk.Frame(pw, width=600, bg="#252526")
        pw.add(frame_right, minsize=200)

        
        # Explorer:
        explorer = ExplorerFeature(frame_left)
        explorer.pack(expand=True, fill="both")

        # TabManager:
        notebook = ttk.Notebook(frame_right)
        notebook.pack(fill="both", expand=True)
        tab_manager = TabManager(notebook)
        analytics_manager = AnalyticsManager()

    def run(self):
        self.root.mainloop()
