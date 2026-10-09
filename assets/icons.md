# Icons

Wie aus `icon.svg` die Größen im Verzeichnis werden – damit es beim nächsten
Mal nachvollziehbar ist und nicht geraten werden muss.

## Die Kette

Von Hand bearbeitet wird **nur** `icon.svg`. Alles andere entsteht aus
[`icons-bauen.py`](icons-bauen.py) und darf überschrieben werden:

```
python3 assets/icons-bauen.py
```

| Datei | Woher |
|---|---|
| `icon.svg` | von Hand – die einzige Quelle |
| `icon-klein.svg` | erzeugt: ohne Schloss, kräftigerer Griff |
| `icon-schrift.svg` | erzeugt: Zeichnung kleiner, Schriftzug darunter |
| `icon-16.png` … `icon-1024.png` | erzeugt |
| `icon.png` | erzeugt, 256 px – für Fenster und Menüeintrag |

Gebraucht wird `rsvg-convert` (Debian `librsvg2-bin`, Arch `librsvg`). Pillow
ist nicht nötig, hilft aber – siehe unten.

## Eine SVG als Quelle, kein Pixelbild

In SPIELRaums [`icons.md`](../../SPIELRaum/assets/icons.md) steht unter »Was
noch fehlt« genau dieser Punkt: Dort stammen alle Größen aus einer gelieferten
PNG-Datei, und drei Dinge mussten von Hand nachgezogen werden – das Blau auf
die Palette holen, über tausend Rauschtöne einfangen, den weißen Rand
durchsichtig machen.

Mit einer SVG stellt sich das nicht. Die Farben stehen als Werte darin und
kommen aus [`profilkoffer/farben.py`](../profilkoffer/farben.py):

    BLAU_HELL  #0e8af6    oberes Ende des Verlaufs
    BLAU_TIEF  #0047a7    unteres Ende
    BLAU       #1668e3    das Band über dem Koffer
    WEISS      #ffffff    die Zeichnung

## Zwei Fassungen, und warum

    16, 24, 32, 48    icon-klein.svg     ohne Schriftzug, ohne Schloss
    64 und größer     icon-schrift.svg   mit beidem

**Der Schriftzug.** Unter 64 Pixeln ist »PROFILKoffer« ein grauer Streifen.
Dieselbe Erfahrung wie bei SPIELRaum; die Grenze ist von dort übernommen.

**Das Schloss.** Bei 16 Pixeln wird es zu einem Fleck mitten im Band und nimmt
dem Koffer mehr, als es ihm gibt. Es fällt deshalb bei den kleinen Größen weg.

**Der Griff.** Ein 54er Strich verschwindet bei 16 Pixeln zwischen zwei
Pixelreihen – in der kleinen Fassung sind es 64.

**Das Band.** Ohne es ist der Koffer bei kleinen Größen ein weißes Rechteck und
von einem Fenster oder einer Notiz nicht zu unterscheiden. In der kleinen
Fassung ist es schmaler, damit die beiden weißen Flächen nicht gleich breit
werden – sonst liest sich der Koffer als Liste.

## Der Schriftzug musste gemessen werden

`textLength` wäre der Weg aus der SVG-Norm. `rsvg-convert` setzt es nicht um:
Beim ersten Versuch lief »PROFILKoffer« links und rechts aus dem Icon heraus.

`icons-bauen.py` misst die Breite deshalb vorher mit Pillow und schreibt eine
fertige Schriftgröße in die SVG. Für DejaVu Sans Bold sind das **109** – der
Schriftzug ist dort 7,471 Zeichenbreiten lang, und 820 von 1024 Pixeln sollen
es werden.

Fehlt Pillow, nimmt das Skript diese 109 als festen Wert. Mit einer anderen
Schrift sitzt der Zug dann nicht genau, läuft aber nicht über.

## Wo die Icons landen

| Ort | Wodurch |
|---|---|
| `/usr/share/icons/hicolor/<größe>/apps/profilkoffer.png` | `packaging/bauen.sh` |
| `~/.local/share/icons/hicolor/<größe>/apps/profilkoffer.png` | `install.sh` |
| Fensterleiste | `profilkoffer/ui/fenster.py` setzt `iconphoto` |

Der Desktop-Eintrag zeigt auf `Icon=profilkoffer` – ohne Pfad und ohne
Endung, damit die Arbeitsumgebung die passende Größe selbst wählt.
