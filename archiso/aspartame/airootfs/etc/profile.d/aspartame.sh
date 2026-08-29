export XDG_CURRENT_DESKTOP=Sugar
export XDG_SESSION_DESKTOP=sugar

# Keep the familiar command name while using Arch's maintained replacement.
if test -x /usr/bin/fastfetch; then
    alias neofetch=fastfetch
fi

# Keep user environments separate from Arch system Python.
if test -x "$HOME/.aspartame/miniconda3/bin/conda"; then
    export PATH="$HOME/.aspartame/miniconda3/bin:$PATH"
fi
