"""Packen und Einspielen - der Teil ohne Oberfläche.

Hier steht nichts über Fenster, Knöpfe oder Tk. Das ist kein Selbstzweck:
Der gefährliche Teil dieses Programms - das Löschen des alten Profils -
lässt sich nur dann prüfen, wenn er sich ohne Bildschirm aufrufen lässt.
Die Tests in ``tests/test_sicherung.py`` spielen genau diesen Weg gegen ein
untergeschobenes Home durch.

Berichtet wird über ``melden``, eine Funktion, die eine Zeile entgegennimmt.
Die Oberfläche schreibt sie ins Protokollfeld, die Kommandozeile auf die
Ausgabe, der Test in eine Liste.

Zwei Entscheidungen, die man im Code nicht sieht:

**Ein Archiv, keine Ordnerkopie.** Eine Sicherung ist eine einzelne Datei.
Sie lässt sich ansehen, kopieren und verschieben, ohne dass auf halbem Weg
die Hälfte der Dateien da ist. Ein ``cp -r`` auf einen Stick, der während
des Kopierens abgezogen wird, hinterlässt genau das.

**Der alte Stand wird verschoben, nicht gelöscht.** Beim Einspielen wandert
das bisherige Profil nach ``<name>_alt_<Zeitstempel>``. Das kostet einmal
Platz und hat sich genau einmal gelohnt - aber dann vollständig.
"""

from __future__ import annotations

import shutil
import tarfile
from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path

from .profile import PROFILE, Profil, laufende, vorhandene

#: Wie die Sicherungen heißen. Der Zeitstempel steht im Namen, damit mehrere
#: nebeneinander liegen können und man ohne Hineinsehen weiß, welche die
#: neuere ist.
MUSTER = "profilkoffer_{stempel}.tar.gz"
SUCHMUSTER = "profilkoffer_*.tar.gz"

#: Auch das alte Namensmuster aus der Zeit vor dem Repository wird gefunden -
#: auf Stephans Platten liegen Sicherungen, die noch so heißen.
ALTES_SUCHMUSTER = "profiles_backup_*.tar.gz"


class Abgebrochen(RuntimeError):
    """Wird geworfen, wenn eine Vorbedingung nicht erfüllt ist.

    Eigene Klasse, damit die Oberfläche sie von einem echten Fehler
    unterscheiden kann: Hier ist nichts kaputt, es fehlt nur etwas.
    """


def _stempel(zeitpunkt: datetime | None = None) -> str:
    return (zeitpunkt or datetime.now()).strftime("%Y%m%d_%H%M%S")


def groesse_schaetzen(home: Path, profile: Iterable[Profil] = PROFILE) -> int:
    """Wie groß die Sicherung ungefähr wird, in Byte.

    Gezählt wird die unkomprimierte Summe. Das ist absichtlich zu viel:
    Profile bestehen zum großen Teil aus Mail-Archiven und Datenbanken, die
    sich gut packen lassen, oft auf die Hälfte. Lieber vorher zu viel Platz
    verlangen als mittendrin stehenbleiben.
    """
    gesamt = 0
    for profil in profile:
        ordner = profil.ordner(home)
        if not ordner.exists():
            continue
        for datei in ordner.rglob("*"):
            try:
                if datei.is_file() and not datei.is_symlink():
                    gesamt += datei.stat().st_size
            except OSError:
                continue
    return gesamt


def sichern(
    ziel: Path,
    home: Path,
    melden: Callable[[str], None] = lambda _: None,
    zeitpunkt: datetime | None = None,
) -> Path:
    """Die vorhandenen Profile in ein Archiv unter ``ziel`` packen."""
    dabei = vorhandene(home)
    if not dabei:
        raise Abgebrochen(
            "Auf diesem Rechner ist weder Thunderbird noch Vivaldi eingerichtet - "
            "es gibt nichts zu sichern."
        )

    archiv = ziel / MUSTER.format(stempel=_stempel(zeitpunkt))
    melden(f"Sicherung wird geschrieben: {archiv.name}")

    try:
        with tarfile.open(archiv, "w:gz") as paket:
            for profil in dabei:
                melden(f"{profil.name} wird eingepackt ...")
                paket.add(profil.ordner(home), arcname=profil.pfad)
                melden(f"{profil.name} ist drin")
    except BaseException:
        # Ein abgebrochener Lauf darf keine halbe Datei hinterlassen. Sie
        # sähe beim Einspielen aus wie eine gültige Sicherung.
        archiv.unlink(missing_ok=True)
        raise

    melden(f"Fertig: {archiv.stat().st_size / 1024**3:.2f} GiB")
    return archiv


