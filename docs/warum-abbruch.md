[Deutsch](warum-abbruch.md) | [Anleitungen](README.md) | [Übersicht](../README.md)

# Warum das Einspielen abbricht, solange ein Browser läuft

Die Meldung lautet:

```
Vivaldi läuft noch.

Ein laufendes Programm schreibt seinen bisherigen Stand beim Beenden
zurück und überschreibt damit alles, was gerade eingespielt wurde -
die alten Lesezeichen wären wieder da.
```

Das sieht aus wie Vorsicht und ist eine Notwendigkeit.

## Was passiert, wenn man es doch tut

Vivaldi hält seine Lesezeichen nicht auf der Platte, sondern im Speicher.
Die Datei `~/.config/vivaldi/Default/Bookmarks` ist eine Abschrift, die beim
Beenden und in Abständen neu geschrieben wird.

Spielt man ein, während Vivaldi läuft, geschieht Folgendes:

1. PROFILKoffer schiebt `~/.config/vivaldi` beiseite und packt den neuen
   Stand aus. Auf der Platte stehen jetzt die neuen Lesezeichen.
2. Vivaldi merkt davon nichts – es hat die alten im Speicher.
3. Beim Beenden schreibt Vivaldi seinen Stand. Die neuen Lesezeichen sind
   weg, die alten stehen wieder da.

Das Tückische daran: Es sieht nicht nach einem Fehler aus. Der Umzug meldet
Erfolg, und erst Tage später fällt auf, dass ein Lesezeichen fehlt. Zu dem
Zeitpunkt weiß niemand mehr, woran es lag.

Bei Thunderbird dasselbe mit den Konten, zusätzlich mit dem Risiko einer
halb geschriebenen Datenbank.

## Warum keine Rückfrage

Eine Rückfrage mit »Trotzdem fortfahren?« wäre bequemer. Sie hätte aber
genau eine Wirkung: Irgendwann klickt man sie weg, weil man es eilig hat,
und bekommt stillschweigend das Ergebnis von oben.

Beim **Packen** gibt es die Rückfrage – dort ist der Schaden kleiner. Eine
Sicherung aus einem laufenden Programm kann eine halbfertige Datenbank
enthalten; das fällt beim Einspielen auf, und man zieht eine neue. Beim
**Einspielen** fällt es nicht auf.

## Wenn Vivaldi gar nicht läuft und es trotzdem meldet

Vivaldi läuft mit geschlossenem Fenster weiter, wenn im Systemabschnitt der
Leiste noch sein Symbol steht. Nachsehen:

```
profilkoffer profile
```

Hilft das nicht:

```
pgrep -a vivaldi
pgrep -a thunderbird
```

Steht dort ein Prozess, der nicht weggehen will, beendet ihn
`pkill vivaldi`. Danach noch einmal nachsehen – erst wenn `pgrep` nichts
mehr meldet, lässt PROFILKoffer einspielen.

## Wenn pgrep fehlt

Dann gelten alle Programme als laufend, und das Einspielen bricht immer ab.
Das ist Absicht: Die Antwort »läuft nicht« wäre geraten, und zwar an der
Stelle, an der Raten Lesezeichen kostet.

```
sudo apt install procps       # Debian
sudo pacman -S procps-ng      # Arch/Manjaro
```
