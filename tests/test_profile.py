"""Welche Profile es gibt und wie erkannt wird, dass eines noch läuft."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from profilkoffer import profile


class Festlegung(unittest.TestCase):
    def test_thunderbird_und_vivaldi_sind_dabei(self):
        namen = {p.name for p in profile.PROFILE}
        self.assertEqual(namen, {"Thunderbird", "Vivaldi"})

    def test_pfade_sind_relativ_zum_home(self):
        # Absolute Pfade ließen sich nicht gegen ein untergeschobenes Home
        # testen - jeder Test schriebe dann im echten Profil herum.
        for profil in profile.PROFILE:
            with self.subTest(profil=profil.name):
                self.assertFalse(Path(profil.pfad).is_absolute())

    def test_zwischenspeicher_liegt_nicht_im_profil(self):
        # Läge er darin, würde er mitgesichert und beim Einspielen zugleich
        # ausgepackt und gelöscht - je nach Reihenfolge.
        for profil in profile.PROFILE:
            for speicher in profil.zwischenspeicher:
                with self.subTest(profil=profil.name, speicher=speicher):
                    self.assertFalse(speicher.startswith(profil.pfad))

    def test_ordner_haengt_am_uebergebenen_home(self):
        home = Path("/anderswo")
        self.assertEqual(profile.PROFILE[0].ordner(home), home / ".thunderbird")


class Vorhandene(unittest.TestCase):
    def test_findet_nur_was_da_ist(self):
        with tempfile.TemporaryDirectory() as ordner:
            home = Path(ordner)
            (home / ".thunderbird").mkdir()

            gefunden = profile.vorhandene(home)

        self.assertEqual([p.name for p in gefunden], ["Thunderbird"])

    def test_leeres_home_ergibt_nichts(self):
        with tempfile.TemporaryDirectory() as ordner:
            self.assertEqual(profile.vorhandene(Path(ordner)), ())


class Laufende(unittest.TestCase):
    def test_nichts_laeuft(self):
        leer = subprocess.CompletedProcess([], returncode=1, stdout="", stderr="")
        with mock.patch("subprocess.run", return_value=leer):
            self.assertEqual(profile.laufende(), [])

    def test_vivaldi_laeuft(self):
        def antwort(befehl, **_):
            muster = befehl[-1]
            treffer = "vivaldi" in muster
            return subprocess.CompletedProcess(
                befehl, returncode=0 if treffer else 1, stdout="4711\n" if treffer else ""
            )

        with mock.patch("subprocess.run", side_effect=antwort):
            self.assertEqual(profile.laufende(), ["Vivaldi"])

    def test_ohne_pgrep_gilt_alles_als_laufend(self):
        # Die vorsichtige Antwort. Geraten wird hier nicht: Wer »läuft
        # nicht« zurückgibt, obwohl er es nicht weiß, lässt genau an der
        # Stelle einspielen, an der Lesezeichen verlorengehen.
        with mock.patch("subprocess.run", side_effect=FileNotFoundError):
            self.assertEqual(profile.laufende(), ["Thunderbird", "Vivaldi"])

    def test_zeitueberschreitung_gilt_als_laufend(self):
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired("pgrep", 5)):
            self.assertEqual(len(profile.laufende()), 2)

    def test_muster_trifft_auch_den_bin_namen(self):
        # Im Prozessbaum heißt Vivaldi »vivaldi-bin«, nicht »vivaldi«.
        gesehen: list[str] = []

        def mitschreiben(befehl, **_):
            gesehen.append(befehl[-1])
            return subprocess.CompletedProcess(befehl, returncode=1, stdout="")

        with mock.patch("subprocess.run", side_effect=mitschreiben):
            profile.laufende()

        self.assertIn("vivaldi|vivaldi-bin", gesehen)


if __name__ == "__main__":
    unittest.main()
