[Deutsch](umzug.md) | [English](umzug.en.md) | [Guides](README.md) | [Overview](../README.en.md)

# The move, step by step

## On the old machine

**1. Close Thunderbird and Vivaldi.**

Not just the window – the program. Vivaldi keeps running with its window
closed if its icon is still in the system tray. To check:

```
profilkoffer profile
```

The last line says what is running.

**2. Attach a drive.**

The filesystem matters. FAT32 refuses any file above 4 GiB, and a
Thunderbird archive easily exceeds that. PROFILKoffer shows the filesystem
in the drive list and warns beforehand. Ext4, btrfs and NTFS are fine.

**3. Start PROFILKoffer, pick a drive, pack.**

This takes a while. At 4.5 GiB it is several minutes; the button reads
»Packen …« and is greyed out meanwhile. The log below shows where it stands.

From the command line:

```
profilkoffer laufwerke
profilkoffer packen /run/media/USER/Linux-Mobil
```

**4. Check what is on the drive.**

There should be three files:

```
profilkoffer_20261009_103000.tar.gz     the backup
profilkoffer_0.1.0_all.deb              for Debian
profilkoffer-0.1.0-1-any.pkg.tar.zst    for Arch/Manjaro
```

PROFILKoffer adds the two packages because it is not yet installed on the
other machine.

## On the new machine

**5. Install PROFILKoffer.**

```
sudo apt install /path/to/drive/profilkoffer_0.1.0_all.deb         # Debian
sudo pacman -U /path/to/drive/profilkoffer-0.1.0-1-any.pkg.tar.zst # Arch
```

The dependencies – Python, Tkinter, `util-linux`, `procps` – come with it.

**6. Close Thunderbird and Vivaldi here too.**

PROFILKoffer refuses otherwise. That is not a defect but the reason the move
is reliable at all – see [warum-abbruch.md](warum-abbruch.md).

**7. Pick the backup and unpack.**

PROFILKoffer searches all mounted drives, `Downloads`, the desktop and
`Dokumente` on its own – two levels deep each. If it finds nothing,
»Andere Datei …« opens the file dialog.

Before unpacking there is a confirmation: the existing state will be
replaced.

From the command line:

```
profilkoffer sicherungen
profilkoffer auspacken /path/to/profilkoffer_20261009_103000.tar.gz --ja
```

**8. Start and check.**

Check the bookmarks first, then sign in to Vivaldi Sync. The other way
round, the service pulls the old state back from the cloud and both states
end up side by side.

## Afterwards

The previous state is still there:

```
~/.thunderbird_alt_20261009_104500
~/.config/vivaldi_alt_20261009_104500
```

These folders take up the full profile size. They may go once the new state
is demonstrably correct – that is, after both programs have run once and
fetched their accounts. Not before.
