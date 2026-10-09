[Deutsch](umzug.md) | [English](umzug.en.md) | [Anleitungen](README.md) | [Übersicht](../README.md)

# Der Umzug, Schritt für Schritt

## Auf dem alten Rechner

**1. Thunderbird und Vivaldi schließen.**

Nicht nur das Fenster – das Programm. Vivaldi läuft mit geschlossenem
Fenster weiter, wenn im Systemabschnitt der Leiste noch sein Symbol steht.
Nachsehen lässt sich das so:

```
profilkoffer profile
```

Die letzte Zeile sagt, was läuft.

**2. Stick oder Platte anschließen.**

Das Dateisystem zählt. FAT32 nimmt keine Datei über 4 GiB an, und ein
Thunderbird-Archiv ist schnell größer. PROFILKoffer zeigt das Dateisystem in
der Laufwerksliste an und warnt vorher. Ext4, btrfs und NTFS sind unkritisch.

**3. PROFILKoffer starten, Laufwerk wählen, packen.**

Das dauert. Bei 4,5 GiB sind es einige Minuten; der Knopf heißt währenddessen
»Packen …« und ist ausgegraut. Der Verlauf darunter zeigt, wo das Programm
gerade steht.

Auf der Kommandozeile:

```
profilkoffer laufwerke
profilkoffer packen /run/media/USER/Linux-Mobil
```

**4. Nachsehen, was auf dem Laufwerk liegt.**

Es sollten drei Dateien sein:

```
profilkoffer_20261009_103000.tar.gz     die Sicherung
profilkoffer_0.1.0_all.deb              für Debian
profilkoffer-0.1.0-1-any.pkg.tar.zst    für Arch/Manjaro
```

Die beiden Pakete legt PROFILKoffer dazu, weil er auf dem anderen Rechner
noch nicht installiert ist.

## Auf dem neuen Rechner

**5. PROFILKoffer einrichten.**

```
sudo apt install /pfad/zum/stick/profilkoffer_0.1.0_all.deb        # Debian
sudo pacman -U /pfad/zum/stick/profilkoffer-0.1.0-1-any.pkg.tar.zst # Arch
```

Die Abhängigkeiten – Python, Tkinter, `util-linux`, `procps` – zieht der
Paketmanager mit.

**6. Auch hier Thunderbird und Vivaldi schließen.**

PROFILKoffer weigert sich sonst. Das ist kein Fehler, sondern der Grund,
warum der Umzug überhaupt verlässlich ist – siehe
[warum-abbruch.md](warum-abbruch.md).

**7. Sicherung wählen und auspacken.**

PROFILKoffer sucht selbst auf allen eingehängten Laufwerken, in `Downloads`,
auf dem Schreibtisch und in `Dokumente` – jeweils zwei Ebenen tief. Findet er
nichts, führt »Andere Datei …« zum Dateidialog.

Vor dem Auspacken kommt eine Rückfrage: Der bisherige Stand wird ersetzt.

Auf der Kommandozeile:

```
profilkoffer sicherungen
profilkoffer auspacken /pfad/zur/profilkoffer_20261009_103000.tar.gz --ja
```

**8. Starten und nachsehen.**

Erst die Lesezeichen prüfen, dann Vivaldi-Sync anmelden. Andersherum holt
der Dienst den alten Stand aus der Wolke zurück, und dann stehen beide
Stände nebeneinander.

## Hinterher

Der bisherige Stand liegt noch da:

```
~/.thunderbird_alt_20261009_104500
~/.config/vivaldi_alt_20261009_104500
```

Diese Ordner belegen die volle Profilgröße. Weg dürfen sie, sobald der neue
Stand nachweislich stimmt – also nachdem beide Programme einmal gelaufen
sind und die Konten abgerufen haben. Vorher nicht.
