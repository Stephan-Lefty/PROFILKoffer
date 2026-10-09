"""Die Kommandozeile.

Sie kann dasselbe wie die Oberfläche. Das ist kein Beiwerk: Auf einem
Rechner, dessen Arbeitsumgebung nicht mehr startet, ist sie der einzige
Weg an die eigenen Mails - und das ist genau die Lage, in der man eine
Sicherung am dringendsten braucht.

    profilkoffer laufwerke
    profilkoffer packen /run/media/stephan/Linux-Mobil
    profilkoffer sicherungen
    profilkoffer auspacken /run/media/stephan/Linux-Mobil/profilkoffer_...tar.gz
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, laufwerke, sicherung
from .profile import PROFILE, laufende, vorhandene


def _melden(zeile: str) -> None:
    print(zeile, flush=True)


def main(argumente: list[str] | None = None) -> int:
    zerleger = argparse.ArgumentParser(
        prog="profilkoffer",
        description="Thunderbird und Vivaldi von einem Rechner auf den anderen.",
    )
    zerleger.add_argument("--version", action="version", version=f"PROFILKoffer {__version__}")
    befehle = zerleger.add_subparsers(dest="befehl")

    befehle.add_parser("profile", help="zeigt, was auf diesem Rechner gefunden wird")
    befehle.add_parser("laufwerke", help="zeigt die beschreibbaren Laufwerke")
    befehle.add_parser("sicherungen", help="sucht vorhandene Sicherungen")

    packen = befehle.add_parser("packen", help="sichert die Profile in ein Archiv")
    packen.add_argument("ziel", type=Path, help="Ordner, in den die Sicherung geschrieben wird")

    auspacken = befehle.add_parser("auspacken", help="spielt eine Sicherung ein")
    auspacken.add_argument("archiv", type=Path)
    auspacken.add_argument(
        "--ja",
        action="store_true",
        help="ohne Rückfrage; der bisherige Stand wird ersetzt",
    )

    gewaehlt = zerleger.parse_args(argumente)
    home = Path.home()

    if gewaehlt.befehl == "profile":
        for profil in PROFILE:
            ordner = profil.ordner(home)
            print(f"{profil.name:<14}{ordner if ordner.exists() else 'nicht eingerichtet'}")
        offen = laufende()
        print(f"\nLäuft gerade:  {', '.join(offen) if offen else 'nichts'}")
        return 0

    if gewaehlt.befehl == "laufwerke":
        for laufwerk in laufwerke.laufwerke(home):
            print(f"{laufwerk.beschriftung()}\n    {laufwerk.pfad}")
        return 0

    if gewaehlt.befehl == "sicherungen":
        orte = [l.pfad for l in laufwerke.laufwerke(home)]
        orte += [home / "Downloads", home / "Schreibtisch", home / "Dokumente"]
        gefunden = sicherung.sicherungen_finden(orte)
        if not gefunden:
            print("Keine Sicherung gefunden.")
            return 1
        for pfad, groesse, datum in gefunden:
            print(f"{datum:%d.%m.%Y %H:%M}  {groesse / 1024**3:6.2f} GiB  {pfad}")
        return 0

    if gewaehlt.befehl == "packen":
        if not gewaehlt.ziel.is_dir():
            print(f"Kein Ordner: {gewaehlt.ziel}", file=sys.stderr)
            return 2
        try:
            geschaetzt = sicherung.groesse_schaetzen(home)
            passend = [l for l in laufwerke.laufwerke(home) if l.pfad == gewaehlt.ziel]
            if passend:
                reicht, grund = laufwerke.passt(passend[0], geschaetzt)
                if not reicht:
                    print(grund, file=sys.stderr)
                    return 1
            archiv = sicherung.sichern(gewaehlt.ziel, home, _melden)
        except sicherung.Abgebrochen as grund:
            print(grund, file=sys.stderr)
            return 1
        print(archiv)
        return 0

    if gewaehlt.befehl == "auspacken":
        if not gewaehlt.ja:
            print(
                "Der bisherige Stand von Thunderbird und Vivaldi wird ersetzt.\n"
                "Die alten Profile bleiben als *_alt_<Datum> liegen.\n"
                "Zum Ausführen: --ja anhängen.",
                file=sys.stderr,
            )
            return 1
        try:
            sicherung.einspielen(gewaehlt.archiv, home, _melden)
        except sicherung.Abgebrochen as grund:
            print(grund, file=sys.stderr)
            return 1
        return 0

    # Ohne Befehl: die Oberfläche. Das ist der übliche Weg; der
    # Desktop-Eintrag ruft das Programm ohne Argumente auf.
    if not vorhandene(home):
        print("Weder Thunderbird noch Vivaldi gefunden.", file=sys.stderr)
    from .ui.fenster import main as fenster_main

    return fenster_main()


if __name__ == "__main__":
    raise SystemExit(main())
