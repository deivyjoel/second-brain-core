import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone

class AnalyticsWindow(tk.Toplevel): 
    def __init__(self, dto):
        super().__init__()
        self.title(f"Analíticas: {dto.name}")
        self.geometry("400x450")
        
        self.frame = AnalyticsFrame(self, dto) 
        self.frame._build_ui()
        self.frame.pack(fill="both", expand=True)


class AnalyticsFrame(tk.Frame):
    def __init__(self, master, dto, **kwargs):
        super().__init__(master, **kwargs)
        self.dto = dto
        self._build_ui

    def _build_ui(self):
        self.configure(padx=14, pady=14)

        self._header()
        ttk.Separator(self).pack(fill="x", pady=8)
        self._metrics()

    def _header(self):
        tk.Label(
            self,
            text=self.dto.name,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w")

        tk.Label(
            self,
            text=self._dates_text(),
            font=("Segoe UI", 9),
            fg="#666"
        ).pack(anchor="w")

    def _metrics(self):
        container = tk.Frame(self)
        container.pack(fill="x", pady=8)

        metrics = self._collect_metrics()

        for i, (label, value) in enumerate(metrics):
            self._metric_card(container, label, value)\
                .grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

    def _metric_card(self, parent, label, value):
        card = tk.Frame(parent, relief="groove", bd=1, padx=10, pady=8)

        tk.Label(card, text=label, font=("Segoe UI", 9), fg="#555").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        return card

    def _dates_text(self):
        created = self._fmt(self.dto.created_at)
        edited = self._fmt(self.dto.last_edited_at)

        return f"Creado: {created} · Última Edición: {edited}"

    def _collect_metrics(self):
        d = self.dto
        data = [
            ("Minutos totales", f"{d.minutes_total:.1f}"),
            ("Días activos", d.n_days_active),
        ]


        if (hasattr(d, 'n_entities')):
            data += [
                ("Notas directas", d.n_notes_directly),
                ("Entidades", d.n_entities),
                ("Palabras", d.n_content_words_total),
                ("Palabras únicas", d.n_u_content_words_totals),
            ]
        else:
            data += [
                ("Sesiones", d.n_sessions),
                ("Palabras", d.n_words_total),
                ("Palabras únicas", d.n_u_content_words_totals),
                ("Diversidad léxica", f"{d.lexical_diversity_rate:.2%}"),
            ]

        return data

    def _fmt(self, dt: datetime):
        if dt is None:
            return ""
        utc_dt = dt.replace(tzinfo=timezone.utc)
        local_dt = utc_dt.astimezone()
        
        return local_dt.strftime("%d %b %Y, %H:%M")
