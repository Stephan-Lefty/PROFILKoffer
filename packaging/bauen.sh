#!/usr/bin/env bash
#
# Baut die Installationspakete für Debian (.deb) und Arch/Manjaro
# (.pkg.tar.zst) und legt sie in packaging/fertig ab.
#
# Besonderheit: Jedes Paket enthält **beide** Installer unter
# /usr/share/profilkoffer. Das klingt nach Doppelung und hat einen Grund -
# auf dem Zielrechner ist PROFILKoffer noch nicht installiert. Die
# Sicherung allein nützt dort nichts; man käme nicht an sie heran. Deshalb
# legt das Programm beim Packen die Installer neben die Sicherung auf den
# Stick.
#
# Gebaut wird in zwei Durchgängen, weil ein Paket nicht sich selbst
# enthalten kann:
#
#     1. Durchgang: beide Pakete ohne Installer darin.
#     2. Durchgang: dieselben Pakete, mit den Dateien aus Durchgang 1.
#
# Die eingebetteten Installer sind also die schlanken aus Durchgang 1. Das
# genügt für den Weg zwischen zwei Rechnern; wer von dort weiterzieht,
# holt sich das Paket aus dem Repository.
#
# Aufruf:  packaging/bauen.sh
# Braucht: dpkg-deb (Debian-Paket), makepkg (Arch-Paket, nur auf Arch)

set -euo pipefail

HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WURZEL="$(dirname "$HIER")"
FERTIG="$HIER/fertig"
BAU="$(mktemp -d)"
trap 'rm -rf "$BAU"' EXIT

FASSUNG="$(python3 -c "import sys; sys.path.insert(0, '$WURZEL'); import profilkoffer; print(profilkoffer.__version__)")"
DEB="profilkoffer_${FASSUNG}_all.deb"
ARCH="profilkoffer-${FASSUNG}-1-any.pkg.tar.zst"

echo "PROFILKoffer $FASSUNG"
mkdir -p "$FERTIG"
rm -f "$FERTIG"/*.deb "$FERTIG"/*.pkg.tar.zst

# -- Der gemeinsame Dateibaum ---------------------------------------------

baum_anlegen() {
    local ziel="$1"
    rm -rf "$ziel"
    mkdir -p "$ziel/usr/lib/profilkoffer" \
             "$ziel/usr/bin" \
             "$ziel/usr/share/applications" \
             "$ziel/usr/share/profilkoffer"

    cp -r "$WURZEL/profilkoffer" "$ziel/usr/lib/profilkoffer/"
    find "$ziel/usr/lib/profilkoffer" -name '__pycache__' -type d -exec rm -rf {} +

    # Ein Startskript statt eines Einstiegspunkts aus setuptools: Das Paket
    # soll ohne pip auskommen und nichts in Pythons Verzeichnisse legen.
    cat > "$ziel/usr/bin/profilkoffer" <<'STARTER'
#!/bin/sh
exec python3 -c 'import sys; sys.path.insert(0, "/usr/lib/profilkoffer"); from profilkoffer.__main__ import main; sys.exit(main())' "$@"
STARTER
    chmod 755 "$ziel/usr/bin/profilkoffer"

    cp "$WURZEL/desktop/profilkoffer.desktop" "$ziel/usr/share/applications/"

    # Die Symbole nach hicolor, in den Größen, die es gibt. Der
    # Desktop-Eintrag zeigt auf »Icon=profilkoffer« ohne Pfad und ohne
    # Endung - die Arbeitsumgebung sucht sich die passende Größe selbst.
    for groesse in 16 24 32 48 64 128 256 512; do
        quelle="$WURZEL/assets/icon-${groesse}.png"
        [ -f "$quelle" ] || continue
        ziel_icon="$ziel/usr/share/icons/hicolor/${groesse}x${groesse}/apps"
        mkdir -p "$ziel_icon"
        cp "$quelle" "$ziel_icon/profilkoffer.png"
    done

    if [ -f "$WURZEL/assets/icon.svg" ]; then
        mkdir -p "$ziel/usr/share/icons/hicolor/scalable/apps"
        cp "$WURZEL/assets/icon.svg" "$ziel/usr/share/icons/hicolor/scalable/apps/profilkoffer.svg"
    fi
}

deb_bauen() {
    local ziel="$1" ausgabe="$2"
    mkdir -p "$ziel/DEBIAN"
    cat > "$ziel/DEBIAN/control" <<CONTROL
Package: profilkoffer
Version: $FASSUNG
Architecture: all
Maintainer: Stephan Roesner
Depends: python3 (>= 3.11), python3-tk, util-linux, procps
Section: utils
Priority: optional
Description: Thunderbird und Vivaldi von einem Rechner auf den anderen
 Packt die Profile von Thunderbird und Vivaldi mitsamt Konten,
 Zugangsdaten, Lesezeichen und Erweiterungen in eine Datei und spielt
 sie auf einem anderen Rechner wieder ein.
 .
 Beim Einspielen wird der bisherige Stand vollstaendig ersetzt, nicht
 ergaenzt - sonst stuenden hinterher die alten Lesezeichen neben den
 neuen. Der alte Stand bleibt als Ordner daneben liegen.
 .
 Laeuft auf Debian 13 und auf Arch/Manjaro.
CONTROL
    dpkg-deb --root-owner-group -b "$ziel" "$ausgabe" > /dev/null
}

arch_bauen() {
    local baumquelle="$1" ausgabe="$2"
    if ! command -v makepkg > /dev/null; then
        echo "   makepkg fehlt - Arch-Paket wird uebersprungen"
        return 1
    fi
    local arbeit="$BAU/arch"
    rm -rf "$arbeit"
    mkdir -p "$arbeit"
    sed "s/@FASSUNG@/$FASSUNG/" "$HIER/PKGBUILD.vorlage" > "$arbeit/PKGBUILD"
    cp -r "$baumquelle" "$arbeit/baum"
    rm -rf "$arbeit/baum/DEBIAN"
    ( cd "$arbeit" && makepkg -f > /dev/null 2>&1 )
    cp "$arbeit"/*.pkg.tar.zst "$ausgabe"
}

# -- Durchgang 1: schlanke Pakete -----------------------------------------

echo "Durchgang 1 ..."
baum_anlegen "$BAU/baum"
deb_bauen "$BAU/baum" "$BAU/$DEB"
arch_bauen "$BAU/baum" "$BAU/$ARCH" || true

# -- Durchgang 2: mit beiden Installern darin -----------------------------

echo "Durchgang 2 ..."
baum_anlegen "$BAU/baum"
cp "$BAU/$DEB" "$BAU/baum/usr/share/profilkoffer/" 2>/dev/null || true
cp "$BAU/$ARCH" "$BAU/baum/usr/share/profilkoffer/" 2>/dev/null || true
deb_bauen "$BAU/baum" "$FERTIG/$DEB"
arch_bauen "$BAU/baum" "$FERTIG/$ARCH" || true

echo
ls -lh "$FERTIG"
