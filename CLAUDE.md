# PROFILKoffer

Thunderbird und Vivaldi von einem Rechner auf den anderen. Zwei Zielsysteme:
Debian 13 und Arch/Manjaro, beide gleichrangig.

## Die Zusage

Nach dem Einspielen steht **genau** der Stand des anderen Rechners da. Keine
alten Lesezeichen daneben, keine doppelten Konten. Das ist der einzige Grund,
warum dieses Programm existiert – alles andere ist Beiwerk.

Drei Dinge tragen sie, und keines davon darf still wegfallen:

1. Der bisherige Ordner wird **verschoben**, nicht überschrieben
   (`<name>_alt_<Zeitstempel>`). Danach wird ausgepackt.
2. Die Zwischenspeicher werden **gelöscht**. Dort steht der alte Stand.
3. Das Einspielen **bricht ab**, solange ein Programm läuft – ohne Rückfrage.
   Ein laufender Vivaldi schreibt beim Beenden seinen Stand zurück.

Wer an `sicherung.einspielen` arbeitet: Die Reihenfolge ist nicht beliebig.
Erst prüfen, dann anfassen. Würde erst verschoben und dann geprüft, stünde
man bei einem Abbruch ohne Profil da.

## Aufbau

| Datei | Wofür |
|---|---|
| `profilkoffer/profile.py` | Welche Profile es gibt, wo sie liegen, ob sie laufen |
| `profilkoffer/sicherung.py` | Packen, Einspielen, Sicherungen finden |
| `profilkoffer/laufwerke.py` | Wechselmedien, Datenträgernamen, Platz- und FAT32-Prüfung |
| `profilkoffer/farben.py` | Die Palette aus MailBurg, unverändert übernommen |
| `profilkoffer/ui/` | Tk-Oberfläche – **hier steht keine Logik** |
| `profilkoffer/__main__.py` | Kommandozeile |

Die Trennung ist kein Selbstzweck: Der gefährliche Teil – das Ersetzen des
Profils – lässt sich nur prüfen, wenn er ohne Bildschirm aufrufbar ist. Jede
Funktion in `sicherung.py` nimmt das Home als Argument entgegen, damit die
Tests ein eigenes unterschieben können.

## Regeln aus Fehlern

- **Nicht rekursiv suchen.** `rglob` über das Home und die eingehängten
  Laufwerke lief auf dem Entwicklungsrechner minutenlang (dort hängt ein
  RAID). Zwei Ebenen genügen und brauchen 1,4 Sekunden.

- **`filter=` bei `extractall` setzen.** Python 3.13 und 3.14 haben
  verschiedene Vorgaben. Ohne die Angabe läuft der Umzug auf einem der
  beiden Zielsysteme und auf dem anderen nicht.

- **Niemals raten, ob ein Programm läuft.** Fehlt `pgrep`, gelten alle als
  laufend. Die bequeme Antwort kostet an dieser Stelle Lesezeichen.

- **Größen in GiB rechnen, nicht in GB.** Die FAT32-Grenze liegt bei
  4·2³⁰−1, nicht bei 4·10⁹. Dazwischen liegen 74 MB, in denen Archive
  steckenbleiben.

- **Keine halben Dateien hinterlassen.** Bricht das Packen ab, wird die
  angefangene Datei gelöscht. Sie sähe in der Auswahlliste aus wie eine
  gültige Sicherung.

## Stil

Deutsche Prosa in Kommentaren und Docstrings, englische Bezeichner nur, wo
die Sprache sie vorgibt. Kommentare erklären das **Warum**; was der Code tut,
steht im Code.

Keine Abhängigkeit aus PyPI. Was gebraucht wird, bringt Python mit oder das
System (`lsblk`, `pgrep`). Tkinter kommt aus der Distribution.

## Was noch niemand belegt hat

- Der Weg Debian → Manjaro ist nicht gelaufen. Nur Manjaro → Debian, und das
  mit dem Vorläuferskript.
- Keine echte Sicherung über 4 GiB mit dieser Fassung. Die Tests arbeiten
  mit Profilen aus `tempfile`.
