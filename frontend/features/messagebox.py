import tkinter as tk

def custom_messagebox(title: str, message: str, options: list[str]) -> str | None:
    """
    Muestra un cuadro de diálogo modal con botones personalizados.
    Retorna el texto del botón presionado.
    """
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("360x150")
    dialog.resizable(False, False)
    dialog.grab_set()  # MODAL

    # Centrado dentro de la ventana principal
    dialog.update_idletasks()
    x = dialog.winfo_screenwidth() // 2 - 180
    y = dialog.winfo_screenheight() // 2 - 75
    dialog.geometry(f"+{x}+{y}")

    tk.Label(dialog, text=message, wraplength=320, justify="center").pack(pady=15)

    result = {"value": None}

    def choose(value):
        result["value"] = value
        dialog.destroy()

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=10)

    for opt in options:
        tk.Button(btn_frame, text=opt, command=lambda o=opt: choose(o)).pack(
            side="left", padx=5
        )

    dialog.wait_window()
    return result["value"]
