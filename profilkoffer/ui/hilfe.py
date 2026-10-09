"""Die Hilfe, im Programm selbst.

Wer nicht weiterkommt, klickt auf Hilfe - und nicht auf GitHub nach einer
README. Der Text steht deshalb hier und wird mit dem Programm ausgeliefert,
nicht nur in ``docs/``.

Er ist bewusst kurz. Eine Hilfe, die alles erklärt, wird nicht gelesen;
diese beantwortet die vier Fragen, die beim Umzug tatsächlich aufkommen.
"""

from __future__ import annotations

import tkinter as tk

from .. import __version__, farben

TEXT = """\
Was PROFILKoffer mitnimmt

    Thunderbird   Konten, Zugangsdaten, Ordner, Filter, Erweiterungen
    Vivaldi       Lesezeichen, Einstellungen, Erweiterungen, Sitzungen

Alles liegt pro Programm in einem Ordner. Der Koffer packt genau diesen
Ordner ein - deshalb ist der Stand hinterher derselbe und nicht nur
ähnlich.


Der Weg von einem Rechner zum anderen

    1. Auf dem alten Rechner beide Programme schließen.
    2. Packen - Laufwerk wählen, Knopf drücken, warten.
    3. Stick an den neuen Rechner.
    4. Dort auch beide Programme schließen.
    5. Auspacken - Sicherung wählen, Knopf drücken.

Neben der Sicherung liegen die Installationspakete für Debian und für
Manjaro. Auf einem Rechner, auf dem PROFILKoffer noch nicht installiert
ist, lässt er sich damit einrichten.


Warum das Auspacken abbricht, wenn Vivaldi noch läuft

Ein laufender Browser hält seine Lesezeichen im Speicher und schreibt sie
beim Beenden auf die Platte - über alles, was gerade eingespielt wurde.
Die alten Lesezeichen wären wieder da, und niemand wüsste, warum.

Deshalb gibt es an dieser Stelle keine Rückfrage, die man wegklicken kann.


Wo der bisherige Stand bleibt

Beim Auspacken wandert das bisherige Profil zur Seite:

    ~/.thunderbird_alt_<Datum>
    ~/.config/vivaldi_alt_<Datum>

Gelöscht wird nichts. Sobald der neue Stand stimmt, können diese Ordner
weg - vorher nicht.


Wenn die Sicherung nicht auf den Stick passt

FAT32 nimmt keine Datei über 4 GiB an, und ein Thunderbird-Archiv ist
schnell größer. PROFILKoffer sagt das vorher statt mittendrin. Ein Stick
mit ext4, btrfs oder NTFS nimmt sie.
"""


def zeigen(eltern: tk.Misc) -> None:
    """Das Hilfefenster öffnen."""
    fenster = tk.Toplevel(eltern)
    fenster.title("Hilfe - PROFILKoffer")
    fenster.configure(bg=farben.GRAU_PAPIER)
    fenster.transient(eltern)
    fenster.minsize(640, 520)

    kopf = tk.Frame(fenster, bg=farben.BLAU)
    kopf.pack(fill=tk.X)
    tk.Label(
        kopf,
        text=f"PROFILKoffer {__version__}",
        font=("Sans", 13, "bold"),
        bg=farben.BLAU,
        fg=farben.WEISS,
        pady=12,
    ).pack()

    rahmen = tk.Frame(fenster, bg=farben.GRAU_PAPIER)
    rahmen.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    rollbalken = tk.Scrollbar(rahmen)
    rollbalken.pack(side=tk.RIGHT, fill=tk.Y)

    feld = tk.Text(
        rahmen,
        wrap=tk.WORD,
        font=("Monospace", 10),
        bg=farben.WEISS,
        fg=farben.GRAU_DUNKEL,
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground=farben.GRAU_HELL,
        padx=14,
        pady=14,
        yscrollcommand=rollbalken.set,
    )
    feld.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    rollbalken.config(command=feld.yview)

    feld.insert("1.0", TEXT)
    feld.configure(state=tk.DISABLED)

    fenster.bind("<Escape>", lambda _: fenster.destroy())

    tk.Button(
        fenster,
        text="Schließen",
        command=fenster.destroy,
        font=("Sans", 10),
        bg=farben.BLAU,
        fg=farben.WEISS,
        activebackground=farben.BLAU_DUNKEL,
        activeforeground=farben.WEISS,
        relief=tk.FLAT,
        padx=18,
        pady=8,
        cursor="hand2",
        highlightthickness=0,
    ).pack(pady=(0, 16))
