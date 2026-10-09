[Deutsch](README.md) | [English](README.en.md) | [Changelog](CHANGELOG.md) | [TODO](TODO.en.md) | [Guides](docs/README.md)

# PROFILKoffer

Moving Thunderbird and Vivaldi from one computer to another – with
everything that belongs to them.

Accounts and credentials, bookmarks and extensions, filters and settings:
each program keeps all of it in exactly one folder. PROFILKoffer packs that
folder into a single file, puts it on a USB drive and restores it on the
other machine. Afterwards the state is the same one – not a similar one.

*PROFILKoffer* is German for »profile suitcase«.

**For Debian 13 and Arch/Manjaro.** Both are intended from the start. That
is not a given: the default for unpacking archives changed between Python
3.13 (Debian) and 3.14 (Manjaro), and the move would have failed in one
direction because of it.

## What travels

| Program | Folder | Contains among others |
|---|---|---|
| Thunderbird | `~/.thunderbird` | accounts, passwords (`key4.db`, `logins.json`), local folders, filters, extensions |
| Vivaldi | `~/.config/vivaldi` | bookmarks, settings, extensions, sessions, speed dial |

Passwords are encrypted, but not tied to anything that stays behind on the
old machine. They survive the move.

## The old state has to go, or nothing adds up

This is the one promise everything else rests on: after restoring, **exactly**
the bookmarks and accounts of the other machine are there. No old ones
beside them, no duplicates, none from an earlier session.

PROFILKoffer does three things for this, and only the first is obvious:

1. **The existing folder is moved aside**, not overwritten. Only then is the
   archive unpacked. Mixing old and new is impossible.

2. **The caches are cleared** (`~/.cache/vivaldi`, `~/.cache/thunderbird`).
   They still hold the old machine's state.

3. **Restoring refuses to start while a program is running.** An open
   Vivaldi keeps its bookmarks in memory and writes them back on exit – over
   everything just restored. The old bookmarks would be back and nobody
   would know why.

   There is deliberately no dialog to click away here.

Nothing is deleted: the previous state is left beside the new one as
`~/.thunderbird_alt_<date>` and `~/.config/vivaldi_alt_<date>`.

## Installing

The lasting way is a package:

```
packaging/bauen.sh

sudo apt install ./packaging/fertig/profilkoffer_*.deb        # Debian
sudo pacman -U packaging/fertig/profilkoffer-*.pkg.tar.zst    # Arch/Manjaro
```

To try it out, or on someone else's machine:

```
./install.sh
```

Either way you get an entry under *Utilities*.

## The packages travel along

When packing, PROFILKoffer puts the installers for Debian **and** Arch next
to the backup on the drive. This is not a nicety: PROFILKoffer is not yet
installed on the target machine, and without it there is no way to get at
the backup. The drive then holds:

```
profilkoffer_20261009_103000.tar.gz     the backup
profilkoffer_0.1.0_all.deb              for Debian
profilkoffer-0.1.0-1-any.pkg.tar.zst    for Arch/Manjaro
```

## Using it

The window has two buttons and a log below them. **F1** opens the help – it
lives in the program, not only here.

The same works from the command line. On a machine whose desktop no longer
starts, that is the only way to your own mail – and that is exactly when a
backup matters most:

```
profilkoffer profile          what is on this machine
profilkoffer laufwerke        where it can be written
profilkoffer packen TARGET
profilkoffer sicherungen      what was found
profilkoffer auspacken FILE --ja
```

## Drives are named the way they are named

Tk's file dialog shows mount points under their device identifiers:

```
/run/media/stephan/89b24b6c-3bf3-4bb9-83dc-dcd6c94013291
```

The file manager shows »NTFS-Mobil« in the same place. PROFILKoffer reads
the volume label via `lsblk` and shows it the same way, together with the
free space.

## Checked before, not noticed halfway through

**FAT32 refuses any file above 4 GiB.** A Thunderbird archive easily exceeds
that – the first one made here was 4.5 GiB. Without warning, writing fails
after a quarter of an hour and leaves half a file on the drive that looks
like a valid backup in the list.

PROFILKoffer reads the filesystem from `/proc/mounts`, estimates the size
beforehand and says so before the first block is written. The same goes for
insufficient space.

If a run fails anyway, the partial file is removed.

## Working on it

```
git clone https://github.com/Stephan-Lefty/PROFILKoffer.git
cd PROFILKoffer
./install.sh
python3 -m unittest discover -s tests -v
```

The logic lives in `profilkoffer/` and knows nothing about Tk; the interface
lives in `profilkoffer/ui/` and holds no logic. That is why replacing a
profile can be tested at all – the tests run the whole path against a
substituted home directory, without touching a real profile.

## Licence

[MIT](LICENSE)
