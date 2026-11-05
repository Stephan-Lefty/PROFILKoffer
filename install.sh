#!/usr/bin/env bash
#
# Richtet PROFILKoffer im eigenen Benutzerkonto ein - ohne sudo, ohne
# Paketmanager, ohne venv.
#
# Kein venv, weil es nichts zu kapseln gibt: PROFILKoffer hat keine
# Abhängigkeit aus PyPI. Was es braucht, bringt Python mit (tarfile,
# shutil, tkinter) oder das System (lsblk, pgrep). Ein venv wäre hier
# ein leeres Verzeichnis mit einem Symlink darin.
#
# Für den dauerhaften Betrieb ist das Paket der bessere Weg:
#
#     packaging/bauen.sh                             # baut beide Pakete
#     sudo apt install ./packaging/fertig/*.deb      # Debian
#     sudo pacman -U packaging/fertig/*.pkg.tar.zst  # Arch/Manjaro
#
# Dieses Skript ist für die Entwicklung und für den Fall, dass man es
# schnell auf einem fremden Rechner braucht.

set -euo pipefail

HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZIEL_BIN="$HOME/.local/bin"
ZIEL_DESKTOP="$HOME/.local/share/applications"

# -- Python ---------------------------------------------------------------

if ! command -v python3 > /dev/null; then
    echo "python3 fehlt." >&2
    exit 1
fi

python3 - <<'PRUEFEN' || exit 1
import sys
if sys.version_info < (3, 11):
    print(f"Python 3.11 oder neuer wird gebraucht, gefunden: "
          f"{sys.version_info.major}.{sys.version_info.minor}", file=sys.stderr)
    raise SystemExit(1)
PRUEFEN

# Tkinter kommt aus der Distribution, nicht aus pip. Fehlt es, hilft nur
# der Paketmanager - deshalb steht hier der Befehl und keine Fehlermeldung,
# die man erst suchen muss.
if ! python3 -c "import tkinter" 2> /dev/null; then
    echo "Tkinter fehlt. Es kommt aus der Distribution, nicht aus pip:" >&2
    echo >&2
    echo "    Debian/Ubuntu   sudo apt install python3-tk" >&2
    echo "    Arch/Manjaro    sudo pacman -S tk" >&2
    exit 1
fi

for werkzeug in lsblk pgrep; do
    if ! command -v "$werkzeug" > /dev/null; then
        echo "Hinweis: $werkzeug fehlt." >&2
        if [ "$werkzeug" = "pgrep" ]; then
            # Ohne pgrep gelten alle Programme als laufend, und das
            # Einspielen bricht immer ab. Das ist Absicht, aber es sollte
            # niemanden überraschen.
            echo "  Ohne pgrep laesst sich nicht pruefen, ob Thunderbird oder" >&2
            echo "  Vivaldi noch laufen. Das Einspielen bricht dann immer ab." >&2
            echo "  Debian: sudo apt install procps / Arch: sudo pacman -S procps-ng" >&2
        else
            echo "  Ohne lsblk heissen die Laufwerke nach ihrem Einhaengepunkt" >&2
            echo "  statt nach ihrem Datentraegernamen." >&2
            echo "  Debian: sudo apt install util-linux / Arch: sudo pacman -S util-linux" >&2
        fi
    fi
done

# -- Starter --------------------------------------------------------------

mkdir -p "$ZIEL_BIN" "$ZIEL_DESKTOP"

cat > "$ZIEL_BIN/profilkoffer" <<STARTER
#!/bin/sh
exec python3 -c 'import sys; sys.path.insert(0, "$HIER"); from profilkoffer.__main__ import main; sys.exit(main())' "\$@"
STARTER
chmod 755 "$ZIEL_BIN/profilkoffer"

sed "s|^Exec=.*|Exec=$ZIEL_BIN/profilkoffer|" \
    "$HIER/desktop/profilkoffer.desktop" > "$ZIEL_DESKTOP/profilkoffer.desktop"
# Die Angaben für die Software-Verwaltung. Ohne sie kennt GNOME
# Software, Discover oder pamac das Programm nicht - es erscheint dort
# weder unter den installierten noch lässt es sich von dort entfernen.
METADATEN="${XDG_DATA_HOME:-$HOME/.local/share}/metainfo"
mkdir -p "$METADATEN"
cp "$HIER/desktop/"*.metainfo.xml "$METADATEN/" 2>/dev/null || true
# Unter KDE bliebe der Menüeintrag sonst bis zum nächsten Anmelden
# unsichtbar. Anderswo läuft die Zeile ins Leere.
command -v kbuildsycoca6 >/dev/null 2>&1 \
    && kbuildsycoca6 --noincremental >/dev/null 2>&1 || true


# Die Symbole nach hicolor im eigenen Konto. Ohne sie steht im Menue ein
# Platzhalter - der Eintrag zeigt auf »Icon=profilkoffer« ohne Pfad.
ZIEL_ICONS="$HOME/.local/share/icons/hicolor"
for groesse in 16 24 32 48 64 128 256 512; do
    quelle="$HIER/assets/icon-${groesse}.png"
    [ -f "$quelle" ] || continue
    mkdir -p "$ZIEL_ICONS/${groesse}x${groesse}/apps"
    cp "$quelle" "$ZIEL_ICONS/${groesse}x${groesse}/apps/profilkoffer.png"
done

if [ -f "$HIER/assets/icon.svg" ]; then
    mkdir -p "$ZIEL_ICONS/scalable/apps"
    cp "$HIER/assets/icon.svg" "$ZIEL_ICONS/scalable/apps/profilkoffer.svg"
fi

if command -v update-desktop-database > /dev/null; then
    update-desktop-database "$ZIEL_DESKTOP" 2> /dev/null || true
fi

# Die Arbeitsumgebung merkt eine neue Datei im Symbolverzeichnis erst,
# wenn der Zwischenspeicher angefasst wurde.
if command -v gtk-update-icon-cache > /dev/null; then
    gtk-update-icon-cache -f -t "$ZIEL_ICONS" 2> /dev/null || true
fi

echo "PROFILKoffer ist eingerichtet."
echo
echo "    profilkoffer            Oberflaeche"
echo "    profilkoffer --help     Kommandozeile"
echo
echo "Im Menue steht es unter Dienstprogramme."

case ":$PATH:" in
    *":$ZIEL_BIN:"*) ;;
    *)
        echo
        echo "Achtung: $ZIEL_BIN liegt nicht im PATH."
        echo "Diese Zeile gehoert in ~/.profile oder ~/.zshrc:"
        echo
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        ;;
esac
