"""Wechselmedien finden und benennen - so, wie sie im Dateimanager heißen.

Der Dateiauswahldialog von Tk zeigt Einhängepunkte an, und die heißen auf
einem heutigen Linux so:

    /run/media/stephan/89b24b6c-3bf3-4bb9-83dc-dcd6c94013291

Damit kann niemand etwas anfangen. Der Dateimanager zeigt an derselben
Stelle »NTFS-Mobil«, weil er den Datenträgernamen aus dem Dateisystem liest.
Dieses Modul tut dasselbe über ``lsblk`` und fällt auf den Ordnernamen
zurück, wenn ``lsblk`` nichts weiß.

Die zweite Aufgabe ist unscheinbarer und hat mehr Schaden angerichtet: das
**Dateisystem** mitzulesen. Ein Sicherungsarchiv von Thunderbird und Vivaldi
liegt schnell über vier Gigabyte, und FAT32 kann keine Datei dieser Größe.
Ohne Vorwarnung bricht das Schreiben mitten im Lauf ab - nach einer
Viertelstunde, mit einer halbfertigen Datei auf dem Stick.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

#: Was FAT32 je Datei zulässt: 4 GiB minus ein Byte. Exakt diese Zahl, nicht
#: »ungefähr 4 GB« - der Unterschied zwischen 4·10^9 und 4·2^30 ist ein
#: Zehntel Gigabyte, und darin ist schon manches Archiv steckengeblieben.
FAT32_GRENZE = 4 * 1024**3 - 1

#: Dateisysteme mit dieser Grenze. vfat ist der Name, unter dem Linux FAT16
#: und FAT32 einhängt; msdos ist der ältere Treiber.
BEGRENZTE_DATEISYSTEME = frozenset({"vfat", "msdos", "exfat_unsupported"})

#: Wo Wechselmedien üblicherweise landen. ``/run/media/<benutzer>`` ist der
#: Weg über udisks2 (KDE, GNOME), ``/media/<benutzer>`` der ältere, ``/mnt``
#: der von Hand eingehängte.
EINHAENGEPUNKTE = ("/run/media/{benutzer}", "/media/{benutzer}", "/media", "/mnt")


@dataclass(frozen=True)
class Laufwerk:
    """Ein beschreibbarer Ort, an den eine Sicherung passen könnte."""

    name: str
    pfad: Path
    frei: int
    gesamt: int
    dateisystem: str

    @property
    def begrenzt(self) -> bool:
        """Ob dieses Dateisystem bei 4 GiB je Datei aufhört."""
        return self.dateisystem in BEGRENZTE_DATEISYSTEME

    def beschriftung(self) -> str:
        """Eine Zeile für die Auswahlliste."""
        text = f"{self.name} - {self.frei / 1024**3:.1f} von {self.gesamt / 1024**3:.1f} GiB frei"
        if self.begrenzt:
            text += f"  [{self.dateisystem}: max. 4 GiB je Datei]"
        return text


def _dateisysteme() -> dict[str, str]:
    """Einhängepunkt -> Dateisystemtyp, gelesen aus /proc/mounts.

    Nicht ``df`` aufrufen: Dessen Ausgabe ist für Menschen gesetzt und
    bricht bei langen Gerätenamen um, was sich nicht zuverlässig zerlegen
    lässt. /proc/mounts ist zeilenweise und feldgetrennt.
    """
    gefunden: dict[str, str] = {}
    try:
        zeilen = Path("/proc/mounts").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return gefunden

    for zeile in zeilen:
        felder = zeile.split()
        if len(felder) < 3:
            continue
        # Oktale Maskierungen, die der Kernel für Sonderzeichen einsetzt.
        punkt = felder[1].replace("\\040", " ").replace("\\011", "\t")
        gefunden[punkt] = felder[2]
    return gefunden


def _datentraegernamen() -> dict[str, str]:
    """Einhängepunkt -> Name des Datenträgers, über lsblk.

    Genau dieser Name steht auch im Dateimanager in der Seitenleiste.
    """
    namen: dict[str, str] = {}
    try:
        fertig = subprocess.run(
            ["lsblk", "--json", "--output", "LABEL,MOUNTPOINTS"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        daten = json.loads(fertig.stdout or "{}")
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return namen

    def durchgehen(knoten: dict) -> None:
        bezeichnung = knoten.get("label")
        for punkt in knoten.get("mountpoints") or []:
            if punkt and bezeichnung:
                namen[punkt] = bezeichnung
        for kind in knoten.get("children") or []:
            durchgehen(kind)

    for knoten in daten.get("blockdevices") or []:
        durchgehen(knoten)
    return namen


def laufwerke(home: Path | None = None, benutzer: str | None = None) -> list[Laufwerk]:
    """Alle beschreibbaren Ziele, Wechselmedien zuerst, Home zuletzt.

    Das Home kommt mit in die Liste, obwohl es kein Wechselmedium ist: Wer
    keinen Stick zur Hand hat, legt die Sicherung dorthin und kopiert sie
    später. Es steht am Ende, damit es nicht versehentlich das Erste ist.
    """
    home = home or Path.home()
    benutzer = benutzer or os.environ.get("USER") or home.name

    systeme = _dateisysteme()
    namen = _datentraegernamen()

    gefunden: list[Laufwerk] = []
    gesehen: set[Path] = set()

    def aufnehmen(pfad: Path, ersatzname: str) -> None:
        try:
            aufgeloest = pfad.resolve()
        except OSError:
            return
        if aufgeloest in gesehen or not os.access(pfad, os.W_OK):
            return
        try:
            platz = shutil.disk_usage(pfad)
        except OSError:
            return
        gesehen.add(aufgeloest)
        gefunden.append(
            Laufwerk(
                name=namen.get(str(pfad)) or ersatzname,
                pfad=pfad,
                frei=platz.free,
                gesamt=platz.total,
                dateisystem=systeme.get(str(pfad), "unbekannt"),
            )
        )

    for vorlage in EINHAENGEPUNKTE:
        wurzel = Path(vorlage.format(benutzer=benutzer))
        if not wurzel.is_dir():
            continue
        try:
            eintraege = sorted(wurzel.iterdir())
        except OSError:
            continue
        for eintrag in eintraege:
            if eintrag.is_dir():
                aufnehmen(eintrag, eintrag.name)

    aufnehmen(home, "Persönlicher Ordner")
    return gefunden


def passt(laufwerk: Laufwerk, groesse: int) -> tuple[bool, str]:
    """Ob eine Sicherung dieser Größe auf das Laufwerk passt.

    Zwei Gründe, warum sie es nicht tut, und sie fühlen sich für den
    Benutzer völlig verschieden an - deshalb auch zwei verschiedene Sätze
    statt eines allgemeinen »Fehler beim Schreiben«.
    """
    if laufwerk.begrenzt and groesse > FAT32_GRENZE:
        return False, (
            f"»{laufwerk.name}« ist mit {laufwerk.dateisystem} formatiert und kann "
            f"keine Datei über 4 GiB aufnehmen. Die Sicherung wird etwa "
            f"{groesse / 1024**3:.1f} GiB groß.\n\n"
            "Nimm ein Laufwerk mit ext4, btrfs oder NTFS."
        )
    # Ein Zehntel Luft: Während des Schreibens entstehen Zwischenstände, und
    # ein randvolles Dateisystem bringt auch andere Programme in Not.
    if groesse * 1.1 > laufwerk.frei:
        return False, (
            f"Auf »{laufwerk.name}« sind {laufwerk.frei / 1024**3:.1f} GiB frei, "
            f"gebraucht werden etwa {groesse / 1024**3:.1f} GiB."
        )
    return True, ""
