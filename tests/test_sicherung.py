"""Packen und Einspielen gegen ein untergeschobenes Home.

Dies ist der Test, wegen dem die Logik von der Oberfläche getrennt ist.
Eingespielt wird in ein Verzeichnis aus ``tempfile``; das echte Profil wird
dabei nicht angefasst - was man bei einem Programm, dessen Hauptaufgabe das
Ersetzen von Profilen ist, nicht oft genug prüfen kann.
"""

from __future__ import annotations

import tarfile
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from profilkoffer import sicherung
from profilkoffer.profile import PROFILE


def _profil_anlegen(home: Path, pfad: str, inhalt: dict[str, str]) -> Path:
    ordner = home / pfad
    ordner.mkdir(parents=True, exist_ok=True)
    for name, text in inhalt.items():
        datei = ordner / name
        datei.parent.mkdir(parents=True, exist_ok=True)
        datei.write_text(text, encoding="utf-8")
    return ordner


class Home(unittest.TestCase):
    """Legt für jeden Test ein vollständiges Scheinprofil an."""

    def setUp(self) -> None:
        self._verzeichnis = tempfile.TemporaryDirectory()
        self.home = Path(self._verzeichnis.name)
        self.ziel = self.home / "stick"
        self.ziel.mkdir()

        _profil_anlegen(self.home, ".thunderbird", {"profiles.ini": "alt", "abc/key4.db": "x"})
        _profil_anlegen(self.home, ".config/vivaldi", {"Default/Bookmarks": "alte Lesezeichen"})

        # In den Tests läuft nie etwas - sonst hinge das Ergebnis davon ab,
        # ob auf dem Rechner gerade ein Browser offen ist.
        self._nichts_laeuft = mock.patch("profilkoffer.sicherung.laufende", return_value=[])
        self._nichts_laeuft.start()
        self.addCleanup(self._nichts_laeuft.stop)
        self.addCleanup(self._verzeichnis.cleanup)


class Packen(Home):
    def test_archiv_enthaelt_beide_profile(self):
        archiv = sicherung.sichern(self.ziel, self.home)
        with tarfile.open(archiv) as paket:
            namen = paket.getnames()
        self.assertIn(".thunderbird/profiles.ini", namen)
        self.assertIn(".config/vivaldi/Default/Bookmarks", namen)

    def test_name_traegt_den_zeitstempel(self):
        archiv = sicherung.sichern(self.ziel, self.home, zeitpunkt=datetime(2026, 10, 9, 8, 30, 15))
        self.assertEqual(archiv.name, "profilkoffer_20261009_083015.tar.gz")

    def test_ohne_profile_wird_abgebrochen(self):
        leer = Path(tempfile.mkdtemp())
        with self.assertRaises(sicherung.Abgebrochen):
            sicherung.sichern(self.ziel, leer)

    def test_ein_fehlgeschlagener_lauf_hinterlaesst_keine_halbe_datei(self):
        # Eine halbe Sicherung ist gefährlicher als gar keine: Sie sieht in
        # der Liste aus wie eine gültige und fällt erst beim Einspielen auf.
        with mock.patch("tarfile.TarFile.add", side_effect=OSError("Stick abgezogen")):
            with self.assertRaises(OSError):
                sicherung.sichern(self.ziel, self.home)
        self.assertEqual(list(self.ziel.glob("*.tar.gz")), [])

    def test_groesse_zaehlt_die_profile_zusammen(self):
        geschaetzt = sicherung.groesse_schaetzen(self.home)
        self.assertGreater(geschaetzt, 0)
        # »alte Lesezeichen« steckt mit drin.
        self.assertGreaterEqual(geschaetzt, len("alte Lesezeichen"))


