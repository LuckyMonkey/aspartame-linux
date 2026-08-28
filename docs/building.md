# Building

Build from an Arch Linux environment with `archiso` installed:

```sh
make iso
make test
```

`out/` contains generated images and `work/` contains archiso working data;
neither is committed. This Ubuntu workstation does not currently have
`mkarchiso`, so the repository reports that prerequisite clearly instead of
silently using a non-Arch substitute.

