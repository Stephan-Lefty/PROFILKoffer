[Deutsch](CHANGELOG.md) | [Übersicht](README.md) | [TODO](TODO.md)

# Änderungsprotokoll

Alle nennenswerten Änderungen an PROFILKoffer stehen hier.

Das Format folgt [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
die Versionsnummern folgen [Semantic Versioning](https://semver.org/lang/de/).

## 0.1.1 – 2026-11-05

### Geändert

- Das Programm erscheint jetzt in der Software-Verwaltung (GNOME
  Software, KDE Discover, Cinnamons Anwendungsverwaltung) - mit
  Beschreibung und zum Entfernen auf Knopfdruck. Dafür fehlten bisher
  die AppStream-Angaben; ohne sie kennen die Verwaltungen ein Programm
  schlicht nicht.

## [0.1.0] – 2026-10-09

Die erste Fassung. Entstanden aus einem Einzelskript, das am 08.10.2026 eine
4,5-GiB-Sicherung von Manjaro nach Debian gebracht hat – und dabei drei
Dinge zeigte, die ein Einzelskript nicht leisten kann.

### Hinzugefügt

- **Packen und Einspielen** für Thunderbird (`~/.thunderbird`) und Vivaldi
  (`~/.config/vivaldi`) in ein `tar.gz`.

- **Der alte Stand wird vollständig ersetzt.** Der bisherige Ordner wandert
  nach `<name>_alt_<Zeitstempel>`, die Zwischenspeicher werden geleert, erst
  dann wird ausgepackt. Ein Vermischen alter und neuer Lesezeichen ist damit
  ausgeschlossen – und das war der Anlass für dieses Programm.

- **Das Einspielen bricht ab, solange Thunderbird oder Vivaldi läuft.** Ein
  laufender Browser schreibt seinen Stand beim Beenden zurück und holt damit
  die alten Lesezeichen wieder. Eine Rückfrage zum Wegklicken genügt an
  dieser Stelle nicht; deshalb gibt es hier keine.

  Fehlt `pgrep`, gelten alle Programme als laufend. Die Antwort wäre sonst
  geraten, und zwar genau dort, wo Raten Daten kostet.

- **Laufwerke mit ihrem Datenträgernamen**, gelesen über `lsblk` – »NTFS-Mobil«
  statt `/run/media/stephan/89b24b6c-…`. Dazu der freie Platz.

- **Die 4-GiB-Grenze von FAT32 wird vorher geprüft.** Die Größe wird aus den
  Profilen geschätzt, das Dateisystem aus `/proc/mounts` gelesen. Ein Abbruch
  nach einer Viertelstunde mit halber Datei auf dem Stick ist die schlechteste
  aller Antworten. Bricht ein Lauf dennoch ab, wird die angefangene Datei
  gelöscht.

- **Der Filter für `tarfile.extractall` ist ausdrücklich gesetzt.** Python 3.14
  (Manjaro) nimmt seit kurzem `data` als Vorgabe und bricht über Verknüpfungen
  ab, die in jedem Vivaldi-Profil stehen; Python 3.13 (Debian 13) tut das noch
  nicht. Ohne diese Zeile liefe der Umzug in die eine Richtung und in die
  andere nicht.

- **Die Installationspakete reisen mit.** Beim Packen legt PROFILKoffer das
  `.deb` und das `.pkg.tar.zst` neben die Sicherung. Auf dem Zielrechner ist
  er noch nicht installiert; ohne ihn käme man an die Sicherung nicht heran.

- **Hilfe im Programm**, auf F1. Wer nicht weiterkommt, klickt auf Hilfe und
  sucht nicht auf GitHub nach einer README.

- **Kommandozeile** mit denselben Fähigkeiten wie die Oberfläche. Auf einem
  Rechner, dessen Arbeitsumgebung nicht mehr startet, ist sie der einzige Weg
  an die eigenen Mails.

- **Ein Symbol**, gebaut aus einer SVG-Quelle statt aus einem Pixelbild. Ein
  Koffer mit Band und Schloss; unter 64 Pixeln ohne Schriftzug, unter 48 auch
  ohne Schloss. In SPIELRaums `assets/icons.md` steht die fehlende SVG als
  offener Punkt – hier entfällt damit die Farbkorrektur von Hand. Siehe
  [assets/icons.md](assets/icons.md).

- **97 Tests**: 74 gegen ein untergeschobenes Home, elf für die Oberfläche
  unter `xvfb`, zwölf für die Symbole. Kein Test fasst ein echtes Profil an.

### Aus dem Vorläufer gelernt

Drei Fehler aus dem Einzelskript vom 08.10.2026, die hier nicht wieder
vorkommen können:

- Die Suche nach Sicherungen lief mit `**` über das ganze Home und jedes
  eingehängte Laufwerk. Auf einem Rechner mit RAID fror das Fenster
  minutenlang ein. Jetzt werden zwei Ebenen durchsucht – dieselbe Suche
  dauert 1,4 Sekunden.

- Eine Pfadberechnung warf eine Ausnahme, sobald eine Datei außerhalb des
  Home lag. Der Auswahldialog öffnete sich dann gar nicht, ohne Meldung –
  also genau dann, wenn die Sicherung auf dem Stick lag.

- Fand die Suche nichts, kam eine Fehlermeldung statt einer Auswahl. Eine
  Liste, die etwas nicht enthält, ist sonst eine Sackgasse; jetzt führt
  »Andere Datei …« zum Dateidialog.

### Noch nicht belegt

Der Weg Debian → Manjaro ist noch nicht gelaufen. Erprobt ist bisher nur
Manjaro → Debian, und das mit dem Vorläufer, nicht mit dieser Fassung.
