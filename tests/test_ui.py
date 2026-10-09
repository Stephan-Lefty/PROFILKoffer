"""Die Oberfläche baut sich auf und bedient sich.

Diese Tests brauchen einen Grafikserver. In der CI läuft deshalb ``xvfb``;
sie dort stillschweigend zu überspringen wäre schlimmer als sie wegzulassen -
ein übersprungener Test sieht im Protokoll aus wie ein bestandener.

Geprüft wird nicht, wie das Fenster aussieht, sondern dass es sich bauen
lässt und dass die Sperren greifen: ohne Ziel kein Packen, ohne Sicherung
kein Auspacken.
"""

from __future__ import annotations

import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest import mock

try:
    _probe = tk.Tk()
    _probe.destroy()
    TK_LAEUFT = True
except Exception:  # noqa: BLE001 - jeder Grund zählt gleich
    TK_LAEUFT = False


@unittest.skipUnless(TK_LAEUFT, "kein Grafikserver")
class Aufbau(unittest.TestCase):
    def setUp(self) -> None:
        self._verzeichnis = tempfile.TemporaryDirectory()
        self.home = Path(self._verzeichnis.name)
        (self.home / ".thunderbird").mkdir()

        self.wurzel = tk.Tk()
        self.wurzel.withdraw()
        self.addCleanup(self.wurzel.destroy)
        self.addCleanup(self._verzeichnis.cleanup)

        from profilkoffer.ui.fenster import Fenster

        self.fenster = Fenster(self.wurzel, home=self.home)

    def test_fenster_baut_sich_auf(self):
        self.assertEqual(self.wurzel.title(), "PROFILKoffer")

    def test_uebersicht_nennt_beide_programme(self):
        gefunden = self._alle_beschriftungen()
        self.assertTrue(any("Thunderbird" in t for t in gefunden))
        self.assertTrue(any("Vivaldi" in t for t in gefunden))

    def test_packen_ohne_ziel_meldet_und_startet_nicht(self):
        with mock.patch("tkinter.messagebox.showerror") as gemeldet:
            with mock.patch("threading.Thread") as strang:
                self.fenster._packen()
        gemeldet.assert_called_once()
        strang.assert_not_called()

    def test_auspacken_ohne_sicherung_meldet_und_startet_nicht(self):
        with mock.patch("tkinter.messagebox.showerror") as gemeldet:
            with mock.patch("threading.Thread") as strang:
                self.fenster._auspacken()
        gemeldet.assert_called_once()
        strang.assert_not_called()

    def test_auspacken_fragt_vor_dem_ersetzen(self):
        # Ohne Zustimmung darf kein Strang starten. Das Ersetzen ist der
        # einzige Schritt in diesem Programm, der etwas wegnimmt.
        self.fenster.archiv = self.home / "irgendeine.tar.gz"
        with mock.patch("tkinter.messagebox.askyesno", return_value=False) as gefragt:
            with mock.patch("threading.Thread") as strang:
                self.fenster._auspacken()
        gefragt.assert_called_once()
        strang.assert_not_called()

    def test_protokoll_nimmt_zeilen_auf(self):
        self.fenster.schreiben("Eine Zeile")
        inhalt = self.fenster.protokoll.get("1.0", tk.END)
        self.assertIn("Eine Zeile", inhalt)

    def test_protokoll_laesst_sich_nicht_beschreiben(self):
        # Ein Verlaufsfeld, in das man hineintippen kann, verwirrt - und
        # der Text darin sähe aus wie eine Meldung des Programms.
        self.assertEqual(str(self.fenster.protokoll.cget("state")), "disabled")

    def test_hilfe_oeffnet_sich(self):
        from profilkoffer.ui import hilfe

        hilfe.zeigen(self.wurzel)
        self.wurzel.update_idletasks()
        fenster = [k for k in self.wurzel.winfo_children() if isinstance(k, tk.Toplevel)]
        self.assertTrue(fenster)

    def _alle_beschriftungen(self) -> list[str]:
        gefunden: list[str] = []

        def durchgehen(knoten: tk.Misc) -> None:
            for kind in knoten.winfo_children():
                try:
                    gefunden.append(str(kind.cget("text")))
                except tk.TclError:
                    pass
                durchgehen(kind)

        durchgehen(self.wurzel)
        return gefunden


@unittest.skipUnless(TK_LAEUFT, "kein Grafikserver")
class Hilfetext(unittest.TestCase):
    def test_nennt_die_sperre_beim_auspacken(self):
        # Die Hilfe muss erklären, warum das Programm sich weigert -
        # sonst hält man die Weigerung für einen Fehler.
        from profilkoffer.ui import hilfe

        self.assertIn("Vivaldi noch läuft", hilfe.TEXT)

    def test_nennt_wo_der_alte_stand_bleibt(self):
        from profilkoffer.ui import hilfe

        self.assertIn("_alt_", hilfe.TEXT)

    def test_nennt_die_fat32_grenze(self):
        from profilkoffer.ui import hilfe

        self.assertIn("4 GiB", hilfe.TEXT)


if __name__ == "__main__":
    unittest.main()
