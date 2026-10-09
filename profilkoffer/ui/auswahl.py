"""Ein Auswahlfenster mit Liste - für Laufwerke wie für Sicherungen.

Warum nicht der Dateidialog von Tk: Er zeigt Einhängepunkte unter ihren
Gerätekennungen an. Der erste Anlauf dieses Programms benutzte ihn, und die
Liste sah so aus:

    /run/media/stephan/89b24b6c-3bf3-4bb9-83dc-dcd6c94013291
    /run/media/stephan/5FB5-7756

Daneben zeigte der Dateimanager dieselben Laufwerke als »NTFS-Mobil« und
»Linux-Mobil«. Wer etwas auf einen Stick legen will, sucht den Stick, nicht
seine Kennung.

Der Dateidialog bleibt als Ausweg erreichbar - über »Andere Datei ...«. Eine
Liste, die etwas nicht enthält, ist sonst eine Sackgasse.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Sequence
from typing import Any

from .. import farben

SCHRIFT = ("Sans", 10)
SCHRIFT_FETT = ("Sans", 10, "bold")


def waehlen(
    eltern: tk.Misc,
    titel: str,
    frage: str,
    eintraege: Sequence[tuple[str, Any]],
    durchsuchen: str | None = None,
) -> Any | None:
    """Eine Zeile aus ``eintraege`` auswählen lassen.

    ``eintraege`` sind Paare aus Beschriftung und Rückgabewert. Gewählt wird
    mit Doppelklick, mit der Eingabetaste oder über den Knopf - alle drei,
    weil sich niemand merken will, welcher Weg in welchem Fenster gilt.

    Ist ``durchsuchen`` gesetzt, erscheint ein Knopf mit diesem Text, der
    ``"durchsuchen"`` zurückgibt.
    """
    fenster = tk.Toplevel(eltern)
    fenster.title(titel)
    fenster.configure(bg=farben.GRAU_PAPIER)
    fenster.transient(eltern)
    fenster.grab_set()
    fenster.minsize(620, 340)

    tk.Label(
        fenster,
        text=frage,
        font=SCHRIFT_FETT,
        bg=farben.GRAU_PAPIER,
        fg=farben.GRAU_DUNKEL,
        anchor="w",
    ).pack(fill=tk.X, padx=16, pady=(16, 8))

    rahmen = tk.Frame(fenster, bg=farben.GRAU_PAPIER)
    rahmen.pack(fill=tk.BOTH, expand=True, padx=16)

    rollbalken = tk.Scrollbar(rahmen)
    rollbalken.pack(side=tk.RIGHT, fill=tk.Y)

    liste = tk.Listbox(
        rahmen,
        yscrollcommand=rollbalken.set,
        font=SCHRIFT,
        bg=farben.WEISS,
        fg=farben.GRAU_DUNKEL,
        selectbackground=farben.BLAU,
        selectforeground=farben.WEISS,
        activestyle="none",
        highlightthickness=1,
        highlightbackground=farben.GRAU_HELL,
        relief=tk.FLAT,
        height=10,
    )
    liste.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    rollbalken.config(command=liste.yview)

    for beschriftung, _ in eintraege:
        liste.insert(tk.END, beschriftung)
    if eintraege:
        liste.selection_set(0)
        liste.activate(0)
    liste.focus_set()

    ergebnis: dict[str, Any] = {"wert": None}

    def uebernehmen(*_: object) -> None:
        gewaehlt = liste.curselection()
        if gewaehlt:
            ergebnis["wert"] = eintraege[gewaehlt[0]][1]
            fenster.destroy()

    def abbrechen(*_: object) -> None:
        fenster.destroy()

    def ausweichen(*_: object) -> None:
        ergebnis["wert"] = "durchsuchen"
        fenster.destroy()

    liste.bind("<Double-Button-1>", uebernehmen)
    liste.bind("<Return>", uebernehmen)
    fenster.bind("<Escape>", abbrechen)

    leiste = tk.Frame(fenster, bg=farben.GRAU_PAPIER)
    leiste.pack(fill=tk.X, padx=16, pady=16)

    _knopf(leiste, "Auswählen", uebernehmen, farben.BLAU).pack(side=tk.RIGHT)
    _knopf(leiste, "Abbrechen", abbrechen, farben.GRAU).pack(side=tk.RIGHT, padx=(0, 8))
    if durchsuchen:
        _knopf(leiste, durchsuchen, ausweichen, farben.GRAU).pack(side=tk.LEFT)

    eltern.wait_window(fenster)
    return ergebnis["wert"]


def _knopf(eltern: tk.Misc, text: str, befehl, grund: str) -> tk.Button:
    return tk.Button(
        eltern,
        text=text,
        command=befehl,
        font=SCHRIFT,
        bg=grund,
        fg=farben.WEISS,
        activebackground=farben.BLAU_DUNKEL,
        activeforeground=farben.WEISS,
        relief=tk.FLAT,
        padx=18,
        pady=8,
        cursor="hand2",
        highlightthickness=0,
    )
