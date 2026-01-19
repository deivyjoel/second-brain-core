import tkinter as tk
from tkinter import ttk, messagebox
import time
from frontend.core.api_provider import ApiProvider
from frontend.core.bus import Bus

import time

class TimerLogic:
    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.perf_counter() - self.elapsed_time

    def stop(self):
        if self.running:
            self.running = False
            self.elapsed_time = time.perf_counter() - self.start_time

    def restart(self):
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0

    def get_elapsed(self):
        return time.perf_counter() - self.start_time if self.running else self.elapsed_time

    def get_time_record_minutes(self):
        self.stop()
        return self.elapsed_time / 60 if self.elapsed_time > 0 else 0


class ChronometerFeature(ttk.Frame):
    def __init__(self, parent, note_id: int):
        super().__init__(parent)
        self.api = ApiProvider.get()
        self.note_id = note_id
        self.timer = TimerLogic()

        self._create_widgets()

    def _create_widgets(self):
        self.label = ttk.Label(self, text="00:00:00", font=("Consolas", 12, "bold"))
        self.label.pack(side="left", padx=5)

        self.btn_toggle = tk.Button(self, text="▷", width=3, command=self.toggle)
        self.btn_toggle.pack(side="left", padx=2)

        self.btn_restart = tk.Button(self, text="↺", width=3, command=self.reiniciar)
        self.btn_restart.pack(side="left", padx=2)

        self.btn_save = tk.Button(self, text="💾", width=3, command=self.guardar)
        self.btn_save.pack(side="left", padx=2)


    def toggle(self):
        if not self.timer.running:
            self.timer.start()
            self.actualizar_ui()
            self.btn_toggle.config(text="||")
        else:
            self.timer.stop()
            self.btn_toggle.config(text="▷")

    def actualizar_ui(self):
        if self.timer.running:
            elapsed = self.timer.get_elapsed()
            mins, secs = divmod(int(elapsed), 60)
            milis = int((elapsed * 100) % 100)
            self.label.config(text=f"{mins:02}:{secs:02}:{milis:02}")
            self.after(50, self.actualizar_ui)

    def reiniciar(self):
        self.timer.restart()
        self.label.config(text="00:00:00")
        self.btn_toggle.config(text="▷")

    def guardar(self):
        minutes = self.timer.get_time_record_minutes()
        
        if minutes > 0:
            res = self.api.register_time_to_note(self.note_id, minutes)
            
            if res.successful:
                self.reiniciar()
                messagebox.showinfo("Éxito", res.info)
            else:
                messagebox.showerror("Error cronómetro", res.info)
        else:
            pass
    