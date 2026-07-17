"""
Tab 4: Statistiken – Häufigkeitsanalyse und Diagramme
"""
import tkinter as tk
from tkinter import ttk
from collections import Counter

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class StatistikTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#F5F5F5")
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Toolbar
        bar = tk.Frame(self, bg="#E8E8E8", pady=6)
        bar.pack(fill="x", padx=10, pady=(10, 0))
        tk.Button(bar, text="  Statistik aktualisieren  ", command=self.refresh,
                  bg="#2E75B6", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", padx=8, pady=4).pack(side="left", padx=6)

        # Diagramm-Auswahl
        tk.Label(bar, text="Anzeige:", bg="#E8E8E8",
                 font=("Segoe UI", 9)).pack(side="left", padx=(16, 4))
        self.chart_var = tk.StringVar(value="Häufigkeit gezogener Zahlen")
        choices = [
            "Häufigkeit gezogener Zahlen",
            "Trefferhäufigkeit deiner Grilles",
            "Gewinn pro Ziehung",
        ]
        cb = ttk.Combobox(bar, textvariable=self.chart_var,
                          values=choices, state="readonly", width=32)
        cb.pack(side="left", padx=4)
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Hauptbereich: Links Tabelle, Rechts Diagramm
        content = tk.Frame(self, bg="#F5F5F5")
        content.pack(fill="both", expand=True, padx=10, pady=8)

        # --- Linke Tabelle: Top-Zahlen ---
        left = tk.LabelFrame(content, text=" Häufigkeitsrangliste (Gezogene Zahlen) ",
                              font=("Segoe UI", 9, "bold"),
                              bg="#F5F5F5", fg="#1F4E79")
        left.pack(side="left", fill="y", padx=(0, 8))

        cols = ("Zahl", "Häufigkeit", "Rang")
        self.tbl = ttk.Treeview(left, columns=cols, show="headings", height=25)
        self.tbl.heading("Zahl",       text="Zahl")
        self.tbl.heading("Häufigkeit", text="Häufigkeit")
        self.tbl.heading("Rang",       text="Rang")
        self.tbl.column("Zahl",       width=70, anchor="center")
        self.tbl.column("Häufigkeit", width=90, anchor="center")
        self.tbl.column("Rang",       width=70, anchor="center")
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=sb.set)
        self.tbl.pack(side="left", fill="y")
        sb.pack(side="left", fill="y")

        # --- Rechts: Diagramm ---
        right = tk.Frame(content, bg="#F5F5F5")
        right.pack(side="left", fill="both", expand=True)

        if HAS_MPL:
            self.fig = Figure(figsize=(7, 5), dpi=96, facecolor="#F5F5F5")
            self.ax  = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=right)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            tk.Label(right,
                     text="matplotlib nicht installiert.\n"
                          "Installiere es mit:\npip install matplotlib",
                     bg="#F5F5F5", fg="#C00000",
                     font=("Segoe UI", 11)).pack(expand=True)
            self.canvas = None

        # --- Untere Info-Zeile ---
        info = tk.Frame(self, bg="#F5F5F5")
        info.pack(fill="x", padx=10, pady=(0, 8))
        self.lbl_info = tk.Label(info, text="", bg="#F5F5F5",
                                  fg="#1F4E79", font=("Segoe UI", 9, "italic"))
        self.lbl_info.pack(side="left")

    def refresh(self):
        ziehungen = self.app.ziehungen
        grilles   = self.app.grilles

        if not ziehungen:
            self.lbl_info.config(text="Keine Ziehungsdaten vorhanden.")
            return

        modus = self.chart_var.get()

        if modus == "Häufigkeit gezogener Zahlen":
            self._chart_ziehung_freq(ziehungen)
        elif modus == "Trefferhäufigkeit deiner Grilles":
            if not grilles:
                self.lbl_info.config(text="Keine Grilles vorhanden.")
                return
            self._chart_grille_treffer(ziehungen, grilles)
        elif modus == "Gewinn pro Ziehung":
            if not grilles:
                self.lbl_info.config(text="Keine Grilles vorhanden.")
                return
            self._chart_gewinn_verlauf(ziehungen, grilles)

    # ── Diagramm 1: Häufigkeit gezogener Zahlen ──────────────────────────────
    def _chart_ziehung_freq(self, ziehungen):
        counter = Counter()
        for z in ziehungen:
            counter.update(z["zahlen"])

        # Tabelle füllen
        self.tbl.delete(*self.tbl.get_children())
        ranked = sorted(counter.items(), key=lambda x: -x[1])
        for rang, (zahl, hfg) in enumerate(ranked, 1):
            self.tbl.insert("", "end", values=(zahl, hfg, rang))

        self.lbl_info.config(
            text=f"{len(ziehungen)} Ziehungen analysiert. "
                 f"Heisseste Zahl: {ranked[0][0]} ({ranked[0][1]}x)")

        if not HAS_MPL or self.canvas is None:
            return

        # Alle 49 Zahlen sortiert
        zahlen  = list(range(1, 50))
        hfgs    = [counter.get(z, 0) for z in zahlen]
        farben  = ["#C00000" if h == max(hfgs) else
                   "#2E75B6" if h >= sorted(hfgs)[-5] else
                   "#BDD7EE" for h in hfgs]

        self.ax.clear()
        bars = self.ax.bar(zahlen, hfgs, color=farben, edgecolor="white", linewidth=0.4)
        self.ax.set_title("Häufigkeit gezogener Zahlen (1–49)",
                           fontsize=11, fontweight="bold", color="#1F4E79")
        self.ax.set_xlabel("Zahl", fontsize=9)
        self.ax.set_ylabel("Häufigkeit", fontsize=9)
        self.ax.set_xlim(0.5, 49.5)
        self.ax.set_xticks(range(1, 50, 2))
        self.ax.tick_params(labelsize=7)
        self.ax.set_facecolor("#F9F9F9")
        self.fig.tight_layout()
        self.canvas.draw()

    # ── Diagramm 2: Treffer deiner Grilles ───────────────────────────────────
    def _chart_grille_treffer(self, ziehungen, grilles):
        from tab_auswertung import berechne_treffer
        treffer_counter = Counter()
        for z in ziehungen:
            for g in grilles:
                t = berechne_treffer(g, z["zahlen"])
                if t >= 2:
                    treffer_counter[t] += 1

        self.tbl.delete(*self.tbl.get_children())
        for t in sorted(treffer_counter, reverse=True):
            self.tbl.insert("", "end", values=(f"{t}er", treffer_counter[t], "–"))

        self.lbl_info.config(
            text=f"{len(grilles)} Grilles × {len(ziehungen)} Ziehungen ausgewertet")

        if not HAS_MPL or self.canvas is None:
            return

        labels = [f"{k}er" for k in sorted(treffer_counter)]
        vals   = [treffer_counter[k] for k in sorted(treffer_counter)]
        farben = ["#BDD7EE", "#2E75B6", "#1F4E79", "#F4B942", "#C00000"]

        self.ax.clear()
        self.ax.bar(labels, vals, color=farben[:len(labels)],
                    edgecolor="white", linewidth=0.5)
        self.ax.set_title("Trefferhäufigkeit (alle Grilles × alle Ziehungen)",
                           fontsize=11, fontweight="bold", color="#1F4E79")
        self.ax.set_ylabel("Anzahl", fontsize=9)
        self.ax.set_facecolor("#F9F9F9")
        for bar, val in zip(self.ax.patches, vals):
            self.ax.text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + 0.3, str(val),
                         ha="center", va="bottom", fontsize=9)
        self.fig.tight_layout()
        self.canvas.draw()

    # ── Diagramm 3: Gewinn/Verlust-Verlauf ───────────────────────────────────
    def _chart_gewinn_verlauf(self, ziehungen, grilles):
        from tab_auswertung import analysiere, EINSATZ
        ergebnisse = analysiere(grilles, ziehungen)

        self.tbl.delete(*self.tbl.get_children())
        kumulativ = 0.0
        for r in ergebnisse:
            kumulativ += r["bilanz"]
            self.tbl.insert("", "end",
                             values=(r["datum"],
                                     f"{r['gewinn']:.2f}",
                                     f"{kumulativ:.2f}"))

        gesamtgewinn = sum(r["gewinn"]  for r in ergebnisse)
        gesamteinsatz= sum(r["einsatz"] for r in ergebnisse)
        self.lbl_info.config(
            text=f"Gesamteinsatz: {gesamteinsatz:,.2f} EUR  |  "
                 f"Gesamtgewinn: {gesamtgewinn:,.2f} EUR  |  "
                 f"Bilanz: {gesamtgewinn-gesamteinsatz:,.2f} EUR")

        if not HAS_MPL or self.canvas is None:
            return

        daten    = list(range(1, len(ergebnisse) + 1))
        gewinne  = [r["gewinn"] for r in ergebnisse]
        kum_vals = []
        kum = 0.0
        for r in ergebnisse:
            kum += r["bilanz"]
            kum_vals.append(kum)

        self.ax.clear()
        ax2 = self.ax.twinx()
        self.ax.bar(daten, gewinne, color="#2E75B6", alpha=0.6,
                    label="Gewinn je Ziehung")
        ax2.plot(daten, kum_vals, color="#C00000", linewidth=2,
                 label="Kumulierte Bilanz")
        ax2.axhline(0, color="gray", linewidth=0.8, linestyle="--")
        self.ax.set_title("Gewinn und kumulierte Bilanz je Ziehung",
                           fontsize=11, fontweight="bold", color="#1F4E79")
        self.ax.set_xlabel("Ziehung #", fontsize=9)
        self.ax.set_ylabel("Gewinn je Ziehung (EUR)", fontsize=9, color="#2E75B6")
        ax2.set_ylabel("Kum. Bilanz (EUR)", fontsize=9, color="#C00000")
        self.ax.set_facecolor("#F9F9F9")
        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.ax.legend(lines1 + lines2, labels1 + labels2,
                       loc="upper left", fontsize=8)
        self.fig.tight_layout()
        self.canvas.draw()
