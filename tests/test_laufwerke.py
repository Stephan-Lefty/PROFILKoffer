"""Laufwerke erkennen, benennen und auf Tauglichkeit prüfen.

Der Teil, der hier wirklich zählt, ist ``passt``: Ob eine Sicherung auf ein
Laufwerk geht, muss **vorher** beantwortet sein. Ein Abbruch nach einer
Viertelstunde mit halber Datei auf dem Stick ist die schlechteste aller
Antworten.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from profilkoffer import laufwerke


def _laufwerk(**abweichend) -> laufwerke.Laufwerk:
    vorgabe = dict(
        name="Linux-Mobil",
        pfad=Path("/run/media/stephan/Linux-Mobil"),
        frei=100 * 1024**3,
        gesamt=200 * 1024**3,
        dateisystem="ext4",
    )
    vorgabe.update(abweichend)
    return laufwerke.Laufwerk(**vorgabe)  # type: ignore[arg-type]


class Grenzen(unittest.TestCase):
    def test_fat32_grenze_ist_vier_gibibyte(self):
        # Nicht 4 Milliarden Byte. Der Unterschied sind 74 MB, und genau in
        # dieser Spanne bricht das Schreiben ab, wenn man falsch rechnet.
        self.assertEqual(laufwerke.FAT32_GRENZE, 4 * 1024**3 - 1)
        self.assertNotEqual(laufwerke.FAT32_GRENZE, 4_000_000_000)

    def test_vfat_gilt_als_begrenzt(self):
        self.assertTrue(_laufwerk(dateisystem="vfat").begrenzt)
        self.assertTrue(_laufwerk(dateisystem="msdos").begrenzt)

    def test_ext4_und_btrfs_sind_nicht_begrenzt(self):
        for system in ("ext4", "btrfs", "xfs", "ntfs3", "ntfs"):
            with self.subTest(dateisystem=system):
                self.assertFalse(_laufwerk(dateisystem=system).begrenzt)


class Passt(unittest.TestCase):
    def test_grosse_sicherung_passt_nicht_auf_fat32(self):
        # Genau der Fall vom 08.10.2026: 4,5 GiB auf einen vfat-Stick.
        stick = _laufwerk(dateisystem="vfat", frei=200 * 1024**3, gesamt=238 * 1024**3)
        reicht, grund = laufwerke.passt(stick, int(4.5 * 1024**3))

        self.assertFalse(reicht)
        self.assertIn("vfat", grund)
        self.assertIn("4 GiB", grund)

    def test_kleine_sicherung_passt_auch_auf_fat32(self):
        stick = _laufwerk(dateisystem="vfat")
        reicht, _ = laufwerke.passt(stick, 2 * 1024**3)
        self.assertTrue(reicht)

    def test_zu_wenig_platz_wird_gemeldet(self):
        voll = _laufwerk(frei=1 * 1024**3)
        reicht, grund = laufwerke.passt(voll, 5 * 1024**3)
        self.assertFalse(reicht)
        self.assertIn("frei", grund)

    def test_knapp_passend_gilt_als_zu_wenig(self):
        # Zehn Prozent Luft. Ein randvolles Dateisystem bringt auch andere
        # Programme in Not, nicht nur dieses.
        knapp = _laufwerk(frei=int(4.1 * 1024**3))
        reicht, _ = laufwerke.passt(knapp, 4 * 1024**3)
        self.assertFalse(reicht)

    def test_der_grund_nennt_das_laufwerk_beim_namen(self):
        # »Fehler beim Schreiben« hilft niemandem. Im Text muss stehen,
        # welcher Stick gemeint ist und was mit ihm nicht geht.
        stick = _laufwerk(name="NTFS-Mobil", dateisystem="vfat")
        _, grund = laufwerke.passt(stick, 9 * 1024**3)
        self.assertIn("NTFS-Mobil", grund)


class Beschriftung(unittest.TestCase):
    def test_zeigt_namen_und_platz(self):
        text = _laufwerk(frei=50 * 1024**3, gesamt=100 * 1024**3).beschriftung()
        self.assertIn("Linux-Mobil", text)
        self.assertIn("50.0", text)
        self.assertIn("100.0", text)

    def test_warnt_bei_begrenztem_dateisystem(self):
        text = _laufwerk(dateisystem="vfat").beschriftung()
        self.assertIn("4 GiB", text)

    def test_warnt_nicht_ohne_grund(self):
        self.assertNotIn("4 GiB", _laufwerk(dateisystem="ext4").beschriftung())


class Finden(unittest.TestCase):
    def test_home_ist_dabei_und_steht_hinten(self):
        with tempfile.TemporaryDirectory() as ordner:
            home = Path(ordner)
            gefunden = laufwerke.laufwerke(home, benutzer="niemand")

        self.assertTrue(gefunden)
        self.assertEqual(gefunden[-1].pfad, home)

    def test_unbeschreibbares_wird_uebergangen(self):
        # Eine schreibgeschützt eingehängte Platte in der Liste anzubieten
        # führt genau zu dem »Permission denied«, das sie verhindern soll.
        with tempfile.TemporaryDirectory() as ordner:
            home = Path(ordner)
            with mock.patch("os.access", return_value=False):
                self.assertEqual(laufwerke.laufwerke(home, benutzer="niemand"), [])

    def test_dateisystem_kommt_aus_proc_mounts(self):
        systeme = laufwerke._dateisysteme()
        self.assertIn("/", systeme)

    def test_leerzeichen_im_einhaengepunkt_werden_entmaskiert(self):
        # /proc/mounts schreibt ein Leerzeichen als \040. Ohne Umwandlung
        # findet sich ein Pfad wie »/mnt/eigene Daten« nie wieder.
        zeile = "/dev/sdb1 /mnt/eigene\\040Daten ext4 rw 0 0"
        with mock.patch("pathlib.Path.read_text", return_value=zeile):
            systeme = laufwerke._dateisysteme()
        self.assertEqual(systeme.get("/mnt/eigene Daten"), "ext4")

    def test_fehlendes_lsblk_wirft_nicht(self):
        with mock.patch("subprocess.run", side_effect=FileNotFoundError):
            self.assertEqual(laufwerke._datentraegernamen(), {})


if __name__ == "__main__":
    unittest.main()
