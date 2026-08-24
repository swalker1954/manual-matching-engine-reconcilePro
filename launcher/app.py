"""Manual Matching Process launcher.

Finds the source Excel file for a given Engine + Date Period and opens it in
Excel (via the file's default application). Excel remains the source of
truth for the actual matching work; this tool only locates and launches it.
"""

from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from path_resolver import (
    ENGINES,
    InvalidPeriodError,
    recent_periods,
    resolve_source_path,
)

APP_TITLE = "Manual Matching Process"


def open_file(path) -> None:
    """Open a file with its default application (Excel, for .xlsx)."""
    path = str(path)
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        os.system(f'open "{path}"')
    else:
        os.system(f'xdg-open "{path}"')


class LauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.resizable(False, False)

        padding = {"padx": 10, "pady": 6}

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="What engine are you using:").grid(row=0, column=0, sticky="w", **padding)
        self.engine_var = tk.StringVar()
        self.engine_combo = ttk.Combobox(
            frame, textvariable=self.engine_var, values=ENGINES, state="readonly", width=30
        )
        self.engine_combo.grid(row=0, column=1, **padding)

        ttk.Label(frame, text="What date period:").grid(row=1, column=0, sticky="w", **padding)
        self.period_var = tk.StringVar()
        self.period_combo = ttk.Combobox(
            frame, textvariable=self.period_var, values=recent_periods(), width=30
        )
        self.period_combo.grid(row=1, column=1, **padding)
        self.period_combo.set(recent_periods()[2])  # defaults to the current month

        self.find_button = ttk.Button(frame, text="Find & Open", command=self.on_find_and_open)
        self.find_button.grid(row=2, column=0, columnspan=2, pady=(10, 4))

        self.status_var = tk.StringVar(value="Select an engine and date period, then Find & Open.")
        self.status_label = ttk.Label(
            frame, textvariable=self.status_var, foreground="gray20", wraplength=380, justify="left"
        )
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="w", **padding)

    def on_find_and_open(self) -> None:
        engine = self.engine_var.get()
        period = self.period_var.get()

        if not engine:
            messagebox.showwarning(APP_TITLE, "Please select an engine.")
            return

        try:
            path = resolve_source_path(engine, period)
        except InvalidPeriodError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return

        if not path.exists():
            self.status_var.set(f"Not found:\n{path}")
            messagebox.showerror(APP_TITLE, f"Could not find the source file:\n\n{path}")
            return

        self.status_var.set(f"Opening:\n{path}")
        try:
            open_file(path)
        except OSError as exc:
            messagebox.showerror(APP_TITLE, f"Found the file but could not open it:\n\n{path}\n\n{exc}")


def main() -> None:
    app = LauncherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