class Einspielen(Home):
    def _fremdes_archiv(self) -> Path:
        """Eine Sicherung von einem anderen Rechner."""
        anderer = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: None)
        _profil_anlegen(anderer, ".thunderbird", {"profiles.ini": "neu"})
        _profil_anlegen(anderer, ".config/vivaldi", {"Default/Bookmarks": "neue Lesezeichen"})
        return sicherung.sichern(self.ziel, anderer)

    def test_alte_lesezeichen_sind_danach_weg(self):
        # Der Punkt, auf den es ankommt: Nach dem Einspielen darf nirgends
        # mehr der alte Stand stehen, sonst ist der Rechner nicht gleich.
        archiv = self._fremdes_archiv()
        sicherung.einspielen(archiv, self.home)

        lesezeichen = (self.home / ".config/vivaldi/Default/Bookmarks").read_text()
        self.assertEqual(lesezeichen, "neue Lesezeichen")

    def test_der_alte_stand_bleibt_daneben_liegen(self):
        archiv = self._fremdes_archiv()
        beiseite = sicherung.einspielen(
            archiv, self.home, zeitpunkt=datetime(2026, 10, 9, 8, 30, 15)
        )

        namen = {p.name for p in beiseite}
        self.assertEqual(namen, {".thunderbird_alt_20261009_083015", "vivaldi_alt_20261009_083015"})
        alt = self.home / ".config/vivaldi_alt_20261009_083015/Default/Bookmarks"
        self.assertEqual(alt.read_text(), "alte Lesezeichen")

    def test_dateien_aus_dem_alten_profil_wandern_nicht_mit(self):
        # Ein Ordner, den es nur auf diesem Rechner gibt. Nach dem Einspielen
        # darf er im Profil nicht mehr auftauchen - sonst wäre eingespielt
        # worden, aber nicht ersetzt.
        _profil_anlegen(self.home, ".config/vivaldi", {"NurHier/datei.txt": "Rest"})
        archiv = self._fremdes_archiv()
        sicherung.einspielen(archiv, self.home)

        self.assertFalse((self.home / ".config/vivaldi/NurHier").exists())

    def test_zwischenspeicher_wird_geleert(self):
        alt = self.home / ".cache/vivaldi"
        alt.mkdir(parents=True)
        (alt / "Cache").write_text("Reste vom alten Rechner")

        archiv = self._fremdes_archiv()
        sicherung.einspielen(archiv, self.home)

        self.assertFalse(alt.exists())

    def test_bricht_ab_solange_ein_programm_laeuft(self):
        archiv = self._fremdes_archiv()
        with mock.patch("profilkoffer.sicherung.laufende", return_value=["Vivaldi"]):
            with self.assertRaises(sicherung.Abgebrochen) as gefangen:
                sicherung.einspielen(archiv, self.home)
        self.assertIn("Vivaldi", str(gefangen.exception))

    def test_ruehrt_nichts_an_solange_ein_programm_laeuft(self):
        # Nicht nur abbrechen, sondern vorher abbrechen. Würde erst das
        # Profil verschoben und dann geprüft, stünde man ohne Profil da.
        archiv = self._fremdes_archiv()
        with mock.patch("profilkoffer.sicherung.laufende", return_value=["Vivaldi"]):
            with self.assertRaises(sicherung.Abgebrochen):
                sicherung.einspielen(archiv, self.home)

        self.assertEqual((self.home / ".config/vivaldi/Default/Bookmarks").read_text(),
                         "alte Lesezeichen")
        self.assertEqual(list(self.home.glob("*_alt_*")), [])

    def test_fehlendes_archiv_wird_gemeldet(self):
        with self.assertRaises(sicherung.Abgebrochen):
            sicherung.einspielen(self.ziel / "gibtesnicht.tar.gz", self.home)

    def test_verknuepfungen_im_profil_ueberstehen_den_umzug(self):
        # Vivaldi legt Verknüpfungen in seinem Profil an. Je nach
        # Python-Fassung bricht extractall darüber ab - Manjaro hat 3.14,
        # Debian 13 hat 3.13. Ohne den gesetzten Filter liefe der Umzug auf
        # einem der beiden Rechner und auf dem anderen nicht.
        anderer = Path(tempfile.mkdtemp())
        _profil_anlegen(anderer, ".config/vivaldi", {"Default/Bookmarks": "neue Lesezeichen"})
        (anderer / ".config/vivaldi/Default/Verweis").symlink_to("Bookmarks")
        archiv = sicherung.sichern(self.ziel, anderer)

        sicherung.einspielen(archiv, self.home)

        verweis = self.home / ".config/vivaldi/Default/Verweis"
        self.assertTrue(verweis.is_symlink())


