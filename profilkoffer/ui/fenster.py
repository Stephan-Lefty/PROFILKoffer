"""Das Hauptfenster: packen, auspacken, zusehen.

Die Oberfläche enthält keine Logik. Sie wählt aus, fragt nach und zeigt an;
gepackt und eingespielt wird in ``sicherung.py``. Das ist der Grund, warum
sich das Löschen des alten Profils überhaupt testen lässt.

Zwei Dinge, die hier aussehen wie Zierrat und keiner sind:

**Der Knopf wird während des Laufs beschriftet.** »Packen ...« statt
»Packen«, dazu ausgegraut. Ohne das steht man vor einem Fenster, in dem
sich nichts rührt, und weiß nicht, ob man richtig geklickt hat. Bei einer
Sicherung von viereinhalb Gigabyte dauert das einige Minuten.

**Die Arbeit läuft in einem eigenen Strang.** Sonst reagiert das Fenster
während des Packens nicht mehr, und die Arbeitsumgebung bietet an, das
abgestürzte Programm zu beenden.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from .. import __version__, farben, laufwerke, sicherung
from ..profile import PROFILE, laufende
from . import auswahl, hilfe

SCHRIFT = ("Sans", 10)
SCHRIFT_FETT = ("Sans", 10, "bold")


class Fenster:
    def __init__(self, wurzel: tk.Tk, home: Path | None = None) -> None:
        self.wurzel = wurzel
        self.home = home or Path.home()
        self.ziel: Path | None = None
        self.archiv: Path | None = None

        # Arbeitsstränge dürfen Tk nicht anfassen - Tk ist nicht für mehrere
        # Stränge gebaut und stürzt dabei gelegentlich ohne Meldung ab.
        # Meldungen gehen deshalb durch diese Schlange, und das Fenster holt
        # sie zehnmal je Sekunde ab.
        self.meldungen: queue.Queue[tuple[str, object]] = queue.Queue()

        wurzel.title("PROFILKoffer")
        wurzel.configure(bg=farben.GRAU_PAPIER)
        wurzel.minsize(760, 700)

        self._kopf()
        self._uebersicht()
        self._packen_teil()
        self._auspacken_teil()
        self._protokoll()

        wurzel.bind("<F1>", lambda _: hilfe.zeigen(self.wurzel))
        self.schreiben("Bereit.")
        self.wurzel.after(100, self._schlange_leeren)

    # -- Aufbau -----------------------------------------------------------

    def _kopf(self) -> None:
        kopf = tk.Frame(self.wurzel, bg=farben.BLAU)
        kopf.pack(fill=tk.X)

        tk.Label(
            kopf,
            text="PROFILKoffer",
            font=("Sans", 17, "bold"),
            bg=farben.BLAU,
            fg=farben.WEISS,
        ).pack(pady=(14, 0))

        tk.Label(
            kopf,
            text="Thunderbird und Vivaldi von einem Rechner auf den anderen",
            font=SCHRIFT,
            bg=farben.BLAU,
            fg=farben.WEISS,
        ).pack(pady=(2, 14))

    def _uebersicht(self) -> None:
        kasten = tk.Frame(
            self.wurzel,
            bg=farben.WEISS,
            highlightthickness=1,
            highlightbackground=farben.GRAU_HELL,
        )
        kasten.pack(fill=tk.X, padx=16, pady=(16, 8))

        zeilen = []
        for profil in PROFILE:
            ordner = profil.ordner(self.home)
            zeilen.append(f"{profil.name:<14}{'gefunden' if ordner.exists() else 'nicht eingerichtet'}")

        tk.Label(
            kasten,
            text="\n".join(zeilen),
            font=("Monospace", 10),
            bg=farben.WEISS,
            fg=farben.GRAU_DUNKEL,
            justify=tk.LEFT,
            anchor="w",
            padx=14,
            pady=12,
        ).pack(fill=tk.X)

    def _abschnitt(self, titel: str) -> tk.LabelFrame:
        rahmen = tk.LabelFrame(
            self.wurzel,
            text=f" {titel} ",
            font=SCHRIFT_FETT,
            bg=farben.GRAU_PAPIER,
            fg=farben.GRAU_DUNKEL,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=farben.GRAU_HELL,
            padx=14,
            pady=12,
        )
        rahmen.pack(fill=tk.X, padx=16, pady=8)
        return rahmen

    def _packen_teil(self) -> None:
        rahmen = self._abschnitt("Packen - auf Stick oder Platte sichern")

        self.ziel_text = tk.StringVar(value="Noch kein Laufwerk gewählt")
        self._pfadfeld(rahmen, self.ziel_text)

        self._knopf(rahmen, "Laufwerk wählen", self._ziel_waehlen, farben.GRAU).pack(
            fill=tk.X, pady=(10, 6)
        )
        self.packen_knopf = self._knopf(rahmen, "Packen", self._packen, farben.BLAU)
        self.packen_knopf.pack(fill=tk.X)

    def _auspacken_teil(self) -> None:
        rahmen = self._abschnitt("Auspacken - Stand auf diesem Rechner herstellen")

        self.archiv_text = tk.StringVar(value="Noch keine Sicherung gewählt")
        self._pfadfeld(rahmen, self.archiv_text)

        self._knopf(rahmen, "Sicherung wählen", self._archiv_waehlen, farben.GRAU).pack(
            fill=tk.X, pady=(10, 6)
        )
        self.auspacken_knopf = self._knopf(rahmen, "Auspacken", self._auspacken, farben.BLAU)
        self.auspacken_knopf.pack(fill=tk.X)

    def _protokoll(self) -> None:
        leiste = tk.Frame(self.wurzel, bg=farben.GRAU_PAPIER)
        leiste.pack(fill=tk.X, padx=16, pady=(8, 0))

        tk.Label(
            leiste, text="Verlauf", font=SCHRIFT_FETT, bg=farben.GRAU_PAPIER, fg=farben.GRAU_DUNKEL
        ).pack(side=tk.LEFT)

        tk.Button(
            leiste,
            text="Hilfe (F1)",
            command=lambda: hilfe.zeigen(self.wurzel),
            font=SCHRIFT,
            bg=farben.GRAU_PAPIER,
            fg=farben.BLAU,
            activebackground=farben.GRAU_PAPIER,
            activeforeground=farben.BLAU_DUNKEL,
            relief=tk.FLAT,
            cursor="hand2",
            highlightthickness=0,
            borderwidth=0,
        ).pack(side=tk.RIGHT)

        rahmen = tk.Frame(self.wurzel, bg=farben.GRAU_PAPIER)
        rahmen.pack(fill=tk.BOTH, expand=True, padx=16, pady=(4, 16))

        rollbalken = tk.Scrollbar(rahmen)
        rollbalken.pack(side=tk.RIGHT, fill=tk.Y)

        self.protokoll = tk.Text(
            rahmen,
            height=9,
            font=("Monospace", 9),
            bg=farben.WEISS,
            fg=farben.GRAU_DUNKEL,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=farben.GRAU_HELL,
            padx=10,
            pady=8,
            yscrollcommand=rollbalken.set,
            state=tk.DISABLED,
        )
        self.protokoll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rollbalken.config(command=self.protokoll.yview)

    def _pfadfeld(self, eltern: tk.Misc, inhalt: tk.StringVar) -> None:
        tk.Label(
            eltern,
            textvariable=inhalt,
            font=("Monospace", 9),
            bg=farben.WEISS,
            fg=farben.GRAU_DUNKEL,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=farben.GRAU_HELL,
            anchor="w",
            justify=tk.LEFT,
            padx=10,
            pady=8,
            wraplength=660,
        ).pack(fill=tk.X)

    def _knopf(self, eltern: tk.Misc, text: str, befehl, grund: str) -> tk.Button:
        return tk.Button(
            eltern,
            text=text,
            command=befehl,
            font=SCHRIFT_FETT if grund == farben.BLAU else SCHRIFT,
            bg=grund,
            fg=farben.WEISS,
            activebackground=farben.BLAU_DUNKEL,
            activeforeground=farben.WEISS,
            disabledforeground=farben.GRAU_HELL,
            relief=tk.FLAT,
            pady=9,
            cursor="hand2",
            highlightthickness=0,
        )

    # -- Meldungen --------------------------------------------------------

    def schreiben(self, zeile: str) -> None:
        self.protokoll.configure(state=tk.NORMAL)
        self.protokoll.insert(tk.END, zeile + "\n")
        self.protokoll.see(tk.END)
        self.protokoll.configure(state=tk.DISABLED)

    def _schlange_leeren(self) -> None:
        while True:
            try:
                art, inhalt = self.meldungen.get_nowait()
            except queue.Empty:
                break
            if art == "zeile":
                self.schreiben(str(inhalt))
            elif art == "fertig":
                self._fertig(*inhalt)  # type: ignore[misc]
        self.wurzel.after(100, self._schlange_leeren)

    def _fertig(self, knopf: tk.Button, text: str, erfolg: bool, nachricht: str) -> None:
        knopf.configure(state=tk.NORMAL, text=text)
        if erfolg:
            messagebox.showinfo("Fertig", nachricht, parent=self.wurzel)
        else:
            messagebox.showerror("Nicht ausgeführt", nachricht, parent=self.wurzel)

    # -- Auswahl ----------------------------------------------------------

    def _ziel_waehlen(self) -> None:
        gefunden = laufwerke.laufwerke(self.home)
        if not gefunden:
            messagebox.showerror(
                "Kein Laufwerk",
                "Es ist kein beschreibbares Laufwerk eingehängt.",
                parent=self.wurzel,
            )
            return

        gewaehlt = auswahl.waehlen(
            self.wurzel,
            "Laufwerk wählen",
            "Wohin soll die Sicherung?",
            [(l.beschriftung(), l) for l in gefunden],
        )
        if gewaehlt is None:
            return

        self.ziel = gewaehlt.pfad
        self.ziel_text.set(str(gewaehlt.pfad))
        self.schreiben(f"Ziel: {gewaehlt.name}")

        if gewaehlt.begrenzt:
            self.schreiben(
                f"Achtung: {gewaehlt.dateisystem} nimmt keine Datei über 4 GiB an."
            )

    def _archiv_waehlen(self) -> None:
        orte = [l.pfad for l in laufwerke.laufwerke(self.home)]
        orte += [self.home / "Downloads", self.home / "Schreibtisch", self.home / "Dokumente"]
        gefunden = sicherung.sicherungen_finden(orte)

        if not gefunden:
            self.schreiben("Keine Sicherung gefunden - bitte selbst heraussuchen.")
            self._archiv_durchsuchen()
            return

        eintraege = [
            (
                f"{datum:%d.%m.%Y %H:%M}   {groesse / 1024**3:5.2f} GiB   {pfad.parent}",
                pfad,
            )
            for pfad, groesse, datum in gefunden
        ]
        gewaehlt = auswahl.waehlen(
            self.wurzel,
            "Sicherung wählen",
            "Welche Sicherung soll eingespielt werden?",
            eintraege,
            durchsuchen="Andere Datei ...",
        )
        if gewaehlt is None:
            return
        if gewaehlt == "durchsuchen":
            self._archiv_durchsuchen()
            return

        self.archiv = gewaehlt
        self.archiv_text.set(str(gewaehlt))
        self.schreiben(f"Sicherung: {gewaehlt.name}")

    def _archiv_durchsuchen(self) -> None:
        start = self.home / "Downloads"
        gewaehlt = filedialog.askopenfilename(
            parent=self.wurzel,
            title="Sicherung wählen",
            initialdir=str(start if start.is_dir() else self.home),
            filetypes=[("Sicherungen", "*.tar.gz"), ("Alle Dateien", "*")],
        )
        if gewaehlt:
            self.archiv = Path(gewaehlt)
            self.archiv_text.set(gewaehlt)
            self.schreiben(f"Sicherung: {self.archiv.name}")

    # -- Arbeit -----------------------------------------------------------

    def _packen(self) -> None:
        if self.ziel is None:
            messagebox.showerror("Kein Ziel", "Bitte zuerst ein Laufwerk wählen.", parent=self.wurzel)
            return

        noch_offen = laufende()
        if noch_offen:
            weiter = messagebox.askyesno(
                "Programm läuft noch",
                f"{' und '.join(noch_offen)} läuft noch.\n\n"
                "Eine Sicherung aus einem laufenden Programm kann halbfertige "
                "Datenbanken enthalten. Trotzdem packen?",
                parent=self.wurzel,
            )
            if not weiter:
                self.schreiben("Abgebrochen.")
                return

        self.packen_knopf.configure(state=tk.DISABLED, text="Packen ...")
        threading.Thread(target=self._packen_lauf, daemon=True).start()

    def _packen_lauf(self) -> None:
        melden = lambda zeile: self.meldungen.put(("zeile", zeile))
        try:
            assert self.ziel is not None
            melden("Größe wird geschätzt ...")
            geschaetzt = sicherung.groesse_schaetzen(self.home)

            fuer_pruefung = [l for l in laufwerke.laufwerke(self.home) if l.pfad == self.ziel]
            if fuer_pruefung:
                reicht, grund = laufwerke.passt(fuer_pruefung[0], geschaetzt)
                if not reicht:
                    raise sicherung.Abgebrochen(grund)

            archiv = sicherung.sichern(self.ziel, self.home, melden)
            mitgenommen = self._pakete_mitnehmen(self.ziel, melden)

            text = f"Die Sicherung liegt als\n{archiv.name}\nauf dem Laufwerk."
            if mitgenommen:
                text += "\n\nDaneben liegen die Installationspakete für Debian und Manjaro."
            self.meldungen.put(("fertig", (self.packen_knopf, "Packen", True, text)))

        except sicherung.Abgebrochen as grund:
            melden(f"Abgebrochen: {grund}")
            self.meldungen.put(("fertig", (self.packen_knopf, "Packen", False, str(grund))))
        except Exception as fehler:  # noqa: BLE001 - der Benutzer soll alles sehen
            melden(f"Fehlgeschlagen: {fehler}")
            self.meldungen.put(("fertig", (self.packen_knopf, "Packen", False, str(fehler))))

    def _auspacken(self) -> None:
        if self.archiv is None:
            messagebox.showerror(
                "Keine Sicherung", "Bitte zuerst eine Sicherung wählen.", parent=self.wurzel
            )
            return

        sicher = messagebox.askyesno(
            "Stand ersetzen",
            "Der bisherige Stand von Thunderbird und Vivaldi auf diesem Rechner "
            "wird vollständig ersetzt.\n\n"
            "Die alten Profile werden nicht gelöscht, sondern als *_alt_<Datum> "
            "daneben gelegt.\n\nFortfahren?",
            parent=self.wurzel,
        )
        if not sicher:
            self.schreiben("Abgebrochen.")
            return

        self.auspacken_knopf.configure(state=tk.DISABLED, text="Auspacken ...")
        threading.Thread(target=self._auspacken_lauf, daemon=True).start()

    def _auspacken_lauf(self) -> None:
        melden = lambda zeile: self.meldungen.put(("zeile", zeile))
        try:
            assert self.archiv is not None
            beiseite = sicherung.einspielen(self.archiv, self.home, melden)
            text = (
                "Der Stand ist eingespielt.\n\n"
                "Thunderbird und Vivaldi können jetzt gestartet werden.\n\n"
                "Vivaldi-Sync erst anmelden, wenn die Lesezeichen stimmen - "
                "sonst holt der Dienst den alten Stand zurück."
            )
            if beiseite:
                text += "\n\nBisheriger Stand:\n" + "\n".join(p.name for p in beiseite)
            self.meldungen.put(("fertig", (self.auspacken_knopf, "Auspacken", True, text)))

        except sicherung.Abgebrochen as grund:
            melden(f"Abgebrochen: {grund}")
            self.meldungen.put(("fertig", (self.auspacken_knopf, "Auspacken", False, str(grund))))
        except Exception as fehler:  # noqa: BLE001
            melden(f"Fehlgeschlagen: {fehler}")
            self.meldungen.put(("fertig", (self.auspacken_knopf, "Auspacken", False, str(fehler))))

    def _pakete_mitnehmen(self, ziel: Path, melden) -> bool:
        """Die Installationspakete neben die Sicherung legen.

        Sie liegen in jedem Paket unter ``/usr/share/profilkoffer``. Auf
        einem Rechner, auf dem PROFILKoffer noch nicht installiert ist,
        nützt die Sicherung allein nichts - man käme nicht an sie heran.
        """
        import shutil

        quellen = [
            Path("/usr/share/profilkoffer"),
            Path(__file__).resolve().parent.parent.parent / "packaging" / "fertig",
        ]
        mitgenommen = False
        for quelle in quellen:
            if not quelle.is_dir():
                continue
            for muster in ("*.deb", "*.pkg.tar.zst"):
                for paket in quelle.glob(muster):
                    try:
                        shutil.copy2(paket, ziel / paket.name)
                        melden(f"Installationspaket mitgenommen: {paket.name}")
                        mitgenommen = True
                    except OSError as fehler:
                        melden(f"{paket.name} nicht mitgenommen: {fehler}")
            if mitgenommen:
                break
        return mitgenommen


def main() -> int:
    wurzel = tk.Tk()
    Fenster(wurzel)
    wurzel.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
