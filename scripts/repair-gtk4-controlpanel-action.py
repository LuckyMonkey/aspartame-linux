#!/usr/bin/env python3
"""Repair the truncated 0058 action in previously exported GTK4 runtimes."""

import ast
from pathlib import Path
import sys


def repair(source):
    tree = ast.parse(source.removeprefix('\ufeff'))
    owner = next(node for node in tree.body
                 if isinstance(node, ast.ClassDef) and node.name == 'UIService')
    method = next(node for node in owner.body
                  if isinstance(node, ast.FunctionDef)
                  and node.name == 'ShowControlPanel')
    expected = ast.parse('self._control_panel = panel\nreturn True').body
    if ([ast.dump(node) for node in method.body[-2:]] ==
            [ast.dump(node) for node in expected]):
        return source
    # Only repair the known truncated form. Refuse unfamiliar implementations
    # rather than silently rewriting a future control-panel lifecycle.
    last = ast.parse('panel.set_visible(True)').body[0]
    if ast.dump(method.body[-1]) != ast.dump(last):
        raise ValueError('unrecognized ShowControlPanel implementation')
    lines = source.splitlines(keepends=True)
    lines.insert(method.end_lineno,
                 '        self._control_panel = panel\n        return True\n')
    result = ''.join(lines)
    ast.parse(result.removeprefix('\ufeff'))
    return result


def main():
    path = Path(sys.argv[1])
    source = path.read_text()
    result = repair(source)
    if result != source:
        path.write_text(result)
        print('repaired GTK4 Control Panel ownership and success result')
    else:
        print('verified GTK4 Control Panel ownership and success result')


if __name__ == '__main__':
    main()
