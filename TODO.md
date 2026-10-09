[Deutsch](TODO.md) | [English](TODO.en.md) | [Übersicht](README.md) | [Änderungsprotokoll](CHANGELOG.md)

# TODO

Laufende Liste offener Punkte. Oben steht, was noch offen ist. Erledigtes
wird nicht gelöscht, sondern nach unten verschoben – mit dem Datum, an dem
es fertig wurde.

## Offen

- [ ] **Den Weg Debian → Manjaro einmal gehen.** Erprobt ist bisher nur die
  andere Richtung, und das mit dem Vorläuferskript. Solange das nicht
  gelaufen ist, steht im README eine Zusage, die niemand nachgeprüft hat.

- [ ] **Eine echte Sicherung mit dieser Fassung ziehen.** Die Tests laufen
  gegen Profile aus `tempfile`, nicht gegen 4,5 GiB echte Mails. Was bei
  dieser Größe anders ist: die Dauer, der Platzbedarf beim Auspacken und
  die Frage, ob das Fenster über Minuten hinweg ansprechbar bleibt.

- [ ] **Ein Symbol.** Der Desktop-Eintrag zeigt auf `Icon=profilkoffer`, und
  das gibt es noch nicht – im Menü steht ein Platzhalter. Die Farben stehen
  schon fest ([profilkoffer/farben.py](profilkoffer/farben.py)).

- [ ] **Firefox und Chromium aufnehmen?** Die Profile liegen genauso in
  einem Ordner. Offen ist nicht das Wie, sondern ob das Programm dadurch
  unübersichtlich wird – bei zwei Programmen braucht es keine Auswahl, bei
  fünf schon.

- [ ] **Platz vor dem Auspacken prüfen.** Vor dem Packen wird geprüft, vor
  dem Auspacken nicht. Ein Archiv von 4,5 GiB braucht beim Auspacken ein
  Mehrfaches davon, und das alte Profil liegt zu dem Zeitpunkt noch daneben.

- [ ] **Die alten `*_alt_*`-Ordner anbieten zu löschen.** Sie sammeln sich
  bei jedem Einspielen an und belegen jeweils die volle Profilgröße.
  Löschen darf das Programm nicht von selbst – fragen schon.

## Erledigt

- [x] **Aus dem Einzelskript ein Programm machen.** 09.10.2026. Logik von
  der Oberfläche getrennt, 85 Tests, CI, Pakete für beide Systeme.