def einspielen(
    archiv: Path,
    home: Path,
    melden: Callable[[str], None] = lambda _: None,
    zeitpunkt: datetime | None = None,
) -> list[Path]:
    """Ein Archiv einspielen und den bisherigen Stand vollständig ersetzen.

    Gibt die Pfade zurück, unter denen der alte Stand liegt.

    Die Reihenfolge ist nicht beliebig:

    1. Prüfen, ob die Programme laufen. Erst danach wird irgendetwas
       angefasst - sonst stünde man mit verschobenem Profil und nicht
       eingespieltem Archiv da.
    2. Alten Stand wegschieben.
    3. Zwischenspeicher löschen.
    4. Auspacken.

    Zwischen 2 und 4 darf nichts schiefgehen, das nicht auffällt. Geht beim
    Auspacken etwas schief, bleibt der alte Stand unter seinem neuen Namen
    liegen und ist von Hand zurückzuholen - die Meldung sagt, wie.
    """
    if not archiv.is_file():
        raise Abgebrochen(f"Die Sicherung »{archiv.name}« ist nicht mehr da.")

    noch_offen = laufende()
    if noch_offen:
        raise Abgebrochen(
            f"{' und '.join(noch_offen)} läuft noch.\n\n"
            "Ein laufendes Programm schreibt seinen bisherigen Stand beim Beenden "
            "zurück und überschreibt damit alles, was gerade eingespielt wurde - "
            "die alten Lesezeichen wären wieder da.\n\n"
            "Bitte schließen und erneut versuchen."
        )

    stempel = _stempel(zeitpunkt)
    beiseite: list[Path] = []

    for profil in PROFILE:
        ordner = profil.ordner(home)
        if ordner.exists():
            alt = ordner.with_name(f"{ordner.name}_alt_{stempel}")
            melden(f"Bisheriger {profil.name}-Stand kommt beiseite: {alt.name}")
            shutil.move(str(ordner), str(alt))
            beiseite.append(alt)

        for speicher in profil.speicher(home):
            if speicher.exists():
                melden(f"Zwischenspeicher wird geleert: {speicher.name}")
                shutil.rmtree(speicher, ignore_errors=True)

    melden("Sicherung wird ausgepackt ...")
    with tarfile.open(archiv, "r:gz") as paket:
        # Der Filter muss ausdrücklich gesetzt werden. Python 3.14 (Manjaro)
        # nimmt seit kurzem »data« als Vorgabe und bricht dann über
        # Verknüpfungen ab, die in jedem Vivaldi-Profil stehen; Python 3.13
        # (Debian 13) tut das noch nicht. Ohne diese Zeile liefe der Umzug
        # auf einem der beiden Rechner und auf dem anderen nicht.
        try:
            paket.extractall(path=home, filter="fully_trusted")
        except TypeError:  # Python älter als 3.12
            paket.extractall(path=home)

    melden("Eingespielt. Der alte Stand liegt als *_alt_* daneben.")
    return beiseite


def sicherungen_finden(orte: Iterable[Path]) -> list[tuple[Path, int, datetime]]:
    """Sicherungen an den angegebenen Orten suchen, neueste zuerst.

    Gesucht wird **zwei Ebenen tief**, nicht rekursiv. Das ist keine
    Bequemlichkeit, sondern notwendig: Ein ``rglob`` über das Home und jedes
    eingehängte Laufwerk lief auf dem Entwicklungsrechner minutenlang und
    ließ das Fenster einfrieren - dort hängt ein RAID mit einigen Millionen
    Dateien. Mit zwei Ebenen dauert dieselbe Suche 1,4 Sekunden.

    Zwei Ebenen reichen für den Weg, den eine Sicherung geht: direkt auf dem
    Stick, oder in einem Ordner darauf.
    """
    gefunden: dict[Path, tuple[Path, int, datetime]] = {}

    for ort in orte:
        if not ort.is_dir():
            continue
        for muster in (SUCHMUSTER, ALTES_SUCHMUSTER):
            for tiefe in ("", "*/", "*/*/"):
                try:
                    treffer = ort.glob(f"{tiefe}{muster}")
                except OSError:
                    continue
                for datei in treffer:
                    try:
                        schluessel = datei.resolve()
                        angaben = datei.stat()
                    except OSError:
                        continue
                    if schluessel in gefunden:
                        continue
                    gefunden[schluessel] = (
                        datei,
                        angaben.st_size,
                        datetime.fromtimestamp(angaben.st_mtime),
                    )

    return sorted(gefunden.values(), key=lambda eintrag: eintrag[2], reverse=True)
