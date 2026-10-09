[Deutsch](README.md) | [English](README.en.md) | [Änderungsprotokoll](CHANGELOG.md) | [TODO](TODO.md) | [Anleitungen](docs/README.md)

# PROFILKoffer

Thunderbird und Vivaldi von einem Rechner auf den anderen – mit allem, was
dazugehört.

Konten und Zugangsdaten, Lesezeichen und Erweiterungen, Filter und
Einstellungen: Alles liegt pro Programm in genau einem Ordner. PROFILKoffer
packt diesen Ordner in eine Datei, legt sie auf einen Stick und spielt sie
auf dem anderen Rechner wieder ein. Hinterher ist der Stand derselbe – nicht
ähnlich, sondern derselbe.

**Für Debian 13 und Arch/Manjaro.** Beide Systeme sind von Anfang an gemeint.
Das ist nicht selbstverständlich: Zwischen Python 3.13 (Debian) und 3.14
(Manjaro) hat sich geändert, wie Archive ausgepackt werden, und genau daran
wäre der Umzug in eine Richtung gescheitert.

## Was mitgenommen wird

| Programm | Ordner | Darin unter anderem |
|---|---|---|
| Thunderbird | `~/.thunderbird` | Konten, Passwörter (`key4.db`, `logins.json`), lokale Ordner, Filter, Erweiterungen |
| Vivaldi | `~/.config/vivaldi` | Lesezeichen, Einstellungen, Erweiterungen, Sitzungen, Schnellwahl |

Die Passwörter sind verschlüsselt, aber an nichts gebunden, was auf dem alten
Rechner bleibt. Sie überleben den Umzug.

## Der alte Stand muss weg, sonst stimmt nichts

Das ist die eine Zusage, auf der alles andere steht: Nach dem Einspielen
stehen **genau** die Lesezeichen und Konten des anderen Rechners da. Keine
alten daneben, keine doppelten, keine aus einer früheren Sitzung.

Dafür tut PROFILKoffer drei Dinge, von denen nur das erste offensichtlich
ist:

1. **Der bisherige Ordner wird beiseitegeschoben**, nicht überschrieben.
   Danach wird ausgepackt. Ein Vermischen ist damit ausgeschlossen.

2. **Die Zwischenspeicher werden geleert** (`~/.cache/vivaldi`,
   `~/.cache/thunderbird`). Dort steht noch der Stand des alten Rechners.

3. **Das Einspielen bricht ab, solange ein Programm läuft.** Ein offener
   Vivaldi hält seine Lesezeichen im Speicher und schreibt sie beim Beenden
   zurück – über alles, was gerade eingespielt wurde. Die alten Lesezeichen
   wären wieder da, und niemand wüsste, warum.

   An dieser Stelle gibt es deshalb keine Rückfrage zum Wegklicken.

Gelöscht wird nichts: Der alte Stand liegt hinterher als
`~/.thunderbird_alt_<Datum>` und `~/.config/vivaldi_alt_<Datum>` daneben.

## Einrichten

Der dauerhafte Weg führt über ein Paket:

```
packaging/bauen.sh

sudo apt install ./packaging/fertig/profilkoffer_*.deb        # Debian
sudo pacman -U packaging/fertig/profilkoffer-*.pkg.tar.zst    # Arch/Manjaro
```

Zum Ausprobieren oder auf einem fremden Rechner genügt:

```
./install.sh
```

Beides legt einen Eintrag unter *Dienstprogramme* an.

## Die Pakete reisen mit

Beim Packen legt PROFILKoffer die Installationspakete für Debian **und** für
Arch neben die Sicherung auf den Stick. Das ist kein Beiwerk: Auf dem
Zielrechner ist PROFILKoffer noch nicht installiert, und ohne ihn käme man
an die Sicherung nicht heran. Auf dem Stick liegt dann:

```
profilkoffer_20261009_103000.tar.gz     die Sicherung
profilkoffer_0.1.0_all.deb              für Debian
profilkoffer-0.1.0-1-any.pkg.tar.zst    für Arch/Manjaro
```

## Benutzen

Die Oberfläche hat zwei Knöpfe und einen Verlauf darunter. **F1** öffnet die
Hilfe – sie steht im Programm, nicht nur hier.

Dasselbe geht auf der Kommandozeile. Auf einem Rechner, dessen
Arbeitsumgebung nicht mehr startet, ist das der einzige Weg an die eigenen
Mails – und das ist genau die Lage, in der man eine Sicherung am dringendsten
braucht:

```
profilkoffer profile          was auf diesem Rechner liegt
profilkoffer laufwerke        wohin gepackt werden kann
profilkoffer packen ZIEL
profilkoffer sicherungen      was gefunden wird
profilkoffer auspacken DATEI --ja
```

## Laufwerke heißen, wie sie heißen

Der Dateiauswahldialog von Tk zeigt Einhängepunkte unter ihren
Gerätekennungen an:

```
/run/media/stephan/89b24b6c-3bf3-4bb9-83dc-dcd6c94013291
```

Der Dateimanager zeigt an derselben Stelle »NTFS-Mobil«. PROFILKoffer liest
den Datenträgernamen über `lsblk` und zeigt ihn genauso an, dazu den freien
Platz.

## Was vorher geprüft wird, statt mittendrin aufzufallen

**FAT32 nimmt keine Datei über 4 GiB an.** Ein Thunderbird-Archiv ist
schnell größer – das erste, das hier entstand, hatte 4,5 GiB. Ohne Vorwarnung
bricht das Schreiben nach einer Viertelstunde ab und hinterlässt eine halbe
Datei auf dem Stick, die in der Liste aussieht wie eine gültige Sicherung.

PROFILKoffer liest das Dateisystem aus `/proc/mounts`, schätzt die Größe
vorher und sagt es, bevor der erste Block geschrieben wird. Dasselbe gilt für
zu wenig Platz.

Bricht ein Lauf doch ab, wird die angefangene Datei gelöscht.

## Selbst daran arbeiten

```
git clone https://github.com/Stephan-Lefty/PROFILKoffer.git
cd PROFILKoffer
./install.sh
python3 -m unittest discover -s tests -v
```

Die Logik liegt in `profilkoffer/` und kennt kein Tk; die Oberfläche liegt in
`profilkoffer/ui/` und enthält keine Logik. Das ist der Grund, warum sich das
Ersetzen des Profils überhaupt prüfen lässt – die Tests spielen den ganzen
Weg gegen ein untergeschobenes Home durch, ohne ein echtes Profil anzufassen.

## Lizenz

[MIT](LICENSE)