class SicherungenFinden(unittest.TestCase):
    def setUp(self) -> None:
        self._verzeichnis = tempfile.TemporaryDirectory()
        self.ort = Path(self._verzeichnis.name)
        self.addCleanup(self._verzeichnis.cleanup)

    def _ablegen(self, pfad: str) -> Path:
        datei = self.ort / pfad
        datei.parent.mkdir(parents=True, exist_ok=True)
        datei.write_bytes(b"x" * 10)
        return datei

    def test_findet_direkt_und_zwei_ebenen_tief(self):
        self._ablegen("profilkoffer_20261009_080000.tar.gz")
        self._ablegen("Profil-Sync/profilkoffer_20261009_090000.tar.gz")
        self._ablegen("a/b/profilkoffer_20261009_100000.tar.gz")

        gefunden = sicherung.sicherungen_finden([self.ort])
        self.assertEqual(len(gefunden), 3)

    def test_sucht_nicht_beliebig_tief(self):
        # Die Begrenzung ist der Grund, warum die Suche 1,4 statt vieler
        # Minuten dauert. Fiele sie weg, würde dieser Test grün bleiben und
        # niemandem auffallen - deshalb steht er hier.
        self._ablegen("a/b/c/d/profilkoffer_20261009_110000.tar.gz")
        self.assertEqual(sicherung.sicherungen_finden([self.ort]), [])

    def test_findet_auch_das_alte_namensmuster(self):
        self._ablegen("profiles_backup_20261008_192356.tar.gz")
        self.assertEqual(len(sicherung.sicherungen_finden([self.ort])), 1)

    def test_neueste_zuerst(self):
        aelter = self._ablegen("profilkoffer_20261001_080000.tar.gz")
        neuer = self._ablegen("profilkoffer_20261009_080000.tar.gz")
        import os

        os.utime(aelter, (1_600_000_000, 1_600_000_000))
        os.utime(neuer, (1_700_000_000, 1_700_000_000))

        gefunden = sicherung.sicherungen_finden([self.ort])
        self.assertEqual(gefunden[0][0], neuer)

    def test_dieselbe_datei_ueber_zwei_wege_erscheint_einmal(self):
        self._ablegen("profilkoffer_20261009_080000.tar.gz")
        gefunden = sicherung.sicherungen_finden([self.ort, self.ort])
        self.assertEqual(len(gefunden), 1)

    def test_ein_ort_der_nicht_existiert_stoert_nicht(self):
        self.assertEqual(sicherung.sicherungen_finden([self.ort / "weg"]), [])


class Namensmuster(unittest.TestCase):
    def test_suchmuster_findet_das_eigene_muster(self):
        import fnmatch

        name = sicherung.MUSTER.format(stempel="20261009_083015")
        self.assertTrue(fnmatch.fnmatch(name, sicherung.SUCHMUSTER))

    def test_jedes_profil_hat_prozessnamen(self):
        # Ohne Prozessnamen greift die Sperre nicht, die das Einspielen
        # abbricht - und damit fiele die Zusage, dass der alte Stand weg ist.
        for profil in PROFILE:
            with self.subTest(profil=profil.name):
                self.assertTrue(profil.prozesse)


if __name__ == "__main__":
    unittest.main()
