"""Die Farbpalette – Form der Werte, Kontraste, Vollständigkeit."""

from __future__ import annotations

import re
import unittest

from profilkoffer import farben


def _palette() -> dict[str, str]:
    """Alle Farbkonstanten des Moduls."""
    return {
        name: wert
        for name, wert in vars(farben).items()
        if name.isupper() and isinstance(wert, str) and wert.startswith("#")
    }


class Form(unittest.TestCase):
    def test_alle_werte_sind_sechsstellige_hexwerte(self):
        for name, wert in _palette().items():
            with self.subTest(name=name):
                self.assertRegex(wert, r"^#[0-9a-f]{6}$")

    def test_keine_farbe_doppelt(self):
        werte = list(_palette().values())
        self.assertEqual(len(werte), len(set(werte)))

    def test_palette_ist_nicht_leer(self):
        self.assertGreaterEqual(len(_palette()), 15)

    def test_rgb(self):
        self.assertEqual(farben.rgb("#1668e3"), (22, 104, 227))
        self.assertEqual(farben.rgb("#fff"), (255, 255, 255))

    def test_rgb_lehnt_unsinn_ab(self):
        for falsch in ("blau", "#12345", "#gggggg"):
            with self.subTest(wert=falsch):
                with self.assertRaises(ValueError):
                    farben.rgb(falsch)


def _mischen(vorne: str, hinten: str, anteil: float) -> str:
    """Was `color-mix(in srgb, vorne <anteil>%, hinten)` ergibt.

    In sRGB gemischt heißt: die Kanalwerte linear zwischen beiden Farben,
    ohne Umweg über den Linearraum. Genau das tut der Browser bei
    `in srgb`, und nur deshalb darf hier so einfach gerechnet werden.
    """
    v, h = farben.rgb(vorne), farben.rgb(hinten)
    kanäle = (round(v[i] * anteil + h[i] * (1 - anteil)) for i in range(3))
    return "#" + "".join(f"{k:02x}" for k in kanäle)


class Kontraste(unittest.TestCase):
    """WCAG 2.1 verlangt 4.5 für Fließtext und 3.0 für große Schrift.

    Bei einem Werkzeug, das neben einem Programm für blinde und motorisch
    eingeschränkte Nutzer entsteht, sollte das nicht nur eine Zahl in einer
    Norm sein. Deshalb steht die Prüfung hier und nicht in einer Anleitung.
    """

    def test_weiss_auf_blau(self):
        # Das Icon: weiße Zeichnung auf blauem Grund.
        self.assertGreater(farben.kontrast(farben.WEISS, farben.BLAU), 4.5)
        self.assertGreater(farben.kontrast(farben.WEISS, farben.BLAU_TIEF), 4.5)

    def test_fliesstext_im_hellen_thema(self):
        self.assertGreater(farben.kontrast(farben.GRAU, farben.GRAU_PAPIER), 4.5)
        self.assertGreater(farben.kontrast(farben.GRAU_DUNKEL, farben.WEISS), 4.5)

    def test_fliesstext_im_dunklen_thema(self):
        self.assertGreater(farben.kontrast(farben.GRAU_HELL, farben.GRAU_NACHT), 4.5)
        self.assertGreater(farben.kontrast(farben.GRAU_HELL, farben.GRAU_KOHLE), 4.5)

    def test_verweise_sind_lesbar(self):
        self.assertGreater(farben.kontrast(farben.BLAU, farben.GRAU_PAPIER), 4.5)
        # Auf dunklem Grund braucht es das helle Blau; das dunkle wäre zu leise.
        self.assertGreater(farben.kontrast(farben.BLAU_LEUCHT, farben.GRAU_NACHT), 4.5)

    def test_signalfarben_sind_lesbar(self):
        self.assertGreater(farben.kontrast(farben.ROT, farben.GRAU_PAPIER), 4.5)
        self.assertGreater(farben.kontrast(farben.GRUEN, farben.GRAU_PAPIER), 4.5)
        self.assertGreater(farben.kontrast(farben.ROT_HELL, farben.GRAU_NACHT), 4.5)
        self.assertGreater(farben.kontrast(farben.GRUEN_HELL, farben.GRAU_NACHT), 4.5)

    def test_zweitangaben_sind_lesbar(self):
        # Zurückgenommener Text braucht je Thema einen eigenen Ton. GRAU_MITTE
        # auf hellem Grund erreicht nur 2,48 und verfehlt damit sogar die 3,0
        # für große Schrift - deshalb gibt es GRAU_LEISE. Der Fehler stand in
        # der übernommenen Palette und ist erst hier aufgefallen.
        self.assertGreater(farben.kontrast(farben.GRAU_LEISE, farben.GRAU_PAPIER), 4.5)
        self.assertGreater(farben.kontrast(farben.GRAU_MITTE, farben.GRAU_NACHT), 4.5)

    def test_die_warnleiste_ist_in_beiden_themen_lesbar(self):
        # Die Leiste unter dem Kopf, die stehen bleibt, solange der Denker
        # nicht antwortet. Ihr Grund ist in der CSS ein `color-mix`: zwölf
        # Prozent Rot in der Fläche. Getönte Gründe sind die Stelle, an der
        # ein Kontrast unbemerkt wegrutscht - am Bildschirm sieht rosa immer
        # harmlos aus.
        hell = _mischen(farben.ROT, farben.WEISS, 0.12)
        self.assertGreater(farben.kontrast(farben.GRAU_DUNKEL, hell), 4.5)
        dunkel = _mischen(farben.ROT_HELL, farben.GRAU_KOHLE, 0.12)
        self.assertGreater(farben.kontrast(farben.GRAU_HELL, dunkel), 4.5)

    def test_grau_mitte_taugt_nicht_fuer_hellen_grund(self):
        # Hält den Grund fest, warum es zwei Töne gibt. Wer GRAU_MITTE hier
        # einsetzt, macht Text unlesbar, ohne dass es auffällt.
        self.assertLess(farben.kontrast(farben.GRAU_MITTE, farben.GRAU_PAPIER), 3.0)

    def test_kontrast_ist_symmetrisch(self):
        a = farben.kontrast(farben.WEISS, farben.BLAU)
        b = farben.kontrast(farben.BLAU, farben.WEISS)
        self.assertAlmostEqual(a, b, places=10)

    def test_gleiche_farbe_hat_kontrast_eins(self):
        self.assertAlmostEqual(farben.kontrast(farben.BLAU, farben.BLAU), 1.0)

    def test_schwarz_auf_weiss_ist_das_hoechste(self):
        self.assertAlmostEqual(farben.kontrast("#000000", "#ffffff"), 21.0, places=1)


