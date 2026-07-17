"""
Tab 1: Grilles verwalten (manuell eingeben oder CSV importieren)
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv


class GrillesTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#F5F5F5")
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # --- Linke Seite: Eingabe ---
        left = tk.LabelFrame(self, text=" Grille manuell hinzufügen ",
                             font=("Segoe UI", 10, "bold"),
                             bg="#F5F5F5", fg="#1F4E79", padx=10, pady=10)
        left.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(left, text="6 Zahlen eingeben (1–49), mit Komma getrennt:",
                 bg="#F5F5F5", font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 2))

        self.entry_grille = tk.Entry(left, font=("Segoe UI", 12), width=25,
                                     relief="solid", bd=1)
        self.entry_grille.pack(pady=4)
        self.entry_grille.bind("<Return>", lambda e: self._add_grille())

        tk.Label(left, text="Beispiel: 5, 12, 23, 34, 41, 49",
                 bg="#F5F5F5", fg="gray", font=("Segoe UI", 8)).pack()

        tk.Button(left, text="Grille hinzufügen", command=self._add_grille,
                  bg="#2E75B6", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", padx=10, pady=5).pack(pady=8, fill="x")

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        tk.Label(left, text="CSV-Import (eine Grille pro Zeile):",
                 bg="#F5F5F5", font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(left, text="Format: 5,12,23,34,41,49",
                 bg="#F5F5F5", fg="gray", font=("Segoe UI", 8)).pack(anchor="w")
        tk.Label(left, text="         5;12;23;34;41;49",
                 bg="#F5F5F5", fg="gray", font=("Segoe UI", 8)).pack(anchor="w")
        tk.Label(left, text="         5-12-23-34-41-49",
                 bg="#F5F5F5", fg="gray", font=("Segoe UI", 8)).pack(anchor="w")

        tk.Button(left, text="CSV importieren", command=self._import_csv,
                  bg="#1F4E79", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", padx=10, pady=5).pack(pady=6, fill="x")

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        tk.Button(left, text="Alle Grilles loeschen", command=self._clear_all,
                  bg="#C00000", fg="white", font=("Segoe UI", 9),
                  relief="flat", cursor="hand2", padx=10, pady=4).pack(fill="x")

        # Zähler
        self.lbl_count = tk.Label(left, text="Grilles: 0",
                                   bg="#F5F5F5", fg="#1F4E79",
                                   font=("Segoe UI", 11, "bold"))
        self.lbl_count.pack(pady=10)

        # --- Rechte Seite: Liste ---
        right = tk.Frame(self, bg="#F5F5F5")
        right.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        tk.Label(right, text="Alle Grilles", font=("Segoe UI", 11, "bold"),
                 bg="#F5F5F5", fg="#1F4E79").pack(anchor="w", pady=(0, 4))

        cols = ("#", "Nummern", "Aktion")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=25)
        self.tree.heading("#", text="#")
        self.tree.heading("Nummern", text="Nummern")
        self.tree.heading("Aktion", text="")
        self.tree.column("#", width=50, anchor="center")
        self.tree.column("Nummern", width=300, anchor="center")
        self.tree.column("Aktion", width=80, anchor="center")

        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        self.tree.bind("<Delete>", lambda e: self._delete_selected())
        tk.Button(right, text="Ausgewaehlte loeschen", command=self._delete_selected,
                  bg="#C00000", fg="white", font=("Segoe UI", 9),
                  relief="flat", cursor="hand2").pack(pady=6)

    def _parse_grille(self, text):
        """Erkennt automatisch Trennzeichen: Komma ',', Semikolon ';' oder Bindestrich '-'"""
        t = text.strip()
        # Semikolon hat Vorrang, dann Komma, dann Bindestrich
        if ";" in t:
            parts = [p.strip() for p in t.split(";") if p.strip()]
        elif "," in t:
            parts = [p.strip() for p in t.split(",") if p.strip()]
        elif "-" in t:
            parts = [p.strip() for p in t.split("-") if p.strip()]
        else:
            parts = [t]
        if len(parts) != 6:
            raise ValueError(
                f"Genau 6 Zahlen erforderlich (gefunden: {len(parts)}).\n"
                "Trennzeichen: Komma ',', Semikolon ';' oder Bindestrich '-'"
            )
        nums = [int(p) for p in parts]
        for n in nums:
            if not (1 <= n <= 49):
                raise ValueError(f"Zahl {n} ungültig (erlaubt: 1–49)")
        if len(set(nums)) != 6:
            raise ValueError("Keine doppelten Zahlen erlaubt")
        return sorted(nums)

    def _add_grille(self):
        text = self.entry_grille.get().strip()
        if not text:
            return
        try:
            grille = self._parse_grille(text)
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))
            return
        self.app.grilles.append(grille)
        self._refresh_tree()
        self.entry_grille.delete(0, "end")
        self.app.notify_data_changed()

    def _import_csv(self):
        path = filedialog.askopenfilename(
            title="CSV-Datei wählen",
            filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
        )
        if not path:
            return
        count = 0
        errors = 0
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                # Trennzeichen automatisch erkennen: ; oder ,
                sample = f.read(2048)
                f.seek(0)
                delimiter = ";" if sample.count(";") >= sample.count(",") else ","
                reader = csv.reader(f, delimiter=delimiter)
                for row in reader:
                    if not row:
                        continue
                    # Header-Zeile überspringen
                    if row[0].strip().lower() in ("grille", "#", "nr", "nummer"):
                        continue
                    try:
                        # Alle Spalten einer Zeile zusammenführen und parsen
                        raw = delimiter.join(row).strip()
                        nums = self._parse_grille(raw)
                        self.app.grilles.append(nums)
                        count += 1
                    except (ValueError, TypeError):
                        errors += 1
        except Exception as e:
            messagebox.showerror("Fehler", f"CSV konnte nicht gelesen werden:\n{e}")
            return
        self._refresh_tree()
        self.app.notify_data_changed()
        msg = f"{count} Grilles importiert."
        if errors:
            msg += f"\n{errors} Zeilen übersprungen (Fehler)."
        messagebox.showinfo("Import abgeschlossen", msg)

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, g in enumerate(self.app.grilles, 1):
            nums = " – ".join(f"{n:02d}" for n in g)
            self.tree.insert("", "end", iid=str(i-1), values=(i, nums, ""))
        self.lbl_count.config(text=f"Grilles: {len(self.app.grilles)}")

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        indices = sorted([int(iid) for iid in selected], reverse=True)
        for idx in indices:
            self.app.grilles.pop(idx)
        self._refresh_tree()
        self.app.notify_data_changed()

    def _clear_all(self):
        if not self.app.grilles:
            return
        if messagebox.askyesno("Bestätigung", "Alle Grilles wirklich löschen?"):
            self.app.grilles.clear()
            self._refresh_tree()
            self.app.notify_data_changed()
