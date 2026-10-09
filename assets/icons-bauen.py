#!/usr/bin/env python3
"""Erzeugt alle Icon-Größen aus assets/icon.svg.

Von Hand bearbeitet wird **nur** `icon.svg`. Alles andere in diesem
Verzeichnis entsteht hier und darf überschrieben werden.

Der Grund steht in SPIELRaums `assets/icons.md` als offener Punkt: Dort
stammen alle Größen aus einem Pixelbild, und bei jeder Änderung muss die
Farbkorrektur von Hand nachgezogen werden. Mit einer SVG als Quelle fällt
dieser Schritt weg.

Zwei Fassungen, weil eine nicht für alle Größen taugt:

    16, 24, 32, 48    ohne Schriftzug und ohne Schloss (icon-klein.svg)
    64 und größer     mit Schriftzug (icon-schrift.svg)

Unter 64 Pixeln ist »PROFILKoffer« nur noch ein grauer Streifen - dieselbe
Erfahrung wie bei SPIELRaum. Das Schloss wird bei 16 Pixeln zu einem Fleck
mitten im Band und nimmt dem Koffer mehr, als es ihm gibt.

Aufruf:

    python3 assets/icons-bauen.py

Gebraucht wird `rsvg-convert` (Paket librsvg).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
QUELLE = ASSETS / "icon.svg"

KLEINE = (16, 24, 32, 48)
GROSSE = (64, 128, 256, 512, 1024)

#: So breit darf der Schriftzug werden. 820 von 1024 lässt links und rechts
#: so viel Luft wie der Koffer darüber.
SCHRIFT_BREITE = 820

#: Der Schriftzug selbst.
SCHRIFTZUG = "PROFILKoffer"

#: Die Schrift, in der gebaut wird. DejaVu Sans Bold liegt auf Debian wie
#: auf Arch; Liberation ist der Rückfall.
SCHRIFTEN = (
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/LiberationSans-Bold.ttf",
    "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)

#: Rückfallgröße, falls sich die Schrift nicht messen lässt. Gemessen für
#: DejaVu Sans Bold: »PROFILKoffer« ist dort 7,471 Zeichenbreiten lang.
SCHRIFTGROESSE_NOTFALL = 109


def schriftgroesse() -> int:
    """Die Schriftgröße, bei der der Schriftzug genau SCHRIFT_BREITE misst.

    `textLength` wäre der Weg aus der Norm, aber `rsvg-convert` setzt es
    nicht um: Der Schriftzug lief beim ersten Versuch links und rechts aus
    dem Icon heraus. Gemessen wird deshalb vorher, und in die SVG geht eine
    fertige Zahl.
    """
    try:
        from PIL import ImageFont
    except ImportError:
        return SCHRIFTGROESSE_NOTFALL

    for pfad in SCHRIFTEN:
        try:
            schrift = ImageFont.truetype(pfad, 100)
        except OSError:
            continue
        breite = schrift.getlength(SCHRIFTZUG)
        if breite:
            return int(100 * SCHRIFT_BREITE / breite)
    return SCHRIFTGROESSE_NOTFALL


def _ohne(text: str, *zeilen: str) -> str:
    for zeile in zeilen:
        text = text.replace(zeile, "")
    return text


def klein_bauen(quelle: str) -> str:
    """Die Fassung für 16 bis 48 Pixel."""
    text = quelle
    # Kräftigerer Griff: Ein 54er Strich verschwindet bei 16 Pixeln
    # zwischen zwei Pixelreihen.
    text = text.replace('stroke-width="54"', 'stroke-width="64"')
    # Schmaleres Band, damit die beiden weißen Flächen nicht gleich breit
    # werden - sonst liest sich der Koffer als Liste.
    text = text.replace(
        '<rect x="218" y="508" width="588" height="76" fill="#1668e3"/>',
        '<rect x="218" y="516" width="588" height="64" fill="#1668e3"/>',
    )
    text = _ohne(
        text,
        "  <!-- Das Schloss auf dem Band. -->\n",
        '  <rect x="462" y="486" width="100" height="120" rx="26" fill="#ffffff"/>\n',
        '  <rect x="496" y="528" width="32" height="38" rx="12" fill="#0047a7"/>\n',
    )
    return text.replace(
        "PROFILKoffer - die Quelle für alle Icon-Größen.",
        "ERZEUGT von assets/icons-bauen.py - nicht von Hand ändern.\n\n"
        "  Die Fassung für 16 bis 48 Pixel: ohne Schloss, mit kräftigerem Griff.",
    )


def schrift_bauen(quelle: str) -> str:
    """Die Fassung ab 64 Pixeln, mit Schriftzug."""
    kopf, rest = quelle.split('<rect x="36" y="36"', 1)
    grund, zeichnung = rest.split("/>", 1)
    zeichnung = zeichnung.rsplit("</svg>", 1)[0]

    # Die Zeichnung rückt nach oben und wird kleiner, damit unten Platz für
    # den Schriftzug bleibt. 0,8 um die Mitte: 512 * (1 - 0.8) = 102.4.
    neu = (
        kopf
        + '<rect x="36" y="36"'
        + grund
        + "/>\n"
        + '  <g transform="translate(102.4, 20) scale(0.8)">'
        + zeichnung.rstrip()
        + "\n  </g>\n"
        + f'  <text x="512" y="818" text-anchor="middle"\n'
        + '        font-family="DejaVu Sans, Liberation Sans, sans-serif"\n'
        + f'        font-weight="bold" font-size="{schriftgroesse()}"\n'
        + f'        fill="#ffffff">{SCHRIFTZUG}</text>\n'
        + "</svg>\n"
    )
    return neu.replace(
        "PROFILKoffer - die Quelle für alle Icon-Größen.",
        "ERZEUGT von assets/icons-bauen.py - nicht von Hand ändern.\n\n"
        "  Die Fassung ab 64 Pixeln, mit Schriftzug.",
    )


def rendern(svg: Path, groesse: int, ziel: Path) -> None:
    subprocess.run(
        ["rsvg-convert", "-w", str(groesse), "-h", str(groesse), str(svg), "-o", str(ziel)],
        check=True,
    )


def main() -> int:
    if not QUELLE.is_file():
        print(f"{QUELLE} fehlt.", file=sys.stderr)
        return 1
    try:
        subprocess.run(["rsvg-convert", "--version"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        print(
            "rsvg-convert fehlt.\n"
            "    Debian: sudo apt install librsvg2-bin\n"
            "    Arch:   sudo pacman -S librsvg",
            file=sys.stderr,
        )
        return 1

    quelle = QUELLE.read_text(encoding="utf-8")

    klein = ASSETS / "icon-klein.svg"
    schrift = ASSETS / "icon-schrift.svg"
    klein.write_text(klein_bauen(quelle), encoding="utf-8")
    schrift.write_text(schrift_bauen(quelle), encoding="utf-8")

    for groesse in KLEINE:
        rendern(klein, groesse, ASSETS / f"icon-{groesse}.png")
    for groesse in GROSSE:
        rendern(schrift, groesse, ASSETS / f"icon-{groesse}.png")

    # Das Symbol für den Desktop-Eintrag und das Fenster.
    rendern(schrift, 256, ASSETS / "icon.png")

    gebaut = sorted(KLEINE + GROSSE)
    print("Gebaut:", ", ".join(f"{g}px" for g in gebaut))
    print(f"Dazu icon.png (256), {klein.name}, {schrift.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
