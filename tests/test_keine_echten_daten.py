"""Wacht darüber, dass nichts Persönliches ins Repository gerät.

PROFILKoffer ist quelloffen, die Profile, die damit umziehen, sind es nicht.
Ein Programm, dessen Thema Mailkonten und Lesezeichen sind, lädt dazu ein,
beim Fehlersuchen »nur kurz« einen echten Pfad einzutragen. Das steht dann
auch dann noch da, wenn man es längst entfernt hat - in der Geschichte.

Geprüft wird von der anderen Seite: nicht, ob bestimmte Adressen fehlen
(die müssten dann ja hier stehen), sondern ob **jede** Adresse im
Repository in einer kurzen, offenen Liste steht.

``.example`` ist nach RFC 2606 für Beispiele reserviert und kann niemandem
gehören. Wer eine neue Beispieladresse braucht, nimmt eine solche.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent

#: Was dastehen darf: Werkzeugkette, Norm, Anbieterdokumentation. Nichts
#: davon verrät, wer PROFILKoffer wofür einsetzt.
ERLAUBTE_ADRESSEN = {
    "github.com",
    "raw.githubusercontent.com",
    "keepachangelog.com",
    "semver.org",
    "spdx.org",
    "opensource.org",
    "www.vivaldi.com",
    "vivaldi.com",
    "www.thunderbird.net",
    "thunderbird.net",
    "docs.python.org",
    "wiki.archlinux.org",
    "www.debian.org",
    "developer.gnome.org",
}

#: Nur, was der Entwicklungsrechner ohnehin verrät. Ein Benutzername in
#: einem Beispielpfad ist das eine - eine Mailadresse das andere.
VERBOTENE_MUSTER = {
    "Mailadresse": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}"),
    "IPv4-Adresse": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

#: Was keine Mailadresse ist, auch wenn es so aussieht.
KEINE_MAILADRESSE = re.compile(
    r"""(
        \w+@\{        # Formatvorlagen wie benutzer@{host}
      | @\w+\.\w+\(   # Pythons Dekoratoren mit Punktaufruf
      | \d+\.\d+\.\d+ # Versionsnummern, von der IPv4-Regel gefangen
    )""",
    re.VERBOSE,
)

#: Dateien, die nie geprüft werden.
UEBERGANGEN = {".git", "__pycache__", ".pytest_cache", ".venv", "packaging/fertig"}

ZU_PRUEFEN = {".py", ".md", ".sh", ".toml", ".yml", ".yaml", ".desktop", ".cfg", ".txt"}


def _dateien():
    for pfad in WURZEL.rglob("*"):
        if not pfad.is_file() or pfad.suffix not in ZU_PRUEFEN:
            continue
        verhaeltnis = pfad.relative_to(WURZEL)
        if any(teil in UEBERGANGEN for teil in verhaeltnis.parts):
            continue
        if str(verhaeltnis).startswith(tuple(UEBERGANGEN)):
            continue
        yield verhaeltnis, pfad.read_text(encoding="utf-8", errors="replace")


class Adressen(unittest.TestCase):
    MUSTER = re.compile(r"https?://([\w.-]+)")

    def test_nur_erlaubte_adressen(self):
        for verhaeltnis, inhalt in _dateien():
            for wirt in self.MUSTER.findall(inhalt):
                if wirt.endswith(".example") or wirt in ("localhost", "127.0.0.1"):
                    continue
                with self.subTest(datei=str(verhaeltnis), adresse=wirt):
                    self.assertIn(
                        wirt,
                        ERLAUBTE_ADRESSEN,
                        f"{wirt} steht in {verhaeltnis} und nicht in ERLAUBTE_ADRESSEN. "
                        "Entweder gehört sie dort hinein, oder sie hat hier nichts verloren.",
                    )


class Persoenliches(unittest.TestCase):
    def test_keine_mailadressen_und_keine_ip(self):
        for verhaeltnis, inhalt in _dateien():
            for zeilennummer, zeile in enumerate(inhalt.splitlines(), start=1):
                if KEINE_MAILADRESSE.search(zeile):
                    continue
                for was, muster in VERBOTENE_MUSTER.items():
                    treffer = muster.search(zeile)
                    if treffer and not treffer.group(0).endswith(".example"):
                        with self.subTest(datei=str(verhaeltnis), zeile=zeilennummer):
                            self.fail(f"{was} »{treffer.group(0)}« in {verhaeltnis}:{zeilennummer}")

    def test_keine_echten_profildaten_mitgepackt(self):
        # Ein versehentlich eingechecktes Archiv wäre das Schlimmste, was
        # diesem Repository passieren könnte: Es enthielte Passwörter.
        gefunden = [p.name for p in WURZEL.rglob("*.tar.gz")]
        self.assertEqual(gefunden, [], "Hier liegt eine Sicherung im Repository")

    def test_keine_profildateien(self):
        for name in ("key4.db", "logins.json", "Bookmarks", "profiles.ini"):
            with self.subTest(datei=name):
                self.assertEqual(list(WURZEL.rglob(name)), [])


if __name__ == "__main__":
    unittest.main()
