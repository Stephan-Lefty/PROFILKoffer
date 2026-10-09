[Deutsch](TODO.md) | [English](TODO.en.md) | [Overview](README.en.md) | [Changelog](CHANGELOG.md)

# TODO

Running list of open points. What is still open stands at the top. Finished
items are not deleted but moved down – with the date they were done.

## Open

- [ ] **Walk the Debian → Manjaro path once.** Only the other direction has
  been tried, and that with the predecessor script. Until this has been
  done, the README makes a promise nobody has verified.

- [ ] **Make a real backup with this version.** The tests run against
  profiles from `tempfile`, not against 4.5 GiB of real mail. What differs
  at that size: the duration, the space needed while unpacking, and whether
  the window stays responsive over several minutes.

- [ ] **An icon.** The desktop entry points at `Icon=profilkoffer`, which
  does not exist yet – the menu shows a placeholder. The colours are already
  settled ([profilkoffer/farben.py](profilkoffer/farben.py)).

- [ ] **Add Firefox and Chromium?** Their profiles live in a single folder
  just the same. The open question is not how, but whether the program
  becomes cluttered – with two programs no selection is needed, with five it
  is.

- [ ] **Check free space before unpacking.** It is checked before packing,
  but not before unpacking. A 4.5 GiB archive needs several times that while
  unpacking, and the old profile is still lying beside it at that point.

- [ ] **Offer to delete the old `*_alt_*` folders.** They pile up with every
  restore and each takes the full profile size. The program must not delete
  them on its own – asking is fine.

## Done

- [x] **Turn the single script into a program.** 2026-10-09. Logic separated
  from the interface, 85 tests, CI, packages for both systems.
