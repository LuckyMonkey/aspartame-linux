# Conda and application environments

The bootstrap image includes Arch's signed `python-pip`, `python-pipx`, and
`python-virtualenv`. These are for user environments and must not be used to
modify Arch's system Python with `sudo pip`.

Miniconda is available through the explicit `aspartame-install-miniconda`
command. It downloads the current official Anaconda installer, verifies its
published SHA-256 file, and installs into `~/.aspartame/miniconda3`. It is not
downloaded automatically and does not replace `/usr/bin/python`.

Navigator and Jupyter remain future integration work; they should appear as
Activities or Activity-like applications after the environment substrate is
stable.

Activity environment manifests may eventually describe isolated dependencies
and be provisioned on demand. Isolation comes before deduplication: unrelated
Activities should not silently share environments and create dependency
conflicts. The system Python remains outside this mechanism.

