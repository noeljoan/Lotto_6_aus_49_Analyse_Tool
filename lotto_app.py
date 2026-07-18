"""
Lotto 6 aus 49 - Analyse GUI - © 2026 - N. Joan
Hauptdatei - startet die Anwendung
"""
import tkinter as tk
from tkinter import ttk
from tab_grilles import GrillesTab
from tab_ziehungen import ZiehungenTab
from tab_auswertung import AuswertungTab
from tab_statistik import StatistikTab

class LottoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lotto 6 aus 49 - Analyse Tool - © 2026 - N. Joan")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg="#1F4E79")

        # Gemeinsame Datenspeicher
        self.grilles = []       # Liste von Listen mit 6 Zahlen
        self.ziehungen = []     # Liste von {"datum": str, "zahlen": [int,...]}

        self._build_ui()

    def _build_ui(self):
        # Titelzeile
        header = tk.Frame(self, bg="#1F4E79", pady=10)
        header.pack(fill="x")
        tk.Label(
            header, text="LOTTO 6 aus 49 - Analyse Tool",
            font=("Segoe UI", 18, "bold"), fg="white", bg="#1F4E79"
        ).pack()
        tk.Label(
            header, text="Importiere deine Tipps und Ziehungen – unbegrenzt",
            font=("Segoe UI", 10), fg="#BDD7EE", bg="#1F4E79"
        ).pack()

        # Notebook (Tabs)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#1F4E79", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"),
                         padding=[14, 6], background="#2E75B6", foreground="white")
        style.map("TNotebook.Tab",
                  background=[("selected", "#FFFFFF")],
                  foreground=[("selected", "#1F4E79")])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tab_grilles    = GrillesTab(self.notebook, self)
        self.tab_ziehungen  = ZiehungenTab(self.notebook, self)
        self.tab_auswertung = AuswertungTab(self.notebook, self)
        self.tab_statistik  = StatistikTab(self.notebook, self)

        self.notebook.add(self.tab_grilles,    text="  1 - Meine Tipps  ")
        self.notebook.add(self.tab_ziehungen,  text="  2 - Ziehungen  ")
        self.notebook.add(self.tab_auswertung, text="  3 - Auswertung  ")
        self.notebook.add(self.tab_statistik,  text="  4 - Statistiken  ")

    def notify_data_changed(self):
        """Wird aufgerufen wenn Tipps oder Ziehungen aktualisiert werden."""
        self.tab_auswertung.refresh()
        self.tab_statistik.refresh()


if __name__ == "__main__":
    app = LottoApp()
    app.mainloop()