class Oberflaeche(unittest.TestCase):
    """Die Paarungen, die im Fenster tatsächlich vorkommen.

    Die allgemeinen Kontrastprüfungen oben sagen, dass die Palette taugt.
    Sie sagen nicht, dass sie auch richtig eingesetzt wird - ein weißer
    Text auf grauem Knopf besteht keine davon und sieht am Bildschirm
    trotzdem erst einmal normal aus.
    """

    def test_kopfzeile(self):
        # Weiß auf Blau, die Leiste über dem Fenster.
        self.assertGreater(farben.kontrast(farben.WEISS, farben.BLAU), 4.5)

    def test_knopfbeschriftungen(self):
        # Beide Knopffarben tragen weiße Schrift.
        for grund in (farben.BLAU, farben.GRAU, farben.BLAU_DUNKEL):
            with self.subTest(grund=grund):
                self.assertGreater(farben.kontrast(farben.WEISS, grund), 4.5)

    def test_verlauf_und_pfadfelder(self):
        # Protokollfeld, Pfadanzeigen, Hilfetext: dunkles Grau auf Weiß.
        self.assertGreater(farben.kontrast(farben.GRAU_DUNKEL, farben.WEISS), 4.5)

    def test_beschriftungen_auf_dem_seitengrund(self):
        self.assertGreater(farben.kontrast(farben.GRAU_DUNKEL, farben.GRAU_PAPIER), 4.5)

    def test_hilfeverweis(self):
        # Der Hilfe-Knopf ist flach und trägt blaue Schrift auf dem
        # Seitengrund - der einzige Text im Fenster, der nicht grau ist.
        self.assertGreater(farben.kontrast(farben.BLAU, farben.GRAU_PAPIER), 4.5)

    def test_ausgegrauter_knopf_bleibt_erkennbar(self):
        # Während des Packens steht »Packen ...« auf ausgegrautem Knopf.
        # Lesbar muss er bleiben, sonst sieht es aus wie ein Absturz.
        # 3.0 genügt: Der Text ist fett und zählt als große Schrift.
        self.assertGreater(farben.kontrast(farben.GRAU_HELL, farben.BLAU), 3.0)
