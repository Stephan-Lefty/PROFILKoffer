"""Die Symbole: vollständig, richtig groß, und aus der aktuellen Quelle.

Der letzte Punkt ist der eigentliche Grund für diese Datei. `icon.svg` wird
von Hand bearbeitet, alles andere erzeugt `assets/icons-bauen.py`. Wer die
Quelle ändert und das Skript nicht laufen lässt, hat im Repository ein Icon,
das anders aussieht als seine Quelle – und merkt es erst, wenn jemand ein
Paket baut.

Die Größe eines PNG wird aus dem IHDR-Block gelesen, nicht mit Pillow:
PROFILKoffer hat keine Abhängigkeit aus PyPI, und dafür eine einzuführen
wäre ein schlechter Tausch.
"""

from __future__ import annotations

import struct
import unittest
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

GROESSEN = (16, 24, 32, 48, 64, 128, 256, 512, 1024)

#: Die Werte aus profilkoffer/farben.py, die in der SVG stehen müssen.
#: Steht hier ein anderes Blau, ist das Icon aus der Familie gefallen.
PALETTE = ("#0e8af6", "#0047a7", "#1668e3", "#ffffff")


def _png_groesse(pfad: Path) -> tuple[int, int]:
    """Breite und Höhe aus dem IHDR-Block."""
    daten = pfad.read_bytes()
    if daten[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{pfad.name} ist kein PNG")
    breite, hoehe = struct.unpack(">II", daten[16:24])
    return breite, hoehe


class Quelle(unittest.TestCase):
    def test_icon_svg_ist_da(self):
        self.assertTrue((ASSETS / "icon.svg").is_file())

    def test_farben_stammen_aus_der_palette(self):
        from profilkoffer import farben

        inhalt = (ASSETS / "icon.svg").read_text(encoding="utf-8")
        for wert in PALETTE:
            with self.subTest(farbe=wert):
                self.assertIn(wert, inhalt)

        # Und umgekehrt: Die Werte in der SVG sind dieselben wie im Modul.
        self.assertEqual(farben.ICON_VERLAUF, (farben.BLAU_HELL, farben.BLAU_TIEF))
        self.assertIn(farben.BLAU_HELL, inhalt)
        self.assertIn(farben.BLAU_TIEF, inhalt)


class Groessen(unittest.TestCase):
    def test_alle_groessen_liegen_vor(self):
        for groesse in GROESSEN:
            with self.subTest(groesse=groesse):
                self.assertTrue((ASSETS / f"icon-{groesse}.png").is_file())

    def test_jedes_png_ist_so_gross_wie_sein_name(self):
        for groesse in GROESSEN:
            pfad = ASSETS / f"icon-{groesse}.png"
            with self.subTest(groesse=groesse):
                self.assertEqual(_png_groesse(pfad), (groesse, groesse))

    def test_icon_png_fuer_fenster_und_menue(self):
        self.assertEqual(_png_groesse(ASSETS / "icon.png"), (256, 256))


class Aktuell(unittest.TestCase):
    """Die erzeugten SVGs müssen zur Quelle passen.

    Verglichen wird gegen das, was `icons-bauen.py` aus der aktuellen
    `icon.svg` machen würde. Schlägt das fehl, wurde die Quelle geändert,
    ohne das Skript laufen zu lassen:

        python3 assets/icons-bauen.py
    """

    def setUp(self) -> None:
        import importlib.machinery
        import importlib.util

        pfad = ASSETS / "icons-bauen.py"
        lader = importlib.machinery.SourceFileLoader("icons_bauen", str(pfad))
        spezifikation = importlib.util.spec_from_loader("icons_bauen", lader)
        self.bauen = importlib.util.module_from_spec(spezifikation)
        spezifikation.loader.exec_module(self.bauen)
        self.quelle = (ASSETS / "icon.svg").read_text(encoding="utf-8")

    def test_kleine_fassung_ist_aktuell(self):
        erwartet = self.bauen.klein_bauen(self.quelle)
        vorhanden = (ASSETS / "icon-klein.svg").read_text(encoding="utf-8")
        self.assertEqual(vorhanden, erwartet, "icons-bauen.py wurde nicht neu ausgeführt")

    def test_schriftfassung_ist_aktuell(self):
        erwartet = self.bauen.schrift_bauen(self.quelle)
        vorhanden = (ASSETS / "icon-schrift.svg").read_text(encoding="utf-8")
        self.assertEqual(vorhanden, erwartet, "icons-bauen.py wurde nicht neu ausgeführt")

    def test_die_kleine_fassung_traegt_kein_schloss(self):
        # Das Schloss wird bei 16 Pixeln zu einem Fleck mitten im Band.
        klein = self.bauen.klein_bauen(self.quelle)
        self.assertNotIn("Das Schloss", klein)

    def test_die_schriftfassung_traegt_den_namen(self):
        schrift = self.bauen.schrift_bauen(self.quelle)
        self.assertIn("PROFILKoffer</text>", schrift)

    def test_der_schriftzug_passt_ins_icon(self):
        # rsvg-convert setzt textLength nicht um; beim ersten Versuch lief
        # der Zug links und rechts heraus. Die Groesse wird deshalb
        # gemessen - hier wird geprueft, dass dabei nichts Unsinniges
        # herauskommt.
        groesse = self.bauen.schriftgroesse()
        self.assertGreater(groesse, 60)
        self.assertLess(groesse, 160)


class Verwendung(unittest.TestCase):
    def test_desktop_eintrag_zeigt_auf_den_namen_ohne_pfad(self):
        # Mit Pfad und Endung sucht die Arbeitsumgebung keine passende
        # Groesse aus, sondern skaliert eine einzige Datei.
        eintrag = (ASSETS.parent / "desktop" / "profilkoffer.desktop").read_text(encoding="utf-8")
        self.assertIn("Icon=profilkoffer\n", eintrag)

    def test_das_fenster_sucht_an_den_richtigen_stellen(self):
        from profilkoffer.ui import fenster

        orte = [str(o) for o in fenster.SYMBOL_ORTE]
        self.assertTrue(any(o.startswith("/usr/share/icons/hicolor") for o in orte))
        self.assertTrue(any(o.endswith("assets/icon-128.png") for o in orte))


if __name__ == "__main__":
    unittest.main()
