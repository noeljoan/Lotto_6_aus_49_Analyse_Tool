"""
Tab 2: Ziehungsergebnisse verwalten (manuell oder CSV)
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from datetime import datetime


class ZiehungenTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#F5F5F5")
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # --- Linke Seite: Eingabe ---
        left = tk.LabelFrame(self, text=" Ziehung manuell hinzufügen ",
                             font=("Segoe UI", 10, "bold"),
                             bg="#F5F5F5", fg="#1F4E79", padx=10, pady=10)
        left.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(left, text="Datum (TT.MM.JJJJ):",
                 bg="#F5F5F5", font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 2))
        self.entry_datum = tk.Entry(left, font=("Segoe UI", 12), width=18,
                                    relief="solid", bd=1)
        self.entry_datum.pack(pady=2)
        self.entry_datum.insert(0, datetime.today().strftime("%d.%m.%Y"))

        tk.Label(left, text="6 Zahlen (1–49), mit Komma getrennt:",
                 bg="#F5F5F5", font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 2))
        self.entry_zahlen = tk.Entry(left, font=("Segoe UI", 12), width=25,
                                     relief="solid", bd=1)
        self.entry_zahlen.pack(pady=2)
        self.entry_zahlen.bind("<Return>", lambda e: self._add_ziehung())

        tk.Label(left, text="Beispiel: 7, 14, 23, 35, 42, 49",
                 bg="#F5F5F5", fg="gray", font=("Segoe UI", 8)).pack()

        tk.Button(left, text="Ziehung hinzufügen", command=self._add_ziehung,
                  bg="#2E75B6", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", padx=10, pady=5).pack(pady=8, fill="x")

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        tk.Label(left, text="CSV-Import:", bg="#F5F5F5",
                 font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(left, text="Datum,Z1,Z2,Z3,Z4,Z5,Z6",
                 bg="#F5F5F5", fg="gray", font=("Segoe UI", 8)).pack(anchor="w")
        tk.Label(left, text="Datum;Z1;Z2;Z3;Z4;Z5;Z6",
                 bg="#F5F5F5", fg="gray", font=("Segoe UI", 8)).pack(anchor="w")
        tk.Label(left, text="Datum,Z1-Z2-Z3-Z4-Z5-Z6",
                 bg="#F5F5F5", fg="gray", font=("Segoe UI", 8)).pack(anchor="w")

        tk.Button(left, text="CSV importieren", command=self._import_csv,
                  bg="#1F4E79", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", padx=10, pady=5).pack(pady=6, fill="x")

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        tk.Button(left, text="Alle Ziehungen loeschen", command=self._clear_all,
                  bg="#C00000", fg="white", font=("Segoe UI", 9),
                  relief="flat", cursor="hand2", padx=10, pady=4).pack(fill="x")

        self.lbl_count = tk.Label(left, text="Ziehungen: 0",
                                   bg="#F5F5F5", fg="#1F4E79",
                                   font=("Segoe UI", 11, "bold"))
        self.lbl_count.pack(pady=10)

        # --- Rechte Seite: Liste ---
        right = tk.Frame(self, bg="#F5F5F5")
        right.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        tk.Label(right, text="Alle Ziehungen", font=("Segoe UI", 11, "bold"),
                 bg="#F5F5F5", fg="#1F4E79").pack(anchor="w", pady=(0, 4))

        cols = ("#", "Datum", "Gezogene Zahlen")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=25)
        self.tree.heading("#", text="#")
        self.tree.heading("Datum", text="Datum")
        self.tree.heading("Gezogene Zahlen", text="Gezogene Zahlen")
        self.tree.column("#", width=50, anchor="center")
        self.tree.column("Datum", width=120, anchor="center")
        self.tree.column("Gezogene Zahlen", width=280, anchor="center")

        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        self.tree.bind("<Delete>", lambda e: self._delete_selected())
        tk.Button(right, text="Ausgewaehlte loeschen", command=self._delete_selected,
                  bg="#C00000", fg="white", font=("Segoe UI", 9),
                  relief="flat", cursor="hand2").pack(pady=6)

    def _parse_zahlen(self, text):
        """Erkennt automatisch Trennzeichen: Semikolon ';', Komma ',' oder Bindestrich '-'"""
        t = text.strip()
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

    def _parse_datum(self, text):
        for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(text.strip(), fmt).strftime("%d.%m.%Y")
            except ValueError:
                continue
        raise ValueError(f"Datum '{text}' nicht erkannt. Format: TT.MM.JJJJ")

    def _add_ziehung(self):
        datum_text = self.entry_datum.get().strip()
        zahlen_text = self.entry_zahlen.get().strip()
        try:
            datum = self._parse_datum(datum_text)
            zahlen = self._parse_zahlen(zahlen_text)
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))
            return
        self.app.ziehungen.append({"datum": datum, "zahlen": zahlen})
        self._sort_ziehungen()
        self._refresh_tree()
        self.entry_zahlen.delete(0, "end")
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
                    # Header überspringen
                    first = row[0].strip().lower()
                    if first in ("datum", "date", "ziehung", "#"):
                        continue
                    try:
                        datum = self._parse_datum(row[0])
                        if len(row) == 2:
                            # Format: Datum;Z1-Z2-Z3-Z4-Z5-Z6
                            zahlen = self._parse_zahlen(row[1])
                        elif len(row) >= 7:
                            # Format: Datum;Z1;Z2;Z3;Z4;Z5;Z6
                            zahlen = self._parse_zahlen(delimiter.join(row[1:7]))
                        else:
                            raise ValueError("Unbekanntes Format")
                        self.app.ziehungen.append({"datum": datum, "zahlen": zahlen})
                        count += 1
                    except (ValueError, IndexError):
                        errors += 1
        except Exception as e:
            messagebox.showerror("Fehler", f"CSV konnte nicht gelesen werden:\n{e}")
            return
        self._sort_ziehungen()
        self._refresh_tree()
        self.app.notify_data_changed()
        msg = f"{count} Ziehungen importiert."
        if errors:
            msg += f"\n{errors} Zeilen übersprungen (Fehler)."
        messagebox.showinfo("Import abgeschlossen", msg)

    def _sort_ziehungen(self):
        def sort_key(z):
            try:
                return datetime.strptime(z["datum"], "%d.%m.%Y")
            except ValueError:
                return datetime.min
        self.app.ziehungen.sort(key=sort_key)

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, z in enumerate(self.app.ziehungen, 1):
            nums = " – ".join(f"{n:02d}" for n in z["zahlen"])
            self.tree.insert("", "end", iid=str(i-1), values=(i, z["datum"], nums))
        self.lbl_count.config(text=f"Ziehungen: {len(self.app.ziehungen)}")

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        indices = sorted([int(iid) for iid in selected], reverse=True)
        for idx in indices:
            self.app.ziehungen.pop(idx)
        self._refresh_tree()
        self.app.notify_data_changed()

    def _clear_all(self):
        if not self.app.ziehungen:
            return
        if messagebox.askyesno("Bestätigung", "Alle Ziehungen wirklich löschen?"):
            self.app.ziehungen.clear()
            self._refresh_tree()
            self.app.notify_data_changed()
