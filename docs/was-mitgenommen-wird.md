[Deutsch](was-mitgenommen-wird.md) | [Anleitungen](README.md) | [Übersicht](../README.md)

# Was in der Sicherung steckt

## Thunderbird: `~/.thunderbird`

| Darin | Was es ist |
|---|---|
| `profiles.ini` | Welche Profile es gibt und welches benutzt wird |
| `<zufall>.default/` | Das Profil selbst |
| `key4.db` | Der Schlüsselspeicher |
| `logins.json` | Die Zugangsdaten, mit dem Schlüssel aus `key4.db` verschlüsselt |
| `prefs.js` | Alle Einstellungen, auch die Serverangaben der Konten |
| `Mail/`, `ImapMail/` | Die Nachrichten |
| `extensions/` | Erweiterungen |
| `msgFilterRules.dat` | Filter |

**Zu den Passwörtern.** `logins.json` ist mit dem Schlüssel aus `key4.db`
verschlüsselt, und `key4.db` liegt im selben Ordner. Beide ziehen zusammen
um, also funktionieren die Passwörter auf dem neuen Rechner.

Das ist zugleich die unbequeme Wahrheit über die Sicherung: Wer sie in die
Hand bekommt, hat die Zugangsdaten – außer es ist ein Hauptpasswort gesetzt.
Ein Stick mit einer Sicherung darauf ist so schützenswert wie der Rechner
selbst.

## Vivaldi: `~/.config/vivaldi`

| Darin | Was es ist |
|---|---|
| `Default/Bookmarks` | Die Lesezeichen |
| `Default/Preferences` | Einstellungen |
| `Default/Login Data` | Gespeicherte Anmeldungen |
| `Default/Extensions/` | Erweiterungen |
| `Default/Sessions/` | Offene Tabs und Fenster |
| `Default/History` | Verlauf |

## Was mit Absicht nicht mitkommt

**Die Zwischenspeicher** (`~/.cache/vivaldi`, `~/.cache/thunderbird`). Sie
sind groß, die Programme legen sie neu an – und vor allem steht darin noch
der Stand des alten Rechners. Beim Einspielen werden sie deshalb nicht nur
übergangen, sondern **gelöscht**.

**Alles, was nicht in diesen beiden Ordnern liegt.** Keine Systemeinstellungen,
keine anderen Programme, keine Dateien aus dem Home. PROFILKoffer ist kein
Sicherungsprogramm für den ganzen Rechner.

## Wie groß das wird

Fast alles davon sind die Mails. Ein Konto mit einigen Jahren Post bringt
mehrere Gigabyte mit; die erste Sicherung, die hier entstand, hatte 4,5 GiB.

PROFILKoffer schätzt die Größe vor dem Packen – aus der **unkomprimierten**
Summe. Das ist absichtlich zu viel: Mail-Archive und Datenbanken lassen sich
gut packen, oft auf die Hälfte. Lieber vorher zu viel Platz verlangen als
mittendrin stehenbleiben.

## Ob die Sicherung heil ist

Sie ist ein gewöhnliches `tar.gz` und lässt sich mit Bordmitteln ansehen:

```
tar -tzf profilkoffer_20261009_103000.tar.gz | head
tar -tzf profilkoffer_20261009_103000.tar.gz > /dev/null && echo "heil"
```

Der zweite Befehl liest das ganze Archiv durch. Bei 4,5 GiB dauert das
etwas, prüft aber jeden Block.
