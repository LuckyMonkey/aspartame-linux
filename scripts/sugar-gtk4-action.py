#!/usr/bin/env python3
"""Invoke canonical semantic actions on the running GTK4 Sugar shell."""

import argparse

import dbus


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("home",),
                        help="semantic action to invoke")
    args = parser.parse_args()

    bus = dbus.SessionBus()
    shell = dbus.Interface(
        bus.get_object("org.laptop.Shell", "/org/laptop/Shell"),
        "org.laptop.Shell")
    result = shell.ShowHome()
    print(f"action={args.action} result={bool(result)}")
    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())
