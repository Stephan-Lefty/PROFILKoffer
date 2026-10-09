"""Was mitgenommen wird - und was dafür vorher weichen muss.

Ein Profil ist hier kein Benutzerkonto, sondern der Ordner, in dem ein
Programm alles ablegt: Konten, Passwörter, Lesezeichen, Erweiterungen,
Einstellungen. Bei Thunderbird und Vivaldi ist das jeweils **ein** Ordner,
und genau das macht den Umzug überhaupt möglich.

Drei Angaben gehören zu jedem Profil, und alle drei haben einen Grund:

``pfad``
    Der Ordner selbst. Relativ zum Home, nicht absolut - sonst ließe sich
    gegen ein untergeschobenes Home nicht testen, und jeder Test schriebe
    im echten Profil herum.

``zwischenspeicher``
    Was das Programm neu anlegen kann. Diese Ordner werden beim Einspielen
    **gelöscht** statt mitgenommen. Sie sind groß, sie sind wertlos, und
    vor allem: In ihnen steht noch der Stand des alten Rechners. Bleiben
    sie liegen, mischt sich Altes unter Neues.

``prozesse``
    Woran man erkennt, dass das Programm noch läuft. Das ist die wichtigste
    Angabe von allen. Ein laufender Vivaldi hält seine Lesezeichen im
    Speicher und schreibt sie beim Beenden zurück - über alles, was man
    gerade eingespielt hat. Deshalb bricht das Einspielen ab, solange hier
    noch etwas antwortet; eine Rückfrage zum Wegklicken genügt nicht.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Profil:
    """Ein Programm und der Ordner, in dem sein ganzer Stand liegt."""

    name: str
    pfad: str
    zwischenspeicher: tuple[str, ...]
    prozesse: tuple[str, ...]

    def ordner(self, home: Path) -> Path:
        return home / self.pfad

    def speicher(self, home: Path) -> tuple[Path, ...]:
        return tuple(home / p for p in self.zwischenspeicher)


#: Thunderbird legt unter ``.thunderbird`` ab - inklusive ``key4.db`` und
#: ``logins.json``, in denen die Passwörter stehen. Beide sind an nichts
#: gebunden, was auf dem Rechner bleibt; deshalb überlebt der Umzug sie.
#: Vivaldi liegt unter ``.config/vivaldi``, Lesezeichen in ``Default/Bookmarks``.
PROFILE: tuple[Profil, ...] = (
    Profil(
        name="Thunderbird",
        pfad=".thunderbird",
        zwischenspeicher=(".cache/thunderbird",),
        prozesse=("thunderbird",),
    ),
    Profil(
        name="Vivaldi",
        pfad=".config/vivaldi",
        zwischenspeicher=(".cache/vivaldi",),
        # "vivaldi" trifft auch "vivaldi-bin" - so heißt der Prozess
        # tatsächlich, der Name im Menü ist nicht der im Prozessbaum.
        prozesse=("vivaldi",),
    ),
)


def vorhandene(home: Path) -> tuple[Profil, ...]:
    """Die Profile, die es auf diesem Rechner überhaupt gibt."""
    return tuple(p for p in PROFILE if p.ordner(home).exists())


def laufende(profile: tuple[Profil, ...] = PROFILE) -> list[str]:
    """Namen der Programme, die gerade laufen.

    Gefragt wird ``pgrep``, nicht ``ps | grep``: Letzteres findet sich
    zuverlässig selbst und meldet dann, Vivaldi laufe, weil in der eigenen
    Befehlszeile das Wort steht.

    Fehlt ``pgrep``, wird **nicht** »läuft nicht« zurückgegeben. Die Antwort
    wäre geraten, und sie führte an genau der Stelle zu Datenverlust, an der
    diese Funktion gebraucht wird. Stattdessen gelten dann alle als laufend.
    """
    gefunden: list[str] = []
    for profil in profile:
        for muster in profil.prozesse:
            try:
                fertig = subprocess.run(
                    ["pgrep", "-x", f"{muster}|{muster}-bin"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            except (OSError, subprocess.SubprocessError):
                gefunden.append(profil.name)
                break
            if fertig.returncode == 0 and fertig.stdout.strip():
                gefunden.append(profil.name)
                break
    return gefunden
