# SPDX-FileCopyrightText: 2025 Patrick McCarty <pnorcks@gmail.com>
#
# SPDX-License-Identifier: MIT

from importlib.resources import open_text
import sys

from rich import print as rprint


def debug(msg):
    rprint(fr"[purple italic]\[DEBUG][/purple italic] {msg}")


def info(msg):
    rprint(fr"[bold blue]\[INFO][/bold blue] {msg}")


def warning(msg):
    rprint(fr"[bold yellow]\[WARNING][/bold yellow] {msg}")


def error(msg):
    rprint(fr"[bold red]\[ERROR][/bold red] {msg}")


def fatal(s):
    error(f"{s}")
    sys.exit(1)


def int_in_range(val):
    ret = True
    try:
        orig = val
        test = int(orig)
        if test < 0 or test > 127:
            ret = False
    except:
        ret = False

    return ret


def load_id_name_mapping():
    mapping = dict()
    with open_text("midi_velocity_mapper", "data/keys-all.tsv") as f:
        for line in f:
            fields = line.split()
            note_id = fields[0]
            note_name = fields[1]
            mapping[note_id] = note_name
    return mapping


# FIXME: should merge this function with the previous one
def load_name_id_mapping():
    mapping = dict()
    with open_text("midi_velocity_mapper", "data/keys-all.tsv") as f:
        for line in f:
            fields = line.split()
            note_id = fields[0]
            note_name = fields[1]
            mapping[note_name] = note_id
    return mapping
